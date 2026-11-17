"""E0033: fixed E0027 emission gating on independent-author Modern Hall Cycles EXRs.

All inputs and AOVs must come from the same seed. References are never used
to compute an inference weight. This reports quantitative metrics, not a
perceptual assessment and not a claim of reference convergence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from acd_lab.core import compare_images, rgb
from acd_lab.detail import detail_fidelity
from acd_lab.emission_guide import emission_guided_blend
from acd_lab.hdr_tail import hdr_tail_breakdown
from acd_lab.highlight_blend import blend_constant
from acd_lab.io import read_arrays, write_report

SOURCE_SHA256 = "b35b6694eb231d0d4d5d9ee9bbe63122218183fd519a05c7d5db0e62cbdaeca1"
METHODS = ("Raw", "OIDN", "STANDARD", "ACD High", "ACD Super",
           "Emission50", "Emission100", "ConstantMatched50")
METRICS = ("rmse_hdr", "mae_hdr", "edge_gradient_rmse",
           "brightest_1pct_rmse", "outside_brightest_1pct_rmse")


def build_candidates(raw, oidn, standard, high, super_image, emission):
    """Inference only: the same-seed noisy beauty, OIDN, and emission AOV."""
    half, stat50 = emission_guided_blend(
        raw, oidn, emission, scale=0.25, max_raw_fraction=0.5
    )
    full, stat100 = emission_guided_blend(
        raw, oidn, emission, scale=0.25, max_raw_fraction=1.0
    )
    constant = blend_constant(raw, oidn, raw_fraction=stat50["mean_raw_weight"])
    return {
        "Raw": raw,
        "OIDN": oidn,
        "STANDARD": standard,
        "ACD High": high,
        "ACD Super": super_image,
        "Emission50": half,
        "Emission100": full,
        "ConstantMatched50": constant,
    }, {"Emission50": stat50, "Emission100": stat100}


def score_against_reference(reference, images):
    raw = images["Raw"]
    highlights = hdr_tail_breakdown(
        reference, raw, {key: img for key, img in images.items() if key != "Raw"},
        top_fraction=0.01
    )["masks"]["reference_brightest"]["methods"]
    scores = {}
    for name, image in images.items():
        basic = compare_images(reference, image)
        edge = detail_fidelity(reference, image)
        scores[name] = {
            "rmse_hdr": basic["rmse_linear"],
            "mae_hdr": basic["mae_linear"],
            "edge_gradient_rmse": edge["edge_gradient_rmse"],
            "brightest_1pct_rmse": highlights[name]["rmse_inside"],
            "outside_brightest_1pct_rmse": highlights[name]["rmse_outside"],
        }
    return scores


def analyze(root: Path):
    meta = json.loads((root / "metadata.json").read_text())
    if (meta.get("source_blend_sha256") != SOURCE_SHA256
            or not meta.get("second_reference")
            or not meta.get("capture_aov")):
        raise ValueError("Wrong immutable scene source or missing refs/AOV")
    folders = [root] + sorted(path for path in root.glob("seed_*") if path.is_dir())
    if len(folders) != 3:
        raise ValueError("E0033 requires 3 distinct noisy seed outputs")
    if meta.get("samples") != 24 or meta.get("reference_samples") != 1024:
        raise ValueError("Unexpected sampling protocol, do not compare")
    audit = json.loads((root / "seed_aggregate.json").read_text())
    first = read_arrays(root / "reference.exr")["image"]
    second = read_arrays(root / "reference_check.exr")["image"]
    refs = {"ref1": first, "ref2": second}
    observations = {label: {name: [] for name in METHODS} for label in refs}
    emission_stats = []
    for folder in folders:
        read = lambda name: read_arrays(folder / ("acd_compare_" + name + ".exr"))["image"]
        raw, oidn = read("Raw"), read("NATIVE_COMP_OIDN")
        standard, high, super_image = read("STANDARD"), read("HIGH"), read("SUPER")
        layer = read_arrays(folder / "raw_multilayer.exr", layer=meta["view_layer"])
        if "emission" not in layer:
            raise ValueError("Cycles Emission AOV required, even if all zero")
        mismatch = np.max(np.abs(rgb(raw) - rgb(layer["image"])))
        if mismatch > 1e-5:
            raise ValueError("Same seed Raw beauty does not match multilayer")
        images, stats = build_candidates(
            raw, oidn, standard, high, super_image, layer["emission"]
        )
        emission_stats.append({"seed": folder.name, "aov_raw_delta_max": float(mismatch),
                               **stats})
        for label, reference in refs.items():
            scored = score_against_reference(reference, images)
            for name, numbers in scored.items():
                observations[label][name].append(numbers)
    results = {
        label: {
            name: {metric: float(np.mean([row[metric] for row in numbers]))
                   for metric in METRICS}
            for name, numbers in methodrows.items()
        } for label, methodrows in observations.items()
    }
    return {
        "experiment": "E0033", "source_blend_sha256": SOURCE_SHA256,
        "source_license": "Origin Modern Hall by NewSee2l035, CC BY 3.0; intermediary conversion cuteday/Bitterli; binary NOT republished",
        "samples": meta["samples"], "reference_samples": meta["reference_samples"],
        "seeds": 3, "resolution": meta["resolution"],
        "reference_disagreement_rmse": compare_images(first, second)["rmse_linear"],
        "input_seed_diversity_heuristic_passed":
            bool(audit.get("input_diversity_heuristic_passed")),
        "convergence_proven": False,
        "emission_aov_stats_by_seed": emission_stats,
        "frozen_inference": {"scale": 0.25, "max_raw_fraction": [0.5, 1.0],
                             "constant_control": "same-seed Emission50 mean Raw weight"},
        "first_and_second_reference_mean_metrics_over_three_seeds": results,
        "caveat": "New artist versus E0023/E0029. Finite sample references and heuristic seed diversity; quality requires visual inspection at scale. The emitted results are not an endorsement of any denoiser.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    report = analyze(args.directory.resolve())
    write_report(args.output, report)
    print("E0033_VERIFIED_ANALYSIS", json.dumps({
        "source_sha256": report["source_blend_sha256"],
        "resolution": report["resolution"],
        "seed_diversity": report["input_seed_diversity_heuristic_passed"],
        "reference_disagreement_rmse": report["reference_disagreement_rmse"],
        "metrics": report["first_and_second_reference_mean_metrics_over_three_seeds"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()
