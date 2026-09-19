"""Feature-selection and correlation-weighting helpers.

Moved out of notebooks/00_eda.ipynb (cells under "Flaggers / Indicators &
Standardizers" and "Correlation Analysis") so the scoring logic is
reusable and testable outside the notebook.
"""

from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.feature_selection import f_regression


def f_regression_scores(X: np.ndarray, y: np.ndarray, x_cols: Sequence[str]) -> pd.DataFrame:
    """F-score + p-value of each column in `x_cols` against target `y`."""
    f_scores, p_values = f_regression(X, y)
    return pd.DataFrame({"feature": list(x_cols), "f_score": f_scores, "p_value": p_values})


def select_top_features(
    X: np.ndarray,
    y: np.ndarray,
    x_cols: Sequence[str],
    topk: int,
    ascending: bool = False,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Score `x_cols` by f_regression against `y`, keep the top `topk`, and
    return (scored subset, {feature: normalized_score}).

    `ascending=False` (the default) keeps the *highest*-scoring (most
    predictive) features, matching the notebook's original single-pass
    selection (cell 22). The notebook's rolling-window loop (cell 24)
    called this with `ascending=True` instead, which keeps the *lowest*-
    scoring features -- that looks like a bug (feature selection usually
    wants the strongest signal), but the intent wasn't documented, so it's
    preserved here as a caller-supplied choice rather than silently
    "corrected". Confirm the intended direction before relying on it.
    """
    scored = f_regression_scores(X, y, x_cols)
    scored = scored.sort_values("f_score", ascending=ascending).head(topk)

    scores = scored["f_score"].fillna(0.0).values
    scores_norm = scores / scores.max() if scores.max() > 0 else scores
    weights = dict(zip(scored["feature"], scores_norm))

    return scored, weights


def top_correlated_pairs(
    df: pd.DataFrame,
    x_cols: Sequence[str],
    y_cols: Sequence[str],
    k: int = 10,
    steepness: float = 5.0,
) -> pd.Series:
    """Rank (x, y) column pairs by a sigmoid-weighted |correlation| score.

    `steepness` controls how sharply the sigmoid separates weak from
    strong correlations (the notebook's cell 28 hardcoded this as global
    `D = 5.0`, an implicit dependency this function makes explicit).
    Returns the top `k` pairs as a Series indexed by (x_col, y_col).

    Note: `k` does double duty here exactly as in the original notebook --
    it's both the "how many top pairs" count *and* the upper-triangle
    mask's diagonal offset (`np.triu(..., k=k)`), which looks like a
    coincidental reuse of one variable for two unrelated purposes rather
    than intentional. Preserved as-is (not silently "corrected") since
    changing the mask offset changes which pairs get deduplicated.
    """
    corr = df[list(x_cols) + list(y_cols)].corr().loc[x_cols, y_cols]
    abs_corr = corr.abs().map(lambda v: 1 / (1 + np.exp(v * -steepness)))

    mask = np.triu(np.ones_like(corr, dtype=bool), k=k)
    pairs = abs_corr.mask(mask).stack().sort_values(ascending=False)
    return pairs.head(k)
