"""Execute the restored Stage 3 notebook and export its existing analysis.

No optimizer is implemented here. Model and method definitions come from
stage3.ipynb; this runner records the actual observations and checks admissibility.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import time

for variable in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"
os.environ["MPLBACKEND"] = "Agg"

ROOT = Path(__file__).resolve().parent
BASELINE = "b5e2468320d437bce5ddec8025ba409e5a26dc5b"


def execute_cell(index):
    exec(compile("".join(notebook["cells"][index]["source"]),
                 f"stage3.ipynb:cell{index}", "exec"), globals())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    global notebook, rows, stage3_results, N_JOBS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/stage3_controlled")
    parser.add_argument("--jobs", type=int, default=25, help="Execution workers only; original default 25")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--pilot", action="store_true", help="Six methods, B=10, seeds 0/1; not final evidence")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    notebook = json.loads((ROOT / "stage3.ipynb").read_text())
    baseline = json.loads(subprocess.check_output(
        ["git", "show", f"{BASELINE}:stage3.ipynb"], cwd=ROOT))
    for index in (1, 2, 3):
        assert notebook["cells"][index]["source"] == baseline["cells"][index]["source"]
    for filename in ("README.md", "stage1.ipynb", "stage2.ipynb"):
        assert (ROOT / filename).read_bytes() == subprocess.check_output(
            ["git", "show", f"{BASELINE}:{filename}"], cwd=ROOT)
    for index in range(5):
        execute_cell(index)
    components = {
        "efficacy_without_constant_c0": float(beta_ratio_flat[best_mask] - c0),
        "count": float(LAMBDA_COUNT * best_bits.sum()),
        "energy": float(LAMBDA_ENERGY * A_UNIT**2 * (IMP_FACTOR @ best_bits)),
        "risk": float(LAMBDA_RISK * (RISK @ best_bits)),
        "overlap": float(LAMBDA_OVERLAP * sum(OVERLAP[i, j] * best_bits[i] * best_bits[j]
                         for i in range(N_CONTACTS) for j in range(i+1, N_CONTACTS))),
        "charge_density": float(LAMBDA_QD * (QD_SOFT_PEN @ best_bits)),
    }
    assert abs(sum(components.values()) - best_cost) < 1e-12
    assert not admissible_flat[0] and not admissible_flat[-1]
    assert np.all(active_count_flat[admissible_flat] == 6)
    assert np.all(beta_ratio_flat[admissible_flat] <= BETA_RATIO_LIMIT)
    assert np.all(np.isinf(oracle_cost_flat[~admissible_flat]))
    domain = {
        "baseline_commit": BASELINE,
        "beta_definition": "Original fitted c0 + c1*A_eff + c2*A_eff**2, including c0",
        "beta_limit": BETA_RATIO_LIMIT,
        "total_masks": N_MASKS,
        "exactly_six_masks": int(np.sum(active_count_flat == 6)),
        "admissible_masks": int(admissible_flat.sum()),
        "percentage_full_space": float(100 * admissible_flat.mean()),
        "best_mask": best_mask,
        "best_mask_binary_msb_first": format(best_mask, "016b"),
        "best_bits_contact_0_first": best_bits.astype(int).tolist(),
        "active_contacts_zero_based": np.flatnonzero(best_bits).tolist(),
        "beta_ratio": float(beta_ratio_flat[best_mask]),
        "A_eff": float(A_UNIT * (FOCUS @ best_bits)),
        "total_cost": best_cost,
        "objective_components": components,
        "omitted_constant_c0": float(c0),
        "fit_coefficients": [float(c0), float(c1), float(c2)],
        "simulator_calls_for_fit_including_baseline": len(Aeff_samples) + 1,
    }
    write_json(out / "domain.json", domain)
    np.savez_compressed(out / "oracle.npz", mask=np.arange(N_MASKS),
                        active_count=active_count_flat, beta_ratio=beta_ratio_flat,
                        admissible=admissible_flat, cost=oracle_cost_flat)
    np.savez_compressed(out / "fit.npz", amplitude=Aeff_samples, observed_ratio=ratios,
                        coefficients=np.array([c0, c1, c2]), Q=Q)
    manifest = {
        "baseline_commit": BASELINE,
        "execution_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "tracked_dirty": bool(subprocess.check_output(["git", "diff", "HEAD", "--name-only"], cwd=ROOT, text=True).strip()),
        "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in ("stage3.ipynb", "run_stage3.py", "requirements-stage3.txt")},
        "python": platform.python_version(), "platform": platform.platform(),
        "packages": {p: importlib.metadata.version(p) for p in
                     ("numpy", "scipy", "scikit-learn", "qiskit", "qiskit-aer", "cma", "joblib", "pandas", "matplotlib")},
        "budgets": BUDGETS, "seeds": list(range(SEEDS_SWEEP)),
        "workers": args.jobs, "pilot": args.pilot,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "original_model_cells_unchanged": True,
        "stage1_stage2_readme_byte_identical": True,
    }
    write_json(out / "manifest.json", manifest)
    if args.validate_only:
        print(json.dumps(domain, indent=2), flush=True)
        return
    for index in (5, 6, 7):
        execute_cell(index)
    # Retain the original job definitions, order, budgets, methods and seed count.
    setup = "".join(notebook["cells"][8]["source"]).split('print(f"Launching')[0]
    exec(compile(setup, "stage3.ipynb:cell8_setup", "exec"), globals())
    N_JOBS = args.jobs
    selected_jobs = [(m, 10, s) for m in stage3_methods for s in (0, 1)] if args.pilot else jobs
    print(f"Launching {len(selected_jobs)} jobs on {N_JOBS} workers", flush=True)
    rows = []
    start = time.time()
    with (out / "runs.jsonl").open("w") as trace:
        completed = Parallel(n_jobs=N_JOBS, backend="loky", verbose=10, return_as="generator_unordered")(
            delayed(one_job)(m, b, s) for m, b, s in selected_jobs)
        for row in completed:
            method, budget, seed, best, regret, observations = row
            assert len(observations) == budget == len({m for m, _ in observations})
            assert all(is_admissible_mask(m) and c == oracle_cost_flat[m] for m, c in observations)
            trace.write(json.dumps(dict(method=method, budget=budget, seed=seed,
                                        best_cost=best, regret=regret, observations=observations), allow_nan=False) + "\n")
            trace.flush()
            rows.append(row)
    rows.sort(key=lambda r: (r[1], list(stage3_methods).index(r[0]), r[2]))
    expected = len(selected_jobs)
    assert len(rows) == expected
    write_json(out / "validation.json", dict(status="PASS", runs=expected,
        observations=sum(r[1] for r in rows), all_feasible=True,
        all_budgets_complete=True, wall_seconds=time.time()-start))
    if args.pilot:
        print("Pilot passed; these are not publication results.", flush=True)
        return
    assembly = "".join(notebook["cells"][8]["source"]).split("stage3_results = {}", 1)[1]
    exec("stage3_results = {}" + assembly, globals())
    for index in (9, 10, 11):
        execute_cell(index)
    stage3_summary_df.to_csv(out / "summary.csv", index=False)
    sig_df.to_csv(out / "qaoa_statistics.csv", index=False)
    ranking = stage3_summary_df.sort_values(["Budget", "Mean Regret"])
    ranking.to_csv(out / "ranking.csv", index=False)
    # Original mean ± population SD plot and B=30 distribution plot.
    import matplotlib.pyplot as plt
    plt.show = lambda: None
    for index, name in ((13, "regret_vs_budget"), (15, "regret_distribution_B30")):
        execute_cell(index)
        plt.savefig(out / (name + ".png"), dpi=180)
        plt.savefig(out / (name + ".svg"))
        plt.close("all")
    print(f"Complete: {out}", flush=True)


if __name__ == "__main__":
    main()
