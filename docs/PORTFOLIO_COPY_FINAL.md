# Quantum-assisted Optimization of Parkinson's DBS Parameters

**A ground-truth benchmark for optimization under constrained trial budgets**

Co-developed a simulation-based benchmark for Parkinsonian DBS tuning that compares classical and quantum-assisted optimization under fixed evaluation budgets. The project asks a narrower question than 'is quantum better?': which optimization methods fit which kinds of search structure?

DBS programming is an optimization problem under constraints. Frequency, amplitude, pulse width, and contact choices interact, while only a limited number of settings can realistically be tested. We built a benchmark that makes those tradeoffs measurable by scoring optimizers against an exhaustively computed ground truth.

Here, ground truth means the minimum of a specified simulation/proxy objective
over a finite grid or binary contact space. It does not mean the best treatment
for a patient. Query budgets are a research convention, not validated clinical trial counts.

## What the corrected experiments show

A fresh comparison across ten paired optimizer seeds did not support the
original claim that QAOA was the strongest Stage 3 method.

- **Stage 1:** at 40 objective queries, CMA-ES had the lowest observed mean regret (0.0585 ± 0.0340 sample SD); QAOA p=1 had 0.1009 ± 0.0281.
- **Stage 2:** exhaustive surrogate search had the lowest observed mean regret (0.0604 ± 0.0294); QAOA had 0.0734 ± 0.0207.
- **Stage 3:** the current objective prefers zero active contacts. With a shared no-stimulation control, every method reached zero regret. In a separate nonempty-domain check, QAOA and several classical baselines all reached the same singleton optimum by budget 40.

The contribution is a reproducible framework for asking the comparison fairly,
including evidence that an apparently large combinatorial space can have a
trivial optimum. A later validation audit identified inconsistent feasible sets,
a misleading “exact” comparator label, an incorrect cost-circuit mapping and
budget leakage. The corrected pipeline addresses these issues and retains the
negative results.

These runs use one simplified, noise-free STN–GPe model and beta-band/energy
proxies. QAOA is simulated on classical hardware. Objective queries, neural
simulations and internal circuit shots are counted separately. The work does
not demonstrate clinical efficacy, quantum hardware speedup or quantum superiority.

## Collaboration note

This was a collaborative project. Individual historical responsibilities are
still being verified; Esther should not be presented as sole author. The later
correction, rerun and portfolio preparation used Codex assistance at Xin's request.
Do not attribute all code or validation discoveries to Esther independently.

## Links and figure captions

- **Code and reproduction:** use the delivered corrected repository commit and README.
- **Results:** `results/RESULTS.md`, with complete seed data and paired confidence intervals.
- **Architecture:** “Offline simulator/oracle construction is separate from budgeted optimizer access.”
- **Results figure:** “Corrected B=40 regret on the original finite domains. Dots show ten paired optimizer seeds; diamonds show means; whiskers are descriptive 95% bootstrap intervals. Compare methods within each stage.”
- **Stage 3 figure:** “Every contact increases this fitted objective. The nonempty check is a sensitivity analysis, not a therapeutic redesign.”
- **Paper:** “Historical March 2026 manuscript — results and conclusions require revision.”

Do not publish “first rigorous benchmark,” “quantum advantage,” “QAOA becomes
best as constraints increase,” “clinically realistic/validated budgets,” or
“75–80% improvement” from the historical manuscript. This copy supersedes those
performance claims. Contribution-specific elaboration awaits `COLLABORATION_TODO.md`.
