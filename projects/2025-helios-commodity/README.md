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

1. **Feature selection** (`src/features/selection.py`) — `f_regression`
   (sklearn) scoring of climate features against futures targets, keeping
   the top-k by F-score (`select_top_features`, used both as a single
   pass and in a rolling-window loop over 20/60/120-day means).
2. **Correlation-based signal weighting** (`src/features/selection.py`)
   — sigmoid-scaled correlation matrices to rank the strongest
   feature/target pairs (`top_correlated_pairs`).
3. **Custom evaluation metric** — a mock implementation of the
   competition's Climate-Futures Correlation Score, generalized over
   arbitrary feature/target column sets (`mock_evaluation_metric`, still
   inline in the notebook).

`notebooks/00_eda.ipynb` now imports the feature-selection/correlation
logic from `src/` instead of defining it inline; `src/config.py` is the
single source of truth for the column-group config (`ClimateLabels`,
`FutureLabels`, `MetaLabels`, `ConfigLabels`), which the notebook
previously redefined locally and had drifted out of sync with.

**Bugs found and fixed** (`tests/test_selection.py` covers the two
selection functions):
- `MetaLabels.temporal` was `["harvest_period" "growing_season_year", "date_on"]`
  — two adjacent string literals with no comma between them, which Python
  silently concatenates into one string (`"harvest_periodgrowing_season_year"`)
  instead of two list elements. Fixed in `src/config.py`.
- `all_inputs = list(set(ConfigLabels.x + NEW_COLS))` in the rolling-window
  feature-selection loop references `NEW_COLS`, which is never defined
  anywhere in the notebook — this raises `NameError` on a fresh run.
  **Not fixed** (can't guess what it should contain); flagged inline in
  the notebook and here.

**Flagged, not changed** — two things that look like bugs but weren't
touched since the original intent isn't documented (see
`select_top_features` / `top_correlated_pairs` docstrings for detail):
the rolling-window loop selects the *lowest*-scoring features
(`ascending=True`), and the correlation-pairs ranking reuses `k` for two
unrelated purposes (top-N count and a triu mask offset).

## Evaluation

Official metric: **Climate-Futures Correlation Score (CFCS)**. A local mock
of this metric is implemented in `notebooks/00_eda.ipynb` for offline
validation before submission.

## Results

_Leaderboard score not yet recorded — update after a scored submission._

## Extensions

- Define what `NEW_COLS` should contain (see the bug above) so the
  rolling-window feature-selection loop actually runs.
- Confirm whether the rolling-window loop's `ascending=True` and the
  correlation-pairs `k` double-duty are intentional or bugs (see
  "Flagged, not changed" above) and fix if not.
- Add `01_feature_engineering.ipynb` / `02_model_selection.ipynb` between
  EDA and submission, or document why the pipeline currently skips them.
- Validate the mock CFCS implementation against the official scorer once
  available; consider moving it into `src/features/` too.

## References

None yet — add any competition discussion posts or papers referenced
during feature design.
