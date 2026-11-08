# Default Kaggle Project Directory Structure for ML Predictive Tasks

Each Kaggle project is organised in the following structure and assumes the same setup detailed in [Remote Access to Dataset Setup Guide](./SETUP.md).

```text
kaggle-<comp-name>/
├── README.md
├── pyproject.toml            # or requirements.txt
├── .gitignore
├── .env.example              # optional (API keys, paths)
│
├── notebooks/
│   ├── 00_exploration.ipynb
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_selection.ipynb
│
├── src/
│   ├── config.py             # paths, seeds, constants
│   ├── data/
│   │   ├── load_data.py       # load/split/validate
│   │   └── preprocess.py      # cleaning + transforms
│   ├── features/
│   │   └── build_features.py  # feature engineering
│   ├── models/
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── evaluate.py
│   └── utils/
│       ├── tools.py           # save/load tasks
│       └── eval.py            # hackathon custom evaluation metrics and results
│
├── models/                   # saved model artifacts (joblib, .pkl, .pt)
│   ├── lgbm_v1.pkl
│   └── xgb_v2.json
│
└── submissions/
    ├── sub_001_baseline.csv
    └── notes.csv             # optional: score, params, commit hash
```

## Kaggle Jupyter Server

The notebooks are mounted over Jupyter Servers on Kaggle. This means that the projects frequently query the cloud data directories of Kaggle Server.

Base Kaggle Directory References:

- `<kaggle-competition>/inputs/*`: Input Directory containing data from Competition.
- `<kaggle-competition>/working/*`: Output Directory containing data from project e.g. test data submission.
