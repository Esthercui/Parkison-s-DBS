> Historical bounded audit (October 2, 2026). Its pending-work status is superseded by [the corrected protocol](CORRECTED_PROTOCOL.md) and [fresh results](../results/RESULTS.md). The original findings are retained below.

# Minimal corrective experiment plan — v1, pending Esther's approval

No full rerun is authorized or executed by this plan. First decide the scientific
domain and confirm contribution attribution. Preserve the historical notebooks
and compare against their frozen hashes.

| Question | Smallest resolving action | Status / estimated resources |
|---|---|---|
| Is empty allowed? | Esther states the research question and any preexisting nonzero/efficacy requirement, with its rationale | required input; no computation |
| Does the objective reward a trivial answer? | reconstruct saved Q, sign check, enumerate both declared domains | done in bounded audit; about 1 second for the combined example, no simulator refit |
| Is the underlying fit reproducible? | baseline plus 41 saved amplitude settings; compare all ratios, fit residuals and coefficients before optimizer work | pending approval; 840,000 total time steps; plan 1–5 min, <512 MiB, <1 MiB output; measured calibration required |
| Is the surrogate minimizer exact on the finite set? | asymmetric small cases plus known 16-bit optimum; enumerate every feasible candidate after each fit | implementation and tests done; no revised ranking |
| Does the real cost circuit match f(x)? | basis energies and gate-phase check, then actual Qiskit statevector check for 2–3 bits | algebra/gate recorder checks done; actual Qiskit check pending in pinned isolated environment, plan <1 min / <512 MiB |
| Are budgets enforced in real libraries? | common oracle, shared initial design, explicit termination inside batches, all resource counters | wrapper and bounded path tests done; real CMA/Qiskit integration still pending |
| Does any ranking survive repair? | one prespecified domain, one unchanged instance, six methods, budget 10, three paired seeds | approval required; pilot only, no generalization claim |

Planning figures are conservative allowances, not measured full-run runtimes.
No cloud or paid compute is proposed; incremental service charges are $0 on the
existing local machine, with electricity/opportunity cost unmeasured. Do not
extrapolate the historical notebook's reported 2.16-minute sweep to a repaired
implementation or different environment.

## Freeze before the pilot

Record a configuration with source commit and dirty hashes, objective/fit
coefficients and their hashes, feasibility rule, initial mask list, ridge,
budget definition, optimizer settings, seed handling (including Aer), machine,
versions and output paths. The same rule applies to the oracle and every
optimizer. If no stimulation is allowed, include zero in the shared initial
design and charge it once per method. Under the present positive Q, every method
then reaches the global minimum immediately; that is an informative control,
not a reason to remove zero to rescue a ranking. An efficacy-constrained or
otherwise changed problem is a separately named experiment with a scientific
justification, never a retrospective patch to the historical table.

Before fitting in the current environment, resolve the historical `np.trapz`
call (absent in installed NumPy 2.5.3). Either recover the original compatible
environment or validate a narrowly scoped `np.trapezoid` substitution on fixed
arrays and record it as a changed implementation. Original package pins are
not known; the audit's version record does not recover them.

For a nontrivial prespecified case, propose five shared initial masks, total
budget ten, and three paired optimizer seeds on one instance. All methods get
the same initial costs charged within their ten-call allowance. Subsequent
duplicate requests use a cache and do not create extra training information.
Define batch stopping behavior before running CMA; define how QAOA exclusions
relate to its cost Hamiltonian. Scores may use only budget-accessible records.
Keep the full oracle outside optimizer access, exclusively for evaluator-side
scoring.

This six-method pilot permits 180 charged objective attempts across all jobs,
including repeated charging of the shared design for fair per-method budgets.
There are still only one problem instance and three optimizer repetitions.
At five QAOA proposals per seed, 30 objective iterations, 256 shots plus a final
1,024-shot proposal sample, a nominal upper allowance is 465 circuit executions
and 130,560 shots across three seeds (check actual optimizer stopping behavior).
Resource records must contain the actual counts, not just these nominal caps.

Use one worker initially. A 16-qubit complex128 state has 1 MiB of raw amplitudes;
simulator, transpiler and Python overhead can be much larger. Set a planning
allowance of 2 GiB RAM, 30 minutes wall time and 10 MiB output for this pilot;
first measure one circuit and one short optimizer call, then stop for revised
approval if those limits are implausible. Do not launch the old 720-job/25-worker
sweep. Exhaustive quadratic prediction can be chunked into 4,096-mask batches,
avoiding a full 65,536 by 137 feature matrix (~68.5 MiB just for float64 features).

## Stop and reporting rules

Fail the comparison if any method receives forbidden masks, extra true
information or unlogged post-budget values; if a mapping check fails; or if the
initial design differs. Preserve failures as evidence. Report objective calls,
upstream simulator work, cache hits, surrogate fits/predictions, optimizer
steps, circuits, shots and wall time separately. Require measured peak memory
for further scale-up.

After approval and a successful pilot, generate new tables only from recorded
per-run rows and the frozen configuration. Keep historical labels/data separate.
Any multiple-instance extension requires a prespecified family of patient/model
and geometry parameters, not selecting instances where QAOA wins. Statistical
results on optimizer seeds alone do not establish cross-instance performance.
