"""Exploratory postprocess comparison on existing two seen scenes; no rerender.

All candidate weights from Raw only. Reference appears exclusively in scoring.
This is not held-out validation: both scenes were previously examined.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.hdr_tail import hdr_tail_breakdown
from acd_lab.highlight_blend import blend_input_highlights,blend_constant
from acd_lab.io import read_arrays, write_report

SCENES = {
    "CozyKitchen": {"sha":"5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395",
                    "run":43289852695, "license":"CC BY-SA (Nicole Morena)"},
    "TerracedHouses": {"sha":"37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84",
                      "run":43291659387, "license":"MIT (Yunus Emre Karaman)"},
}
ORDER=("Raw","OIDN","ACD_HIGH","ACD_SUPER","FIXED10","FIXED50","RAW_BRIGHT50","RAW_BRIGHT100")


def analyze_scene(name: str, root: Path) -> dict:
    meta=json.loads((root/"metadata.json").read_text())
    config=SCENES[name]
    if meta.get("source_blend_sha256") != config["sha"]:
        raise ValueError("Fixture mismatch on "+name)
    if not meta.get("second_reference"):
        raise ValueError("Need 2 high-spp references")
    seeds=[root]+sorted(p for p in root.glob("seed_*") if p.is_dir())
    by_reference={}
    for refname in ("reference.exr","reference_check.exr"):
        ref=read_arrays(root/refname)["image"]
        results={}
        raw_weights=[]
        for seed_dir in seeds:
            raw=read_arrays(seed_dir/"acd_compare_Raw.exr")["image"]
            denoised=read_arrays(seed_dir/"acd_compare_NATIVE_COMP_OIDN.exr")["image"]
            high=read_arrays(seed_dir/"acd_compare_HIGH.exr")["image"]
            sup=read_arrays(seed_dir/"acd_compare_SUPER.exr")["image"]
            local_half,weight_half=blend_input_highlights(raw,denoised,max_raw_fraction=.5)
            local_full,weight_full=blend_input_highlights(raw,denoised,max_raw_fraction=1.0)
            raw_weights.append({"seed":seed_dir.name,"half":weight_half,"full":weight_full})
            imgs={
                "Raw":raw, "OIDN":denoised, "ACD_HIGH":high,"ACD_SUPER":sup,
                "FIXED10":blend_constant(raw,denoised,raw_fraction=.1),
                "FIXED50":blend_constant(raw,denoised,raw_fraction=.5),
                "RAW_BRIGHT50":local_half, "RAW_BRIGHT100":local_full,
            }
            detail_masks=hdr_tail_breakdown(ref,raw,{
                key:img for key,img in imgs.items() if key != "Raw"
            })["masks"]["reference_brightest"]["methods"]
            for method in ORDER:
                image=imgs[method]
                metric=compare_images(ref,image)
                grad=detail_fidelity(ref,image)
                rec={
                    "rmse_linear":metric["rmse_linear"],
                    "mae_linear":metric["mae_linear"],
                    "edge_gradient_rmse":grad["edge_gradient_rmse"],
                    "flat_gradient_rmse":grad["flat_gradient_rmse"],
                    "bright_ref_rmse":detail_masks[method]["rmse_inside"],
                    "outside_bright_ref_rmse":detail_masks[method]["rmse_outside"],
                    "bright_ref_sse_fraction":detail_masks[method]["sse_fraction_inside"],
                }
                results.setdefault(method,[]).append(rec)
        summary={
            method:{
                field:float(np.mean([r[field] for r in rows]))
                if all(r[field] is not None for r in rows) else None
                for field in rows[0]
            } for method,rows in results.items()
        }
        by_reference[refname]={
            "scores":summary,
            "per_seed":results,
            "raw_only_weights":raw_weights,
        }
    return {
        "scene":name, "original_scene_sha":config["sha"],
        "original_render_run":config["run"],"license":config["license"],
        "width_height":meta["resolution"], "input_samples":meta["samples"],
        "reference_samples":meta["reference_samples"],
        "seed_count":len(seeds), "second_reference":True,
        "variants":{
            "RAW_BRIGHT50":"Raw-luminance quantile 0.97->0.995 smoothstep, max raw weight 0.5",
            "RAW_BRIGHT100":"Same quantiles, max raw weight 1.0",
            "FIXED10":"Global weight Raw 0.1 (control)",
            "FIXED50":"Global weight Raw 0.5 (control)"
        },
        "reference_scores":by_reference,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cozy",required=True,type=Path)
    p.add_argument("--terraced",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    scenes={
        "CozyKitchen":analyze_scene("CozyKitchen",args.cozy.resolve()),
        "TerracedHouses":analyze_scene("TerracedHouses",args.terraced.resolve()),
    }
    output={
        "experiment":"E0026", "no_rerender":True,
        "fixed_inference_parameters":True,
        "scenes_examined_before_experiment":True,
        "not_heldout":True, "results":scenes,
        "warning":"No algorithmic superiority claimed. Both scenes observed before selecting hypotheses. Source reference masks used only for scoring; raw thresholds used only at inference. Requires third unseen scene.",
    }
    write_report(args.output,output)
    for scene,group in scenes.items():
        for ref,ref_group in group["reference_scores"].items():
            print("ACD_E0026_RESULT",scene,ref)
            for method in ORDER:
                s=ref_group["scores"][method]
                print(json.dumps({"method":method,**{
                    k:round(s[k],8) if s[k] is not None else None
                    for k in ("rmse_linear","mae_linear","edge_gradient_rmse",
                              "bright_ref_rmse","outside_bright_ref_rmse")
                }},sort_keys=True))


if __name__=="__main__":
    main()
