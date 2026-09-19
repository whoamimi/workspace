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

AIRR-format immune repertoire sequencing data, one row per receptor
(`train_dataset_*/metadata` batches, loaded in `notebooks/00_eda.ipynb`
"Data Loader"). Columns seen in the EDA: `junction_aa` (CDR3 amino acid
sequence), `v_call` / `d_call` / `j_call` (V/D/J gene segment calls),
`age`, `sex`, and HLA alleles `A` / `B` / `C`.

## Methods Implemented

- **Embedding generation** — `wukevin/tcr-bert` (a BERT model pretrained
  on T-cell receptor sequences) encodes `junction_aa` sequences into
  768-dim vectors, batched with GPU utilization monitoring
  (`get_embeddings_batched`).
- **N-gram kernel** (`src/features/ngram.py`) — `NGramKernelProcessor`
  turns a repertoire DataFrame column (default `v_call`) into
  `(context_indices, target_index)` training pairs over a sliding window
  of `context_size` gene calls, feeding `NGramKernel` (`torch.nn.Module`:
  embedding → FC → log-softmax over the gene-call vocabulary `vj_size`)
  for next-gene-call prediction — a classic neural n-gram LM (Bengio et
  al.) applied to V/J gene usage instead of words.
  **Assumption to confirm**: `__call__` treats the DataFrame's row order
  as the sequence order (it does not sort) — decide and document what
  ordering is scientifically meaningful here (e.g. per-repertoire, by
  clone rank) before training on it for real.

## Evaluation

_Not yet documented — record the official competition metric here._

## Results

_EDA and utility scaffolding only — no trained model or submission yet._

## Extensions

- Decide and document the row ordering `NGramKernelProcessor` should
  assume (see the assumption noted under Methods above) before training
  on it for real.
- Document the exact competition objective and evaluation metric.
- Move the embedding/GPU-monitoring utilities out of the notebook's
  "Epilogue" section into `src/utils/`.
- Clear out `notebooks/00_eda.ipynb`'s "Scratchpad for dummy runs" section
  before treating this as portfolio-ready, or move it to a clearly marked
  scratch notebook.

## References

None yet.
