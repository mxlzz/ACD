"""Inspect concentration of HDR squared errors, without claiming perceptual quality."""
from __future__ import annotations
import math
import numpy as np
from .core import rgb


def error_concentration(reference: np.ndarray, candidate: np.ndarray, *,
                        top_fraction: float=0.01) -> dict:
    if not (math.isfinite(top_fraction) and 0 < top_fraction <= 1):
        raise ValueError("top_fraction must be in (0,1]")
    ref=rgb(reference,"reference")
    cand=rgb(candidate,"candidate")
    if ref.shape != cand.shape:
        raise ValueError("reference/candidate shapes differ")
    if not np.isfinite(ref).all() or not np.isfinite(cand).all():
        raise ValueError("Images must be finite")
    per_pixel=np.mean((ref.astype(np.float64)-cand.astype(np.float64))**2,axis=2).ravel()
    n=len(per_pixel)
    if n == 0: raise ValueError("Empty image")
    k=max(1,min(n,int(math.ceil(n*top_fraction))))
    top=np.partition(per_pixel,n-k)[-k:]
    total=float(np.sum(per_pixel))
    return {
        "top_fraction_requested":top_fraction,
        "top_pixel_count":k,
        "pixel_count":n,
        "fraction_squared_error_in_top_pixels":float(np.sum(top)/total) if total else None,
        "max_pixel_rmse":float(np.sqrt(np.max(per_pixel))),
        "p99_pixel_rmse":float(np.sqrt(np.quantile(per_pixel,.99))),
        "linear_rgb_rmse":float(np.sqrt(total/n)),
        "warning":"Descriptive error concentration; no causal attribution or perceptual quality."
    }
