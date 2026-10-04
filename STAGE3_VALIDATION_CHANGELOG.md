# Stage 3 Validation Changelog

Base: `b43e30bdccba85767f3a8835ab30e313a60b9977`.
Branch: `research/stage3-methodology-validation`.

## Changed

- `stage3.ipynb`: only cells 7–9. Correct binary-QUBO-to-Ising cost rotations, use the same quadratic ridge fit for QAOA and a new Exhaustive comparator, add proposal/shot/fallback diagnostics and the comparator to the benchmark list. Existing Pool logic, initial sampling and QAOA fallback/parameter settings retained.

## Added

- `stage3_validation_core.py`: testable mapping, cost-layer, identical surrogate-fit, full feasible enumeration and count diagnostics.
- `validate_stage3.py`: mapping gate, unchanged-model validation, cached amplitude comparisons, primary benchmark recording and scope preservation checks.
- `stage3_validation_analysis.py`: paired statistics, complete summaries, five figure families and raw-data acceptance checks. Final visual inspection required only a plot z-order correction so markers remain visible over boxplots; experiment code/results were unaffected.
- `test_stage3_validation.py`: six targeted tests for full-space mapping, old/new fit identity, exhaustive selection/ties, initial matching, instrumentation neutrality and forced fallback.
- `STAGE3_VALIDATION_REPORT.md`: requested A–L scientific report, all result tables, interpretation, limitations and reproduction commands.
- `STAGE3_VALIDATION_CHANGELOG.md`: this bounded change inventory.
- `results/stage3_validated/`: new raw observations, counts, validations, statistics, provenance and PNG/PDF/SVG figures. See the report's data inventory. Pilot data remain labeled and excluded from the primary analysis.

## Removed

None. No old experiments, branches or controlled outputs were removed.

## Unchanged / verified

- Stage 1 and Stage 2 are byte-identical to the controlled parent.
- Notebook cells 0–6, including simulator, beta power, fit expression, contact metadata, objective weights, feasibility rules and classical method definitions, are source-identical.
- The historical Pool function is AST-identical; all 600 Random/GA/BO/CMA-ES/Pool runs exactly reproduce the controlled observations.
- Original budgets 10/20/30/40, 30 seeds, p=1, X mixer, COBYLA procedure, shots and fallback remain frozen.
- README, requirements-stage3.txt, run_stage3.py and STAGE3_RESULTS.md are byte-identical.
- Every file under results/stage3_controlled/ is byte-identical. The controlled branch is unchanged.
- **The research manuscript was not modified.** No Abstract, Results, Discussion or Conclusion was rewritten.
- No new algorithm, objective, clinical variable, cardinality penalty, XY mixer, increased QAOA depth or performance-driven tuning was introduced.

Evidence: results/stage3_validated/starting_state.json, frozen_scope_validation.json, unchanged_classical_replay.json, acceptance_checks.json and source_provenance.json.
