# NCAA March Madness 2026

## Competition Brief

Kaggle's annual NCAA March Madness bracket-prediction competition:
predict win probabilities for every possible matchup in the men's/women's
tournament.

## Objective

Given team/season/game data, predict the probability that Team 1 beats
Team 2 for each tournament matchup, across all rounds (First Four →
Round of 64 → Round of 32 → Sweet 16 → Elite 8 → Final Four →
Championship).

## Data

- `teams`, `seasons`, `game_cities` — competition config tables.
- Game-by-game results, keyed to tournament day ranges per round (see
  `notebooks/00_eda.ipynb`, "Processing Draft 2").
- Massey Ordinals (external ranking system) — used for feature
  engineering and as an Elo-adjacent baseline.

## Methods Implemented

1. **Rank-based heuristic**: transform the ordinal rank difference
   `Δr = r1 - r2` between two teams into a win probability via a
   logistic-style map `p(Team1 wins) = 1 / (1 + exp(aΔr + b))`, with
   `a, b` fit from historical results.
2. **Massey features**: engineered features from Massey Ordinals rankings,
   including bookmaker-odds normalization ("Normalizing Bookies").
3. **Statistical summary** baseline using 2025 season data.
4. External reference approaches kept under [`references/`](./references)
   (see below) — **not authored work**, kept for comparison:
   - `ncaa-basketball-predictions-with-xgboost.ipynb` — gradient-boosted
     tree model over engineered features.
   - `ncaa-model-building-based-on-the-elo.ipynb` — Elo-rating-based win
     probability model.

## Evaluation

Official Kaggle metric: **Brier score** (or log-loss, depending on
competition year — confirm against the current competition page).

## Results

_Not yet recorded — the notebook is at "Processing Draft 2," i.e. still
iterating on feature engineering, with no scored submission yet._

## Extensions

- Resolve the "Processing Draft 2" iteration into a single canonical EDA
  notebook before treating this as portfolio-ready.
- Decide whether the logistic rank-difference heuristic, Massey features,
  or an XGBoost/Elo approach (per `references/`) becomes the primary
  model, and document the comparison.
- Move feature engineering (Massey normalization, rank-difference logit)
  into `src/features/` so it's reusable and testable outside the notebook.

## References

- [Data-driven March Madness predictions](https://towardsdatascience.com/data-driven-march-madness-predictions/) (approach inspiration).
- `references/ncaa-basketball-predictions-with-xgboost.ipynb` and
  `references/ncaa-model-building-based-on-the-elo.ipynb` — external
  reference notebooks kept for comparison, not authored by this project.
