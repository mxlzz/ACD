"""Interpretably evaluate denoisers in spatial and AOV-contribution regions.

An AOV-based region represents *where a class of radiance contributes*, not a
segmentation of the material physically visible in each pixel. E.g. a "glossy"
region can include glossy indirect reflections of nonmetallic surfaces.

All calculations use scene-linear RGB. No tone mapping or automatic clipping.
"""
from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np

from .core import FAMILIES, ADDITIVE, compare_images, rgb

_LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float64)


def contributions(passes: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Return per-family and additive radiance terms; reject incomplete families."""
    out: dict[str, np.ndarray] = {}
    shape = None
    for family in FAMILIES:
        keys = [f"{family}_{name}" for name in ("direct", "indirect", "color")]
        provided = [key for key in keys if key in passes]
        if not provided:
            continue
        if len(provided) != 3:
            missing = sorted(set(keys) - set(provided))
            raise ValueError(f"{family}: incomplete family; missing: {missing}")
        direct, indirect, color = (rgb(passes[key], key) for key in keys)
        if not (direct.shape == indirect.shape == color.shape):
            raise ValueError(f"{family}: inconsistent dimensions")
        out[family] = (direct + indirect) * color
        shape = shape or direct.shape
    for key in ADDITIVE:
        if key in passes:
            out[key] = rgb(passes[key], key)
    if not out:
        raise ValueError("No recognized AOV contribution data")
    if len({array.shape for array in out.values()}) > 1:
        raise ValueError("AOV contributions have inconsistent dimensions")
    return out


def aov_energy_masks(
    passes: Mapping[str, np.ndarray], *, threshold: float = 0.35,
    min_signal: float = 0.01
) -> dict[str, np.ndarray]:
    """Mask pixels where contribution's absolute luminance is >= threshold
    of total contribution magnitude (and total magnitude >= min_signal).

    This is a *relative energy attribution diagnostic*, not a material ID mask.
    Absolute contributions are used to avoid cancellation of signed RGB terms.
    A threshold below 1 can produce overlapping masks by construction.
    """
    if not math.isfinite(threshold) or not 0 < threshold <= 1:
        raise ValueError("threshold must be finite in (0,1]")
    if not math.isfinite(min_signal) or min_signal < 0:
        raise ValueError("min_signal must be finite and >= 0")
    terms = contributions(passes)
    energy = {name: np.abs(value) @ _LUMA for name, value in terms.items()}
    total = np.zeros_like(next(iter(energy.values())))
    for values in energy.values():
        total += values
    valid = total >= min_signal
    return {
        name: valid & (values >= threshold * np.maximum(total, 1e-15))
        for name, values in energy.items()
    }


def rectangle_mask(
    size: tuple[int, int], rect: tuple[float, float, float, float],
    *, normalized: bool = True
) -> np.ndarray:
    """Rasterized rectangle using top-left origin, half-open bounds [x0,x1) x [y0,y1).

    Normalized coords are fractions in [0,1], where image width/height may
    differ. Pixel coords must be integer-like. Reject empty rectangles.
    """
    height, width = size
    if height < 1 or width < 1:
        raise ValueError("Invalid image size")
    if len(rect) != 4 or any(not math.isfinite(float(v)) for v in rect):
        raise ValueError("Rect must contain four finite numbers")
    x0, y0, x1, y1 = (float(x) for x in rect)
    limit_x, limit_y = ((1, 1) if normalized else (width, height))
    if not (0 <= x0 < x1 <= limit_x and 0 <= y0 < y1 <= limit_y):
        raise ValueError("Rect must be inside image bounds, positive and ordered")
    if normalized:
        x0, y0, x1, y1 = (
            math.floor(x0 * width), math.floor(y0 * height),
            math.ceil(x1 * width), math.ceil(y1 * height)
        )
    elif any(x != int(x) for x in (x0, y0, x1, y1)):
        raise ValueError("Pixel coordinates must be integers")
    mask = np.zeros((height, width), dtype=bool)
    mask[int(y0):int(y1), int(x0):int(x1)] = True
    return mask


def assess_regions(
    reference: np.ndarray,
    candidates: Mapping[str, np.ndarray],
    masks: Mapping[str, np.ndarray],
) -> dict[str, object]:
    """Compare masked RGB samples without rescaling or treating unselected
    pixels as zeros (which would bias the results).

    Zero-area masks remain explicitly empty and have null metrics.
    """
    target = rgb(reference, "reference")
    height, width, _ = target.shape
    if not candidates:
        raise ValueError("At least one candidate is required")
    normalized_candidates = {name: rgb(value, name) for name, value in candidates.items()}
    if any(image.shape != target.shape for image in normalized_candidates.values()):
        raise ValueError("Candidate image dimensions must match reference")
    results: dict[str, object] = {}
    for name, mask in masks.items():
        mask = np.asarray(mask)
        if mask.shape != (height, width) or mask.dtype != np.bool_:
            raise ValueError(f"{name}: expected a boolean mask with image dimensions")
        count = int(mask.sum())
        metrics = (
            {method: compare_images(target[mask][None, :, :], candidate[mask][None, :, :])
             for method, candidate in normalized_candidates.items()}
            if count else None
        )
        results[name] = {
            "pixels": count, "coverage": count / (width * height), "metrics": metrics
        }
    return {"size": [width, height], "regions": results}


def save_error_maps(
    path: str, reference: np.ndarray, candidates: Mapping[str, np.ndarray]
) -> None:
    """Write compressed EXR-free error maps (.npz) for offline visualization.

    Signed and absolute *per-channel* maps are stored; preserves HDR values.
    """
    target = rgb(reference, "reference")
    arrays = {}
    for name, candidate in candidates.items():
        if not name.isidentifier():
            raise ValueError(f"Invalid candidate name for map: {name}")
        image = rgb(candidate, name)
        if image.shape != target.shape:
            raise ValueError(f"{name}: dimension mismatch")
        delta = image - target
        arrays[name + "_signed"] = delta.astype(np.float32)
        arrays[name + "_absolute"] = np.abs(delta).astype(np.float32)
    np.savez_compressed(path, **arrays)
