"""Honest pilot report: multiple noisy seeds, two finite spp references."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from acd_lab.core import compare_images
from acd_lab.io import read_arrays

NAMES=("Raw","STANDARD","HIGH","SUPER","SID4_STANDARD","SID4_HIGH",
       "SID4_SUPER","NATIVE_COMP_OIDN")

def summarize(path):
    metrics=json.loads((path/"metrics.json").read_text())
    metadata=json.loads((path/"metadata.json").read_text())
    missing=[key for key in NAMES if key not in metrics["measurements"]]
    if missing: raise ValueError("Missing candidates: "+repr(missing))
    audit=metrics["reference_quality_diagnostic"]
    if audit is None: raise ValueError("Need second reference for uncertainty")
    seed=path/"seed_aggregate.json"
    if not seed.is_file(): raise ValueError("Missing seed aggregation")
    seed_report=json.loads(seed.read_text())
    pairings=(("STANDARD","NATIVE_COMP_OIDN"),("HIGH","SID4_HIGH"),
              ("SUPER","SID4_SUPER"),("STANDARD_emission_preserved","STANDARD"))
    direct_pair_differences={}
    for a,b in pairings:
        left=path/("acd_compare_"+a+".exr")
        right=path/("acd_compare_"+b+".exr")
        if left.is_file() and right.is_file():
            direct_pair_differences[a+"_vs_"+b]=compare_images(
                read_arrays(left)["image"],read_arrays(right)["image"])
    validity={
        "input_seed_diversity_passed":bool(seed_report["input_diversity_heuristic_passed"]),
        "references_almost_identical":bool(audit["almost_identical_reference_images"]),
        "large_reference_discrepancy":bool(audit["large_reference_discrepancy_alert"]),
        "suitable_for_exploratory_quality_ranking":bool(
            seed_report["input_diversity_heuristic_passed"]
            and not audit["almost_identical_reference_images"]
            and not audit["large_reference_discrepancy_alert"]),
        "convergence_proven":False,
    }
    result={
        "scene":metadata["scene"],
        "source_blend_sha256":metadata.get("source_blend_sha256"),
        "color_management":metadata.get("color_management"),
        "validity":validity,
        "direct_method_pair_differences":direct_pair_differences,"resolution":metadata["resolution"],
        "low_spp":metadata["samples"],"reference_spp_each":metadata["reference_samples"],
        "noisy_seeds":[metadata["seed"]]+metadata["extra_input_seeds"],
        "reference_seeds":[metadata["reference_seed"],metadata["second_reference_seed"]],
        "ranking_ref1":metrics["rank_by_rmse"],
        "ranking_ref2":metrics["rank_against_second_reference"],
        "reference_ranking_consistent":metrics["reference_ranking_consistent"],
        "reference_disagreement_rmse":audit["pair_difference"]["rmse_linear"],
        "reference_disagreement_over_raw_error":audit["reference_disagreement_over_raw_error"],
        "reference_convergence_proven":audit["convergence_proven"],
        "methods":{key:{
            "rmse":metrics["measurements"][key]["rmse_linear"],
            "mae":metrics["measurements"][key]["mae_linear"],
            "log_luma_rmse":metrics["measurements"][key]["log1p_luminance_rmse"],
        } for key in NAMES},
        "seed_aggregate":seed_report,
        "scope":"Pilot only; this cannot prove reference convergence or universal quality",
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=summarize(args.directory)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print("M3.9 REAL SCENE SUMMARY",json.dumps({
        k:result[k] for k in ("scene","ranking_ref1","ranking_ref2",
                              "reference_disagreement_over_raw_error","validity")},indent=2))

if __name__=="__main__": main()
