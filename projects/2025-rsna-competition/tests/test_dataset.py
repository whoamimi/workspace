"""Unit tests for the pure preprocessing helpers in src/data/dataset.py.

These are white-box tests of internal (`_`-prefixed) helpers -- there's no
public API around them yet, and they're exactly the functions a bad DICOM
value or an odd volume shape would silently break. Run with:

    pytest projects/2025-rsna-competition/tests
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

# Every project in this monorepo uses the same top-level package name `src`
# (see projects/README.md), so running more than one project's tests in a
# single pytest process needs the previous project's `src` cleared from
# sys.modules first -- otherwise Python's import cache resolves `from
# src...` to whichever project imported it first.
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.dataset import (
    _apply_rescale,
    _ct_mr_normalize,
    _resize_zyx,
    _select_indices,
    _series_cache_path,
    _to_pil_uint8,
    _to_zyx_layout,
)


class TestApplyRescale:
    def test_applies_slope_and_intercept(self):
        img = np.array([[0.0, 10.0], [20.0, 30.0]], dtype=np.float32)
        ds = SimpleNamespace(RescaleSlope=2.0, RescaleIntercept=-5.0)
        out = _apply_rescale(img, ds)
        np.testing.assert_allclose(out, img * 2.0 - 5.0)
        assert out.dtype == np.float32

    def test_defaults_to_identity_when_tags_missing(self):
        img = np.array([[1.0, 2.0]], dtype=np.float32)
        ds = SimpleNamespace()  # no RescaleSlope/RescaleIntercept
        out = _apply_rescale(img, ds)
        np.testing.assert_allclose(out, img)


class TestCtMrNormalize:
    def test_ct_clips_to_hu_window_and_scales_to_unit_range(self):
        vol = np.array([-2000, -1000, 0, 1000, 2000], dtype=np.float32)
        out = _ct_mr_normalize(vol, "CT")
        assert out.min() >= 0.0 and out.max() <= 1.0
        np.testing.assert_allclose(out, [0.0, 0.0, 0.5, 1.0, 1.0], atol=1e-6)

    def test_cta_modality_also_treated_as_ct(self):
        vol = np.array([0.0], dtype=np.float32)
        out = _ct_mr_normalize(vol, "CTA")
        np.testing.assert_allclose(out, [0.5], atol=1e-6)

    def test_mr_uses_robust_zscore_and_clips_to_unit_range(self):
        vol = np.array([1.0, 2.0, 3.0, 4.0, 1000.0], dtype=np.float32)  # outlier
        out = _ct_mr_normalize(vol, "MR")
        assert out.min() >= 0.0 and out.max() <= 1.0
        assert out.dtype == np.float32

    def test_mr_is_default_when_modality_unknown(self):
        vol = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        out_unknown = _ct_mr_normalize(vol, "")
        out_mr = _ct_mr_normalize(vol, "MR")
        np.testing.assert_allclose(out_unknown, out_mr)


class TestResizeZyx:
    @pytest.mark.parametrize("src_shape", [(10, 20, 30), (100, 100, 100), (64, 64, 64)])
    def test_output_always_matches_target_shape(self, src_shape):
        vol = np.random.rand(*src_shape).astype(np.float32)
        out = _resize_zyx(vol, target=(64, 64, 64))
        assert out.shape == (64, 64, 64)

    def test_rejects_non_3d_input(self):
        with pytest.raises(AssertionError):
            _resize_zyx(np.zeros((5, 5)), target=(64, 64, 64))


class TestSelectIndices:
    def test_all_mode_returns_full_range_regardless_of_target(self):
        assert _select_indices(10, "all", 4) == list(range(10))

    def test_n_less_than_or_equal_target_returns_full_range(self):
        assert _select_indices(3, "uniform", 10) == list(range(3))
        assert _select_indices(3, "center", 3) == list(range(3))

    def test_center_mode_returns_contiguous_middle_slice(self):
        assert _select_indices(10, "center", 4) == [3, 4, 5, 6]

    def test_uniform_mode_spans_full_range(self):
        idxs = _select_indices(10, "uniform", 4)
        assert idxs[0] == 0
        assert idxs[-1] == 9
        assert len(idxs) == 4


class TestToPilUint8:
    def test_converts_float_array_to_grayscale_image(self):
        arr = np.full((4, 4), 0.5, dtype=np.float32)
        img = _to_pil_uint8(arr)
        assert img.mode == "L"
        assert img.size == (4, 4)
        assert np.array(img)[0, 0] == 127  # (0.5 * 255) truncated to uint8

    def test_clips_out_of_range_values(self):
        arr = np.array([[-1.0, 2.0]], dtype=np.float32)
        img = _to_pil_uint8(arr)
        pixels = np.array(img)
        assert pixels[0, 0] == 0
        assert pixels[0, 1] == 255


class TestSeriesCachePath:
    """Regression test for a Copilot-flagged bug on PR #3: the cache key used
    to bake in the global TARGET_SIZE regardless of what target_size a
    Dataset instance was actually configured with, so a non-default
    target_size would silently read/write the wrong cache file."""

    def test_cache_path_reflects_the_given_target_size_not_a_global(self, tmp_path):
        p1 = _series_cache_path("abc", target_size=(64, 64, 64), cache_dir=tmp_path)
        p2 = _series_cache_path("abc", target_size=(32, 32, 32), cache_dir=tmp_path)
        assert p1 != p2
        assert "64x64x64" in p1.name
        assert "32x32x32" in p2.name


class TestToZyxLayout:
    """Regression test for a Copilot-flagged bug on PR #3: the original
    heuristic (`shape[-1] > shape[0]`) got the transpose backwards for a
    common (H, W, Z) NIfTI layout like (512, 512, 100), leaving it
    untransposed and corrupting the mask when later treated as (Z, H, W)."""

    def test_transposes_hwz_layout_to_zhw(self):
        seg = np.zeros((512, 512, 100), dtype=np.uint8)  # (H, W, Z), Z smallest
        out = _to_zyx_layout(seg)
        assert out.shape == (100, 512, 512)  # (Z, H, W)

    def test_leaves_already_zhw_layout_unchanged(self):
        seg = np.zeros((100, 512, 512), dtype=np.uint8)  # already (Z, H, W)
        out = _to_zyx_layout(seg)
        assert out.shape == (100, 512, 512)

    def test_leaves_non_3d_input_unchanged(self):
        seg = np.zeros((512, 512), dtype=np.uint8)
        out = _to_zyx_layout(seg)
        assert out.shape == (512, 512)
