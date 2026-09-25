# NCAA March Madness 2026

## Overview

Kaggle's annual NCAA March Madness bracket-prediction competition:
predict win probabilities for every possible matchup in the men's/women's
tournament.

#### Objective

Given team/season/game data, predict the probability that Team 1 beats
Team 2 for each tournament matchup, across all rounds (First Four →
Round of 64 → Round of 32 → Sweet 16 → Elite 8 → Final Four →
Championship).

#### Data

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

*Not available*

## References

- [Data-driven March Madness predictions](https://towardsdatascience.com/data-driven-march-madness-predictions/) (approach inspiration).
- `references/ncaa-basketball-predictions-with-xgboost.ipynb` and
  `references/ncaa-model-building-based-on-the-elo.ipynb` — external
  reference notebooks kept for comparison, not authored by this project.
