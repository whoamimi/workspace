# Kaggle Hackathons

## A Kaggle Project Directory Setup for ML Predictive Tasks

```text
kaggle-<comp-name>/
├── README.md
├── pyproject.toml            # or requirements.txt
├── .gitignore
├── .env.example              # optional (API keys, paths)
│
├── data/
│   ├── raw/                  # immutable Kaggle files
│   │   ├── train.csv
│   │   ├── test.csv
│   │   └── sample_submission.csv
│   ├── interim/              # cached intermediate datasets (optional)
│   └── processed/            # features, cleaned tables, etc.
│
├── notebooks/
│   ├── 00_exploration.ipynb
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_selection.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py             # paths, seeds, constants
│   ├── data/
│   │   ├── make_dataset.py    # load/split/validate
│   │   └── preprocess.py      # cleaning + transforms
│   ├── features/
│   │   └── build_features.py  # feature engineering
│   ├── models/
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── evaluate.py
│   └── utils/
│       ├── io.py             # save/load helpers
│       └── metrics.py
│
├── models/                   # saved model artifacts (joblib, .pkl, .pt)
│   ├── lgbm_v1.pkl
│   └── xgb_v2.json
│
├── submissions/
│   ├── sub_001_baseline.csv
│   ├── sub_002_fe_lgbm.csv
│   └── notes.csv             # optional: score, params, commit hash
│
├── reports/
│   ├── figures/
│   └── eda_summary.md
│
└── scripts/
    ├── train.sh              # optional
    └── make_submission.sh    # optional
```

**Git Ignore Addons**

```text
__pycache__/
.ipynb_checkpoints/
.env
data/raw/
data/interim/
data/processed/
models/
```

## Dependency Convention

The root [`requirements.txt`](../requirements.txt) is a full freeze of the
shared workspace environment (Jupyter, numpy/pandas/scipy/scikit-learn,
torch, transformers, sentence-transformers, etc.) — install it first for
any project.

A project adds its **own** `requirements-extra.txt` only when it needs
packages beyond that base (e.g. `2025-rsna-competition/requirements-extra.txt`
for `pydicom`/`nibabel`/`open-clip-torch`/`albumentations`). Install it
alongside the root file:

```bash
pip install -r requirements.txt -r projects/<project>/requirements-extra.txt
```

Don't use a project-local `pyproject.toml` unless a project needs a fully
separate, isolated environment (dependency conflicts, a different Python
version). `2026-aimo3` is the one exception in this repo: its Unsloth/vLLM
stack is deliberately installed by `notebooks/00_dependency_setup.ipynb`
itself, not a static requirements file, because the competition kernel has
no internet access at submission time and needs specific packages
uninstalled first to avoid version conflicts — see that project's README.

## Testing Convention

A project's `tests/` (where present) is run independently:

```bash
pytest projects/<project>/tests
```

**Every project's `src/` uses the same top-level package name `src`**
(per the directory template above). Running more than one project's
tests in a single `pytest` process — e.g. `pytest projects/` from the
repo root — needs the previous project's `src` cleared from
`sys.modules` first, or Python's import cache resolves a later
project's `from src...` to whichever project imported it first and
fails with a confusing `ModuleNotFoundError`. Each `tests/*.py` file
handles this itself (see the comment above its `sys.path` setup); it's
not something a project relying on this template gets for free.

## Project Status

Tracks actual state against the [portfolio cleanup checklist](./TODO.md).
Update this table whenever a project's status changes.

| Project | Competition | Status | Result |
|---|---|---|---|
| [`2025-adaptive-immune-profiling`](./2025-adaptive-immune-profiling) | Adaptive Immune Profiling Challenge 2025 | Draft (EDA only) | — |
| [`2025-brain-to-text`](./2025-brain-to-text) | Brain-to-Text '25 | In Progress | — |
| [`2025-chart-students-map`](./2025-chart-students-map) | Map Charting Student Math Misunderstandings | Draft | — |
| [`2025-hedge-fund-forecasting`](./2025-hedge-fund-forecasting) | Hull Tactical / Hedge Fund Forecasting | Draft | — |
| [`2025-helios-commodity`](./2025-helios-commodity) | Helios Corn Climate Challenge | In Progress | — |
| [`2025-rsna-competition`](./2025-rsna-competition) | RSNA Intracranial Aneurysm Detection | Draft (EDA only) | — |
| [`2026-aimo3`](./2026-aimo3) | AI Mathematical Olympiad 3 | Draft | — |
| [`2026-customer-analytics-with-dl`](./2026-customer-analytics-with-dl) | Customer Segmentation with Deep Learning | Draft | — |
| [`2026-march-madness-ncaa`](./2026-march-madness-ncaa) | NCAA March Madness 2026 | Draft | — |

Status legend: **Draft** (exploration/EDA only, no submission) · **In Progress**
(iterating on a submitted model) · **Submitted** (final entry made) ·
**Written Up** (README complete with results/extensions, portfolio-ready).

## Kaggle Jupyter Server

The notebooks are mounted over Jupyter Servers on Kaggle. This means that the projects frequently query the cloud data directories of Kaggle Server.

Base Kaggle Directory References:

- `<kaggle-competition>/inputs/*`: Input Directory containing data from Competition.
- `<kaggle-competition>/working/*`: Output Directory containing data from project e.g. test data submission.
