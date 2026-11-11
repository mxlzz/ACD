"""Quantify agreement between two finite-spp reference renders.

Important: comparing the output pixels of two references cannot establish
independence of their underlying Monte Carlo sample streams or convergence to
the true expected radiance. This module reports diagnostics, not certification.
"""
from __future__ import annotations

import math

import numpy as np

from .core import compare_images, rgb


def audit_reference_pair(
    noisy: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    *,
    discrepancy_ratio_alert: float = 0.25,
    minimum_relative_variation: float = 1e-4,
) -> dict:
    """Measure reference disagreement relative to a noisy input and signal.

    - discrepancy_ratio_alert is a *heuristic warning threshold* only, not
      an absolute threshold for reference convergence or image fidelity.
    - minimum_relative_variation detects effectively identical references.
      Such an outcome may mean correlated sampling OR genuine convergence;
      image values alone cannot distinguish those explanations.
    - A lower reference spread does not prove absence of systematic bias.
    """
    raw = rgb(noisy, "raw")
    a = rgb(first, "first_reference")
    b = rgb(second, "second_reference")
    if raw.shape != a.shape or a.shape != b.shape:
        raise ValueError("Reference and noisy image shapes differ")
    if not math.isfinite(discrepancy_ratio_alert) or not 0 < discrepancy_ratio_alert <= 1:
        raise ValueError("discrepancy_ratio_alert must be in (0, 1]")
    if not math.isfinite(minimum_relative_variation) or not 0 < minimum_relative_variation < 1:
        raise ValueError("minimum_relative_variation must be in (0, 1)")

    disagreement = compare_images(a, b)
    first_error = compare_images(a, raw)["rmse_linear"]
    second_error = compare_images(b, raw)["rmse_linear"]
    reference_midpoint = (a + b) / 2
    raw_to_midpoint = compare_images(reference_midpoint, raw)["rmse_linear"]
    signal_rms = math.sqrt(float(np.mean(reference_midpoint * reference_midpoint)))
    disagreement_rmse = float(disagreement["rmse_linear"])
    disagreement_over_signal = disagreement_rmse / max(signal_rms, 1e-12)
    spread_relative_to_raw_noise = (
        disagreement_rmse / raw_to_midpoint if raw_to_midpoint > 1e-12 else None
    )

    near_identical = bool(disagreement_over_signal < minimum_relative_variation)
    large_spread = bool(
        spread_relative_to_raw_noise is not None
        and spread_relative_to_raw_noise >= discrepancy_ratio_alert
    )
    if near_identical:
        interpretation = (
            "Reference images are numerically almost indistinguishable. "
            "They may have correlated sampling or be genuinely converged; "
            "independence cannot be inferred from this comparison."
        )
    elif large_spread:
        interpretation = (
            "Reference discrepancy is material relative to noisy-image error; "
            "candidate rankings may be sensitive to reference uncertainty."
        )
    else:
        interpretation = (
            "Reference discrepancy is below the chosen relative warning "
            "threshold, but correlation, convergence and bias remain unverified."
        )

    return {
        "pair_difference": disagreement,
        "raw_vs_first_reference_rmse": float(first_error),
        "raw_vs_second_reference_rmse": float(second_error),
        "raw_vs_reference_midpoint_rmse": float(raw_to_midpoint),
        "reference_disagreement_over_signal_rms": disagreement_over_signal,
        "reference_disagreement_over_raw_error": spread_relative_to_raw_noise,
        "almost_identical_reference_images": near_identical,
        "large_reference_discrepancy_alert": large_spread,
        "discrepancy_ratio_alert_threshold": discrepancy_ratio_alert,
        "minimum_relative_variation_threshold": minimum_relative_variation,
        "independent_sampling_proven": False,
        "convergence_proven": False,
        "interpretation": interpretation,
    }
