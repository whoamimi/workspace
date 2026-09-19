# ngram.py

import torch
import torch.nn as nn

CONTEXT_SIZE = 1
KNER_EMBEDDING_DIM = 128
KNER_HIDDEN_DIM = 384

class NGramKernelProcessor:
    def __init__(self, context_size: int = CONTEXT_SIZE):

        self.context_size = context_size
        self.ngrams = []
        self.tag2id = {}
        self.id2tag = {}

    def __call__(self, data: pd.DataFrame):
        pass

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
