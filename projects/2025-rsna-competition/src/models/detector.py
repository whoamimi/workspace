"""Baseline 3D CNN aneurysm-detection head.

Fills the gap flagged in TODO.md: prior code stopped at BiomedCLIP
zero-shot image-text scoring (src/models/biomedclip.py) with no trained
detector. This is a starting architecture, not a tuned model -- it has
not been trained or validated against real competition data (unavailable
in this environment). Takes the `volume` tensor produced by
`BrainAneurysmDataset` (src/data/dataset.py), shape [B, 1, D, H, W], and
predicts one logit per column in src.config.LABEL_COLS.
"""

import torch
import torch.nn as nn

from src.config import LABEL_COLS, NUM_LABELS


class AneurysmDetector3D(nn.Module):
    """Simple 3D CNN classifier: 4 conv/pool blocks -> global average pool -> linear head."""

    def __init__(self, num_labels: int = NUM_LABELS, base_channels: int = 16, dropout: float = 0.3):
        super().__init__()
        c = base_channels
        self.features = nn.Sequential(
            self._conv_block(1, c),
            self._conv_block(c, c * 2),
            self._conv_block(c * 2, c * 4),
            self._conv_block(c * 4, c * 8),
        )
        self.pool = nn.AdaptiveAvgPool3d(1)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout),
            nn.Linear(c * 8, num_labels),
        )

    @staticmethod
    def _conv_block(in_channels: int, out_channels: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(2),
        )

    def forward(self, volume: torch.Tensor) -> torch.Tensor:
        """volume: [B, 1, D, H, W] -> logits: [B, num_labels] (one per LABEL_COLS entry)."""
        x = self.features(volume)
        x = self.pool(x)
        return self.classifier(x)


def compute_loss(logits: torch.Tensor, labels: torch.Tensor, pos_weight: torch.Tensor | None = None) -> torch.Tensor:
    """Multi-label BCE loss over LABEL_COLS. `labels` must match `logits`' shape [B, NUM_LABELS]."""
    if logits.shape != labels.shape:
        raise ValueError(f"logits shape {tuple(logits.shape)} != labels shape {tuple(labels.shape)}")
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    return loss_fn(logits, labels)


def predict_probabilities(logits: torch.Tensor) -> dict[str, torch.Tensor]:
    """Sigmoid-activate `logits` [B, NUM_LABELS] and label each column by LABEL_COLS."""
    probs = torch.sigmoid(logits)
    return {label: probs[:, i] for i, label in enumerate(LABEL_COLS)}
