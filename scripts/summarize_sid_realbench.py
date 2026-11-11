"""Honest pilot report: multiple noisy seeds, two finite spp references."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

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
    result={
        "scene":metadata["scene"],"resolution":metadata["resolution"],
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
        "seed_aggregate":json.loads(seed.read_text()),
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
                              "reference_disagreement_over_raw_error")},indent=2))

if __name__=="__main__": main()
