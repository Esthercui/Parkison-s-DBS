# Current-state and source audit — October 3, 2026

## Scope and source selection

The supplied workspace was a broader Esther project folder with an unborn Git
branch, not the DBS checkout. The existing DBS checkout was located at
`/Users/xincui/Documents/PLTR-Research-Review/Parkison-s-DBS`, on
`review/pltr-bounded-audit` at `6aa827e4af5b234bdb9c1b8a6583d3c8ec398acd`, clean.
An independent local clone under the current project carries the corrected work
on `research/corrected-portfolio`. No unrelated project files were changed.

Live GitHub branch enumeration (including pagination), `git ls-remote --heads`
and issue/PR search found only `main` at
`b5e2468320d437bce5ddec8025ba409e5a26dc5b`, with no issues/PRs at audit arrival.
The local October audit branch was inspected in full. No other DBS correction
branch appeared in the inspected local checkout/worktree list or remote refs.
This is the inspected scope, not a claim about unknown unpublished copies.

| Source | Use and authority |
|---|---|
| Public GitHub main, b5e2468 | Three original notebooks and historical saved figures/tables; not corrected results |
| Local bounded audit, 6aa827e | Reproducible discrepancy probes, budget wrapper, explicit domain, exact surrogate helper; no integrated repaired benchmark |
| March paper from “Esther’s Project v2.0” | 22-page historical scientific description and claims; read text and visually checked the Stage 3 result page |
| Q.ESS checkout and its bounded-review references | Cross-project context only; selected files/searches found no alternative DBS engine/corrected result set |
| Joint PLTR review index and DBS technical summary | Records the DBS caveats and unresolved attribution associated with the Q.ESS review; not new scientific evidence |
| Fresh current and nonempty runs | Sole source for portfolio performance numbers |

The local Q.ESS repository, its Step 5/6 branches and concurrent tasks are
separate research. Their quantum-game results are not evidence about DBS, and
no Q.ESS source was modified or executed for this benchmark. Cross-project review
notes were used only to trace the existing DBS validation issues.

The paper was downloaded through the authenticated source-project UI. Its file
hash and page-specific revision requirements are in `PAPER_REVISION.md`. Its
author field is empty; no named contribution breakdown was found.

## History, notebooks, outputs and reproducibility

Original March history: initial Stage 1/2 upload `e6c366c`; temporary correction
files `Edits` (`73ba3cc`) and `edits_2` (`e5bc0c9`); Stage 3 upload `b0a1ac9`;
deletions of those temporary files; README `b5e2468`. The temporary files were
inspected from Git history: they contain BO initialization/sweep/plot changes,
not a repair of Stage 3 domain or Hamiltonian mapping.

| Component at arrival | Finding |
|---|---|
| Stage 1 | 19 cells, 9 saved outputs; 65,536-point grid; full-objective reads in BO, CMA batch leakage; QAOA cost mapping inconsistent with binary surrogate; no authoritative current raw seed export |
| Stage 2 | 19 cells, 10 saved outputs; 131,072 encodings; asymmetric feasibility access; “exact” surrogate is a 5,000-candidate pool for this grid; QAOA requires 17 observations before circuit proposals, so B=10 is random-only; notebook depends on helper state not defined locally |
| Stage 3 | 20 cells, 18 saved outputs; zero included in ground truth, excluded/repaired by some methods; misnamed exact pool, incorrect cost phase, CMA leakage |
| Reusable modules | October audit helpers exist; optimizer integration, fresh fit and real-circuit comparison were explicitly pending |
| Tests | Eight audit tests; several call-path checks intentionally use doubles, not performance runs |
| Config/seeds | Notebook constants, incomplete sampler seeding and no original dependency lock |
| Paper/figures/tables | Saved historical results; no clean current corrected experiment before this task |

Original notebooks are byte-for-byte preserved against b5e2468:

- Stage 1 SHA-256 `37135175904f45dea9dc435a8312f9027333a5c27c5db7aae74c9b054dd66f07`
- Stage 2 SHA-256 `44bba622f89ddb8f4a7ae4de7fafde9372241f1644e0d90fc4228983cc9f35cf`
- Stage 3 SHA-256 `ae382e730009bdb33affeee4ea6399e7b11b8f06b144874acb6eb572e57bf19f`

## Were the comparison problems already fixed?

**Partly implemented in audit helpers, not fixed end-to-end.** The October branch
introduced explicit domains, an exact surrogate helper, correct phase construction
and a budget wrapper, but left the three original notebooks untouched and explicitly
withheld a new ranking. The current task integrates those principles into a fresh
pipeline, documented in `CORRECTED_PROTOCOL.md`.

Zero stimulation is admissible in the declared primary benchmark because the
source defines all binary masks and no nonzero/efficacy requirement. It is now
accessible to every method and included as a shared charged control. The separate
nonempty check excludes it for all methods and the oracle. The fresh fit verifies
the original sign argument; no objective weights were changed to preserve a result.

The new exhaustive surrogate enumerates all encoded predictions and selects the
minimum feasible unseen setting. It minimizes the fitted surrogate, not an unknown
biological objective. The actual QAOA phase matches that same surrogate; all shots
and optimizer calls are counted. CMA stops inside batches. All methods receive the
same initial observations and feasible set. Source hashes and actual traces are
saved for every run.

## Evidence strength

The corrected engine commit is `2f89b91a2b7bd3fbd3e3aead9f2597c200390d24`.
Fresh primary oracles use 65,537 Stage 1, 77,505 Stage 2, and 42 Stage 3 simulator
calls, including baselines. The nonempty diagnostic independently refits Stage 3
(another 42). Optimizer runs replay the resulting finite objectives; they make no
additional neural-simulator calls. There are 260 optimizer runs / 10,400 charged
queries across the two experiments. Repeated budgets are prefixes, not extra runs.

Validation checks all recorded costs, domains, initialization, budgets, oracle
hashes and current source hashes. Unit tests compare recurrence/metric numerics,
real Qiskit statevectors, exhaustive prediction, seeds and all method domains.
This is a local computational reproduction with AI assistance, not independent
researcher replication, external peer review or clinical evidence.

Published engine source: [`3edf0f154febabf7347546944dc12e69cb7fd0ef`](https://github.com/Esthercui/Parkison-s-DBS/tree/3edf0f154febabf7347546944dc12e69cb7fd0ef). Its Git tree is byte-identical to execution commit C (`2f89b91`); publication changes commit metadata/parentage, not executed source.
