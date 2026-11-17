"""Compare multiple candidate denoisers to an independent linear EXR reference."""
from __future__ import annotations

from pathlib import Path

from .core import compare_images
from .detail import detail_fidelity
from .io import read_arrays

NAMES = ("Raw", "STANDARD", "HIGH", "SUPER")
OPTIONAL = (
    "RawRecomposed", "HIGH_no_final", "SUPER_no_final",
    "HIGH_no_guides", "SUPER_no_guides", "STANDARD_emission_preserved",
    "STANDARD_no_guides",
    "HIGH_component_no_guides", "SUPER_component_no_guides",
    "HIGH_component_albedo", "SUPER_component_albedo",
    "HIGH_component_normal", "SUPER_component_normal",
    "SID4_STANDARD", "SID4_HIGH", "SID4_SUPER", "NATIVE_COMP_OIDN",
)


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
        results[name] = {**compare_images(reference, candidate), "detail": detail_fidelity(reference, candidate)}

    for name in OPTIONAL:
        candidate_file = root / ("acd_compare_" + name + ".exr")
        if candidate_file.is_file():
            candidate = read_arrays(candidate_file)["image"]
            results[name] = {**compare_images(reference, candidate), "detail": detail_fidelity(reference, candidate)}

    check_file = root / "reference_check.exr"
    ref_disagreement = None
    independent_ranking = None
    reference_quality_diagnostic = None
    if check_file.is_file():
        second_reference = read_arrays(check_file)["image"]
        from .reference_audit import audit_reference_pair
        raw = read_arrays(root / "acd_compare_Raw.exr")["image"]
        reference_quality_diagnostic = audit_reference_pair(raw, reference, second_reference)
        ref_disagreement = compare_images(reference, second_reference)
        independent_scores = {
            name: compare_images(second_reference, read_arrays(root / ("acd_compare_" + name + ".exr"))["image"])
            for name in results
        }
        independent_ranking = sorted(results, key=lambda name: independent_scores[name]["rmse_linear"])

    raw_rmse = float(results["Raw"]["rmse_linear"])
    relative_change = {
        name: (None if raw_rmse == 0 else 1 - float(report["rmse_linear"]) / raw_rmse)
        for name, report in results.items()
    }
    return {
        "reference": str(reference_file.name),
        "note": "References are finite-spp and independent sampling/convergence are not verified by image comparison alone",
        "measurements": results,
        "rmse_reduction_vs_raw": relative_change,
        "rank_by_rmse": sorted(results, key=lambda name: results[name]["rmse_linear"]),
        "rank_by_mae": sorted(results, key=lambda name: results[name]["mae_linear"]),
        "rank_by_edge_gradient_rmse": (sorted(
            (name for name in results if results[name]["detail"]["edge_gradient_rmse"] is not None),
            key=lambda name: results[name]["detail"]["edge_gradient_rmse"]
        ) or None),
        "detail_metric_scope": "Reference-defined color gradients; diagnostic, not a perceptual score or proof of reference convergence",
        "rank_by_log1p_luminance": sorted(results, key=lambda name: results[name]["log1p_luminance_rmse"]),
        "independent_reference_difference": ref_disagreement,
        "reference_quality_diagnostic": reference_quality_diagnostic,
        "reference_ranking_consistent": (
            sorted(results, key=lambda name: results[name]["rmse_linear"])
            == independent_ranking if independent_ranking is not None else None
        ),
        "rank_against_second_reference": independent_ranking,
        "raw_recomposition_vs_raw": (
            compare_images(read_arrays(root / "acd_compare_Raw.exr")["image"],
                           read_arrays(root / "acd_compare_RawRecomposed.exr")["image"])
            if (root / "acd_compare_RawRecomposed.exr").is_file() else None
        ),
    }
