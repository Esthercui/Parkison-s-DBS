# Version 2 Table Manifest

Six main tables and eight supplementary tables. R/ denotes `results/stage3_validated/` at the frozen commit. All are formatted from saved sources; there are no new statistical estimates.

## Table 1 — main paper

- Source: `V1 p.13 Table 1; evidence/stage1_transcribed_summary.csv`
- Source label: `tab:s1`

**Caption:** Stage 1 reported mean regret ± SD. Values preserved from Version 1 Table 1, p. 13; the corresponding sweep seed count is unverified.

## Table 2 — main paper

- Source: `stage2.ipynb cell 16; evidence/stage2_transcribed_summary.csv`
- Source label: `tab:s2`

**Caption:** Stage 2 reported mean regret ± SD. Frozen notebook cell 16, 30 seeds; these values agree with Version 1 prose and replace its inconsistent table image.

## Table 3 — main paper

- Source: `R/optimizer_summary.csv (all 28 rows)`
- Source label: `tab:s3`

**Caption:** Validated Stage 3 mean regret ± population SD, 30 seeds per cell. Pool and Full-Domain denote classical surrogate proposal methods; QAOA is the simulated hybrid p=1 method. All selected queries are admissible.

## Table 4 — main paper

- Source: `R/paired_statistics.csv (principal Full-Domain family)`
- Source label: `tab:paired`

**Caption:** Paired QAOA minus Full-Domain (principal family). Negative favors QAOA. W/T/L counts QAOA wins/ties/losses across 30 seed pairs. All intervals include zero.

## Table 5 — main paper

- Source: `R/beta_fit_metrics.json`
- Source label: `tab:model`

**Caption:** Fixed quadratic efficacy approximation versus direct simulation. Local R^2 reflects the nearly flat direct response; it is not a clinical validation metric.

## Table 6 — main paper

- Source: `R/cardinality_sensitivity.csv`
- Source label: `tab:cardinality`

**Caption:** Sensitivity of inherited-threshold admissibility to cardinality and efficacy model. Counts enumerate every mask at each k.

## Table S1 — appendix

- Source: `R/optimizer_summary.csv (B=10)`
- Source label: `tab:complete10`

**Caption:** Complete validated Stage 3 statistics, B=10.

## Table S2 — appendix

- Source: `R/optimizer_summary.csv (B=20)`
- Source label: `tab:complete20`

**Caption:** Complete validated Stage 3 statistics, B=20.

## Table S3 — appendix

- Source: `R/optimizer_summary.csv (B=30)`
- Source label: `tab:complete30`

**Caption:** Complete validated Stage 3 statistics, B=30.

## Table S4 — appendix

- Source: `R/optimizer_summary.csv (B=40)`
- Source label: `tab:complete40`

**Caption:** Complete validated Stage 3 statistics, B=40.

## Table S5 — appendix

- Source: `R/paired_statistics.csv (secondary Pool family)`
- Source label: `tab:paired_pool`

**Caption:** Paired QAOA minus Pool (separate secondary family). Negative favors QAOA. W/T/L counts QAOA wins/ties/losses across 30 seed pairs. All intervals include zero.

## Table S6 — appendix

- Source: `stage1.ipynb cell 3; stage3.ipynb cell 1`
- Source label: `tab:params`

**Caption:** Fixed deterministic STN--GPe simulation parameters from the frozen notebooks. Time constants and delays are in seconds.

## Table S7 — appendix

- Source: `stage3.ipynb cell 3`
- Source label: `tab:metadata`

**Caption:** The single synthetic Stage 3 metadata instance. Contact indices imply no anatomical position. All factors are benchmark inputs.

## Table S8 — appendix

- Source: `R/ground_truth.json objective_components`
- Source label: `tab:components`

**Caption:** Exact fitted-admissible optimum (mask 38180): preserved objective components. The omitted efficacy intercept is common to all masks and cancels from regret.
