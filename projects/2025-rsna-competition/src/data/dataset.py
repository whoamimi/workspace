"""DICOM series loading, preprocessing, and the aneurysm-detection Dataset/DataLoader pair.

Moved out of notebooks/00_eda.ipynb ("Data Loaders / Processors v2") so the
loading/normalization logic is reusable and testable outside the notebook.
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import pydicom
import torch
from PIL import Image
from scipy import ndimage
from torch.utils.data import DataLoader, Dataset

from src.config import (
    DICOM_TAG_ALLOWLIST,
    ID_COL,
    INPUT_SEGMENT_PATH,
    INPUT_SERIES_PATH,
    INPUT_TRAIN_LOCAL_PATH,
    INPUT_TRAIN_PATH,
    LABEL_COLS,
    BASE_OUTPUT_PATH,
    SLICE_SELECTION,
    TARGET_SIZE,
)

CACHE_DIR = BASE_OUTPUT_PATH / "cache"


# ---------- helpers ----------

def _series_cache_path(series_uid: str, target_size: Tuple[int, int, int], cache_dir: Path = CACHE_DIR) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    d, h, w = target_size
    return cache_dir / f"{series_uid}_{d}x{h}x{w}.npz"


def _safe_sort_dicom_files(files: List[Path]) -> List[Path]:
    """Sort by ImagePositionPatient z if present, else InstanceNumber, else filename."""
    triples = []
    for fp in files:
        try:
            ds = pydicom.dcmread(str(fp), stop_before_pixels=True, force=True)
            ipp = ds.get("ImagePositionPatient", None)
            if ipp is not None and hasattr(ipp, "__len__") and len(ipp) >= 3:
                z = float(ipp[2])
            else:
                inst = getattr(ds, "InstanceNumber", None)
                z = float(inst) if inst is not None else None
            triples.append((fp, z))
        except Exception:
            triples.append((fp, None))
    with_z = [t for t in triples if t[1] is not None]
    without_z = [t for t in triples if t[1] is None]
    with_z.sort(key=lambda x: x[1])
    without_z.sort(key=lambda x: str(x[0]))
    return [fp for fp, _ in (with_z + without_z)]


def _apply_rescale(img: np.ndarray, ds) -> np.ndarray:
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
    if slope != 1.0 or intercept != 0.0:
        img = img * slope + intercept
    return img.astype(np.float32)


def _ct_mr_normalize(vol: np.ndarray, modality: str) -> np.ndarray:
    """Return vol in [0,1] robustly; CT gets HU window, MR gets robust z then min-max."""
    m = (modality or "").upper()
    if "CT" in m:  # CT / CTA
        v = np.clip(vol, -1000, 1000)
        v = (v + 1000) / 2000.0
        return v.astype(np.float32)
    # MR / MRA
    med = np.median(vol)
    mad = np.median(np.abs(vol - med))
    std = max(1e-6, 1.4826 * mad)
    z = (vol - med) / std
    z = np.clip(z, -5, 5)
    z = (z + 5) / 10.0
    return z.astype(np.float32)


def _resize_zyx(vol_zyx: np.ndarray, target=(64, 64, 64), order=1) -> np.ndarray:
    """Resize (Z,Y,X) to target (D,H,W) with center crop/pad safety."""
    assert len(vol_zyx.shape) == 3, f"Invalid zyx volume shape: {vol_zyx.shape}"
    z, y, x = vol_zyx.shape

    tz, ty, tx = target
    zoom_f = (tz / max(z, 1), ty / max(y, 1), tx / max(x, 1))
    vol = ndimage.zoom(vol_zyx, zoom_f, order=order)
    # enforce exact size
    out = np.zeros(target, dtype=vol.dtype)
    z2, y2, x2 = vol.shape
    cz, cy, cx = min(z2, tz), min(y2, ty), min(x2, tx)
    sz0, sy0, sx0 = max(0, (z2 - tz) // 2), max(0, (y2 - ty) // 2), max(0, (x2 - tx) // 2)
    dz0, dy0, dx0 = max(0, (tz - z2) // 2), max(0, (ty - y2) // 2), max(0, (tx - x2) // 2)
    out[dz0:dz0 + cz, dy0:dy0 + cy, dx0:dx0 + cx] = vol[sz0:sz0 + cz, sy0:sy0 + cy, sx0:sx0 + cx]
    return out


def _select_indices(n: int, mode: str, target_n: int) -> List[int]:
    if mode == "all" or n <= target_n:
        return list(range(n))
    if mode == "center":
        start = max(0, (n - target_n) // 2)
        return list(range(start, start + target_n))
    # uniform
    return np.linspace(0, n - 1, target_n, dtype=int).tolist()


def _to_pil_uint8(arr2d: np.ndarray) -> Image.Image:
    """2D float [0,1] -> PIL L."""
    a = np.clip(arr2d, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), mode="L")


def _to_zyx_layout(seg: np.ndarray) -> np.ndarray:
    """Detect a (H, W, Z) NIfTI segmentation layout and transpose to (Z, H, W).

    NIfTI segmentations are commonly stored (H, W, Z) with Z the smallest
    axis (in-plane resolution >> slice count); anything else is assumed to
    already be (Z, H, W).
    """
    if seg.ndim == 3 and seg.shape[-1] < seg.shape[0] and seg.shape[-1] < seg.shape[1]:
        return np.transpose(seg, (2, 0, 1))
    return seg


# ---------- Dataset ----------

class BrainAneurysmDataset(Dataset):
    LOCATION_COLUMNS = [
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

    def __init__(
        self,
        csv_path: Path = INPUT_TRAIN_PATH,
        series_dir: Path = INPUT_SERIES_PATH,
        localizers_csv_path: Path | None = INPUT_TRAIN_LOCAL_PATH,
        segmentations_dir: Path | None = INPUT_SEGMENT_PATH,
        slice_selection: str = SLICE_SELECTION,        # "all" | "center" | "uniform"
        target_size: Tuple[int, int, int] = TARGET_SIZE,  # (D,H,W)
        transform=None,
        use_segmentation: bool = True,
        mode: str = "train",
    ):
        self.csv_path = Path(csv_path)
        self.series_dir = Path(series_dir)
        self.localizers_csv_path = Path(localizers_csv_path) if localizers_csv_path else None
        self.segmentations_dir = Path(segmentations_dir) if segmentations_dir else None
        self.slice_selection = slice_selection
        self.target_size = tuple(target_size)
        self.transform = transform
        self.use_segmentation = use_segmentation
        self.mode = mode

        self.df = pd.read_csv(self.csv_path)
        self.localizers_map = self._load_localizers()
        for col in LABEL_COLS:
            if col not in self.df.columns:
                raise ValueError(f"Missing label column {col} in {self.csv_path}")

    def _load_localizers(self):
        m = defaultdict(list)
        if self.localizers_csv_path and self.localizers_csv_path.exists():
            ldf = pd.read_csv(self.localizers_csv_path)
            if len(ldf):
                def parse_c(v):
                    try:
                        return ast.literal_eval(v) if isinstance(v, str) else v
                    except Exception:
                        return None

                for _, r in ldf.iterrows():
                    m[str(r["SeriesInstanceUID"])].append({
                        "sop_uid": r["SOPInstanceUID"],
                        "coordinates": parse_c(r.get("coordinates")),
                        "location": r.get("location"),
                    })
        return m

    def __len__(self):
        return len(self.df)

    def _read_series_build_volume(self, series_uid: str) -> tuple[np.ndarray, dict]:
        """Load -> rescale -> stack -> normalize -> resize -> cache."""
        cache_p = _series_cache_path(series_uid, self.target_size)
        if cache_p.exists():
            d = np.load(str(cache_p), allow_pickle=True)
            return d["volume"], (d["meta"].item() if "meta" in d else {})

        sp = self.series_dir / series_uid
        if not sp.exists():
            raise FileNotFoundError(f"Series not found: {sp}")
        dcm_files = sorted(sp.glob("*.dcm"))
        if len(dcm_files) == 0:
            raise ValueError(f"No DICOMs in {sp}")

        dcm_files = _safe_sort_dicom_files(dcm_files)
        slices, modality, meta = [], None, {}
        for fp in dcm_files:
            try:
                ds = pydicom.dcmread(str(fp), force=True)
                img = ds.pixel_array.astype(np.float32)
                img = _apply_rescale(img, ds)
                slices.append(img)
                if modality is None:
                    modality = str(getattr(ds, "Modality", ""))
                    meta[ID_COL] = series_uid
                    for tag in DICOM_TAG_ALLOWLIST:
                        try:
                            meta[tag] = ds.get(tag, None)
                        except Exception:
                            meta[tag] = None
            except Exception:
                continue

        if len(slices) == 0:
            vol = np.zeros(self.target_size, dtype=np.float32)
            np.savez_compressed(str(cache_p), volume=vol, meta=meta)
            return vol, meta

        vol = np.stack(slices, axis=0)  # (Z,H,W)

        D, Ht, Wt = self.target_size
        idxs = _select_indices(vol.shape[0], self.slice_selection, D)
        vol = vol[idxs]

        vol = _ct_mr_normalize(vol, modality=modality)
        vol = _resize_zyx(vol, target=self.target_size, order=1)

        np.savez_compressed(str(cache_p), volume=vol.astype(np.float32), meta=meta)
        return vol.astype(np.float32), meta

    def _load_segmentation(self, series_uid: str) -> np.ndarray | None:
        if not self.use_segmentation or self.segmentations_dir is None:
            return None
        import nibabel as nib

        for ext in [".nii.gz", ".nii"]:
            p = self.segmentations_dir / f"{series_uid}{ext}"
            if p.exists():
                try:
                    nii = nib.load(str(p))
                    seg = np.asarray(nii.get_fdata(), dtype=np.uint8)  # (Z,H,W) or (H,W,Z)
                    seg = _to_zyx_layout(seg)
                    seg = _resize_zyx(seg.astype(np.float32), target=self.target_size, order=0).astype(np.uint8)
                    return seg
                except Exception:
                    return None
        return None

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        series_uid = str(row[ID_COL])

        vol, meta = self._read_series_build_volume(series_uid)  # (D,H,W) float32 in [0,1]
        D, H, W = vol.shape

        labels = [float(row[col]) for col in LABEL_COLS]

        volume_tensor = torch.from_numpy(vol).unsqueeze(0)  # [1,D,H,W]
        image_tensor = torch.from_numpy(vol[:, None, ...])   # [D,1,H,W]

        if self.transform is not None:
            imgs_aug = []
            for z in range(D):
                out = self.transform(image=vol[z])
                im = out["image"]
                if im.dim() == 2:
                    im = im.unsqueeze(0)
                imgs_aug.append(im)
            image_tensor = torch.stack(imgs_aug, dim=0)  # [D,1,H,W]

        seg = self._load_segmentation(series_uid)
        seg_tensor = torch.from_numpy(seg.astype(np.int64)) if seg is not None else None

        sample = {
            "volume": volume_tensor,  # [1,64,64,64]
            "image": image_tensor,    # [64,1,64,64]
            "labels": torch.tensor(labels, dtype=torch.float32),  # [NUM_LABELS]
            "series_uid": series_uid,
            "metadata": {
                "modality": meta.get("Modality", row.get("Modality", None)),
                "age": row.get("PatientAge", None),
                "sex": row.get("PatientSex", None),
                "num_slices": int(D),  # actual loaded slice count -- DICOM "Rows" is in-plane height, not slice count
                "pixel_spacing": meta.get("PixelSpacing", None),
                "dicom_meta": {k: meta.get(k, None) for k in DICOM_TAG_ALLOWLIST},
            },
        }
        if seg_tensor is not None:
            sample["segmentation"] = seg_tensor  # [64,64,64] class mask

        locs = self.localizers_map.get(series_uid, [])
        if len(locs):
            sample["localizers"] = locs

        return sample

    @staticmethod
    def to_pil_slices(sample) -> List[Image.Image]:
        """Convert sample['image'] (D,1,H,W) to list of PIL L images."""
        imgs = sample["image"]
        if isinstance(imgs, torch.Tensor):
            imgs = imgs.cpu().numpy()
        return [_to_pil_uint8(imgs[z, 0]) for z in range(imgs.shape[0])]


# ---------- dataloaders ----------

def create_dataloaders(
    batch_size: int = 4,
    num_workers: int = 4,
    val_split: float = 0.2,
    random_seed: int = 42,
    use_segmentation: bool = True,
    transform_train=None,
    transform_val=None,
) -> tuple[DataLoader, DataLoader]:
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(INPUT_TRAIN_PATH)

    if "Aneurysm Present" in df.columns and df["Aneurysm Present"].nunique() > 1:
        tr_df, va_df = train_test_split(
            df, test_size=val_split, random_state=random_seed,
            stratify=df["Aneurysm Present"],
        )
    else:
        tr_df, va_df = train_test_split(df, test_size=val_split, random_state=random_seed)

    tr_csv = BASE_OUTPUT_PATH / "train_split.csv"
    va_csv = BASE_OUTPUT_PATH / "val_split.csv"
    tr_df.to_csv(tr_csv, index=False)
    va_df.to_csv(va_csv, index=False)

    if transform_train is None:
        from albumentations import (
            Compose, HorizontalFlip, RandomBrightnessContrast, RandomRotate90,
            ShiftScaleRotate, VerticalFlip,
        )
        from albumentations.pytorch import ToTensorV2

        transform_train = Compose([
            HorizontalFlip(p=0.5),
            VerticalFlip(p=0.3),
            RandomRotate90(p=0.5),
            ShiftScaleRotate(0.05, 0.05, 10, p=0.4),
            RandomBrightnessContrast(0.1, 0.1, p=0.3),
            ToTensorV2(),
        ])
    if transform_val is None:
        from albumentations import Compose
        from albumentations.pytorch import ToTensorV2

        transform_val = Compose([ToTensorV2()])

    train_ds = BrainAneurysmDataset(
        csv_path=tr_csv,
        series_dir=INPUT_SERIES_PATH,
        localizers_csv_path=INPUT_TRAIN_LOCAL_PATH,
        segmentations_dir=INPUT_SEGMENT_PATH,
        slice_selection=SLICE_SELECTION,
        target_size=TARGET_SIZE,
        transform=transform_train,
        use_segmentation=use_segmentation,
        mode="train",
    )
    val_ds = BrainAneurysmDataset(
        csv_path=va_csv,
        series_dir=INPUT_SERIES_PATH,
        localizers_csv_path=INPUT_TRAIN_LOCAL_PATH,
        segmentations_dir=INPUT_SEGMENT_PATH,
        slice_selection=SLICE_SELECTION,
        target_size=TARGET_SIZE,
        transform=transform_val,
        use_segmentation=use_segmentation,
        mode="val",
    )

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True, drop_last=True,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True,
    )
    return train_loader, val_loader
