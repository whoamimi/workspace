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

`notebooks/00_eda.ipynb` now only demonstrates these two modules end to
end; the loading/normalization and zero-shot scoring logic itself lives in
`src/`, importable and testable independent of the notebook.

## Evaluation

_Not yet documented — record the official RSNA competition metric
(commonly AUC or a weighted multi-label score for this challenge series)
once confirmed against the competition page._

## Results

_Data preparation and zero-shot BiomedCLIP scoring only — no trained
detector or submission yet._

## Extensions

- Add the actual aneurysm-detection head/ensembling step; current code
  stops at zero-shot image–text similarity scoring.
- Document the official evaluation metric and add local validation.
- Add unit tests for `src/data/dataset.py`'s preprocessing helpers
  (`_ct_mr_normalize`, `_resize_zyx`, `_select_indices`) now that they're
  standalone functions.

## References

- [BiomedCLIP-PubMedBERT_256-vit_base_patch16_224](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224).
