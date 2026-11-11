"""Aggregate per-region denoising metrics over demonstrably distinct noisy inputs.

A fixed AOV mask from the base input is required for comparability. The same
finite-spp reference is shared, so these means are descriptive, not confidence
bounds or evidence of independent reference convergence.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from .seed_audit import audit_noisy_seed_diversity


def aggregate_region_reports(
    directory: str | Path, *, region: str = "aov_emission",
    baseline: str = "STANDARD", candidate: str = "STANDARD_emission_preserved",
) -> dict:
    root = Path(directory)
    paths = [root / "region_metrics.json"] + sorted(root.glob("seed_*/region_metrics.json"))
    if len(paths) < 2:
        raise ValueError("Need at least two regional reports for distinct noisy inputs")
    if any(not p.is_file() for p in paths):
        raise FileNotFoundError("Missing region metrics file")
    diversity = audit_noisy_seed_diversity(root)
    if diversity["passes_diversity_check"] is not True:
        raise ValueError("Raw noisy inputs not measurably different; regional seed average invalid")

    reports = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    first = reports[0]["regions"].get(region)
    if not first or not first["pixels"]:
        raise ValueError(f"Region {region!r} has no selected pixels")
    definition = reports[0]["region_definitions"][region]
    expected_mask_hash = first.get("mask_sha256")
    if not isinstance(expected_mask_hash, str) or len(expected_mask_hash) != 64:
        raise ValueError(
            "Regional report lacks spatial mask fingerprint; regenerate "
            "all region reports with current ACD Lab"
        )
    # Every report must agree on the *ordered pixel mask*, not only on
    # coverage/count and human-readable definition; mask_sha256 enforces it.
    rows = []
    for path, report in zip(paths, reports):
        target = report["regions"].get(region)
        if (target is None or target["pixels"] != first["pixels"]
                or report["region_definitions"].get(region) != definition
                or target.get("mask_sha256") != expected_mask_hash):
            raise ValueError("Regional definitions/counts differ across seed reports")
        available = target.get("metrics")
        if not available or baseline not in available or candidate not in available:
            raise ValueError(f"Missing {baseline}/{candidate} in {path}")
        b = float(available[baseline]["rmse_linear"])
        c = float(available[candidate]["rmse_linear"])
        rows.append({
            "path": str(path.relative_to(root)),
            "baseline_rmse": b,
            "candidate_rmse": c,
            "candidate_minus_baseline_rmse": c - b,
            "candidate_improves_rmse": bool(c < b),
            "baseline_mae": float(available[baseline]["mae_linear"]),
            "candidate_mae": float(available[candidate]["mae_linear"]),
        })
    deltas = [row["candidate_minus_baseline_rmse"] for row in rows]
    return {
        "region": region,
        "pixel_count": first["pixels"],
        "coverage": first["coverage"],
        "region_definition": definition,
        "mask_sha256": expected_mask_hash,
        "mask_provenance": "Exact ordered pixel membership verified by SHA-256; AOV source declared by caller",
        "baseline": baseline,
        "candidate": candidate,
        "input_seed_count": len(rows),
        "passes_raw_diversity_heuristic": True,
        "per_seed": rows,
        "mean_baseline_rmse": statistics.fmean(r["baseline_rmse"] for r in rows),
        "mean_candidate_rmse": statistics.fmean(r["candidate_rmse"] for r in rows),
        "mean_candidate_minus_baseline_rmse": statistics.fmean(deltas),
        "std_candidate_minus_baseline_rmse": statistics.pstdev(deltas),
        "candidate_improves_count": sum(r["candidate_improves_rmse"] for r in rows),
        "warning": (
            "Small fixed region, finite shared reference and few input seeds; "
            "not evidence of universal superiority or independent ground truth."
        ),
    }
