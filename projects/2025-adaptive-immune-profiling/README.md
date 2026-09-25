# Adaptive Immune Profiling Challenge 2025

## **Overview**

Kaggle competition [Adaptive Immune Receptor Repertoire (AIRR)](https://www.kaggle.com/competitions/adaptive-immune-profiling-challenge-2025/overview) problem scopes the repertoire classification methods with immune receptor sequencing data, specifically V/J gene segment usage and CDR3 sequences.

#### Data

AIRR-format immune repertoire sequencing data. Loaded and previewed in
`notebooks/00_eda.ipynb` ("Data Loader" / "Quick look" sections); no
column schema documented yet.

## **Methods Implemented**

- **Embedding generation** — batched embedding computation with GPU
  utilization monitoring (`get_embeddings_batched`).
- **N-gram kernel processor** (`src/features/ngram.py`) — an
  `NGramKernelProcessor` (data → n-gram context extraction, currently a
  stub) feeding an `NGramKernel` (`torch.nn.Module`: embedding → FC →
  log-softmax over V/J segment vocabulary `vj_size`), for context-window
  based V/J gene usage prediction.

## **Results**

**No evaluation made yet**
**No conclusion or results yet**

## Extensions

- Implement `NGramKernelProcessor.__call__` (currently `pass`) to turn a
  repertoire DataFrame into n-gram training pairs for `NGramKernel`.
- Document the exact competition objective and evaluation metric.
- Move the embedding/GPU-monitoring utilities out of the notebook's
  "Epilogue" section into `src/utils/`.
- Clear out `notebooks/00_eda.ipynb`'s "Scratchpad for dummy runs" section
  before treating this as portfolio-ready, or move it to a clearly marked
  scratch notebook