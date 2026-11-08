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

1. **Image/metadata preparation** — DICOM loading, volume reshaping, and a
   v2 data loader/processor pipeline.
2. **Zero-shot vision-language classification** — [BiomedCLIP
   (`microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224`)](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224)
   via `open_clip`: encode each image slice and a set of modality-prompt
   texts (`"This is a Brain scan of <modality>"`), then score
   image–text similarity (`run_inference`) as an ensemble signal alongside
   the imaging model.

## Evaluation

_Not yet documented — record the official RSNA competition metric
(commonly AUC or a weighted multi-label score for this challenge series)
once confirmed against the competition page._

## Results

_Data preparation and zero-shot BiomedCLIP scoring only — no trained
detector or submission yet._

## Extensions

- Split this single notebook into `notebooks/00_eda.ipynb` (DICOM
  loading/preprocessing) + `src/models/` (BiomedCLIP ensemble logic) — it
  currently mixes both stages in one file, the weakest structure in the
  portfolio.
- Add the actual aneurysm-detection head/ensembling step; current code
  stops at zero-shot image–text similarity scoring.
- Document the official evaluation metric and add local validation.

## References

- [BiomedCLIP-PubMedBERT_256-vit_base_patch16_224](https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224).
