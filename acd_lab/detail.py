"""Reference-defined gradient fidelity diagnostics for denoising research.

The mask is selected using *only the finite-spp reference*, not a method's
output. Scores compare RGB gradients after an invertible asinh HDR compression:
no clamping, color conversion or sharpening is applied to source images.
These are descriptive proxies, NOT calibrated perceptual quality or proof that
high-frequency energy is authentic. The reference itself may contain noise.
"""
from __future__ import annotations

import math
import numpy as np


def detail_fidelity(reference: np.ndarray, candidate: np.ndarray, *,
                    mask: np.ndarray | None = None, edge_fraction: float = 0.2,
                    flat_fraction: float = 0.5) -> dict:
    """Compare adjacent RGB differences on reference-selected edge/flat pairs.

    Pair eligibility requires *both endpoints* inside the ROI. Gradients are
    horizontal and vertical; no artificial adjacency is introduced by
    flattening/concatenating disjoint regions.

    edge_fraction: upper fraction of NONZERO reference gradient magnitudes.
    flat_fraction: lower fraction of ALL eligible reference gradients.
    Contrast ratio alone can reward oversharpening; always inspect error.
    """
    ref = np.asarray(reference)
    cand = np.asarray(candidate)
    if (ref.ndim != 3 or ref.shape[-1] not in (3, 4)
            or ref.shape[:2] != cand.shape[:2] or cand.ndim != 3
            or cand.shape[-1] not in (3, 4)):
        raise ValueError("Expected aligned H x W x 3/4 RGB images")
    if min(ref.shape[:2]) < 1:
        raise ValueError("Empty images are invalid")
    if (not np.issubdtype(ref.dtype, np.number)
            or not np.issubdtype(cand.dtype, np.number)
            or np.iscomplexobj(ref) or np.iscomplexobj(cand)):
        raise ValueError("Images must be real numeric arrays")
    r = np.asarray(ref[..., :3], dtype=np.float64)
    c = np.asarray(cand[..., :3], dtype=np.float64)
    if not (np.isfinite(r).all() and np.isfinite(c).all()):
        raise ValueError("Nonfinite RGB values are invalid")
    if (not math.isfinite(edge_fraction) or not 0 < edge_fraction <= 1
            or not math.isfinite(flat_fraction) or not 0 < flat_fraction <= 1):
        raise ValueError("Gradient selection fractions must be in (0, 1]")

    h, w = r.shape[:2]
    if mask is None:
        roi = np.ones((h, w), dtype=np.bool_)
    else:
        roi = np.asarray(mask)
        if roi.shape != (h, w) or roi.dtype != np.bool_:
            raise ValueError("ROI must be an H x W boolean mask")

    def pairs(x):
        return np.concatenate((
            (x[:, 1:, :] - x[:, :-1, :]).reshape(-1, 3),
            (x[1:, :, :] - x[:-1, :, :]).reshape(-1, 3)
        ), axis=0)

    # asinh preserves signed HDR data and compresses highlights. This is a
    # non-perceptual metric; report it separately from scene-linear RMSE.
    rg = pairs(np.arcsinh(r))
    cg = pairs(np.arcsinh(c))
    eligible = np.concatenate((
        (roi[:, 1:] & roi[:, :-1]).ravel(),
        (roi[1:, :] & roi[:-1, :]).ravel()
    ))
    ref_mag = np.linalg.norm(rg, axis=1) / math.sqrt(3.0)
    cand_mag = np.linalg.norm(cg, axis=1) / math.sqrt(3.0)

    positive = ref_mag[eligible & (ref_mag > 1e-12)]
    if positive.size:
        edge_threshold = float(np.quantile(positive, 1.0 - edge_fraction))
        edge = eligible & (ref_mag >= edge_threshold) & (ref_mag > 1e-12)
    else:
        edge_threshold = None
        edge = np.zeros_like(eligible)
    if np.any(eligible):
        flat_threshold = float(np.quantile(ref_mag[eligible], flat_fraction))
        flat = eligible & (ref_mag <= flat_threshold)
    else:
        flat_threshold = None
        flat = np.zeros_like(eligible)

    def score(selected):
        if not np.any(selected):
            return (None, None)
        difference = cg[selected] - rg[selected]
        return (float(np.sqrt(np.mean(difference * difference))),
                float(np.mean(np.abs(difference))))

    edge_rmse, edge_mae = score(edge)
    flat_rmse, flat_mae = score(flat)
    ratio = (float(np.mean(cand_mag[edge]) / np.mean(ref_mag[edge]))
             if np.any(edge) else None)
    return {
        "transform": "per-channel asinh(scene_linear_RGB), gradient H/V",
        "selection": "reference-only; top 20% of positive gradient strengths unless configured",
        "edge_fraction": float(edge_fraction),
        "flat_fraction": float(flat_fraction),
        "eligible_pair_count": int(np.count_nonzero(eligible)),
        "edge_pair_count": int(np.count_nonzero(edge)),
        "flat_pair_count": int(np.count_nonzero(flat)),
        "edge_threshold": edge_threshold,
        "flat_threshold": flat_threshold,
        "edge_gradient_rmse": edge_rmse,
        "edge_gradient_mae": edge_mae,
        "edge_contrast_ratio": ratio,
        "flat_gradient_rmse": flat_rmse,
        "flat_gradient_mae": flat_mae,
        "warning": (
            "Reference-derived gradients include reference sampling noise; "
            "contrast ratio alone does not measure fidelity. "
            "Selected pairs may tie at quantile thresholds; not a perceptual metric."
        ),
    }
