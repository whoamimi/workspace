"""Paths, label columns, and DICOM metadata tags for the RSNA aneurysm pipeline."""

from pathlib import Path
from typing import List

KAGGLE_WORKSPACE: bool = False

ID_COL = "SeriesInstanceUID"

LABEL_COLS = sorted([
    "Left Infraclinoid Internal Carotid Artery",
    "Right Infraclinoid Internal Carotid Artery",
    "Left Supraclinoid Internal Carotid Artery",
    "Right Supraclinoid Internal Carotid Artery",
    "Left Middle Cerebral Artery",
    "Right Middle Cerebral Artery",
    "Anterior Communicating Artery",
    "Left Anterior Cerebral Artery",
    "Right Anterior Cerebral Artery",
    "Left Posterior Communicating Artery",
    "Right Posterior Communicating Artery",
    "Basilar Tip",
    "Other Posterior Circulation",
    "Aneurysm Present",
])

NUM_LABELS = len(LABEL_COLS)

idxlabel = {i: label for i, label in enumerate(LABEL_COLS)}
labelidx = {label: i for i, label in enumerate(LABEL_COLS)}

DICOM_TAG_ALLOWLIST = [
    "BitsAllocated",
    "BitsStored",
    "Columns",
    "FrameOfReferenceUID",
    "HighBit",
    "ImageOrientationPatient",
    "ImagePositionPatient",
    "InstanceNumber",
    "Modality",
    "PatientID",
    "PhotometricInterpretation",
    "PixelRepresentation",
    "PixelSpacing",
    "PlanarConfiguration",
    "RescaleIntercept",
    "RescaleSlope",
    "RescaleType",
    "Rows",
    "SOPClassUID",
    "SOPInstanceUID",
    "SamplesPerPixel",
    "SliceThickness",
    "SpacingBetweenSlices",
    "StudyInstanceUID",
    "TransferSyntaxUID",
]

BASE_PATH = Path("/kaggle/input/rsna-intracranial-aneurysm-detection")
INPUT_SERIES_PATH = BASE_PATH / "series"
INPUT_SEGMENT_PATH = BASE_PATH / "segmentations"
INPUT_TRAIN_PATH = BASE_PATH / "train.csv"
INPUT_TRAIN_LOCAL_PATH = BASE_PATH / "train_localizers.csv"

BASE_OUTPUT_PATH = Path("/kaggle/working")
SUBMISSION_FILE_PATH = BASE_OUTPUT_PATH / "submission.parquet"
MODEL_PATH = BASE_OUTPUT_PATH / "model_weights.pt"
DATA_TENSOR_PATH = BASE_OUTPUT_PATH / "train_tensor.pt"
DICOM_META_PATH = BASE_OUTPUT_PATH / "dicom_meta_data.parquet"

TARGET_SIZE = (64, 64, 64)  # Reduced size for memory efficiency

# Location labels used by the multi-label head (excludes the binary
# "Aneurysm Present" summary label included in LABEL_COLS).
MULTI_PRED_LABELS = [
    "Left Infraclinoid Internal Carotid Artery",
    "Right Infraclinoid Internal Carotid Artery",
    "Left Supraclinoid Internal Carotid Artery",
    "Right Supraclinoid Internal Carotid Artery",
    "Left Middle Cerebral Artery",
    "Right Middle Cerebral Artery",
    "Anterior Communicating Artery",
    "Left Anterior Cerebral Artery",
    "Right Anterior Cerebral Artery",
    "Left Posterior Communicating Artery",
    "Right Posterior Communicating Artery",
    "Basilar Tip",
    "Other Posterior Circulation",
]
MULTI_LABEL_COUNT = len(MULTI_PRED_LABELS)  # 13

META_LABEL: List[str] = [
    "BitsAllocated", "BitsStored", "FrameOfReferenceUID", "HighBit",
    "ImageOrientationPatient", "ImagePositionPatient", "InstanceNumber",
    "Modality", "PhotometricInterpretation", "PixelRepresentation",
    "PixelSpacing", "PlanarConfiguration", "RescaleIntercept",
    "RescaleSlope", "RescaleType", "SamplesPerPixel", "SliceThickness",
    "SpacingBetweenSlices",
]

NUM_META = len(META_LABEL)

SLICE_SELECTION = "all"  # all | center | uniform
