# Adaptive Immune Profiling Challenge 2025

## Competition Brief

Kaggle competition on Adaptive Immune Receptor Repertoire (AIRR) data —
exploration of immune receptor sequencing data (V/J gene segment usage,
CDR3 sequences).

## Objective

_Not yet documented — infer and state the exact prediction target (e.g.
V/J gene usage prediction, repertoire classification) from the
competition page once work resumes._

## Data

AIRR-format immune repertoire sequencing data. Loaded and previewed in
`notebooks/00_eda.ipynb` ("Data Loader" / "Quick look" sections); no
column schema documented yet.

## Methods Implemented

- **Embedding generation** — batched embedding computation with GPU
  utilization monitoring (`get_embeddings_batched`).
- **N-gram kernel processor** (`src/features/ngram.py`) — an
  `NGramKernelProcessor` (data → n-gram context extraction, currently a
  stub) feeding an `NGramKernel` (`torch.nn.Module`: embedding → FC →
  log-softmax over V/J segment vocabulary `vj_size`), for context-window
  based V/J gene usage prediction.

## Evaluation

_Not yet documented — record the official competition metric here._

## Results

_EDA and utility scaffolding only — no trained model or submission yet._

## Extensions

- Implement `NGramKernelProcessor.__call__` (currently `pass`) to turn a
  repertoire DataFrame into n-gram training pairs for `NGramKernel`.
- Document the exact competition objective and evaluation metric.
- Move the embedding/GPU-monitoring utilities out of the notebook's
  "Epilogue" section into `src/utils/`.
- Clear out `notebooks/00_eda.ipynb`'s "Scratchpad for dummy runs" section
  before treating this as portfolio-ready, or move it to a clearly marked
  scratch notebook.

## References

None yet.
