"""Input-only HDR bright-pixel blending, an unvalidated research ablation.

Infer weights exclusively from RAW scene-linear luminance (no ground truth,
AOV oracle or denoised-output-derived selection). Keep Blender addon untouched.
No spatial smoothing; highlight boundaries can produce visible seams.
"""
from __future__ import annotations

import math
import numpy as np
from .core import rgb


def blend_input_highlights(raw: np.ndarray, denoised: np.ndarray, *,
                           low_quantile: float = .97,
                           high_quantile: float = .995,
                           max_raw_fraction: float = .5) -> tuple[np.ndarray, dict]:
    if not (math.isfinite(low_quantile) and math.isfinite(high_quantile)
            and 0 < low_quantile < high_quantile <= 1):
        raise ValueError("Invalid quantiles")
    if not math.isfinite(max_raw_fraction) or not 0 <= max_raw_fraction <= 1:
        raise ValueError("max_raw_fraction must be in [0,1]")
    raw_rgb = np.asarray(rgb(raw, "raw"), dtype=np.float64)
    filtered_rgb = np.asarray(rgb(denoised, "denoised"), dtype=np.float64)
    if raw_rgb.shape != filtered_rgb.shape or raw_rgb.ndim != 3 or raw_rgb.shape[-1] != 3:
        raise ValueError("Expected aligned HxWx3 RGB")
    if not np.isfinite(raw_rgb).all() or not np.isfinite(filtered_rgb).all():
        raise ValueError("Finite input required")
    lum = np.maximum(0.0, raw_rgb @ np.array([.2126, .7152, .0722]))
    lower = float(np.quantile(lum, low_quantile))
    upper = float(np.quantile(lum, high_quantile))
    if upper <= lower:
        weight = np.zeros_like(lum)
    else:
        t = np.clip((lum - lower) / (upper - lower), 0.0, 1.0)
        # smoothstep is continuous at both thresholds, but not spatially
        # regularized and may retain raw Monte Carlo sparkles.
        weight = (3.0*t*t - 2.0*t*t*t) * max_raw_fraction
    candidate = filtered_rgb * (1 - weight[...,None]) + raw_rgb * weight[...,None]
    stats = {
        "low_quantile": low_quantile, "high_quantile": high_quantile,
        "max_raw_fraction": max_raw_fraction,
        "threshold_low": lower, "threshold_high": upper,
        "mean_raw_weight": float(np.mean(weight)),
        "max_raw_weight_actual": float(np.max(weight)),
        "fraction_nonzero_weight": float(np.mean(weight > 0)),
        "fraction_half_or_more_raw": float(np.mean(weight >= .5)),
        "selection": "Only RAW scene-linear luminance; no reference and no filtered output",
        "warning": "Unvalidated: may restore fireflies or introduce discontinuities.",
    }
    return candidate.astype(np.float32), stats


def blend_constant(raw: np.ndarray, denoised: np.ndarray, *,
                   raw_fraction: float) -> np.ndarray:
    if not math.isfinite(raw_fraction) or not 0 <= raw_fraction <= 1:
        raise ValueError("raw_fraction must be in [0,1]")
    r = np.asarray(rgb(raw,"raw"),dtype=np.float64)
    d = np.asarray(rgb(denoised,"denoised"),dtype=np.float64)
    if r.shape != d.shape or r.ndim != 3 or r.shape[-1]!=3:
        raise ValueError("Expected aligned RGB arrays")
    if not np.isfinite(r).all() or not np.isfinite(d).all():
        raise ValueError("Finite input required")
    return (raw_fraction*r+(1-raw_fraction)*d).astype(np.float32)
