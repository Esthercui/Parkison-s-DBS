# Corrected benchmark protocol

This is a new, explicitly configured comparison of the historical scientific
instance. It preserves the simulator, contact geometry and objective weights.
It does **not** reproduce the historical optimizer table or recover its unknown
package environment. The corrected source is recorded in each run manifest.

## Problem and ground truth

- Stage 1: 64 frequency bins (60–180 Hz), 64 amplitude bins (0–1.5 model units),
  16 pulse-width bins (50–240 microseconds). All 65,536 settings are admissible.
- Stage 2: the same grid plus ring/directional mode; 131,072 encodings,
  77,504 feasible settings. The analytic charge-density proxy must be at most
  0.60 for **every** method. Its area/focus/impedance factors are assumptions,
  not measurements from electrodes or patients. Feasibility needs no response
  value, and is exposed equally to every optimizer.
- Stages 1 and 2 use normalized beta power plus 5 times energy above a
  Pareto-derived knee. The full oracle determines this knee outside the search
  budget; thus this is an offline benchmark, not an end-to-end trial-limited
  deployable procedure. Ties in Pareto sorting now use beta, energy, then index.
- Stage 3: 16 independent binary contacts, 130 Hz, 240 microseconds,
  per-contact scale 0.25. The 41-amplitude fit is recomputed from the simulator,
  with its no-stimulation baseline: 42 simulator calls. All 65,536 masks are
  admissible in the primary benchmark, consistent with the manuscript's full
  binary space and notebook's absence of a nonzero/efficacy constraint.
  This is a **benchmark-domain choice**, not advice to turn off treatment.
- `configs/nonempty.json` changes only the Stage 3 domain and initialization
  control rule. It is a separately labeled sensitivity check over 65,535 masks,
  not a clinically justified replacement objective. Every method, including
  the oracle, excludes mask 0 there.

The Stage 3 objective drops the constant fitted intercept. Cost 0 therefore
does not mean zero beta power or cured symptoms. The fresh fit is
`c0=0.9437580303537096`, `c1=-0.11458817038088681`,
`c2=0.022290112770454028`; RMSE over its 41 samples is 0.02206272592733139.
Every linear and pair coefficient is strictly positive. Consequently mask 0
is the unique full-domain minimum. With nonempty masks, contact 12 (zero-based;
mask 4096) is the unique minimum, cost 0.17361429302581072. Both are confirmed
by exhaustive enumeration. All per-contact charge-density soft penalties are
inactive at the configured settings. Nonempty-only does not create a difficult
therapeutic decision problem; a scientifically motivated efficacy constraint or
reformulated objective, plus independently specified instances, remains future work.

## Equal information and budgets

The public search API exposes a scalar evaluator, public coordinates and public
feasibility, not the complete cost table. `BudgetedOracle` charges initial data
and rejects any unseen objective request after the limit. Cached repeated
requests provide no new observations. True costs never select an uncharged
proposal. Source separation is an auditable API convention, not a security sandbox.

For each seed every method receives the **same five feasible settings and costs**,
charged within the budget. The primary experiment includes mask/index 0 as a
no-stimulation control; the other four are uniformly sampled without replacement.
The nonempty sensitivity uses five uniform feasible masks. Including the obvious
control is deliberate and explains the primary Stage 3 tie from the first query.
It does not show equal general-purpose optimizer ability.

Budget B is the number of distinct **encoded settings** queried. Stages 1/2 replay
simulator-backed objectives already computed offline. Stage 3 replays a fitted
quadratic cost, not a neural simulation. Physically identical zero-amplitude
settings at different frequencies/pulse widths still have different grid indices;
we do not claim a budget counts distinct biological interventions. Cache hits,
failed calls and denied accesses are separately represented by the oracle.

Each method runs to 40 queries; scores at 10, 20, 30 and 40 use prefixes of that
same trajectory. Algorithms and five-point initialization do not depend on B,
so a prefix is the result available if stopped at B. Larger-budget scores are
correlated, not independent replications. A partial CMA population stops before
any extra objective read, and is not passed to `tell` as a complete generation.

## Algorithms and internal computation

| Method | Defined implementation |
|---|---|
| Random | Uniform feasible unseen settings after the shared design |
| GA | Steady-state binary GA; tournament of 3 observed candidates; one-point crossover; bit-flip probability 1/n; reject infeasible/seen proposals; bounded uniform fallback |
| BO | GP on normalized parameter coordinates (bits for Stage 3), Constant×Matérn 5/2, jitter 1e-10, two hyperparameter restarts, full feasible expected-improvement scan, xi=0.01 |
| CMA-ES | `cma` library; sigma=0.3, population=12; initialize at best shared observation clipped to [0.05,0.95]; rounded grid coordinates or threshold bits; invalid settings use known feasibility penalty without a true-cost read |
| Surrogate (exhaustive) | Ridge 0.001, intercept + all binary linear/pair features; **enumerate the entire fitted surface** and minimize over feasible unseen settings |
| QAOA (p=1) | Same surrogate family/ridge as exhaustive baseline; all couplings retained; one random-start COBYLA solve per proposal with at most 30 function calls; 256 shots per function call, 1,024 final shots; choose lowest predicted feasible unseen sampled setting |
| Sparse-first (Stage 3 diagnostic) | Same shared design/budget; query unseen masks in increasing active-contact count, with seeded random tie breaking |

For QAOA, integer bit i corresponds to qubit/contact i, little endian.
The phase is exactly `exp(-i gamma f(x))`, equivalent to
`x_i=(1-Z_i)/2`: `h_i=-l_i/2-sum_j q_ij/4`, `J_ij=q_ij/4`, with the constant
included. The custom NumPy/Numba statevector engine is checked against actual
Qiskit gates and `Statevector` on an asymmetric small instance. This is noiseless
classical circuit simulation with seeded finite-shot sampling, not quantum hardware.

No duplicate-exclusion penalty appears only in the expectation while being
missing from the circuit. The same surrogate supplies cost phases and expected
sample costs. Feasible/novel filtering happens after final measurement; an empty
eligible sample triggers logged uniform feasible fallback. For Stage 2 and the
nonempty sensitivity, the unconstrained mixer can sample inadmissible states;
they never receive true-objective evaluations. This choice can waste internal
shots and is a limitation, not hidden additional simulator information.

The statevector engine computes **all** surrogate energies to form its diagonal
phase. That computation is logged and is not evidence of an efficient hardware
implementation. An exact classical proposal is affordable at these sizes.
`resources.csv` reports full-40-query resource counts; it does not pretend they
are budget-prefix counts. COBYLA statuses and fallback events are preserved.
Failure to converge within 30 calls is a resource-limited termination, not proof
of optimum circuit parameters. No wall-time or hardware speedup claim is made.

## Seeds, precision and inference

Seeds 0–9 repeat **one** fixed, noise-free neural model instance. They are not
patients or independent model instances. Separate stable RNG streams govern
shared initialization and each method; the QAOA sampler is seeded; CMA uses
positive seed `seed+10001` to avoid the library's special seed-zero behavior.

The deterministic simulator runs 2 s with dt=100 microseconds and discards 0.2 s.
Noise-free recurrence acceleration uses Numba without fastmath; it is checked
against the original Python recurrence and beta integral. The unavailable
`np.trapz` call is replaced by `np.trapezoid` and checked against the trapezoidal
formula. The coarse time step under-resolves the smallest pulse widths, and no
time-step convergence/biophysical validation is claimed.

Mean regret and sample SD are reported. Descriptive 95% percentile bootstrap
intervals use 10,000 resamples (seed 20261003); comparisons resample paired-seed
differences. Ten seeds are a small sample; no multiple-comparison-adjusted
significance or population inference is claimed. Stage objectives differ, so
lower absolute regret in another stage does not demonstrate a structure effect.
Neither hyperparameter tuning parity nor robust best-in-class optimization was
established. A broader prespecified instance family is needed for that question.
