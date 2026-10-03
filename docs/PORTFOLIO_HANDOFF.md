# Parkinson's DBS Optimization — Portfolio Handoff

## 1. One-sentence project definition

A collaborative simulation-based benchmark comparing classical and quantum-assisted
optimization for Parkinsonian DBS parameter tuning against finite-domain ground
truth under fixed objective-query budgets.

## 2. The research question

Under limited evaluation budgets, how do classical and quantum-assisted optimization
methods compare as the DBS decision problem becomes more constrained, discrete,
and combinatorial? This is a question, not a presumption of quantum benefit.

## 3. Why the problem is difficult

Frequency, amplitude, pulse width and contact choices interact. Proxy efficacy
must be weighed against energy and modeled safety penalties, with limited
settings available to the optimizer. Adding contact mode and binary combinations
changes the decision structure. However, the current Stage 3 objective is simple
despite 65,536 encodings: every added contact increases cost. Size alone does
not prove difficulty. The budget is a research convention, not a validated
clinical allowance.

## 4. Collaboration and contribution

The project was collaborative. Esther co-developed it, as described in the supplied
project definition; the original uploads are under `Esthercui`. The inspected
paper has no author/contribution list, and upload identity does not establish
who designed models, implemented optimizers, ran experiments or wrote the text.

- **Esther:** co-development may be stated; precise historical responsibilities remain to be confirmed.
- **Collaborators:** names and model/code/experiment/writing responsibilities are not recoverable from this snapshot.
- **Advisor/mentor guidance:** no confirmed scope or endorsement was established; do not invent one.
- **External libraries:** NumPy/SciPy for numerics, scikit-learn for GP regression, `cma` for CMA-ES, Numba for recurrence acceleration, Matplotlib for figures, Qiskit for independent circuit checks. Historical notebooks used Qiskit/Aer sampling.
- **Later validation:** the October review identified comparison defects. The current repairs, tests, reruns and handoff were produced with Codex assistance at Xin's request. Do not attribute these to Esther acting independently.

Use [COLLABORATION_TODO.md](COLLABORATION_TODO.md) before publishing specific
individual contribution claims.

## 5. Benchmark architecture

[Architecture SVG](../assets/architecture.svg) separates offline setup from the
information available to an optimizer:

```text
Declared stage/domain → STN–GPe simulator → normalized beta / fitted QUBO objective
→ full finite feasible oracle → evaluator-held ground truth

Shared five-point initialization → optimization methods ↔ budgeted scalar oracle
→ best observed cost minus ground truth → paired-seed comparison

Separate resource log: simulator setup, objective queries, internal predictions,
optimizer steps, statevector circuits, simulated shots and wall time.
```

Stage 2 checks analytic feasibility before simulation. Stage 3 first fits an
amplitude-response curve; its budgeted contact-QUBO queries are not STN–GPe
simulations. The ground-truth table is withheld from optimizers.

## 6. Why the benchmark has stages

**Stage 1:** three continuous-valued parameters on a 64×64×16 finite grid.
Its minimum is exact on that grid, not on a continuous domain.

**Stage 2:** adds ring/directional mode, charge-density feasibility and energy/focus
factors: 77,504 feasible settings out of 131,072 encodings.

**Stage 3:** fixes temporal settings and selects among 16 contact bits using a
fitted quadratic objective. It isolates binary structure, but the current
penalties produce a trivial optimum. The stages change several assumptions;
they do not identify a causal effect of “more constraints” on quantum performance.

## 7. Three difficult decisions

These are benchmark design choices, not unsupported claims about Esther's individual role.

1. **Score against ground truth.** Exhaustive finite enumeration distinguishes a
   best-found setting from the modeled optimum. It also exposes a trivial optimum
   that a headline ranking could conceal.
2. **Use regret under a fixed information budget.** Charge shared initialization
   and each new objective value. Keep internal computation and setup separate
   so “40 trials” does not imply equal computational resources.
3. **Treat quantum benefit as a hypothesis.** Compare parameter-grid tuning with
   binary contact selection and accept negative results. During later validation,
   we identified inconsistent domains, misleading exact labels, incorrect cost
   phases and budget leakage. Those corrections are documented as later validation,
   not a discovery independently attributed to Esther.

## 8. Corrected results

Fresh simulation, original grids, ten paired seeds (0–9), one fixed model, five
shared charged initial observations including no stimulation. At B=40, regret
is **mean ± sample SD**:

| Method | Stage 1 | Stage 2 | Stage 3, zero allowed |
|---|---:|---:|---:|
| Random | 0.081931 ± 0.025513 | 0.062562 ± 0.017241 | 0 ± 0 |
| GA | 0.062446 ± 0.034186 | 0.068962 ± 0.028586 | 0 ± 0 |
| BO | 0.060335 ± 0.045391 | 0.062060 ± 0.028438 | 0 ± 0 |
| CMA-ES | 0.058542 ± 0.033961 | 0.076401 ± 0.026903 | 0 ± 0 |
| Surrogate (exhaustive) | 0.102693 ± 0.043016 | 0.060433 ± 0.029445 | 0 ± 0 |
| QAOA (p=1) | 0.100912 ± 0.028124 | 0.073358 ± 0.020653 | 0 ± 0 |

**Stage 1:** CMA-ES has the lowest sample mean at B=40; GA and BO are close.
QAOA minus CMA-ES mean regret is +0.042370, descriptive paired 95% bootstrap CI
[+0.025977, +0.062248]. QAOA loses this comparison in all ten seeds.

**Stage 2:** exhaustive surrogate search has the lowest sample mean at B=40.
QAOA minus exhaustive surrogate mean regret is +0.012925, descriptive paired 95%
CI [+0.003070, +0.023734]. This does not establish QAOA superiority or a causal
improvement from constraints. Several other paired intervals include zero.

**Stage 3:** every method attains zero regret because the common no-stimulation
control is the unique modeled optimum. Cost zero omits a constant; it is not
zero beta power. In the separate nonempty sensitivity, BO, exhaustive surrogate,
QAOA and sparse-first all attain the singleton optimum in 10/10 seeds by B=40.
At B=10 QAOA mean regret is 0.014153, exhaustive surrogate 0.010512 and sparse-first
0.006503. No QAOA superiority claim survives these checks.

All budgets (10/20/30/40), intervals and data are in [RESULTS.md](../results/RESULTS.md),
[summary.csv](../results/summary.csv) and [paired_comparisons.csv](../results/paired_comparisons.csv).
Bootstrap intervals use 10,000 paired resamples; they are descriptive, not
multiplicity-adjusted. Objectives differ; compare methods within each stage.

## 9. Interpretation

The corrected evidence supports a reproducible benchmarking and validation
contribution, not the manuscript's progression toward quantum dominance.
Classical methods remain strong on these grids. The Stage 3 objective is inadequate
for demonstrating a nontrivial DBS contact-selection advantage. A QUBO encoding
alone does not establish meaningful combinatorial difficulty. Future work must
prespecify a scientifically justified objective and multiple instances before
testing where, if anywhere, a quantum-assisted method becomes competitive.

## 10. Limitations

- Simulation-based, simplified neural model; beta-band power is a proxy.
- No patient treatment recommendation, patient outcomes or clinical validation.
- Classical statevector simulation; no quantum hardware execution or speedup.
- One noise-free model and hand-set geometry/penalties; seeds are optimizer randomness, not patient variability.
- Coarse integration and finite grids; no continuous-domain optimum or time-step convergence established.
- Stage 3 fit residuals are nonzero; effective amplitude can slightly exceed the fitted range. Zero and the cheapest singleton solve its inspected domains.
- Full-oracle/Pareto setup is outside search budgets. Queries, simulator calls and internal computation are different resources.
- Ten seeds, fixed hyperparameters and bounded QAOA iteration counts; no tuned best-in-class or cross-instance superiority claim.
- Historical contribution details and a reviewed manuscript revision remain outstanding.

## 11. Reproduction

Install the pinned environment using [README](../README.md). Small run:

```bash
python -m dbs_benchmark.cli --config configs/smoke.json --output results/smoke
```

Full benchmark:

```bash
python -m dbs_benchmark.cli --config configs/benchmark.json --output results/current
```

Then run the nonempty sensitivity and `python scripts/report.py` to validate
and regenerate tables/figures. `python scripts/architecture.py` regenerates the
diagram. Source/config/environment hashes and every charged observation are retained.
Corrected engine commit: `2f89b91a2b7bd3fbd3e3aead9f2597c200390d24`.
The website must link the delivered corrected revision, not a moving historical main.

## 12. Website assets

| Asset | File / destination |
|---|---|
| Architecture | `assets/architecture.svg`, PNG fallback alongside |
| Main figure | `assets/corrected_results.svg`: seed dots, means, descriptive intervals |
| Diagnostic figure | `assets/stage3_diagnostic.svg`: objective and nonempty sensitivity |
| Corrected table | `results/summary.csv`; readable `results/RESULTS.md` |
| Bounded copy | `docs/PORTFOLIO_COPY_FINAL.md`, checked against the claim ledger |
| Code | `https://github.com/Esthercui/Parkison-s-DBS`, pinned to the delivered corrected commit |
| Paper | `paper/HISTORICAL_2026-03_DBS_Manuscript.pdf` — historical, requires revision |
| Reproduction | README and `docs/CORRECTED_PROTOCOL.md` |

Do not reuse historical notebook tables or old QAOA superiority figures as
current evidence. Retain the model, initialization, resource and contribution
qualifications when adapting these assets for a website.

Published engine source: [`3edf0f154febabf7347546944dc12e69cb7fd0ef`](https://github.com/Esthercui/Parkison-s-DBS/tree/3edf0f154febabf7347546944dc12e69cb7fd0ef). Its Git tree is byte-identical to execution commit C (`2f89b91`); publication changes commit metadata/parentage, not executed source.
