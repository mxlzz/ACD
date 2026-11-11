"""Aggregate repeated noisy input seeds against shared independent references.

Descriptive estimates only: the references and scene are common to all seeds,
so bootstrap or t-test significance assumptions should not be inferred.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path


METRICS = ("rmse_linear", "mae_linear", "log1p_luminance_rmse", "pixel_rmse_p95")


def aggregate_seed_reports(directory: str | Path) -> dict:
    root = Path(directory)
    paths = [root / "metrics.json"] + sorted(root.glob("seed_*/metrics.json"))
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing seed metrics: {missing}")
    if len(paths) < 2:
        raise ValueError("Need at least two separate input-seed reports")
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    methods = sorted(set.intersection(*(set(report["measurements"]) for report in reports)))
    if not methods:
        raise ValueError("No comparable candidate methods across input seeds")
    per_method = {}
    for method in methods:
        per_method[method] = {}
        for metric in METRICS:
            values = [
                float(report["measurements"][method][metric]) for report in reports
            ]
            per_method[method][metric] = {
                "mean": statistics.fmean(values),
                "population_std": statistics.pstdev(values),
                "per_seed": values,
            }

    return {
        "input_seed_count": len(paths),
        "input_report_paths": [str(p.relative_to(root)) for p in paths],
        "warning": (
            "Exploratory: same scene and shared finite-spp references for every seed. "
            "Uncertainty of reference and other scenes is not sampled by this aggregate."
        ),
        "methods": per_method,
        "rank_by_mean_rmse": sorted(
            methods, key=lambda name: per_method[name]["rmse_linear"]["mean"]
        ),
        "rank_by_mean_mae": sorted(
            methods, key=lambda name: per_method[name]["mae_linear"]["mean"]
        ),
        "rank_by_mean_log1p_luminance": sorted(
            methods, key=lambda name: per_method[name]["log1p_luminance_rmse"]["mean"]
        ),
        "seed_rmse_wins": {
            method: sum(
                method == min(
                    methods,
                    key=lambda name: report["measurements"][name]["rmse_linear"],
                )
                for report in reports
            )
            for method in methods
        },
    }
