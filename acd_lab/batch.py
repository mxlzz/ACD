"""Compare multiple candidate denoisers to an independent linear EXR reference."""
from __future__ import annotations

from pathlib import Path

from .core import compare_images
from .io import read_arrays

NAMES = ("Raw", "STANDARD", "HIGH", "SUPER")
OPTIONAL = ("RawRecomposed", "HIGH_no_final", "SUPER_no_final", "HIGH_no_guides", "SUPER_no_guides")


def evaluate_batch(directory: str | Path) -> dict:
    """Evaluate identical-pixel-size outputs against an independent reference.

    This does not prove convergence of the reference or generalize to other scenes.
    """
    root = Path(directory)
    reference_file = root / "reference.exr"
    reference = read_arrays(reference_file)["image"]

    results: dict[str, dict] = {}
    for name in NAMES:
        target = root / ("acd_compare_" + name + ".exr")
        candidate = read_arrays(target)["image"]
        results[name] = compare_images(reference, candidate)

    for name in OPTIONAL:
        candidate_file = root / ("acd_compare_" + name + ".exr")
        if candidate_file.is_file():
            results[name] = compare_images(reference, read_arrays(candidate_file)["image"])

    raw_rmse = float(results["Raw"]["rmse_linear"])
    relative_change = {
        name: (None if raw_rmse == 0 else 1 - float(report["rmse_linear"]) / raw_rmse)
        for name, report in results.items()
    }
    return {
        "reference": str(reference_file.name),
        "note": "One small test scene; independent reference is not convergence-verified",
        "measurements": results,
        "rmse_reduction_vs_raw": relative_change,
        "rank_by_rmse": sorted(results, key=lambda name: results[name]["rmse_linear"]),
        "raw_recomposition_vs_raw": (
            compare_images(read_arrays(root / "acd_compare_Raw.exr")["image"],
                           read_arrays(root / "acd_compare_RawRecomposed.exr")["image"])
            if (root / "acd_compare_RawRecomposed.exr").is_file() else None
        ),
    }
