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

## Kaggle Jupyter Server

The notebooks are mounted over Jupyter Servers on Kaggle. This means that the projects frequently query the cloud data directories of Kaggle Server.

Base Kaggle Directory References:

- `<kaggle-competition>/inputs/*`: Input Directory containing data from Competition.
- `<kaggle-competition>/working/*`: Output Directory containing data from project e.g. test data submission.
