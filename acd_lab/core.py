"""Deterministic raw-pass reconstruction and linear-light metrics.

Only RGB is evaluated; alpha is deliberately excluded and should be tested separately.
No pixel values are clipped, gamma-corrected or tone-mapped in these functions.
"""
from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np

FAMILIES = ("diffuse", "glossy", "transmission")
ADDITIVE = ("volume_direct", "volume_indirect", "emission", "environment")


def rgb(image: np.ndarray, name: str = "image") -> np.ndarray:
    """Validate a numerical H x W x 3/4 array and return float64 RGB."""
    data = np.asarray(image)
    if data.ndim != 3 or data.shape[-1] not in (3, 4):
        raise ValueError(f"{name}: expected H x W x 3/4, got {data.shape}")
    if min(data.shape[:2]) < 1:
        raise ValueError(f"{name}: empty image")
    if not np.issubdtype(data.dtype, np.number) or np.iscomplexobj(data):
        raise ValueError(f"{name}: expected real numeric data")
    result = np.asarray(data[..., :3], dtype=np.float64)
    if not np.isfinite(result).all():
        raise ValueError(f"{name}: found NaN or infinite values")
    return result


def recompose(passes: Mapping[str, np.ndarray]) -> np.ndarray:
    """Reconstruct unfiltered beauty RGB from named linear-light AOV arrays.

    Each present family needs family_direct, family_indirect and family_color.
    Missing entire families are permitted; partially supplied families are errors.
    This checks supplied contributions but does not imply that all renderer AOVs
    were exported. Compare the result to raw beauty with check_recomposition.
    """
    result = None
    for family in FAMILIES:
        keys = [f"{family}_{part}" for part in ("direct", "indirect", "color")]
        provided = [name for name in keys if name in passes]
        if provided and len(provided) != 3:
            missing = sorted(set(keys) - set(provided))
            raise ValueError(f"{family}: incomplete family; missing: {missing}")
        if not provided:
            continue
        direct, indirect, color = (rgb(passes[name], name) for name in keys)
        if direct.shape != indirect.shape or direct.shape != color.shape:
            raise ValueError(f"{family}: mismatching dimensions")
        component = (direct + indirect) * color
        if result is not None and result.shape != component.shape:
            raise ValueError(f"{family}: mismatching scene dimensions")
        result = component if result is None else result + component

    for name in ADDITIVE:
        if name not in passes:
            continue
        component = rgb(passes[name], name)
        if result is not None and result.shape != component.shape:
            raise ValueError(f"{name}: mismatching scene dimensions")
        result = component if result is None else result + component

    if result is None:
        raise ValueError("No recognized render passes provided")
    return result


def compare_images(
    reference: np.ndarray, candidate: np.ndarray, *, data_range: float | None = None
) -> dict[str, float | bool | None]:
    """Compare same-size linear-light images. PSNR is only defined with explicit range."""
    ref = rgb(reference, "reference")
    cand = rgb(candidate, "candidate")
    if ref.shape != cand.shape:
        raise ValueError(f"Image dimension mismatch: {ref.shape} vs {cand.shape}")
    delta = cand - ref
    mse = float(np.mean(delta * delta))
    rmse = math.sqrt(mse)
    reference_rms = math.sqrt(float(np.mean(ref * ref)))
    if data_range is not None:
        data_range = float(data_range)
        if not math.isfinite(data_range) or data_range <= 0:
            raise ValueError("data_range must be positive and finite")
    psnr = (
        None if data_range is None or mse == 0
        else 20 * math.log10(data_range / rmse)
    )
    return {
        "mae_linear": float(np.mean(np.abs(delta))),
        "rmse_linear": rmse,
        "relative_rmse": rmse / max(reference_rms, 1e-12),
        "psnr_db": psnr,
        "psnr_data_range": data_range,
        "exact_match": bool(mse == 0),
    }


def check_recomposition(beauty: np.ndarray, passes: Mapping[str, np.ndarray]) -> dict:
    """Report raw recomposition error; never compare against denoised beauty."""
    ref = rgb(beauty, "beauty")
    reconstructed = recompose(passes)
    score = compare_images(ref, reconstructed)
    residual = reconstructed - ref
    return {
        "metrics": score,
        "mean_signed_error_rgb": [float(x) for x in residual.mean(axis=(0, 1))],
        "max_abs_error": float(np.max(np.abs(residual))),
        "shape": list(ref.shape),
        "warning": "A small error requires complete compatible AOVs; a large error may indicate omitted contributions.",
    }
