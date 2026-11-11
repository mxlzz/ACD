"""Detect repeated or nearly identical noisy inputs falsely labeled as independent seeds."""
from __future__ import annotations

from pathlib import Path

from .core import compare_images
from .io import read_arrays


def audit_noisy_seed_diversity(directory: str | Path, *, minimum_ratio: float = 0.01) -> dict:
    """Compare each claimed extra seed's raw EXR with the original raw EXR.

    Ratios use the raw-vs-reference RMSE only as a scale. This 1% diagnostic
    threshold is a conservative heuristic, NOT a statistical independence
    test. An almost deterministic scene can legitimately fail the heuristic,
    in which case the test offers no useful noise-seed diversity anyway.
    """
    root = Path(directory)
    raw = read_arrays(root / "acd_compare_Raw.exr")["image"]
    ref = read_arrays(root / "reference.exr")["image"]
    raw_vs_ref = compare_images(ref, raw)["rmse_linear"]
    if raw_vs_ref < 1e-12:
        return {
            "passes_diversity_check": None,
            "reason": "Raw is indistinguishable from reference; no measurable noise scale",
            "raw_reference_rmse": raw_vs_ref,
            "comparisons": [],
        }
    comparisons = []
    for folder in sorted(root.glob("seed_*")):
        path = folder / "acd_compare_Raw.exr"
        if not path.is_file():
            raise FileNotFoundError(f"Missing raw noisy EXR for seed: {path}")
        candidate = read_arrays(path)["image"]
        diff = compare_images(raw, candidate)
        ratio = diff["rmse_linear"] / raw_vs_ref
        comparisons.append({
            "seed_dir": folder.name,
            "raw_pair_rmse": diff["rmse_linear"],
            "raw_pair_vs_raw_reference_rmse_ratio": ratio,
            "passes_heuristic": bool(ratio >= minimum_ratio),
        })
    return {
        "passes_diversity_check": bool(comparisons) and all(c["passes_heuristic"] for c in comparisons),
        "heuristic_min_ratio": minimum_ratio,
        "raw_reference_rmse": raw_vs_ref,
        "comparisons": comparisons,
        "reason": (
            "Conservative image-level heuristic, not a proof of independent sampling. "
            "If false, averaging metrics as independent noise seeds is invalid."
        ),
    }


def verify_sample_variation(
    first, second, *, minimum_relative_rmse: float = 1e-4
) -> dict:
    """Guard against nominally different seeds yielding almost equal sample images.

    Computes RGB RMSE relative to RMS signal. This is deliberately a minimal
    practical smoke threshold, NOT an independence test or a quality measure.
    """
    import numpy as np
    from .core import rgb

    if not (0 < minimum_relative_rmse < 1):
        raise ValueError("minimum_relative_rmse must be between 0 and 1")
    a = rgb(first, "first")
    b = rgb(second, "second")
    if a.shape != b.shape:
        raise ValueError("Sample images have different resolutions")
    difference = a - b
    pair_rmse = float(np.sqrt(np.mean(difference ** 2)))
    scale = float(np.sqrt(np.mean(a ** 2)))
    relative = pair_rmse / max(scale, 1e-12)
    return {
        "meaningfully_different": bool(relative >= minimum_relative_rmse),
        "pair_rmse": pair_rmse,
        "signal_rms": scale,
        "pair_rmse_over_signal_rms": relative,
        "minimum_relative_rmse": minimum_relative_rmse,
        "caveat": (
            "Difference above threshold shows variation, not independent noise. "
            "Almost identical images cannot be treated as independent samples."
        ),
    }
