"""Zero-shot BiomedCLIP image-text scoring, used as an ensemble signal alongside
the volumetric aneurysm detector in src/models/detector.py (trained on the
volumes BrainAneurysmDataset, in src/data/dataset.py, produces).

Moved out of notebooks/00_eda.ipynb ("PUBMed Bert model").
See https://huggingface.co/microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224
"""

import torch

from src.config import MULTI_PRED_LABELS

MODEL_ID = "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224"
PROMPT_TEMPLATE = "This is a Brain scan of"
CONTEXT_LENGTH = 256

MODALITY_INFO = {
    "CT": "Non-contrast CT (NCCT)",
    "CTA": "CT Angiography",
    "MR": "MRI (unspecified sequence)",
    "MRA": "MR Angiography",
    "MRI T1post": "T1-weighted post-contrast (gadolinium)",
    "MRI T2": "T2-weighted MRI",
}
MODALITY_LABELS = list(MODALITY_INFO.values())

# Paired location + modality-description prompts used for zero-shot scoring.
PROMPT_LABELS = [f"{loc} {mod}" for loc, mod in zip(MULTI_PRED_LABELS, MODALITY_LABELS)]


def load_biomedclip_model(device: torch.device | None = None):
    """Load BiomedCLIP + tokenizer, returning (model, preprocess_train, preprocess_val, tokenizer, device)."""
    import open_clip

    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, preprocess_train, preprocess_val = open_clip.create_model_and_transforms(MODEL_ID)
    tokenizer = open_clip.get_tokenizer(MODEL_ID)
    model.to(device)
    model.eval()
    return model, preprocess_train, preprocess_val, tokenizer, device


def build_prompt_inputs(tokenizer, device, labels=PROMPT_LABELS, template: str = PROMPT_TEMPLATE):
    return tokenizer([f"{template} {label}" for label in labels], context_length=CONTEXT_LENGTH).to(device)


def run_inference(model, images, prompt_inputs, labels=PROMPT_LABELS):
    """Score `images` against the fixed prompt set; returns (logits, sorted_indices) as numpy arrays."""
    with torch.no_grad():
        image_features, text_features, logit_scale = model(images, prompt_inputs)

        logits = (logit_scale * image_features @ text_features.t()).detach().softmax(dim=-1)
        sorted_indices = torch.argsort(logits, dim=-1, descending=True)

        logits = logits.cpu().numpy()
        sorted_indices = sorted_indices.cpu().numpy()

        assert logits.shape[-1] == len(labels)
    return logits, sorted_indices
