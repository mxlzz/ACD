"""AOV Emission input-only prototype, same frozen parameters in both seen scenes."""
from __future__ import annotations

import argparse,json
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.emission_guide import emission_guided_blend
from acd_lab.highlight_blend import blend_constant, blend_input_highlights
from acd_lab.hdr_tail import hdr_tail_breakdown
from acd_lab.io import read_arrays,write_report

SCENES={
    "CozyKitchen":("5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395",43289852695),
    "TerracedHouses":("37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84",43291659387),
}
METHODS=("Raw","OIDN","ACD_HIGH","AOV_EMISSION50","AOV_EMISSION100","MEAN_WEIGHT_CONTROL","RAW_BRIGHT100")


def evaluate_scene(name: str, root: Path) -> dict:
    meta=json.loads((root/"metadata.json").read_text())
    sha,run=SCENES[name]
    if meta.get("source_blend_sha256")!=sha or not meta.get("second_reference"):
        raise ValueError("Invalid input provenance")
    if not meta.get("capture_aov"):
        raise ValueError("Emission pass requires multilayer AOV captured")
    layer=meta["view_layer"]
    folders=[root]+sorted(p for p in root.glob("seed_*") if p.is_dir())
    source=[]
    for folder in folders:
        raw=read_arrays(folder/"acd_compare_Raw.exr")["image"]
        native=read_arrays(folder/"acd_compare_NATIVE_COMP_OIDN.exr")["image"]
        high=read_arrays(folder/"acd_compare_HIGH.exr")["image"]
        passes=read_arrays(folder/"raw_multilayer.exr",layer=layer)
        if "emission" not in passes:
            raise ValueError("Required Cycles emission pass missing from "+str(folder))
        emission=passes["emission"]
        half,half_stats=emission_guided_blend(raw,native,emission,max_raw_fraction=.5,scale=.25)
        full,full_stats=emission_guided_blend(raw,native,emission,max_raw_fraction=1.0,scale=.25)
        avg=blend_constant(raw,native,raw_fraction=full_stats["mean_raw_weight"])
        bright,_=blend_input_highlights(raw,native,max_raw_fraction=1.0)
        candidates={
            "Raw":raw,"OIDN":native,"ACD_HIGH":high,
            "AOV_EMISSION50":half,"AOV_EMISSION100":full,
            "MEAN_WEIGHT_CONTROL":avg,"RAW_BRIGHT100":bright,
        }
        source.append({"folder":folder,"outputs":candidates,"guide_stats":full_stats})
    by_reference={}
    for refname in ("reference.exr","reference_check.exr"):
        reference=read_arrays(root/refname)["image"]
        all_metrics={}
        for record in source:
            candidates=record["outputs"]
            raw=candidates["Raw"]
            high_ref=hdr_tail_breakdown(reference,raw,{k:v for k,v in candidates.items() if k!="Raw"})["masks"]["reference_brightest"]["methods"]
            for method in METHODS:
                image=candidates[method]
                overall=compare_images(reference,image)
                detail=detail_fidelity(reference,image)
                all_metrics.setdefault(method,[]).append({
                    "rmse_linear":overall["rmse_linear"],
                    "mae_linear":overall["mae_linear"],
                    "edge_gradient_rmse":detail["edge_gradient_rmse"],
                    "bright_ref_rmse":high_ref[method]["rmse_inside"],
                    "outside_bright_ref_rmse":high_ref[method]["rmse_outside"],
                })
        by_reference[refname]={
            method:{key:float(np.mean([m[key] for m in metrics]))
                    for key in metrics[0]} for method,metrics in all_metrics.items()
        }
    return {
        "scene":name,"sha":sha,"render_run":run,
        "resolution":meta["resolution"],"samples":meta["samples"],
        "ref_samples":meta["reference_samples"],"seed_count":len(source),
        "inference_parameters":{"emission_scale":.25,"max_raw_fraction":[.5,1.0],"raw_bright_control":[.97,.995,1.0]},
        "aov_emission_stats":[{"folder":r["folder"].name,**r["guide_stats"]} for r in source],
        "reference_scores":by_reference
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cozy",type=Path,required=True)
    ap.add_argument("--terraced",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    results={
        "CozyKitchen":evaluate_scene("CozyKitchen",args.cozy.resolve()),
        "TerracedHouses":evaluate_scene("TerracedHouses",args.terraced.resolve()),
    }
    output={
        "experiment":"E0027","rerender":False,
        "input_policy":"same-seed Raw/OIDN/Cycles emission AOV; no reference for blend",
        "not_heldout":True,
        "warning":"Both scenes observed before hypothesis. Do not infer generalization or integrate until unseen validation.",
        "results":results
    }
    write_report(args.output,output)
    for scene,result in results.items():
        print("ACD_E0027_SCENE",json.dumps({
            "scene":scene,
            "emission_guide":result["aov_emission_stats"]
        }))
        for ref,summary in result["reference_scores"].items():
            print("ACD_E0027_METRICS",scene,ref)
            for method in METHODS:
                row=summary[method]
                print(json.dumps({"method":method,**{k:round(v,8) for k,v in row.items()}},sort_keys=True))


if __name__=="__main__":
    main()
