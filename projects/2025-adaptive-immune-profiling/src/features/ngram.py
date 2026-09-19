# ngram.py

import pandas as pd
import torch
import torch.nn as nn

CONTEXT_SIZE = 1
KNER_EMBEDDING_DIM = 128
KNER_HIDDEN_DIM = 384

class NGramKernelProcessor:
    """Turns a repertoire DataFrame column into (context, target) n-gram index
    pairs for NGramKernel.

    Treats the DataFrame's row order as the sequence order -- it does not
    sort. What ordering is scientifically meaningful (per-repertoire, by
    clone rank, ...) is a domain decision left to the caller; sort `data`
    accordingly before calling this.
    """

    def __init__(self, context_size: int = CONTEXT_SIZE, column: str = "v_call"):
        self.context_size = context_size
        self.column = column
        self.ngrams: list[tuple[list[int], int]] = []
        self.tag2id: dict[str, int] = {}
        self.id2tag: dict[int, str] = {}

    def _build_vocab(self, tokens: "pd.Series") -> None:
        """Extend the vocabulary with any tokens not seen in a prior call."""
        for tag in tokens.dropna().unique():
            if tag not in self.tag2id:
                idx = len(self.tag2id)
                self.tag2id[tag] = idx
                self.id2tag[idx] = tag

    def __call__(self, data: pd.DataFrame) -> list[tuple[list[int], int]]:
        if self.column not in data.columns:
            raise KeyError(f"{self.column!r} not in columns: {list(data.columns)}")

        tokens = data[self.column].astype(str)
        self._build_vocab(tokens)

        ids = [self.tag2id[t] for t in tokens]
        self.ngrams = [
            (ids[i - self.context_size:i], ids[i])
            for i in range(self.context_size, len(ids))
        ]
        return self.ngrams

class NGramKernel(nn.Module):
    def __init__(self, vj_size, context_dim: int = CONTEXT_SIZE, embedding_dim: int = KNER_EMBEDDING_DIM, hidden_dim: int = KNER_HIDDEN_DIM):
        super(NGramKernel, self).__init__()
        self.embed = nn.Embedding(vj_size, embedding_dim)
        self.fc1 = nn.Linear(context_dim * embedding_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, vj_size)
        self.relu = nn.ReLU()

    def forward(self, inputs):
        emb = self.embed(inputs).view((1, -1))
        out = self.relu(self.fc1(emb))
        out = self.fc2(out)
        log_probs = out.log_softmax(-1)
        return log_probs
