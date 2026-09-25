# Hedge Fund / Time-Series Forecasting

## Overview

Kaggle time-series prediction competition (`ts-prediction` dataset:
`train.parquet` / `test.parquet`) — forecasting a financial/hedge-fund
target across multiple prediction horizons, grouped by an entity `ID` and
`code`/`sub_code`/`sub_categories` fields.

#### Objective

Predict the target variable(s) per `ID` across the available forecast
horizons. Exact target definition and horizon set to be confirmed against
the competition page.

#### Data

`ts-prediction/train.parquet` and `test.parquet`: `ID`-grouped rows with
`code`/`sub_code`/`sub_categories` fields and multiple horizon columns.

## Methods Implemented

- **Feature exploration** (`notebooks/00_eda.ipynb`, formerly
  `exploratory_analytics.ipynb`): config/utils scaffolding, an example
  model, and a training pass; ends with a save-and-submit step.
- **LightGBM pipeline** (`notebooks/03_submission.ipynb`, formerly
  `submission.ipynb`): config → utils → feature processors → LGBM
  training → predictions — this is the more complete, current approach.

## Results

*Not available*

## Extensions (carried over from the notebook's own TODO list)

- Focus at a single horizon (e.g. horizon 1 = short-term) and segment
  `ID`-grouped rows by quantiles relative to the available horizons.
- Add lag features once focused on the first horizon.
- Test correlation against `code`/`sub_code`/`sub_categories` to decide
  whether these are viable targets or warrant an independent model.
- Consolidate `00_eda.ipynb` and `03_submission.ipynb` so feature/config
  logic isn't duplicated between them (see `src/` template in the parent
  `projects/README.md`).
