# Kaggle Portfolio Cleanup — Checklist TODO

This checklist turns `projects/` from a working scratch space into a
postgrad-research / AI-engineer portfolio. It uses the directory template and
`.gitignore` addons already defined in [`README.md`](./README.md) as the
"definition of done" for every competition folder.

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

- [ ] Add `data/`, `models/`, `submissions/*.csv` (keep `notes.csv`), and
      `reports/figures/` to the root `.gitignore` — the addons are documented
      in `projects/README.md` but not actually applied yet.
- [ ] Decide and document one convention for per-project envs: always root
      `requirements.txt`, or allow a project-local `pyproject.toml` — several
      projects already assume Kaggle-kernel-installed deps with no manifest.
- [ ] Add a short **status table** to `projects/README.md` (Draft / In
      Progress / Submitted / Written Up) so the portfolio index reflects
      reality — currently the README only documents the *ideal* structure,
      not the actual state of each competition folder.
- [ ] Remove or `.gitignore` the stray `.DS_Store` files (`projects/`,
      repo root) and add `.DS_Store` to `.gitignore` if not already covered.

## 1. Per-project checklist

### `2025-adaptive-immune-profiling` — Stub
- [ ] Add `README.md` (competition brief + objective are currently only
      implied by the notebook title).
- [ ] Move `ngram.py` into `src/features/` and import it from the notebook
      instead of keeping logic loose at the project root.
- [ ] Rename `airr_exploration.ipynb` → `notebooks/00_eda.ipynb`.
- [ ] Document current status: EDA only, no model/submission yet — say so
      explicitly rather than leaving the reader to infer it.

### `2025-brain-to-text` — Most complete, needs write-up
- [ ] Expand `README.md` beyond the setup steps: add **Objective**
      (task/metric), **Data**, **Methods Implemented** (which pretrained
      models were ensembled and why), **Results** (leaderboard score if
      any), and **Extensions**.
- [ ] Rename `notebooks/submission.ipynb` → `notebooks/03_submission.ipynb`
      and add a `01_feature_engineering` / `02_model_selection` step, or
      note in the README why the pipeline collapses to eda → submission.
- [ ] Confirm `src/main.py` and `src/utils.py` have module-level docstrings
      or a short "what lives here" note, and that `setup.sh` is referenced
      from the README's Setup section.

### `2025-chart-students-map` — Needs README + src split
- [ ] Add `README.md`: this is the Kaggle "Map Charting Student Math
      Misunderstandings" competition — state the objective (predict
      `Category:Misconception` label from student explanations), data, and
      evaluation metric explicitly (currently only inferable from
      `const.json`'s label definitions).
- [ ] Explain `const.json` in the README (label taxonomy) or move it under
      `src/config/` with a docstring.
- [ ] Notebooks are already well-numbered (`00`, `01`, `02`) — keep this
      pattern, just add `src/` for any reusable preprocessing/model code
      currently inlined in `01_map_model_building.ipynb`.
- [ ] Record final result in the README (`02_map_final.ipynb` output).

### `2025-hedge-fund-forecasting` — Draft, has TODO buried in notebook
- [ ] Extract the planning checklist currently living as a markdown cell in
      `exploratory_analytics.ipynb` into the project `README.md` under
      **Methods / Next Steps** — a notebook cell is not discoverable as
      project documentation.
- [ ] Resolve `archived.ipynb`: either delete it (git history preserves it)
      or move it to `notebooks/_archive/` with a one-line note on why it was
      abandoned. Don't leave "archived" work as a top-level sibling to
      active work.
- [ ] Add `README.md` with competition brief/objective/evaluation metric —
      none of this is documented outside notebook comments today.
- [ ] Rename `submission.ipynb` → `notebooks/03_submission.ipynb`.

### `2025-helios-commodity` — Good structure, missing README
- [ ] Add `README.md` — objective and evaluation metric ("Climate-Futures
      Correlation Score") already exist as a markdown cell in
      `notebooks/eda.ipynb`; promote that to the README's **Brief /
      Objective / Evaluation** sections.
- [ ] Move `config.py` under `src/config.py` (currently at project root,
      inconsistent with the template's `src/config.py` convention used
      elsewhere).
- [ ] Rename `notebooks/eda.ipynb` → `00_eda.ipynb`,
      `notebooks/submission.ipynb` → `03_submission.ipynb`; add the
      intermediate feature/model steps or note their absence.

### `2025-rsna-competition` — Stub, single notebook
- [ ] Add `README.md`: objective (intracranial aneurysm detection), data
      modality (imaging + metadata), evaluation metric, and current status.
- [ ] Split `rsna-ensemble-model.ipynb` into `notebooks/00_eda.ipynb` +
      `src/models/` for the ensembling logic — a single monolithic notebook
      mixing data prep and ensembling is the weakest structure in the
      portfolio right now.

### `2026-aimo3` — Needs consolidation
- [ ] Add `README.md`: objective (AI Mathematical Olympiad), constraint that
      matters most for methods (**no internet access at submission time**,
      already noted inline in `aimo3-utility-notebook-dependency-install-1-2`)
      — this constraint should be a first-class README note since it drives
      the whole dependency-bundling approach.
- [ ] Rename for a linear read order: `00_dependency_setup.ipynb` (from
      `aimo3-utility-notebook-dependency-install-1-2.ipynb`),
      `01_eda_or_baseline.ipynb` (from `aimo-3-notebook.ipynb`),
      `02_submission.ipynb`.
- [ ] `example_submission.ipynb` has a single cell — confirm whether it's a
      Kaggle-provided template (mark clearly as reference/not-authored) or
      delete if superseded.
- [ ] Move `aimo3_unsloth_submission.py` into `src/models/` and document the
      Unsloth fine-tuning approach in the README's **Methods** section.

### `2026-customer-analytics-with-dl` — Good objective writeup, needs structure
- [ ] Promote the notebook's existing **objective / domain background**
      markdown cell into `README.md` verbatim — it's already
      portfolio-quality prose, just in the wrong place.
- [ ] Split `customer_segments_som.ipynb` into `00_eda.ipynb` +
      `src/models/som.py` (or similar) once the SOM/clustering approach
      stabilizes; note in README which of PCA/t-SNE/UMAP/SOM were actually
      used vs. considered.
- [ ] Add **Evaluation** section: how is segment quality assessed
      (silhouette score, business interpretability, label agreement)?

### `2026-march-madness-ncaa` — Draft, mixes own work with references
- [ ] Add `README.md` with objective (bracket/win-probability prediction),
      data (historical NCAA results, Elo/seed features), and evaluation
      metric (Kaggle's log-loss).
- [ ] Clearly label `references/*.ipynb` as **external reference
      notebooks** (not authored work) in the README — right now they sit
      indistinguishable from own analysis; consider a `references/README.md`
      with source links/attribution.
- [ ] Rename `exploratory_notebook.ipynb` → `00_eda.ipynb`; the "Processing
      Draft 2" section heading signals unresolved iteration — resolve into a
      single canonical EDA notebook before portfolio write-up.

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

## 3. Suggested execution order

1. Repo-level `.gitignore` + status table (§0) — one PR, unblocks everything.
2. `2025-brain-to-text` and `2025-helios-commodity` — closest to done; write
   these up first for quick portfolio wins.
3. `2025-chart-students-map` and `2026-customer-analytics-with-dl` — already
   have strong objective write-ups buried in notebooks; promoting them to
   READMEs is low effort, high payoff.
4. Remaining stubs (`2025-adaptive-immune-profiling`, `2025-rsna-competition`,
   `2025-hedge-fund-forecasting`, `2026-aimo3`, `2026-march-madness-ncaa`) —
   decide per project whether to finish, or document as "paused" with a
   clear objective/status so it still reads as intentional in a portfolio.
