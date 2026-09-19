"""Unit tests for src/features/selection.py.

Uses small synthetic data since real Kaggle climate/futures data isn't
available in this environment.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Every project in this monorepo uses the same top-level package name `src`
# (see projects/README.md), so running more than one project's tests in a
# single pytest process needs the previous project's `src` cleared from
# sys.modules first -- otherwise Python's import cache resolves `from
# src...` to whichever project imported it first.
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.selection import f_regression_scores, select_top_features, top_correlated_pairs


@pytest.fixture
def linear_signal():
    rng = np.random.default_rng(0)
    n = 200
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)  # unrelated to y
    y = 3 * x1 + rng.normal(scale=0.1, size=n)  # strongly driven by x1
    X = np.column_stack([x1, x2])
    return X, y, ["x1", "x2"]


class TestFRegressionScores:
    def test_returns_one_row_per_feature(self, linear_signal):
        X, y, cols = linear_signal
        scores = f_regression_scores(X, y, cols)
        assert list(scores["feature"]) == cols
        assert len(scores) == 2

    def test_predictive_feature_scores_higher(self, linear_signal):
        X, y, cols = linear_signal
        scores = f_regression_scores(X, y, cols).set_index("feature")
        assert scores.loc["x1", "f_score"] > scores.loc["x2", "f_score"]


class TestSelectTopFeatures:
    def test_ascending_false_keeps_highest_scoring(self, linear_signal):
        X, y, cols = linear_signal
        scored, weights = select_top_features(X, y, cols, topk=1, ascending=False)
        assert scored["feature"].tolist() == ["x1"]
        assert weights["x1"] == pytest.approx(1.0)

    def test_ascending_true_keeps_lowest_scoring(self, linear_signal):
        X, y, cols = linear_signal
        scored, _weights = select_top_features(X, y, cols, topk=1, ascending=True)
        assert scored["feature"].tolist() == ["x2"]

    def test_weights_are_normalized_to_max_one(self, linear_signal):
        X, y, cols = linear_signal
        _scored, weights = select_top_features(X, y, cols, topk=2, ascending=False)
        assert max(weights.values()) == pytest.approx(1.0)
        assert all(0.0 <= w <= 1.0 for w in weights.values())


class TestTopCorrelatedPairs:
    def test_finds_the_strongly_correlated_pair(self):
        rng = np.random.default_rng(0)
        n = 200
        x1 = rng.normal(size=n)
        df = pd.DataFrame({
            "x1": x1,
            "x2": rng.normal(size=n),
            "y1": x1 * 2 + rng.normal(scale=0.05, size=n),  # near-perfectly correlated with x1
            "y2": rng.normal(size=n),
        })

        pairs = top_correlated_pairs(df, x_cols=["x1", "x2"], y_cols=["y1", "y2"], k=4)
        top_pair = pairs.index[0]
        assert top_pair == ("x1", "y1")

    def test_returns_at_most_k_pairs(self):
        rng = np.random.default_rng(1)
        n = 50
        df = pd.DataFrame(rng.normal(size=(n, 4)), columns=["x1", "x2", "y1", "y2"])
        pairs = top_correlated_pairs(df, x_cols=["x1", "x2"], y_cols=["y1", "y2"], k=2)
        assert len(pairs) <= 2
