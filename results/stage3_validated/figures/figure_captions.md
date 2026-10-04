# Stage 3 validation figure captions

All figures concern the unchanged fitted objective, k=6, fitted BetaRatio ≤ 0.8228585, unless explicitly labeled direct simulation. No figure implies patient validation or anatomical geometry.

**A — stage3_regret_vs_budget.** Thirty matched seeds per method/budget. Mean best-found cost minus exhaustive feasible ground-truth cost; lower is better. Error bars are seed-level 95% percentile bootstrap CIs (10,000 resamples). Small horizontal offsets prevent error-bar overlap and do not change budgets. Data: optimizer_summary.csv and optimizer_runs.csv. These intervals describe optimizer randomness on one model.

**B — stage3_qaoa_vs_surrogate_exhaustive.** Each point is a paired seed difference (QAOA minus Exhaustive); positive favors Exhaustive. Diamonds are means with paired 95% bootstrap CIs. Symmetric limits show every observation and zero. Initial samples are identical; subsequent adaptive histories are independent. Data: optimizer_runs.csv and paired_statistics.csv.

**C — stage3_beta_fit_validation.** The original quadratic approximation and unchanged direct STN–GPe simulator on 401 uniformly spaced amplitudes from 0 to 4. Shading marks the entire reachable k=6 interval, 1.40–1.72. Residual is fitted minus direct. The threshold is inherited from Stage 2, not a clinical treatment threshold. Local metrics use a denser 129-point amplitude grid. Data: beta_fit_validation.csv and beta_fit_metrics.json.

**D — stage3_cardinality_sensitivity.** Top: minimum fitted BetaRatio at each k and direct simulation of that same mask. Bottom: percentage of all C(16,k) masks passing each model's threshold, using cached direct simulations at every unique effective amplitude. Six is a fixed-cardinality design choice; the fit can reject masks that the simulator accepts. Data: cardinality_sensitivity.csv and fit_vs_direct_feasibility.csv.

**E — stage3_qaoa_feasibility_and_fallback.** Left: distribution across final 1,024-shot adaptive batches (median, IQR and 1.5-IQR whiskers; outlier markers omitted), mean sampled admissibility and mean exact statevector mass. Right: fallback rate and numerator/denominator among adaptive proposals. Both axes span 0–100%. Internal 256-shot COBYLA batches are accounted for separately. Raw sample admissibility does not imply a true evaluation: final proposals are filtered and all true evaluations are admissible. Data: qaoa_trace.csv, qaoa_fallback_summary.csv and qaoa_parameter_search_summary.csv.
