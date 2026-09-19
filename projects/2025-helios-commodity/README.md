# Helios Corn Climate Challenge

## Competition Brief

Kaggle competition: *"Forecasting the Future — The Helios Corn Climate
Challenge"* (`forecasting-the-future-the-helios-corn-climate-challenge`).

## Objective

Encode climate-driven signals about corn futures behaviour (prices,
returns, volatility, term structure) so a supervised model using those
features can predict corn futures variables well.

## Data

Two Kaggle-provided tables (see `src/config.py`):

- **Futures/climate data** (`FutureLabels`, `ClimateLabels`): daily corn
  (`ZC`), wheat (`ZW`), and soybean (`ZS`) futures prices/returns, moving
  averages and volatility measures, plus regional climate-risk counts
  (heat/cold/precipitation/drought stress, at low/medium/high severity).
- **Regional market-share data** (`MetaLabels`): country/region production
  share, used to weight regional climate risk economically.

## Methods Implemented

1. **Feature selection** — `f_regression` (sklearn) scoring of climate
   features against futures targets, keeping the top-k by F-score
   (`notebooks/00_eda.ipynb`).
2. **Correlation-based signal weighting** — softmax/sigmoid-scaled
   correlation matrices to rank feature relevance (`build_weights`).
3. **Custom evaluation metric** — a mock implementation of the
   competition's Climate-Futures Correlation Score, generalized over
   arbitrary feature/target column sets (`mock_evaluation_metric`).

## Evaluation

Official metric: **Climate-Futures Correlation Score (CFCS)**. A local mock
of this metric is implemented in `notebooks/00_eda.ipynb` for offline
validation before submission.

## Results

_Leaderboard score not yet recorded — update after a scored submission._

## Extensions

- Move the ad hoc feature-selection/correlation logic out of
  `notebooks/00_eda.ipynb` into `src/features/` so it's reusable across the
  EDA and submission notebooks.
- Add `01_feature_engineering.ipynb` / `02_model_selection.ipynb` between
  EDA and submission, or document why the pipeline currently skips them.
- Validate the mock CFCS implementation against the official scorer once
  available.

## References

None yet — add any competition discussion posts or papers referenced
during feature design.
