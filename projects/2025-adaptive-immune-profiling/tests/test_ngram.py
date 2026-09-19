"""Unit tests for src/features/ngram.py (NGramKernelProcessor + NGramKernel).

Uses a small synthetic repertoire-like DataFrame since real AIRR data
isn't available in this environment.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest
import torch

# Every project in this monorepo uses the same top-level package name `src`
# (see projects/README.md), so running more than one project's tests in a
# single pytest process needs the previous project's `src` cleared from
# sys.modules first -- otherwise Python's import cache resolves `from
# src...` to whichever project imported it first.
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.features.ngram import NGramKernel, NGramKernelProcessor


@pytest.fixture
def repertoire_df():
    # 6 rows, 3 distinct v_call tokens, deliberately repeated/ordered
    return pd.DataFrame({
        "v_call": ["TRBV5-1", "TRBV7-2", "TRBV5-1", "TRBV12-3", "TRBV7-2", "TRBV12-3"],
        "junction_aa": ["CASSL", "CASSQ", "CASSL", "CASSY", "CASSQ", "CASSY"],
    })


class TestNGramKernelProcessor:
    def test_builds_vocab_from_unique_column_values(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="v_call")
        proc(repertoire_df)
        assert set(proc.tag2id.keys()) == set(repertoire_df["v_call"].unique())
        assert proc.id2tag == {v: k for k, v in proc.tag2id.items()}

    def test_ngram_count_matches_context_size(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="v_call")
        ngrams = proc(repertoire_df)
        assert len(ngrams) == len(repertoire_df) - 1

    def test_context_and_target_are_consistent_with_row_order(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="v_call")
        ngrams = proc(repertoire_df)

        ids = [proc.tag2id[v] for v in repertoire_df["v_call"]]
        expected = [([ids[i - 1]], ids[i]) for i in range(1, len(ids))]
        assert ngrams == expected

    def test_context_size_greater_than_one(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=2, column="v_call")
        ngrams = proc(repertoire_df)
        assert len(ngrams) == len(repertoire_df) - 2
        for context, _target in ngrams:
            assert len(context) == 2

    def test_missing_column_raises(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="does_not_exist")
        with pytest.raises(KeyError):
            proc(repertoire_df)

    def test_vocab_extends_across_repeated_calls(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="v_call")
        proc(repertoire_df.iloc[:3])
        first_vocab_size = len(proc.tag2id)

        proc(repertoire_df)  # includes tokens not seen in the first slice
        assert len(proc.tag2id) >= first_vocab_size


class TestNGramKernel:
    def test_forward_produces_log_probs_over_full_vocab(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="v_call")
        ngrams = proc(repertoire_df)
        vj_size = len(proc.tag2id)

        model = NGramKernel(vj_size=vj_size, context_dim=1)
        context, _target = ngrams[0]
        log_probs = model(torch.tensor(context))

        assert log_probs.shape == (1, vj_size)
        # log_softmax output should exponentiate to a valid probability distribution
        probs = log_probs.exp()
        assert torch.allclose(probs.sum(), torch.tensor(1.0), atol=1e-5)

    def test_end_to_end_training_step_reduces_loss(self, repertoire_df):
        proc = NGramKernelProcessor(context_size=1, column="v_call")
        ngrams = proc(repertoire_df)
        vj_size = len(proc.tag2id)

        model = NGramKernel(vj_size=vj_size, context_dim=1)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        loss_fn = torch.nn.NLLLoss()

        context, target = ngrams[0]
        context_t = torch.tensor(context)
        target_t = torch.tensor([target])

        losses = []
        for _ in range(5):
            optimizer.zero_grad()
            log_probs = model(context_t)
            loss = loss_fn(log_probs, target_t)
            loss.backward()
            optimizer.step()
            losses.append(loss.item())

        assert losses[-1] < losses[0]
