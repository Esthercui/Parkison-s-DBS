"""Saved-data statistics, figures and acceptance checks for Stage 3 validation."""
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

METHODS = ["Random", "GA", "BO", "CMA-ES", "Surrogate (Pool)",
           "Surrogate (Exhaustive)", "QAOA (p=1)"]
BUDGETS = [10, 20, 30, 40]
SEED = 20261003
TOL = 1e-12


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def bootstrap_mean(values, seed):
    values = np.asarray(values)
    rng = np.random.default_rng(seed)
    means = values[rng.integers(len(values), size=(10000, len(values)))].mean(axis=1)
    return tuple(float(x) for x in np.quantile(means, [.025, .975]))


def paired_randomization(difference, seed):
    # Two-sided sign randomization of paired differences; ties contribute zero.
    d = np.asarray(difference).copy()
    d[np.abs(d) <= TOL] = 0
    d = d[d != 0]
    if not len(d):
        return 1., "all ties", 1
    observed = abs(d.sum())
    if len(d) <= 16:
        signs = 1-2*((np.arange(2**len(d))[:, None] >> np.arange(len(d))) & 1)
        null = np.abs(signs @ d)
        return float(np.mean(null >= observed-1e-14)), "exact paired sign randomization", len(null)
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(100):
        signs = rng.integers(0, 2, size=(1000, len(d)))*2-1
        exceed += int(np.sum(np.abs(signs @ d) >= observed-1e-14))
    return (exceed+1)/100001, "Monte Carlo paired sign randomization (plus-one)", 100000


def holm(values):
    values = np.asarray(values)
    order = np.argsort(values)
    adjusted = np.maximum.accumulate(values[order]*(len(values)-np.arange(len(values))))
    result = np.empty(len(values))
    result[order] = np.minimum(adjusted, 1)
    return result


def statistics(out):
    runs = pd.read_csv(out/"optimizer_runs.csv")
    cfg = json.loads((out/"run_configuration.json").read_text())
    assert cfg["statistical_plan"]["bootstrap_resamples"] == 10000
    assert cfg["statistical_plan"]["paired_permutation_resamples"] == 100000
    rows = []
    for budget in BUDGETS:
        for index, method in enumerate(METHODS):
            r = runs[(runs.budget == budget) & (runs.method == method)].sort_values("seed")
            assert r.seed.tolist() == list(range(30))
            v = r.regret.to_numpy()
            low, high = bootstrap_mean(v, SEED+budget*100+index)
            q1, q3 = np.quantile(v, [.25, .75])
            rows.append(dict(budget=budget, method=method, n=len(v), mean_regret=float(v.mean()),
                population_sd=float(v.std(ddof=0)), median_regret=float(np.median(v)),
                q1=float(q1), q3=float(q3), iqr=float(q3-q1), minimum=float(v.min()),
                maximum=float(v.max()), mean_ci_low=low, mean_ci_high=high,
                feasible_success_rate=float(r.feasible.mean())))
    summary = pd.DataFrame(rows)
    summary["descriptive_rank"] = summary.groupby("budget").mean_regret.rank(method="min").astype(int)
    summary.to_csv(out/"optimizer_summary.csv", index=False)
    pairs = []
    for ci, comparator in enumerate(METHODS[4:6]):
        for budget in BUDGETS:
            q = runs[(runs.method == METHODS[-1]) & (runs.budget == budget)].set_index("seed").sort_index()
            c = runs[(runs.method == comparator) & (runs.budget == budget)].set_index("seed").sort_index()
            assert q.index.equals(c.index)
            d = (q.regret-c.regret).to_numpy()
            low, high = bootstrap_mean(d, SEED+10000+budget*100+ci)
            p, test, draws = paired_randomization(d, SEED+20000+budget*100+ci)
            pairs.append(dict(budget=budget, comparator=comparator, n=len(d),
                mean_difference=float(d.mean()), median_difference=float(np.median(d)),
                paired_ci_low=low, paired_ci_high=high, qaoa_wins=int((d < -TOL).sum()),
                ties=int((np.abs(d) <= TOL).sum()), qaoa_losses=int((d > TOL).sum()),
                p_two_sided=p, test=test, randomizations=draws,
                family="principal" if ci == 1 else "secondary"))
    paired = pd.DataFrame(pairs)
    for comparator in METHODS[4:6]:
        selected = paired.comparator == comparator
        paired.loc[selected, "p_holm_four_budgets"] = holm(paired.loc[selected, "p_two_sided"])
    paired.to_csv(out/"paired_statistics.csv", index=False)
    trace = pd.read_csv(out/"qaoa_trace.csv")
    fallback = []
    def aggregate(scope, budget, step, t):
        unseen = t.unseen_admissible_unique
        fb = t.proposal_source == "CLASSICAL_FALLBACK"
        return dict(scope=scope, budget=budget, adaptive_step=step, proposals=len(t),
            qaoa_sample_proposals=int((~fb).sum()), fallback_proposals=int(fb.sum()),
            fallback_rate=float(fb.mean()), no_unseen_candidate_steps=int(t.no_unseen_admissible_candidate.sum()),
            mean_admissible_shot_fraction=float(t.admissible_shot_fraction.mean()),
            median_admissible_shot_fraction=float(t.admissible_shot_fraction.median()),
            mean_exact_admissible_mass=float(t.exact_admissible_mass.mean()),
            median_exact_admissible_mass=float(t.exact_admissible_mass.median()),
            unseen_min=int(unseen.min()), unseen_q1=float(unseen.quantile(.25)),
            unseen_median=float(unseen.median()), unseen_q3=float(unseen.quantile(.75)),
            unseen_mean=float(unseen.mean()), unseen_max=int(unseen.max()),
            total_internal_shots=int(t.total_qaoa_shots.sum()), total_circuits=int(t.total_qaoa_circuits.sum()),
            cobyla_budget_exhaustions=int((t.cobyla_status == 3).sum()),
            same_history_exhaustive_agreements=int((t.selected_mask == t.same_history_exhaustive_mask).sum()),
            mean_selected_surrogate_gap=float(t.selected_surrogate_gap.mean()),
            sample_best_cost_improvement=float((t.best_cost_before-t.best_cost_after)[~fb].sum()),
            fallback_best_cost_improvement=float((t.best_cost_before-t.best_cost_after)[fb].sum()))
    fallback.append(aggregate("overall", "", "", trace))
    fallback.extend(aggregate("budget", b, "", t) for b, t in trace.groupby("budget"))
    fallback.extend(aggregate("adaptive_step", "", s, t) for s, t in trace.groupby("adaptive_step"))
    pd.DataFrame(fallback).to_csv(out/"qaoa_fallback_summary.csv", index=False)
    distribution = trace.groupby(["budget", "unseen_admissible_unique"]).size().rename("steps").reset_index()
    distribution.to_csv(out/"qaoa_unseen_candidate_distribution.csv", index=False)
    # Recorded diagnostics for all parameter-search circuits, separate from final 1024-shot proposals.
    training = pd.read_json(out/"qaoa_optimizer_history.jsonl.gz", lines=True, compression="gzip")
    training_summary = training.groupby("budget").agg(circuits=("shots", "size"), shots=("shots", "sum"),
        admissible_shots=("admissible_shots", "sum"), mean_admissible_fraction=("admissible_shot_fraction", "mean"))
    training_summary.to_csv(out/"qaoa_parameter_search_summary.csv")
    plan = cfg["statistical_plan"] | dict(bootstrap="Percentile CI for seed-level mean, 10000 resamples",
        pairing="QAOA minus comparator; same seed and exact initial observations; independent adaptive histories",
        randomization="Two-sided sign randomization of paired differences; exact if <=16 nonzero pairs, otherwise 100000 draws with plus-one correction",
        ties="abs(difference)<=1e-12; ties set to zero in randomization; observed differences retained for estimates and bootstrap",
        holm="Separate four-budget families: Exhaustive principal, Pool secondary; no claims based on ranks alone",
        initialization_at_b10="9 shared observations and 1 adaptive evaluation; other budgets start with 10",
        uncertainty_scope="Variation over algorithm seeds on one deterministic fitted benchmark, not biological uncertainty")
    save_json(out/"statistical_analysis_plan.json", plan)
    print(summary.to_string(index=False))
    print(paired.to_string(index=False))


def figures(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "pdf.fonttype": 42, "svg.fonttype": "none",
        "axes.labelsize": 11, "legend.fontsize": 8, "savefig.dpi": 300})
    target = out/"figures"
    target.mkdir(exist_ok=True)
    colors = dict(zip(METHODS, ["#777777", "#009E73", "#0072B2", "#CC79A7", "#E69F00", "#6D4C41", "#D55E00"]))
    def save(fig, name):
        for suffix in ("png", "pdf", "svg"):
            fig.savefig(target/f"{name}.{suffix}", bbox_inches="tight")
        plt.close(fig)
    summary = pd.read_csv(out/"optimizer_summary.csv")
    fig, ax = plt.subplots(figsize=(8.6, 5.4), layout="constrained")
    for i, method in enumerate(METHODS):
        t = summary[summary.method == method].sort_values("budget")
        ax.errorbar(t.budget+(i-3)*.21, t.mean_regret,
            yerr=np.vstack([t.mean_regret-t.mean_ci_low, t.mean_ci_high-t.mean_regret]),
            label=method, color=colors[method], marker="o", markersize=4, capsize=2, linewidth=1.4)
    ax.set(xlabel="True-objective evaluation budget", ylabel="Mean regret (lower is better)",
        xticks=BUDGETS, ylim=(0, None), title="Stage 3: corrected fixed-cardinality benchmark")
    ax.grid(axis="y", alpha=.2)
    ax.legend(loc="upper right", ncol=2, frameon=False)
    fig.supxlabel("30 matched seeds · k = 6 · fitted BetaRatio ≤ 0.8228585 · 95% bootstrap CIs", fontsize=9)
    save(fig, "stage3_regret_vs_budget")
    runs = pd.read_csv(out/"optimizer_runs.csv")
    paired = pd.read_csv(out/"paired_statistics.csv")
    fig, ax = plt.subplots(figsize=(8.2, 5), layout="constrained")
    extremes = []
    for index, budget in enumerate(BUDGETS):
        p = runs[runs.budget == budget].pivot(index="seed", columns="method", values="regret")
        d = (p[METHODS[-1]]-p[METHODS[-2]]).to_numpy()
        t = paired[(paired.budget == budget) & (paired.comparator == METHODS[-2])].iloc[0]
        jitter = np.random.default_rng(SEED+budget).uniform(-.16, .16, len(d))
        ax.scatter(index+jitter, d, s=23, color="#666666", alpha=.65, edgecolors="none")
        ax.errorbar(index+.27, t.mean_difference,
            yerr=[[t.mean_difference-t.paired_ci_low], [t.paired_ci_high-t.mean_difference]],
            color=colors[METHODS[-1]], fmt="D", capsize=4, markersize=6)
        extremes.extend(d)
    limit = max(abs(np.array(extremes)))*1.12
    ax.axhline(0, color="black", linewidth=.9)
    ax.set(xticks=range(4), xticklabels=BUDGETS, xlabel="True-objective evaluation budget",
        ylabel="Paired regret difference: QAOA − Exhaustive", ylim=(-limit, limit),
        title="Positive differences favor Surrogate (Exhaustive)")
    ax.grid(axis="y", alpha=.2)
    fig.supxlabel("Each dot is one matched seed; diamonds and bars are mean difference and paired 95% bootstrap CI", fontsize=9)
    save(fig, "stage3_qaoa_vs_surrogate_exhaustive")
    beta = pd.read_csv(out/"beta_fit_validation.csv")
    t = beta[beta.global_uniform_grid].sort_values("effective_amplitude")
    metrics = json.loads((out/"beta_fit_metrics.json").read_text())
    lower = metrics["primary_k6_interval"]["amplitude_min"]
    upper = metrics["primary_k6_interval"]["amplitude_max"]
    fig, axes = plt.subplots(2, 1, figsize=(8.2, 6.2), sharex=True, layout="constrained", gridspec_kw={"height_ratios": [2.1, 1]})
    axes[0].plot(t.effective_amplitude, t.direct_beta_ratio, color="#0072B2", label="Direct STN–GPe")
    axes[0].plot(t.effective_amplitude, t.fitted_beta_ratio, color="#D55E00", label="Original quadratic fit")
    axes[0].axhline(.8228585, color="#444444", linestyle="--", linewidth=1, label="Inherited benchmark threshold")
    for ax in axes:
        ax.axvspan(lower, upper, color="#009E73", alpha=.16, label="k = 6 reachable interval")
        ax.grid(alpha=.15)
    axes[0].set(ylabel="BetaRatio", title="Validation of the unchanged Stage 3 efficacy approximation")
    axes[0].legend(frameon=False, loc="upper right")
    axes[1].plot(t.effective_amplitude, t.residual, color="#6D4C41")
    axes[1].axhline(0, color="black", linewidth=.8)
    axes[1].set(xlabel="Effective amplitude (model units)", ylabel="Fitted − direct", xlim=(0, 4))
    save(fig, "stage3_beta_fit_validation")
    sens = pd.read_csv(out/"cardinality_sensitivity.csv")
    fig, axes = plt.subplots(2, 1, figsize=(8, 6.3), sharex=True, layout="constrained")
    axes[0].plot(sens.k, sens.minimum_fitted_beta, "o-", color="#D55E00", label="Lowest fitted BetaRatio")
    axes[0].plot(sens.k, sens.best_fitted_beta_direct_ratio, "s-", color="#0072B2", label="Direct simulation at that same mask")
    axes[0].axhline(.8228585, color="#444444", linestyle="--", label="Inherited benchmark threshold")
    axes[0].set(ylabel="BetaRatio", title="Cardinality sensitivity: k = 6 is a benchmark choice")
    axes[0].legend(frameon=False, loc="upper right")
    axes[1].bar(sens.k-.16, 100*sens.fitted_admissible_masks/sens.total_masks, width=.3, color="#D55E00", label="Fitted model")
    axes[1].bar(sens.k+.16, 100*sens.direct_pass_masks/sens.total_masks, width=.3, color="#0072B2", label="Direct simulator")
    axes[1].set(xticks=[4,5,6,7], xlabel="Number of active contacts", ylabel="Masks passing threshold (%)", ylim=(0, 108))
    axes[1].legend(frameon=False, loc="lower right")
    for ax in axes: ax.grid(axis="y", alpha=.15)
    save(fig, "stage3_cardinality_sensitivity")
    trace = pd.read_csv(out/"qaoa_trace.csv")
    fb = pd.read_csv(out/"qaoa_fallback_summary.csv")
    b = fb[fb.scope == "budget"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), layout="constrained")
    for index, budget in enumerate(BUDGETS):
        t = trace[trace.budget == budget]
        # Distribution over adaptive proposal steps; not an independent-seed CI.
        axes[0].boxplot(100*t.admissible_shot_fraction, positions=[index], widths=.42,
            showfliers=False, patch_artist=True, boxprops={"facecolor": "#B3D9EA"}, medianprops={"color": "black"})
        axes[0].scatter(index, 100*t.admissible_shot_fraction.mean(), marker="D", color="#0072B2", s=26, zorder=4)
        axes[0].scatter(index+.17, 100*t.exact_admissible_mass.mean(), marker="x", color="#D55E00", s=30, zorder=4)
    axes[0].set(xticks=range(4), xticklabels=BUDGETS, xlabel="Evaluation budget", ylabel="Admissible final shots (%)", ylim=(0, 100), title="Final 1,024-shot proposal batches")
    axes[0].plot([], [], "D", color="#0072B2", label="Mean sampled fraction")
    axes[0].plot([], [], "x", color="#D55E00", label="Mean exact statevector mass")
    axes[0].legend(frameon=False, loc="upper left")
    axes[1].bar(range(4), b.fallback_rate*100, color="#D55E00", width=.5)
    for index, (_, row) in enumerate(b.iterrows()):
        axes[1].text(index, row.fallback_rate*100+2, f"{int(row.fallback_proposals)}/{int(row.proposals)}", ha="center", fontsize=9)
    axes[1].set(xticks=range(4), xticklabels=BUDGETS, xlabel="Evaluation budget", ylabel="Classical fallback proposals (%)", ylim=(0, 100), title="Fallback among adaptive proposals")
    for ax in axes: ax.grid(axis="y", alpha=.15)
    save(fig, "stage3_qaoa_feasibility_and_fallback")
    (target/"figure_captions.md").write_text("""# Stage 3 validation figure captions

All figures concern the unchanged fitted objective, k=6, fitted BetaRatio ≤ 0.8228585, unless explicitly labeled direct simulation. No figure implies patient validation or anatomical geometry.

**A — stage3_regret_vs_budget.** Thirty matched seeds per method/budget. Mean best-found cost minus exhaustive feasible ground-truth cost; lower is better. Error bars are seed-level 95% percentile bootstrap CIs (10,000 resamples). Small horizontal offsets prevent error-bar overlap and do not change budgets. Data: optimizer_summary.csv and optimizer_runs.csv. These intervals describe optimizer randomness on one model.

**B — stage3_qaoa_vs_surrogate_exhaustive.** Each point is a paired seed difference (QAOA minus Exhaustive); positive favors Exhaustive. Diamonds are means with paired 95% bootstrap CIs. Symmetric limits show every observation and zero. Initial samples are identical; subsequent adaptive histories are independent. Data: optimizer_runs.csv and paired_statistics.csv.

**C — stage3_beta_fit_validation.** The original quadratic approximation and unchanged direct STN–GPe simulator on 401 uniformly spaced amplitudes from 0 to 4. Shading marks the entire reachable k=6 interval, 1.40–1.72. Residual is fitted minus direct. The threshold is inherited from Stage 2, not a clinical treatment threshold. Local metrics use a denser 129-point amplitude grid. Data: beta_fit_validation.csv and beta_fit_metrics.json.

**D — stage3_cardinality_sensitivity.** Top: minimum fitted BetaRatio at each k and direct simulation of that same mask. Bottom: percentage of all C(16,k) masks passing each model's threshold, using cached direct simulations at every unique effective amplitude. Six is a fixed-cardinality design choice; the fit can reject masks that the simulator accepts. Data: cardinality_sensitivity.csv and fit_vs_direct_feasibility.csv.

**E — stage3_qaoa_feasibility_and_fallback.** Left: distribution across final 1,024-shot adaptive batches (median, IQR and 1.5-IQR whiskers; outlier markers omitted), mean sampled admissibility and mean exact statevector mass. Right: fallback rate and numerator/denominator among adaptive proposals. Both axes span 0–100%. Internal 256-shot COBYLA batches are accounted for separately. Raw sample admissibility does not imply a true evaluation: final proposals are filtered and all true evaluations are admissible. Data: qaoa_trace.csv, qaoa_fallback_summary.csv and qaoa_parameter_search_summary.csv.
""")
    print(f"Generated five figures in PNG, PDF and SVG: {target}")


def check(out):
    from stage3_validation_core import sampled_diagnostics
    from validate_stage3 import verify_scope, require_mapping
    verify_scope(out)
    require_mapping(out)
    cfg = json.loads((out/"run_configuration.json").read_text())
    assert cfg["budgets"] == BUDGETS and cfg["seeds"] == list(range(30)) and not cfg["pilot"]
    oracle = np.load(out/"oracle.npz")
    feasible, cost = oracle["feasible"], oracle["cost"]
    assert np.array_equal(feasible, (oracle["active_count"] == 6) & (oracle["beta"] <= .8228585))
    gt = json.loads((out/"ground_truth.json").read_text())
    assert gt["admissible_masks"] == feasible.sum()
    assert cost[feasible].min() == gt["cost"] and int(np.argmin(cost)) == gt["optimal_mask"]
    records = [json.loads(line) for line in (out/"raw_runs.jsonl").read_text().splitlines()]
    keys = {(r["method"], r["budget"], r["seed"]) for r in records}
    assert len(records) == len(keys) == 840
    assert keys == {(m,b,s) for m in METHODS for b in BUDGETS for s in range(30)}
    records = {(r["method"], r["budget"], r["seed"]):r for r in records}
    initial = pd.read_csv(out/"initial_samples_by_seed.csv")
    observed = 0
    for (method,budget,seed), r in records.items():
        obs = r["observations"]
        assert len(obs) == budget == len({m for m,_ in obs})
        assert all(feasible[m] and value == cost[m] for m,value in obs)
        assert min(v for _,v in obs) == r["best_cost"]
        assert r["regret"] == r["best_cost"]-gt["cost"]
        observed += len(obs)
        if method in METHODS[4:]:
            actual = [m for m,_ in obs[:len(r["initial_masks"])]]
            assert actual == r["initial_masks"]
            assert actual == initial[(initial.budget == budget) & (initial.seed == seed)].sort_values("initial_order")["mask"].tolist()
    trace = pd.read_csv(out/"qaoa_trace.csv")
    assert len(trace) == 1830
    indexed = trace.set_index(["budget", "seed", "adaptive_step"])
    total_final_shots = 0
    with gzip.open(out/"qaoa_final_samples.jsonl.gz", "rt") as stream:
        sample_rows = [json.loads(line) for line in stream]
    assert len(sample_rows) == len(trace)
    for raw in sample_rows:
        b,s,step = raw["budget"],raw["seed"],raw["adaptive_step"]
        t = indexed.loc[(b,s,step)]
        r = records[(METHODS[-1],b,s)]
        n = len(r["initial_masks"])+step-1
        assert n == t.training_observations
        seen = {m for m,_ in r["observations"][:n]}
        counts = {int(m):int(v) for m,v in raw["counts"].items()}
        d = sampled_diagnostics(counts, seen, oracle["active_count"], oracle["beta"], feasible, .8228585)
        assert d["shots"] == 1024
        total_final_shots += d["shots"]
        for name,value in d.items():
            assert (pd.isna(t[name]) if value is None else abs(t[name]-value)<1e-12), name
        mask,value = r["observations"][n]
        assert mask == t.selected_mask and abs(value-t.true_objective)<1e-12
        fallback = t.proposal_source == "CLASSICAL_FALLBACK"
        assert fallback == (d["unseen_admissible_unique"] == 0)
        if not fallback: assert mask in counts
        assert t.selected_surrogate_gap >= -1e-10
        assert t.surrogate_absolute_coefficient_bound < 1000
        assert t.total_qaoa_shots == t.cobyla_nfev*256+1024
        assert t.total_qaoa_circuits == t.cobyla_nfev+1
    history = pd.read_json(out/"qaoa_optimizer_history.jsonl.gz", lines=True, compression="gzip")
    h = history.groupby(["budget", "seed", "adaptive_step"]).size().sort_index()
    assert np.array_equal(h.to_numpy(), indexed.sort_index().cobyla_nfev.to_numpy())
    assert len(history) == trace.cobyla_nfev.sum()
    assert (history.shots == 256).all()
    model = pd.read_csv(out/"fit_vs_direct_feasibility.csv")
    assert len(model) == 65536 and model["mask"].tolist() == list(range(65536))
    assert np.array_equal(model.fit_pass, model.fitted_beta_ratio <= .8228585)
    assert np.array_equal(model.direct_pass, model.direct_beta_ratio <= .8228585)
    assert np.array_equal(model.fit_pass, oracle["beta"] <= .8228585)
    assert len(pd.read_csv(out/"optimizer_summary.csv")) == 28
    assert len(pd.read_csv(out/"paired_statistics.csv")) == 8
    names = ["stage3_regret_vs_budget", "stage3_qaoa_vs_surrogate_exhaustive", "stage3_beta_fit_validation",
        "stage3_cardinality_sensitivity", "stage3_qaoa_feasibility_and_fallback"]
    for name in names:
        for suffix in ("png", "pdf", "svg"):
            assert (out/"figures"/f"{name}.{suffix}").stat().st_size > 1000
    result = dict(status="PASS", runs=len(records), selected_true_evaluations=observed,
        all_selected_evaluations_admissible=True, all_initial_samples_matched=True,
        qaoa_adaptive_steps=len(trace), final_batch_shots=total_final_shots,
        internal_circuits=len(history), total_internal_shots=int(trace.total_qaoa_shots.sum()),
        raw_final_counts_reconciled=True, model_masks_classified=len(model), figures=15,
        stage1_stage2_simulator_objective_unchanged=True, controlled_results_preserved=True,
        manuscript_unchanged=True, mapping_max_error=json.loads((out/"mapping_validation_summary.json").read_text())["max_abs_error"])
    save_json(out/"acceptance_checks.json", result)
    print(json.dumps(result, indent=2))
