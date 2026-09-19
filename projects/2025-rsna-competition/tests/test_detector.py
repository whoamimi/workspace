"""Unit tests for the baseline AneurysmDetector3D head (src/models/detector.py).

Uses synthetic tensors shaped like BrainAneurysmDataset's real output
(volume: [B,1,64,64,64]) since real Kaggle DICOM data isn't available in
this environment -- these check the architecture is wired correctly
(shapes, loss, gradients), not model quality.
"""

import sys
from pathlib import Path

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

from src.config import LABEL_COLS, NUM_LABELS, TARGET_SIZE
from src.models.detector import AneurysmDetector3D, compute_loss, predict_probabilities


@pytest.fixture
def batch_volume():
    batch_size = 2
    d, h, w = TARGET_SIZE
    return torch.rand(batch_size, 1, d, h, w)


class TestAneurysmDetector3D:
    def test_forward_output_shape_matches_num_labels(self, batch_volume):
        model = AneurysmDetector3D()
        logits = model(batch_volume)
        assert logits.shape == (batch_volume.shape[0], NUM_LABELS)

    def test_forward_accepts_smaller_target_size(self):
        # sanity check the architecture isn't hardcoded to 64^3
        model = AneurysmDetector3D()
        small_volume = torch.rand(1, 1, 32, 32, 32)
        logits = model(small_volume)
        assert logits.shape == (1, NUM_LABELS)

    def test_gradients_flow_to_all_parameters(self, batch_volume):
        model = AneurysmDetector3D()
        labels = torch.randint(0, 2, (batch_volume.shape[0], NUM_LABELS)).float()

        logits = model(batch_volume)
        loss = compute_loss(logits, labels)
        loss.backward()

        for name, param in model.named_parameters():
            assert param.grad is not None, f"no gradient reached {name}"


class TestComputeLoss:
    def test_raises_on_shape_mismatch(self, batch_volume):
        model = AneurysmDetector3D()
        logits = model(batch_volume)
        wrong_shape_labels = torch.zeros(batch_volume.shape[0], NUM_LABELS - 1)
        with pytest.raises(ValueError):
            compute_loss(logits, wrong_shape_labels)

    def test_perfect_prediction_gives_near_zero_loss(self):
        # large-magnitude logits matching the labels' sign should drive BCE toward 0
        labels = torch.tensor([[1.0, 0.0, 1.0]])
        logits = torch.tensor([[20.0, -20.0, 20.0]])
        loss = compute_loss(logits, labels)
        assert loss.item() < 1e-4


class TestPredictProbabilities:
    def test_keys_match_label_cols_and_values_are_probabilities(self, batch_volume):
        model = AneurysmDetector3D()
        logits = model(batch_volume)
        probs = predict_probabilities(logits)

        assert set(probs.keys()) == set(LABEL_COLS)
        for tensor in probs.values():
            assert tensor.shape == (batch_volume.shape[0],)
            assert torch.all((tensor >= 0) & (tensor <= 1))
