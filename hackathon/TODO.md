# Kaggle Portfolio Cleanup — Checklist TODO

This checklist turns `projects/` from a working scratch space into a
postgrad-research / AI-engineer portfolio. It uses the directory template and
`.gitignore` addons already defined in [`README.md`](./README.md) as the
"definition of done" for every competition folder.

**Status:** the documentation pass (READMEs, safe renames/moves) below is
done for all 9 projects. What's left is deeper, per-project engineering
work (splitting notebook internals into `src/`, implementing stubbed
functions, producing scored results) — see the unchecked items.

## Definition of Done (per project)

A project is portfolio-ready when it has:

1. A `README.md` with **Competition Brief, Objective, Data, Methods,
   Evaluation, Results, Extensions, References** (template below).
2. Code split out of notebooks into `src/` (config, data, features, models,
   utils), with notebooks kept for EDA/reporting only.
3. Numbered, linearly-readable notebooks (`00_eda`, `01_feature_engineering`,
   `02_model_selection`, `03_submission`) — no `archived.ipynb`,
   `exploratory_analytics.ipynb`-style ad hoc names, or duplicate drafts.
4. No large/regeneratable artifacts committed (`data/raw`, `data/interim`,
   `data/processed`, `models/`, `.ipynb_checkpoints/`) — these are
   `.gitignore`d and documented as "download via Kaggle API" instead.
5. Pinned dependencies (`pyproject.toml` or `requirements.txt`) if the
   project deviates from the root `requirements.txt`.
6. A one-line entry in the root `projects/README.md` (or a portfolio index)
   summarizing status and result.

---

## 0. Repo-level (do first, unblocks everything below)

- [x] Add `data/`, `models/`, `submissions/*.csv` (keep `notes.csv`), and
      `reports/figures/` to the root `.gitignore` — scoped to
      `projects/*/...` (one path segment) so it doesn't also match nested
      `src/models/` code directories.
- [ ] Decide and document one convention for per-project envs: always root
      `requirements.txt`, or allow a project-local `pyproject.toml` — several
      projects already assume Kaggle-kernel-installed deps with no manifest.
- [x] Add a short **status table** to `projects/README.md` (Draft / In
      Progress / Submitted / Written Up).
- [x] Remove and `.gitignore` the stray `.DS_Store` files.

## 1. Per-project checklist

### `2025-adaptive-immune-profiling`
- [x] Add `README.md`.
- [x] Move `ngram.py` into `src/features/`; fixed a real `NameError` bug
      (`pd.DataFrame` type hint used without importing pandas).
- [x] Rename notebook to `notebooks/00_eda.ipynb`.
- [x] Document current status (EDA/scaffolding only) in the README.
- [ ] Implement `NGramKernelProcessor.__call__` (currently `pass`).
- [ ] Confirm the exact competition objective/metric (not yet documented).
- [ ] Clear or relocate the "Scratchpad for dummy runs" notebook section.

### `2025-brain-to-text`
- [x] Expand `README.md`: Objective, Data, Methods Implemented (baseline
      RNN + n-gram/LM rescoring ensemble), Evaluation (WER), Results
      placeholder, Extensions, References.
- [x] Rename notebooks to `00_eda.ipynb` / `03_submission.ipynb`.
- [ ] Add the `01_feature_engineering` / `02_model_selection` step, or
      confirm the pipeline intentionally collapses eda → submission.
- [ ] Add module-level docstrings to `src/main.py` / `src/utils.py`.

### `2025-chart-students-map`
- [x] Add `README.md` documenting the MAP misconception taxonomy and the
      two-stage (correctness + misconception) model approach.
- [x] Explain `const.json` in the README.
- [ ] Extract the two-stage model classes and data processors out of
      `01_map_model_building.ipynb` / `02_map_final.ipynb` into `src/`.
- [ ] Finish the stubbed improvements in `01_map_model_building.ipynb`
      (`child_role_play`, `add_contrast_responses`, `build_feature_pool`).
- [ ] Record the final scored result once submitted.

### `2025-hedge-fund-forecasting`
- [x] Extract the notebook's TODO checklist into `README.md` under
      Extensions.
- [x] Move `archived.ipynb` (duplicate draft, identical TODO list to the
      EDA notebook) into `notebooks/_archive/`.
- [x] Add `README.md`.
- [x] Rename notebooks to `00_eda.ipynb` / `03_submission.ipynb`.
- [ ] Consolidate config/feature logic shared between the EDA and
      submission notebooks into `src/` instead of duplicating it.

### `2025-helios-commodity`
- [x] Add `README.md` (CFCS objective/evaluation promoted from the
      notebook).
- [x] Move `config.py` / `__init__.py` under `src/`.
- [x] Rename notebooks to `00_eda.ipynb` / `03_submission.ipynb`.
- [ ] Move the feature-selection/correlation-weighting logic out of
      `00_eda.ipynb` into `src/features/`.
- [ ] Add the intermediate feature-engineering/model-selection notebooks,
      or confirm the pipeline intentionally skips them.

### `2025-rsna-competition`
- [x] Add `README.md` (BiomedCLIP zero-shot image-text ensemble approach).
- [x] Move the notebook into `notebooks/00_eda.ipynb`.
- [ ] **Not done**: split the notebook's ensembling logic into
      `src/models/` — it still mixes DICOM data prep and BiomedCLIP
      scoring in one file, the weakest structure in the portfolio.
- [ ] Add the actual aneurysm-detection head; current code stops at
      zero-shot image–text similarity scoring.
- [ ] Confirm the official evaluation metric.

### `2026-aimo3`
- [x] Add `README.md` documenting the no-internet-at-submission
      constraint and the Unsloth/QLoRA + vLLM pipeline.
- [x] Rename notebooks to `00_dependency_setup.ipynb` / `01_baseline.ipynb`;
      marked `example_submission.ipynb` as
      `notebooks/reference_example_submission.ipynb` (Kaggle-provided
      template, not authored work).
- [x] Move `aimo3_unsloth_submission.py` into `src/models/`.
- [ ] Split the fine-tune (Part 1) and inference (Part 2) halves of
      `src/models/aimo3_unsloth_submission.py` into separate entry points.
- [ ] Confirm whether `01_baseline.ipynb` is superseded by the Unsloth
      pipeline or still an active fallback/ensemble member.

### `2026-customer-analytics-with-dl`
- [x] Promote the notebook's objective/domain-background markdown into
      `README.md`.
- [x] Add an Evaluation section (silhouette score today; flagged that
      segment-quality assessment beyond that isn't implemented).
- [ ] Implement the SOM model referenced by the project/notebook name —
      not yet in the notebook (K-Means is the only clustering implemented).
- [ ] Split `customer_segments_som.ipynb` into `00_eda.ipynb` +
      `src/models/` once the approach stabilizes.
- [ ] Scale beyond the 100-row embedding sample.

### `2026-march-madness-ncaa`
- [x] Add `README.md` (rank-difference logit heuristic, Massey features).
- [x] Add `references/README.md` attributing the two external
      XGBoost/Elo notebooks (kernel URLs still unknown — see TODO there).
- [x] Rename notebook to `00_eda.ipynb`.
- [ ] Resolve "Processing Draft 2" into a single canonical EDA notebook.
- [ ] Move Massey/rank-difference feature engineering into `src/features/`.
- [ ] Back-fill the original kernel URLs in `references/README.md`.

---

## 2. README documentation template (apply per project)

```markdown
# <Competition Name>

## Competition Brief
Link, host, timeline, prize/purpose, and why this competition was chosen.

## Objective
What is being predicted, from what inputs, and why it's a hard problem.

## Data
Source, size, modality, key fields, any licensing/access constraints
(e.g. Kaggle-only, no internet at inference).

## Methods Implemented
Approach(es) tried, in order, with rationale for each (baseline →
iteration). Link to the relevant `src/` module or notebook per method.

## Evaluation
Official competition metric + any additional validation strategy
(CV scheme, holdout, leaderboard score if available).

## Results
Best score achieved, what worked, what didn't, and why.

## Extensions
Concrete next steps if resumed — not aspirational, but a scoped backlog.

## References
Papers, notebooks, or discussions referenced/borrowed from, with attribution.
```

## 3. Remaining work, in priority order

1. Decide the per-project dependency convention (§0) — the one open
   repo-level item.
2. `2025-rsna-competition` — the only project whose notebook still mixes
   data prep and modeling in one file; splitting it into `src/models/` is
   the highest-value remaining structural fix.
3. Fill in real **Results** once each project has a scored Kaggle
   submission (`2025-brain-to-text` and `2025-helios-commodity` are
   closest to a first submission).
4. Finish stubbed functions called out per project above
   (`NGramKernelProcessor.__call__`, MAP model-building TODOs, the SOM
   model, `01_map_model_building.ipynb`'s flagged improvements).
5. Back-fill `references/README.md` kernel URLs for march-madness-ncaa.
