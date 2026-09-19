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
