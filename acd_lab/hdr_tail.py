"""Shared-mask diagnostic of rare HDR outliers in Monte Carlo denoising.

Two masks, fixed across every candidate: top luminance in *reference* and
highest raw-input error against reference. The latter has explicit
selection bias toward the raw image and is never a ranking or training mask.
No tone mapping, exposure change, epsilon clamp or pixel-value clipping.
"""
from __future__ import annotations

import math
import numpy as np

from .core import rgb


def _mask_top(values: np.ndarray, fraction: float) -> np.ndarray:
    count = values.size
    select = max(1, int(math.ceil(count * fraction)))
    flat = np.zeros(count, dtype=np.bool_)
    # Exact, deterministic cardinality, even when thousands of values tie.
    indices = np.argsort(-values.ravel(), kind="stable")[:select]
    flat[indices] = True
    return flat.reshape(values.shape)


def _scores(ref: np.ndarray, candidate: np.ndarray, mask: np.ndarray) -> dict:
    residual = candidate - ref
    squared = np.mean(residual * residual, axis=-1)
    absolute = np.mean(np.abs(residual), axis=-1)
    total = float(np.sum(squared))
    on = float(np.sum(squared[mask]))
    off = float(np.sum(squared[~mask]))
    return {
        "mask_pixel_count": int(mask.sum()),
        "rmse_inside": float(np.sqrt(np.mean(squared[mask]))) if mask.any() else None,
        "rmse_outside": float(np.sqrt(np.mean(squared[~mask]))) if (~mask).any() else None,
        "mae_inside": float(np.mean(absolute[mask])) if mask.any() else None,
        "mae_outside": float(np.mean(absolute[~mask])) if (~mask).any() else None,
        "sse_fraction_inside": (on / total if total else None),
        "rmse_full": float(np.sqrt(np.mean(squared))),
        "mae_full": float(np.mean(absolute)),
        "total_rgb_mean_sse": total,
        "sse_inside": on,
        "sse_outside": off,
    }


def hdr_tail_breakdown(reference: np.ndarray, raw: np.ndarray,
                       candidates: dict[str, np.ndarray], *,
                       top_fraction: float = 0.01) -> dict:
    if not math.isfinite(top_fraction) or not 0 < top_fraction < 1:
        raise ValueError("top_fraction must be in (0,1)")
    ref = np.asarray(rgb(reference, "reference"), dtype=np.float64)
    noise = np.asarray(rgb(raw, "raw"), dtype=np.float64)
    if ref.ndim != 3 or ref.shape[-1] != 3 or ref.shape != noise.shape:
        raise ValueError("Images must be aligned HxWx3 RGB")
    if ref.shape[0] * ref.shape[1] < 2:
        raise ValueError("Require at least 2 pixels to evaluate inside and outside")
    if not (np.isfinite(ref).all() and np.isfinite(noise).all()):
        raise ValueError("Nonfinite reference or raw pixels")
    processed = {"Raw": noise}
    for name, arr in candidates.items():
        if name == "Raw":
            raise ValueError("Raw is reserved for shared noisy input")
        v = np.asarray(rgb(arr, name), dtype=np.float64)
        if v.shape != ref.shape or not np.isfinite(v).all():
            raise ValueError("Mismatched or nonfinite candidate: " + name)
        processed[name] = v
    # Reference-selected highlights: this mask never depends on denoising.
    # Scene-linear Rec.709 luminance (negative luminance is allowed).
    luminance = ref[..., 0] * .2126 + ref[..., 1] * .7152 + ref[..., 2] * .0722
    raw_error = np.mean((noise - ref) ** 2, axis=2)
    masks = {
        "reference_brightest": _mask_top(luminance, top_fraction),
        "raw_largest_errors": _mask_top(raw_error, top_fraction),
    }
    report = {}
    for key, mask in masks.items():
        by_method = {name: _scores(ref, image, mask)
                     for name, image in processed.items()}
        baseline = by_method["Raw"]["rmse_inside"]
        report[key] = {
            "mask_origin": ("reference_luminance_only" if key == "reference_brightest"
                            else "shared_raw_reference_error; selection biased toward raw"),
            "pixel_count": int(mask.sum()),
            "pixel_fraction_actual": float(np.mean(mask)),
            "methods": by_method,
            "mask_coordinate_hash": __import__("hashlib").sha256(
                np.ascontiguousarray(mask).tobytes()
            ).hexdigest(),
            "baseline_raw_rmse_inside": baseline,
        }
    return {
        "top_fraction_requested": float(top_fraction),
        "shape": list(ref.shape[:2]),
        "masks": report,
        "warning": (
            "Diagnostic not causal. Reference brightest and raw-error masks are common "
            "to all methods, but raw-error selection favors raw input, and finite-spp "
            "reference noise can distort the masks. No model training or ranking "
            "may use the reference-based masks at inference."
        ),
    }


def highlight_signed_bias(reference: np.ndarray, raw: np.ndarray,
                          candidates: dict[str, np.ndarray], *,
                          top_fraction: float = 0.01) -> dict:
    """Signed scene-linear luminance bias on reference-only bright pixels.

    Never select from candidates: an aggressive denoiser must not be able
    to move the test ROI. Ratios are used only if reference sum > 0.
    No gamma, display transform or clipping. Not a perceptual metric.
    """
    if not math.isfinite(top_fraction) or not 0 < top_fraction < 1:
        raise ValueError("top_fraction must be in (0,1)")
    ref = np.asarray(rgb(reference, "reference"), dtype=np.float64)
    noise = np.asarray(rgb(raw, "raw"), dtype=np.float64)
    if ref.ndim != 3 or ref.shape[-1] != 3 or ref.shape != noise.shape:
        raise ValueError("Expected aligned RGB images")
    if not np.isfinite(ref).all() or not np.isfinite(noise).all():
        raise ValueError("Nonfinite reference or raw")
    if ref.shape[0] * ref.shape[1] < 2:
        raise ValueError("Need >=2 pixels")
    weights = np.array((0.2126, 0.7152, 0.0722))
    ref_luma = np.sum(ref * weights, axis=2)
    mask = _mask_top(ref_luma, top_fraction)
    chosen_ref = ref_luma[mask]
    methods = {"Raw": noise, **candidates}
    if "Raw" in candidates:
        raise ValueError("Raw reserved")
    out = {}
    for name, value in methods.items():
        array = np.asarray(rgb(value, name), dtype=np.float64)
        if array.shape != ref.shape or not np.isfinite(array).all():
            raise ValueError("Mismatched/nonfinite candidate " + name)
        c_luma = np.sum(array * weights, axis=2)[mask]
        signed = c_luma - chosen_ref
        # Prefer mean over any one pixel: extreme sparkles can dominate
        # this difference; also report under/over count.
        total_ref = float(np.sum(chosen_ref))
        out[name] = {
            "reference_mean_luminance": float(np.mean(chosen_ref)),
            "candidate_mean_luminance": float(np.mean(c_luma)),
            "mean_signed_luminance_delta": float(np.mean(signed)),
            "mean_absolute_luminance_delta": float(np.mean(np.abs(signed))),
            "fraction_below_reference": float(np.mean(signed < 0)),
            "fraction_above_reference": float(np.mean(signed > 0)),
            "reference_luminance_sum": total_ref,
            "candidate_luminance_sum": float(np.sum(c_luma)),
            "candidate_to_reference_sum_ratio": (
                float(np.sum(c_luma) / total_ref) if total_ref > 0 else None
            ),
            "max_reference_luminance": float(np.max(chosen_ref)),
            "max_candidate_luminance": float(np.max(c_luma)),
        }
    return {
        "selection": "reference_top_scene_linear_luminance; shared by all candidates",
        "top_fraction_requested": float(top_fraction),
        "selected_pixel_count": int(mask.sum()),
        "mask_sha256": __import__("hashlib").sha256(
            np.ascontiguousarray(mask).tobytes()
        ).hexdigest(),
        "methods": out,
        "warning": "Signed HDR luminance diagnostic on finite reference; no causal inference, no perceptual color transform.",
    }
