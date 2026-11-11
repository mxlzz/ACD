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
