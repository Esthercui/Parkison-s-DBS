> Publication note: this report records the original manuscript delivery. GitHub integration subsequently updates the root README and adds `paper/v2/`; scientific code and results remain frozen. Local delivery paths have been omitted from this public copy.

# DBS Manuscript Version 2 — Read First

**Benchmarking Quantum-Assisted Optimization for Parkinson’s Deep Brain Stimulation: A Ground-Truth Validation Study**

October 2026 Validated Revision — completed October 4, 2026.

## Read and edit

- **`CURRENT_v2_DBS_Manuscript.pdf`** — complete manuscript, 22 PDF pages including title, references and appendices; 4,859 words of main prose including the 226-word abstract (excluding equations, tables, captions, headings, references and appendices).
- **`CURRENT_v2_DBS_Manuscript.tex`** — canonical editable, PDF-ready source. Keep `tables/` and `figures/` beside it. All citations are self-contained in the source; no external bibliography download is needed to compile.
- **`CURRENT_v2_DBS_Validation_Note.pdf`** and **`RESEARCH_EVOLUTION_AND_VALIDATION_NOTE.md`** — concise research-evolution/validation note.
- **`VERSION2_CLAIM_AUDIT.md`**, **`REFERENCES_AUDIT.md`**, **`VERSION2_CHANGELOG.md`**, **`VERSION2_OLD_VS_NEW.md`**, **`FIGURE_MANIFEST.md`**, **`TABLE_MANIFEST.md`**, **`FINAL_QUALITY_CHECK.md`**, **`VERSION2_COMPLETION_REPORT.md`** — claims, provenance, differences, manifest and completion records.
- **`evidence/`** — selected frozen data, reference metadata, source-preservation checks and manuscript QA; full raw research data remain in the frozen repository.
- **`version1-preserved/PRESERVED_v1_DBS_March2026.pdf`** — byte-identical March 2026 Version 1, preserved for reference.

The full directory is delivered as **`CURRENT_v2_DBS_Manuscript_Package.zip`**. This is a manuscript/source package, not a new experimental-code release.

## Scientific result

Corrected simulated p=1 QAOA remains competitive in objective-query efficiency but is not statistically separated from full-domain classical surrogate search at any tested budget. All principal Holm-adjusted p values are 1.000; this is not equivalence. Fallback is zero. The efficacy-model mismatch and cardinality sensitivity prevent physiological or clinical interpretation of the six-contact requirement. Strong classical methods remain practical current-scale benchmark choices.

## Important source qualification

Stage 1/2 values are preserved with disclosed historical limits. The Stage 2 table-image conflict is resolved to the frozen notebook/prose-consistent sweep. The Stage 1 sweep raw data/n are not supplied. Historical Stage 1/2 phase and budget-accounting routines are not retroactively covered by corrected Stage 3 validation. These qualifications are in the manuscript, not only this note.

## Build

From this directory, a Tectonic installation can compile:

```sh
tectonic CURRENT_v2_DBS_Manuscript.tex
```

The local delivery was built with the existing bundled Tectonic 0.17.0 through the LaTeX plugin compiler. This command builds the document only and does not execute research code. Standard XeLaTeX with the listed packages is an alternative; it was not tested in this task.

## Provenance and delivery

Frozen research commit: `a94acf521bc596583b873283a509b43418b0fb76`.

Mac source directory: `paper/v2/`.


NAS current filenames: `CURRENT_v2_DBS_Manuscript.pdf`, `CURRENT_v2_DBS_Manuscript_Package.zip`, `CURRENT_v2_DBS_Validation_Note.pdf`, and `CURRENT_v2_DBS_Read_First.md`.

No previous manuscript delivery is replaced or archived; Version 1 remains unchanged. Existing Stage 3 validation reports/source packages remain separate evidence products.
