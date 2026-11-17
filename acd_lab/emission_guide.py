"""Experimental Cycles Emission AOV guide for selective Raw/OIDN blending.

Inference inputs: original Raw RGB, native OIDN RGB and actual Cycles Emission
AOV from the SAME seed. Never evaluates reference in inference. Unvalidated.
"""
from __future__ import annotations

import math
import numpy as np
from .core import rgb


def emission_guided_blend(raw: np.ndarray, filtered: np.ndarray,
                          emission: np.ndarray, *,
                          scale: float = .25,
                          max_raw_fraction: float = .5) -> tuple[np.ndarray, dict]:
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("scale must be positive and finite")
    if not math.isfinite(max_raw_fraction) or not 0 <= max_raw_fraction <= 1:
        raise ValueError("max_raw_fraction must be in [0,1]")
    r=np.asarray(rgb(raw,"Raw"),dtype=np.float64)
    d=np.asarray(rgb(filtered,"OIDN"),dtype=np.float64)
    e=np.asarray(rgb(emission,"Emission"),dtype=np.float64)
    if not (r.ndim==3 and r.shape[-1]==3 and r.shape==d.shape==e.shape):
        raise ValueError("Expected aligned HxWx3 RGB for Raw/OIDN/Emission")
    if not (np.isfinite(r).all() and np.isfinite(d).all() and np.isfinite(e).all()):
        raise ValueError("Finite input required")
    # Scene-linear emission AOV, nonnegative luminance for blending weight.
    # This is a render pass, *not* a neural variance estimate, nor a ground truth.
    energy=np.maximum(0, e @ np.array([.2126,.7152,.0722]))
    weight=max_raw_fraction*energy/(energy+scale)
    out=(1.0-weight[...,None])*d+weight[...,None]*r
    return out.astype(np.float32), {
        "scale":scale, "max_raw_fraction":max_raw_fraction,
        "mean_raw_weight":float(np.mean(weight)),
        "nonzero_emission_fraction":float(np.mean(energy>0)),
        "mean_emission_luminance":float(np.mean(energy)),
        "max_emission_luminance":float(np.max(energy)),
        "max_raw_weight_actual":float(np.max(weight)),
        "input_policy":"Raw/OIDN/Emission AOV of the same render and seed; no reference",
        "warning":"AOV data may contain noise; this does not preserve denoised light transport exactly; not validated.",
    }
