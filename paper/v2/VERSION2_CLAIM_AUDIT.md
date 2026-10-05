# Version 2 Claim Audit

**Audit date:** October 4, 2026. **Research authority:** `a94acf521bc596583b873283a509b43418b0fb76`.

Paths below are relative to the frozen research repository unless prefixed `V1` or `package`. `R/` means `results/stage3_validated/`. The exact quantitative tables are generated from saved artifacts or explicitly transcribed historical sources. D = direct result/source observation; I = interpretation; H = hypothesis/future work. Confidence concerns source support, not clinical validity.

## Major quantitative and methodological claims

| ID | Final wording / quantitative content | Source file or artifact | Type | Confidence and caveat |
|---|---|---|---|---|
| C01 | “Version 2”; “October 2026 Validated Revision”; October 4, 2026 | Local completion date; `package/evidence/preservation_before.json` | D | High; not dated October 26. V1 remains unchanged. |
| C02 | “supersedes the original Stage 3 conclusions following methodological re-audit” | `STAGE3_VALIDATION_REPORT.md`, sections A, J | I | High; same research program, not a new unrelated project. |
| C03 | Baseline peak approximately 19.53 Hz | `stage1.ipynb` cell 4 saved output; V1 p.12 | D | High source fidelity; simplified model, not patient physiology. |
| C04 | 2 s duration, 0.1 ms step, 0.2 s transient removal; Welch ≤8,192 samples, beta 13–30 Hz | Stage 1 cells 1–3; Stage 3 cell 1 | D | High; numerical waveform resolution is a model limitation. |
| C05 | Stage 1 64×64×16 = 65,536; f 60–180 Hz, A 0–1.5, PW 50–240 µs | `stage1.ipynb` cell 1 | D | High; amplitude is in model units. |
| C06 | Stage 1 109 Pareto points; optimum 176.19 Hz, 0.667, 227.33 µs; cost 0.7844227120082152 | `stage1.ipynb` cells 5/7 saved outputs; V1 p.12 | D | High; optimum depends on the chosen scalarization. |
| C07 | Stage 1 complete four-budget mean±SD table; CMA-ES lowest reported means; endpoint QAOA 0.1039±0.0342 → 0.0799±0.0387 | V1 Table 1 p.13, visual inspection; `package/evidence/stage1_transcribed_summary.csv` | D | Faithful transcription; sweep raw records and sweep-specific n unavailable. Do not substitute separate B=40 notebook summaries. |
| C08 | Stage 2 131,072 settings and 77,504 feasible; optimum ring 159.05 Hz, 0.5, 240 µs; cost 0.8228584997287205 | `stage2.ipynb` cells 0,4–6 | D | High; synthetic charge/impedance/focus assumptions, not clinical limits. |
| C09 | Stage 2 CMA-ES means 0.0839/0.0749/0.0658/0.0602; QAOA 0.0974/0.0860/0.0751/0.0659; full table SDs | `stage2.ipynb` cell 16 saved output, 30 seeds; cell 17 figure; V1 prose p.15 | D | High source support; V1 table image conflicts and is superseded for these entries only. |
| C10 | B=40 descriptive QAOA−CMA-ES gap 0.0321 in Stage 1, 0.0057 in Stage 2 | Arithmetic from C07/C09 (rounded published means) | D/I | Descriptive only; not a paired test or causal effect of structure. |
| C11 | Stage 3 “16 binary variables”; “exactly six”; fitted BetaRatio ≤0.8228585 | `stage3.ipynb` cells 0/4; `R/run_configuration.json` | D | High; fixed benchmark design, not physiological necessity. |
| C12 | Full 65,536; exactly-six 8,008; fitted-admissible 6,881 | `R/ground_truth.json`, `R/feasible_domain_k6.csv` | D | High; exact for the fitted screen. |
| C13 | Optimum mask 38180, binary 1001010100100100, indices [2,5,8,10,12,15] | `R/ground_truth.json` | D | High; indices are identifiers, no electrode anatomy. |
| C14 | Effective amplitude 1.57; fitted beta 0.8187975018236102; objective 1.5690394714699 | `R/ground_truth.json` | D | High; fitted objective, not treatment outcome. |
| C15 | Validation-only direct beta 0.8149348670459028 | `R/beta_fit_metrics.json` | D | High; not used to rescore optimizer runs. |
| C16 | Quadratic coefficients, amplitude formula, weights, objective components, synthetic metadata and overlap rule | `stage3.ipynb` cells 0–4; `R/ground_truth.json`; Appendix C | D | High; count term constant on k=6; charge soft term zero for this instance; c0 cancels from regret. |
| C17 | Complete binary surrogate transformed using x=(1−Z)/2 and xx=(1−Z−Z+ZZ)/4 | `stage3_validation_core.py`; report C | D | High; no hard-constraint terms are present in the phase QUBO. Hard filtering and sampled classical barrier are separate. |
| C18 | Each of three checks validates 65,536 states; max discrepancy 2.84217e−14, combined mean 1.58893e−15 | `R/mapping_validation_summary.json`, `R/qubo_ising_validation.csv` | D | High; the mean is across all three full-space tests, not one test; correctness only. |
| C19 | Actual circuit statevector discrepancy 6.05913e−17 | `R/mapping_validation_summary.json`; report C | D | High; does not imply performance benefit. |
| C20 | Rejection barrier 1,000; largest absolute-prediction bound 10.502754 | `R/cardinality_penalty_rule.json`, `R/qaoa_trace.csv`; report C | D | High; barrier is in classical expectation, not Hamiltonian; mixer does not preserve k. |
| C21 | 137 ridge features; coefficient 0.001; nine initial observations at B=10, ten otherwise; matched starts | `R/run_configuration.json`, `R/initial_samples_by_seed.csv`; report B | D | High; adaptive histories subsequently differ. |
| C22 | Pool makes 5,000 admissible draws; Full-Domain predicts all unseen admissible masks then queries one | `stage3.ipynb` cell 7; `stage3_validation_core.py` | D | High; pool can repeat; Full-Domain is not exhaustive true-objective testing. |
| C23 | p=1, 16 qubits, all 120 pairs, X mixer, COBYLA ≤30 calls, 256 training shots, 1,024 final shots | `R/run_configuration.json`; report B/H | D | High; simulated hybrid, classical neurodynamics. |
| C24 | B=10,20,30,40; 30 seeds; 840 runs; all 21,000 selected observations admissible | `R/optimizer_runs.csv`, `R/acceptance_checks.json`; report A/F | D | High for Stage 3; not fresh simulator calls or patient trials. |
| C25 | Complete Table 3 and Tables S1–S4: every method/budget mean, population SD, rank, median, IQR, range and 95% mean CI | `R/optimizer_summary.csv` (28 rows) | D | High; tables copied at six decimals; intervals describe seeds on one instance. |
| C26 | Random first at B=10; Full-Domain at B=20; Pool at B=30/40; QAOA ranks 3/2/3/2 | `R/optimizer_summary.csv` | D | High; descriptive ranks only; Pool and Full-Domain tie at B=10. |
| C27 | Principal differences −0.002339/+0.011083/+0.004004/−0.001316, all Holm p=1.000; all paired CIs include zero | `R/paired_statistics.csv` principal family, report G | D | High; B=10 upper CI endpoint exactly zero, 28 ties. No equivalence conclusion. |
| C28 | Table S5 Pool paired results, separate four-budget Holm family | `R/paired_statistics.csv` secondary family | D | High; not substituted for principal family; no supported separation. |
| C29 | 1,830/1,830 adaptive proposals sampled by QAOA; fallback 0% | `R/qaoa_trace.csv`, `R/qaoa_fallback_summary.csv` | D | High; excludes fallback explanation, not classical contributions or need for causal ablations. |
| C30 | 3,000 QAOA budgeted queries = 1,170 initial + 1,830 adaptive; 54,829 sampling circuits; 15,441,664 shots | `R/qaoa_parameter_search_summary.csv`; report H | D | High; excludes offline preparation and diagnostic statevectors; no speedup claim. |
| C31 | Mean final-shot admissibility 18.934746%; exact mass 17.740169%; same-history minimizer 70/1,830 (3.825%); predicted gap 0.0877704473 | `R/qaoa_trace.csv`; report H | D | High; sampled vs exact probabilities differ; surrogate diagnostic not counterfactual true regret. |
| C32 | Global metrics: R² 0.761188, RMSE 0.021294003, MAE 0.017489552, max error 0.056353984, n=401 | `R/beta_fit_metrics.json` global block | D | High; unchanged fit on direct simulator grid; no clinical validity. |
| C33 | Local metrics: R² −986.838188, RMSE 0.005985589, MAE 0.004834978, max error 0.011614132, n=129 | `R/beta_fit_metrics.json` local block | D | High; direct response nearly flat, large negative R² is correct. |
| C34 | “performs worse by squared error than a constant predictor using the local direct mean” | R² definition plus `R/beta_fit_validation.csv`, report E | I | High; not evidence of large absolute clinical error or a formatting error. |
| C35 | Downward crossings 1.482746 fitted vs 0.923268 direct; difference 0.559478; fitted upward crossing 3.658017 absent in direct grid through 4 | `R/threshold_validation.json`, `R/threshold_refinement.csv` | D | High within validated amplitude range; model units only. |
| C36 | k=4/5/6/7 counts and pass counts: 1,820/0/1,817; 4,368/0/4,368; 8,008/6,881/8,008; 11,440/11,440/11,440 | `R/cardinality_sensitivity.csv`, `R/fit_vs_direct_feasibility.csv` | D | High; total/fitted/direct; not optimizer comparisons at alternative k. |
| C37 | 1,127 six-contact masks rejected by fit but pass direct criterion | `R/feasibility_confusion.csv`; 8,008−6,881 | D | High; model-based classification, not clinical false negatives. |
| C38 | 1,044/1,830 angle searches reach cap; per-run seed reuse correlates shot randomness | `R/qaoa_parameter_search_summary.csv`; report H/K | D | High; retained protocol, not a claim that angle optimization converged. |
| C39 | Stage 1/2 retain legacy direct coefficient-to-phase routines and sparsification; historical CMA-ES may read beyond recorded budget at final population | `stage1.ipynb` cells 13/16; `stage2.ipynb` cells 10/12 | D (source inspection) | High for source behavior; not a rerun, not a quantified historical performance correction. Corrected Stage 3 not affected by these statements. |

## Interpretive and contribution claims

| ID | Final wording / content | Evidence | Type | Confidence / caveat |
|---|---|---|---|---|
| I01 | “not statistically separated in this experiment” | C27–C28 | I | Supported; not equivalence, noninferiority, or proof of equal future performance. |
| I02 | “competitive” corrected QAOA query efficiency | C25–C28 | I | Descriptive range/ranks; no predefined practical equivalence margin. |
| I03 | “The original apparent 75–80% Stage 3 regret advantage does not survive” | V1 pp.16–20 versus frozen report A/G | I | Supported for combined corrections; individual causal effects not isolated. |
| I04 | “An optimizer cannot compensate for a poorly validated objective” | C32–C37 and distinction between optimizing J and therapeutic response | I | Systems interpretation; not an independently randomized clinical finding. |
| I05 | At current scale strong classical approaches remain practical choices for benchmark optimization | C25–C30; domain size 6,881 | I | Resource-informed inference; no measured runtime comparison and no treatment recommendation. |
| I06 | Ground-truth benchmark, staged comparison, corrected verified pipeline, strong full-domain comparator, and validation framework | Frozen code and named artifact sets | I/contribution | Artifacts exist; no claim to priority, universal novelty, or first-of-kind status. |
| I07 | Apparent optimizer claims must survive domain, implementation, and baseline validation | Combined audit outcome | I | Supported case study; no factorial attribution. |
| H01 | Full-domain surrogate enumeration may become impractical for much larger, richer DBS formulations | Candidate combinatorics and current limited domain | H | Untested scaling hypothesis; stronger classical alternatives must also be evaluated. |
| H02 | Pre-specified 10–30+ synthetic instances can test robustness/generalization | Single current instance; report K; Future Work | H | Proposal only; no instances generated or algorithms run. |
| H03 | Richer current steering, anatomy, patient variability, side effects, multiobjective scoring, real LFP data, closed-loop policies, deeper QAOA, mixers, hardware | Future Work; relevant literature used only for context | H | Explicitly future, not delivered evidence or clinical promise. |

## Phrase audit and withdrawn claims

The manuscript source and rendered text are searched for `75`, `80`, `QAOA strongest`, `lowest regret at every budget`, `quantum advantage`, `quantum superiority`, `clinically necessary`, `exact surrogate solver`, `computational speedup`, `statistically equivalent`, and treatment/readiness language. Numerical substrings inside coefficients, sample counts, references, and legacy explanatory notes are reviewed by context rather than deleted blindly.

- **75–80%:** retained only in the explicit historical invalidation statement and evolution/comparison/audit documents; never a positive V2 result.
- **QAOA strongest / lowest at every budget:** withdrawn and contradicted by the complete validated rank table.
- **Quantum advantage / superiority:** no affirmative finding; only rejection of an assumption or unsupported interpretation.
- **Six contacts clinically necessary:** expressly rejected; no new clinical threshold invented.
- **Exact surrogate solver:** Pool renamed; Full-Domain described as exact prediction minimization over current candidates, not exact objective optimization.
- **Computational speedup:** expressly not demonstrated.
- **Treatment recommendation or patient readiness:** none; synthetic optimum is not a clinical recommendation.
- **Statistical equivalence:** never asserted; nonsignificance is non-separation only.
- **First rigorous benchmark / identified quantum turning point:** withdrawn; bounded references review cannot establish priority or a causal structural transition.
- **Anatomical contact placement / realistic clinical trial budgets:** replaced by synthetic indices and model query budgets with explicit calibration limits.

## Remaining reviewer vulnerabilities

The most significant are historical Stage 1/2 implementation/provenance limits, the single Stage 3 instance, a materially distorted efficacy approximation, underdetermined surrogate fitting, free feasibility/surrogate work under B, correlated QAOA sampler randomness, and lack of a quantum-evolution ablation. “Competitive” is descriptive, and “practical choice” is not a measured runtime result. The manuscript states these boundaries rather than claiming the validation resolved them. Submission-specific authorship, affiliations, funding, conflicts, and any journal-required AI-assistance disclosure require author-supplied facts; none is fabricated.
