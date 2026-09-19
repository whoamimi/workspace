# RSNA Intracranial Aneurysm Detection

## Competition Brief

Kaggle competition hosted by the Radiological Society of North America
(RSNA): detect intracranial aneurysms from brain imaging.

## Objective

Given brain imaging studies (CT/CTA/MR/MRA) plus study metadata, predict
aneurysm presence/location. Modeling combines image and text (modality
description) modalities via a CLIP-style vision-language model.

## Data

- DICOM image series (loaded via `pydicom`), one 3D volume per study
  (`sample["image"]`, reshaped to `64x64x64`).
- Study modality metadata, mapped to natural-language descriptions
  (`MODALITY_INFO`: NCCT, CT Angiography, MRI, MR Angiography, etc.) used
  as zero-shot text prompts.

## Methods Implemented

1. **Image/metadata preparation** (`src/data/dataset.py`) — DICOM loading,
   CT/MR-specific normalization, volume resizing/caching, and a
   `BrainAneurysmDataset` + `create_dataloaders` pipeline with
   segmentation/localizer support.
2. **Zero-shot vision-language classification** (`src/models/biomedclip.py`)
   — [BiomedCLIP
   (`microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224`)](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224)
   via `open_clip`: encode each image slice and a set of modality-prompt
   texts (`"This is a Brain scan of <modality>"`), then score
   image–text similarity (`run_inference`) as an ensemble signal alongside
   the imaging model.
3. **Baseline 3D CNN detector** (`src/models/detector.py`) —
   `AneurysmDetector3D`: 4 conv/batchnorm/pool blocks over the
   `(1, 64, 64, 64)` volume, global average pooled and projected to one
   logit per `LABEL_COLS` entry (13 locations + the binary "Aneurysm
   Present" summary), trained with multi-label BCE (`compute_loss`).
   **Not yet trained** — this is a starting architecture, wired and
   unit-tested against synthetic tensors, not validated against real
   competition data.

`notebooks/00_eda.ipynb` now only demonstrates these modules end to end;
the loading/normalization, zero-shot scoring, and detector logic itself
lives in `src/`, importable and testable independent of the notebook.

**Bugs found and fixed** (via automated code review on the src/ split,
`tests/test_dataset.py` has regression tests for the two data bugs):
- `_series_cache_path` baked the *global* `TARGET_SIZE` into cache
  filenames instead of the `Dataset`'s actual `target_size`, so a
  non-default `target_size` could silently read/write the wrong cache
  file. Pre-existing in the original notebook, not introduced by the split.
- The NIfTI segmentation orientation heuristic (`shape[-1] > shape[0]`)
  had the comparison backwards for a common `(H, W, Z)` layout like
  `(512, 512, 100)`, leaving it untransposed and corrupting the mask.
  Also pre-existing; now a standalone, tested `_to_zyx_layout`.
- `metadata["num_slices"]` was populated from the DICOM `Rows` tag
  (in-plane height), not the actual slice count — now uses `D` directly.
- The notebook's `sys.path` setup assumed `Path.cwd().parent` always
  points at the project root, which breaks depending on how the notebook
  is launched — now tries a few candidates and fails loudly if none
  contain `src/`.

## Evaluation

_Not yet documented — record the official RSNA competition metric
(commonly AUC or a weighted multi-label score for this challenge series)
once confirmed against the competition page._

## Results

_Data preparation, zero-shot BiomedCLIP scoring, and an untrained
baseline detector architecture — no training run or submission yet._

## Extensions

- Train `AneurysmDetector3D` against real competition data once available
  (unavailable in this environment) and record results here.
- Combine the 3D CNN's per-label logits with BiomedCLIP's zero-shot
  modality scores into a single ensemble prediction (currently two
  separate, uncombined signals).
- Document the official evaluation metric and add local validation
  (train/val split, early stopping).

## References

- [BiomedCLIP-PubMedBERT_256-vit_base_patch16_224](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224).
