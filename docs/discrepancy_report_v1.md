> Historical bounded audit (October 2, 2026). Its pending-work status is superseded by [the corrected protocol](CORRECTED_PROTOCOL.md) and [fresh results](../results/RESULTS.md). The original findings are retained below.

# Stage 3 discrepancy report — v1

**Recommendation: present the model and this audit, not a quantum performance
advantage.** No revised benchmark table or clinical efficacy claim is supported.

Source: repository commit `b5e2468320d437bce5ddec8025ba409e5a26dc5b`, Stage 3
blob `42132bda2aea58c4e209170e4899997bfa5ada07`. The GitHub checkout matches the
handoff evidence. No newer DBS checkout was found in the searched local project
folders, and no alternative location has been supplied. That does not prove
newer work does not exist elsewhere. The original notebook is unchanged.

## Findings and reproduction strength

| Issue | Exact source | Finding | Evidence status |
|---|---|---|---|
| Empty-mask optimum | cells 2–4 | saved oracle says cost 0.0, contacts [], active 0 | locally reproduced conditional on saved fit coefficients |
| Unequal domains | cell 5 `decode_threshold`; cell 6 BO/CMA | all-zero threshold result activates argmax; oracle includes zero | inspected implementation and locally reproduced decoder |
| Misnamed exact baseline | cell 7 `run_surrogate_exact`; cell 8 registry; cell 9 table | up to 5,000 random draws per fitted proposal, with replacement and evaluated masks skipped | inspected implementation; bounded call-path execution |
| Cost-unitary mismatch | cell 7 nested `build_qaoa` | binary QUBO coefficients are used directly as Z/ZZ coefficients | locally reproduced on all 65,536 basis energies; historical gate builder inspected/executed with gate recorder |
| Budget leakage | cell 6 `run_cma_es.eval_x` | entire ask batch is evaluated even after logging reaches budget | locally reproduced with deterministic CMA ask/tell double |
| Reproducibility gaps | cells 0, 7–11 | no dependency lock, sampler seed, raw per-seed exported results or full resource log | inspected implementation |

The installed NumPy 2.5.3 no longer exposes `np.trapz`, which cell 1 calls.
`np.trapezoid` is available. The bounded audit avoids that simulator/metric path;
it does not certify that the historical notebook runs end to end in this
environment. Reconstruct the original dependency versions or separately test
a minimal compatibility substitution before a fresh fit; do not upgrade all
packages or silently claim an unchanged-environment reproduction.

The finite objective and mapping checks are mathematical/computational audits.
The simulator fit, Qiskit sampler and published optimizer sweep were not rerun.
No item is labeled independently reproduced by another researcher or externally
scientifically reviewed.

## Scientific question and objective

Is no stimulation an admissible treatment choice, or is there a scientifically
prespecified nonzero/efficacy requirement? This remains unanswered. Both domain
calculations below are descriptive; neither is selected to improve QAOA's rank.

The saved quadratic fit has `c0=0.9437580303537099`,
`c1=-0.11458817038088728`, `c2=0.02229011277045427`.
Reconstructing the unchanged Q gives minimum linear coefficient
`0.1736142930258106` and minimum upper-triangular pair coefficient
`0.002280278536417472`. Every coefficient is positive. Consequently every
nonempty binary mask has strictly positive cost, so the empty mask is the
unique minimum of this recorded objective. If at least one bit is required,
the unique minimum is the cheapest singleton, mask 4096/contact 12, cost
`0.1736142930258106`. Exhaustive finite enumeration confirms both statements.

This is an analytic sign argument for the specified fitted QUBO, supported by a
local enumeration. It says nothing about the best biological intervention.
Cost zero comes from dropping the constant `c0`; it does not mean beta power
is zero. With the intercept included, the no-stimulation fitted value is c0.
The saved fit's no-stimulation intercept also differs from the original
normalized baseline near 1; the fit residuals were not re-estimated here.
The current charge-density soft penalties are all zero: saved proxy range
0.1667–0.2976 is below threshold 0.55. The `INFEAS_COST` constant does not add a
hard feasibility rule to the Stage 3 cost function.

## Domains and information access

| Method | Historical access to empty mask | Initial information and other access |
|---|---|---|
| Full oracle | yes | all 65,536 values; used for ground truth outside optimizer budget |
| Random | yes | uniform masks, distinct values counted |
| GA | possible at initialization | generated crossover/mutation empties forced nonempty; cache plus repeated raw reads |
| BO | no | threshold decoder; about 8–10 random initial vectors; repeated observations can reuse a mask |
| CMA-ES | no | threshold decoder, population 18; can read unseen values past budget |
| Historical surrogate pool | yes | 9 or 10 initial masks; quadratic ridge model, 5,000 candidate draws |
| Historical QAOA | yes | same surrogate initialization rule; simulated samples plus random-pool fallback |

All optimizer functions receive the full precomputed cost array, though their
code is intended to treat scalar reads as black-box queries. Stage 3's counted
evaluation is a cached fitted-QUBO lookup, not a new STN–GPe simulation. The
upstream baseline plus 41 amplitude simulations build the fit once outside
these budgets. The ground-truth table is another separately charged setup cost.
No claim that a budget of 10 means ten expensive patient/simulator evaluations
is justified. The quadratic surrogate has 137 coefficients (intercept, 16
linear, 120 pair terms); 9–40 observations leave it underdetermined without its
ridge prior. Shared model structure, training data and regularization matter.

## Exact label and provenance of the published table

There is exactly one `run_surrogate_exact` definition in the stored Stage 3
notebook, in cell 7. Cell 8 maps “Surrogate (Exact)” to it and executes the
sweep; cell 9 builds the saved table from `stage3_results`. No later cell in
this notebook overrides the definition. Execution counts progress 8 (definition)
to 10 (sweep) and 11 (table). This supports the source-to-table attribution, but
notebook history cannot exclude unsaved kernel edits. The source/saved-output
inspection is not a fresh reproduction of those performance statistics.

The corrected descriptive name is **Surrogate (random pool, 5,000 draws)**.
The old notebook/table label is retained only as historical evidence. New
`minimize_surrogate_exhaustive` enumerates all feasible masks; when exclusions
are supplied it finds the best *unevaluated* mask. New
`run_surrogate_exhaustive` fits and proposes through `BudgetedOracle`, charging
initial data as well as proposals. Exact enumeration of a fitted prediction
surface is not exact minimization of an unknown true biological objective.

## Hamiltonian mapping

For `f(x)=b0+sum_i l_i*x_i+sum_(i<j) q_ij*x_i*x_j`, use
`x_i=(1-Z_i)/2`. The matching Hamiltonian coefficients are:

```
constant = b0 + sum(l)/2 + sum(q)/4
h_i = -l_i/2 - sum(all pair coefficients incident to i)/4
J_ij = q_ij/4
```

Contact i is the integer mask's bit i. Qiskit output strings must be reversed
when converted to contact-order bit arrays; the historical reversal does that.
The historical circuit instead applies `RZ(2*gamma*l_i)` and
`RZZ(2*gamma*q_ij)`. This implements different diagonal energy differences;
the error cannot be repaired by a constant offset. On the reconstructed Q,
maximum basis-energy error after aligning the zero-mask energy is about
18.8712679658. The corrected mapping agrees within 1.60e-14 on all 65,536
states. An eight-state asymmetric test also verifies the emitted rotations,
global phase and bit order independently.

The historical objective additionally penalizes already evaluated masks by 1000
when computing expected sampled cost. That exclusion penalty is not encoded in
its cost layer, and pair sparsification could also separate the sampled circuit
from the scoring model if `max_pairs` were reduced. Current default 120 keeps
all 16-bit pairs. A revised QAOA definition must explicitly decide how novelty
exclusion affects training and proposal selection; simply fixing RZ/RZZ factors
does not validate the entire optimizer.

## Oracle accounting

In a controlled 18-member CMA ask batch at budget 10, the original code returns
10 logged evaluations but makes 38 array reads covering 18 distinct masks. This
probe uses the original function with an ask/tell double; it is not a real CMA
optimizer run. The new wrapper completes exactly 10 distinct underlying calls,
serves repeated masks from its cache, and raises before the 11th unseen call.
It logs failed underlying calls as charged attempts and cached post-budget
reads separately. Whole-array export, iteration and slicing are rejected.

Bounded real call-path executions cover random, GA, BO and the random-pool
surrogate. QAOA tests exercise normal sampling selection and its fallback with
circuit/sampler/minimizer doubles; no Qiskit packages were installed. The
adapter protects all scalar-read paths; it does not by itself equalize the
historical search domains or initialize all methods identically. It is a
single-worker accounting interface, not protection against adversarial code.

Objective calls, cache hits, underlying evaluation time and wall time are logged
separately. The revised exhaustive baseline also counts surrogate fits,
predictions and proposal steps. Uninstrumented historical shots, optimizer
steps and surrogate predictions are `null`, not inferred zeros. A full repaired
benchmark must wire those counters into every real optimizer before publication.

## Interpretation and next decision

The 30 seeds repeat one objective instance; they are not 30 patients or 30
independent problem instances. Sampler randomness is not pinned by the NumPy
seed alone. Saved significance calculations and simulator regret cannot imply
hardware speedup, clinical effectiveness or general quantum advantage.
See the [corrective plan](corrective_plan_v1.md) for the smallest approved next
experiment and resource limits. Historical outputs remain unchanged.
