# Version 2 Figure Manifest

All Stage 3 assets are byte-for-byte copies of frozen validated PDFs. Stage 1/2 artwork is extracted from saved sources; no plots are regenerated. R/ denotes `results/stage3_validated/` at the frozen commit. Source artwork labels are retained and explained in captions.

## Figure 1 — main paper

- Source artifact: `V1 p.12, original Figure 3 (embedded PDF image xref 32)`
- Data: `V1 preserved PDF`
- Package file: `figures/stage1_pareto_v1.png`
- SHA-256: `6e4da84272a8dcf16196b6fad20aa1bb2cdc27e0f55479668dfa463fd0e63fd3`

**Caption:** Stage 1 efficacy--energy Pareto front, extracted from the preserved March manuscript (original Figure 3, p. 12). Blue points show normalized beta-power/energy pairs from the 65,536-setting grid, orange points show the nondominated Pareto front, and the marked knee defines the scalar objective's energy reference. This is a simulator tradeoff, not a clinical therapeutic window.

## Figure 2 — main paper

- Source artifact: `stage2.ipynb, cell 17 stored PNG output`
- Data: `stage2.ipynb cell 16 saved sweep`
- Package file: `figures/stage2_performance_saved.png`
- SHA-256: `abeebbef3d0c4cff0732459d809e66b74e3a6de09fe8e9acd6367a6dc0ba5f54`

**Caption:** Stage 2 historical optimizer performance, extracted from the stored output of stage2.ipynb, cell 17 (zero-based). Means and ±1 population SD describe 30 runs at each budget for five displayed methods; Table 2 includes the classical surrogate pool. The horizontal axis counts benchmark settings, not observed patient trials. No optimizer was rerun for this figure.

## Figure 3 — main paper

- Source artifact: `results/stage3_validated/figures/stage3_regret_vs_budget.pdf`
- Data: `R/optimizer_summary.csv; R/optimizer_runs.csv`
- Package file: `figures/stage3_regret_vs_budget.pdf`
- SHA-256: `56e7e66fb15b117eee1042938fef9706c39f5f97ca5fac4077c1ea0c90351c45`

**Caption:** Validated Stage 3 mean simple regret versus budget, over 30 seeds per method/budget on one synthetic instance. Error bars are seed-level 95% percentile-bootstrap confidence intervals (10,000 resamples), not SD. Small horizontal offsets separate intervals without changing budgets. ``Surrogate (Exhaustive)'' in the unchanged source artwork means Surrogate (Full-Domain). Ground truth is the fitted-admissible minimum 1.5690394714699.

## Figure 4 — main paper

- Source artifact: `results/stage3_validated/figures/stage3_beta_fit_validation.pdf`
- Data: `R/beta_fit_validation.csv; R/beta_fit_metrics.json`
- Package file: `figures/stage3_beta_fit_validation.pdf`
- SHA-256: `f4316e496bce37105f61651caaad69acea8f11e1fe51b17bdb8d1868c902ee6f`

**Caption:** Unchanged quadratic efficacy fit versus the unchanged direct STN--GPe simulator on 401 amplitudes from 0 to 4. Shading marks the entire k=6 reachable interval, 1.40--1.72. Residuals are fitted minus direct beta ratio; local metrics use a separate 129-point grid. The inherited threshold 0.8228585 is a benchmark efficacy criterion, not a clinical treatment threshold.

## Figure S1 — appendix

- Source artifact: `results/stage3_validated/figures/stage3_cardinality_sensitivity.pdf`
- Data: `R/cardinality_sensitivity.csv; R/fit_vs_direct_feasibility.csv`
- Package file: `figures/stage3_cardinality_sensitivity.pdf`
- SHA-256: `273920220f8500b6d57443879d4460d3bdb5f768ca35ac4417cec2fb40d964fd`

**Caption:** Cardinality sensitivity at k=4,5,6,7. Top: minimum fitted beta ratio at each cardinality and direct simulation at that same mask. Bottom: percentage of all \binom{16}{k} masks passing each model's inherited efficacy threshold. The best fitted-beta mask need not minimize total objective. The figure tests model-dependent admissibility, not clinical contact necessity.

## Figure S2 — appendix

- Source artifact: `results/stage3_validated/figures/stage3_qaoa_vs_surrogate_exhaustive.pdf`
- Data: `R/optimizer_runs.csv; R/paired_statistics.csv`
- Package file: `figures/stage3_qaoa_vs_surrogate_exhaustive.pdf`
- SHA-256: `f941ad8b394b61195102d369845a03c0b2ac4d5a647e4de2f9c5ef3a2cd382b7`

**Caption:** Per-seed paired regret differences, QAOA minus Surrogate (Full-Domain). Negative favors QAOA. Diamonds are means with paired 95% bootstrap intervals; the axis includes all observations and zero. Initial observations are identical but subsequent adaptive histories are independent. ``Exhaustive'' in the source artwork means full-domain surrogate prediction, not exhaustive objective evaluation.

## Figure S3 — appendix

- Source artifact: `results/stage3_validated/figures/stage3_qaoa_feasibility_and_fallback.pdf`
- Data: `R/qaoa_trace.csv; R/qaoa_fallback_summary.csv; R/qaoa_parameter_search_summary.csv`
- Package file: `figures/stage3_qaoa_feasibility_and_fallback.pdf`
- SHA-256: `dc3168692fce29b108f4c1f6737f08ca1fcb10255ccd7913288206ab30303072`

**Caption:** QAOA final-batch admissibility and fallback. Left: distributions over final 1,024-shot batches (median, IQR, and 1.5-IQR whiskers; outlier markers omitted), mean sampled admissibility, and mean exact statevector admissible mass. Right: fallback counts/rates among adaptive proposals. Internal 256-shot angle-search batches are accounted for separately. Final selected objective queries are all admissible after filtering; this does not mean every raw sample is admissible.
