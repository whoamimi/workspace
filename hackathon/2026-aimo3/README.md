# AI Mathematical Olympiad Progress Prize 3 (AIMO3)

## Competition Brief

Kaggle's AI Mathematical Olympiad (AIMO) Progress Prize 3: solve
competition-level math problems with an LLM, submitted as a **no-internet-
access** Kaggle kernel (a key constraint that shapes the whole pipeline).

## Objective

Given a math competition problem, produce the correct final numeric/exact
answer, evaluated by the Kaggle-run submission harness under the
competition's no-internet, limited-runtime constraints.

## Data

Competition-provided math problem sets (train/public/private test), used
for fine-tuning data construction and for scoring inference outputs.

## Methods Implemented

1. **Dependency bundling** (`aimo3-utility-notebook-dependency-install-1-2.ipynb`):
   since submission kernels have no internet access and can't reliably use
   a prebuilt-wheel dataset either, this notebook pins and installs exact
   package versions (uninstalling conflicting Kaggle-preinstalled packages
   first, notably around vLLM) so the environment can be snapshotted for
   submission.
2. **Baseline exploration** (`aimo-3-notebook.ipynb`): workspace config,
   data loaders, pretrained model loading, a main entry point, and
   comparison/analytics across candidate approaches.
3. **QLoRA fine-tune + vLLM inference** (`aimo3_unsloth_submission.py`):
   - Part 1 — fine-tune `unsloth/Qwen3-30B-A3B-unsloth-bnb-4bit` with
     QLoRA (Unsloth `FastLanguageModel`, rank-16 LoRA over attention/MLP
     projections), then merge adapters into the base model.
   - Part 2 — serve the merged model with vLLM for inference, using
     Tool-Integrated Reasoning (TIR) and majority-vote decoding across
     multiple samples per problem.
4. `example_submission.ipynb` — Kaggle-provided submission template
   (reference only, not authored work).

## Evaluation

Official AIMO3 scoring: exact-match accuracy on held-out problems, run by
the Kaggle no-internet submission harness.

## Results

_Not yet recorded — update after a scored submission run._

## Extensions

- Confirm whether `aimo-3-notebook.ipynb`'s baseline approach is superseded
  by the Unsloth/QLoRA pipeline, or still needed as a fallback/ensemble
  member.
- Move `aimo3_unsloth_submission.py` under `src/models/` and split its two
  parts (fine-tune vs. inference) into separate, independently runnable
  entry points.
- Rename notebooks to a linear order:
  `00_dependency_setup.ipynb` (from `aimo3-utility-notebook-dependency-install-1-2.ipynb`),
  `01_baseline.ipynb` (from `aimo-3-notebook.ipynb`),
  `02_submission.ipynb` (wrapping `aimo3_unsloth_submission.py`).
- Document majority-voting sample count and TIR tool set actually used at
  submission time.

## References

- [Unsloth](https://github.com/unslothai/unsloth) (QLoRA fine-tuning).
- [vLLM](https://github.com/vllm-project/vllm) (inference serving).
- `unsloth/Qwen3-30B-A3B-unsloth-bnb-4bit` (base model).
