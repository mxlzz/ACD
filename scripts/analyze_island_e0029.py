"""Frozen E0027 emission guide on an unseen (by denoiser) Cycles island scene."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.emission_guide import emission_guided_blend
from acd_lab.highlight_blend import blend_constant,blend_input_highlights
from acd_lab.hdr_tail import hdr_tail_breakdown
from acd_lab.io import read_arrays,write_report

EXPECTED_SHA="0fceb72489873a1ebbdf8210c435713e5fee1b3c58ffa4105187023f6896b701"
METHODS=("Raw","OIDN","HIGH","SUPER","EMISSION50","EMISSION100","CONSTANT","RAW_BRIGHT100")

def analyze(root):
    metadata=json.loads((root/"metadata.json").read_text())
    if metadata.get("source_blend_sha256")!=EXPECTED_SHA or not metadata.get("second_reference") or not metadata.get("capture_aov"):
        raise ValueError("Wrong source or missing two references or AOVs")
    folders=[root]+sorted(p for p in root.glob("seed_*") if p.is_dir())
    if len(folders)!=3: raise ValueError("Expected three independent seed files")
    prepared=[]
    for folder in folders:
        raw=read_arrays(folder/"acd_compare_Raw.exr")["image"]
        oidn=read_arrays(folder/"acd_compare_NATIVE_COMP_OIDN.exr")["image"]
        hi=read_arrays(folder/"acd_compare_HIGH.exr")["image"]
        sup=read_arrays(folder/"acd_compare_SUPER.exr")["image"]
        passes=read_arrays(folder/"raw_multilayer.exr",layer=metadata["view_layer"])
        if "emission" not in passes: raise ValueError("Missing same-seed emission AOV")
        if np.max(np.abs(raw[...,:3]-passes["image"][...,:3]))>1e-5:
            raise ValueError("Raw beauty differs from same-seed multilayer")
        half,_=emission_guided_blend(raw,oidn,passes["emission"],scale=.25,max_raw_fraction=.5)
        full,stat=emission_guided_blend(raw,oidn,passes["emission"],scale=.25,max_raw_fraction=1.)
        constant=blend_constant(raw,oidn,raw_fraction=stat["mean_raw_weight"])
        bright,_=blend_input_highlights(raw,oidn,max_raw_fraction=1.)
        prepared.append({"seed":folder.name,"emission":stat,"images":{
            "Raw":raw,"OIDN":oidn,"HIGH":hi,"SUPER":sup,
            "EMISSION50":half,"EMISSION100":full,"CONSTANT":constant,
            "RAW_BRIGHT100":bright}})
    audit=json.loads((root/"seed_aggregate.json").read_text())
    if audit.get("input_diversity_heuristic_passed") is not True:
        raise ValueError("Noisy seed diversity failed")
    refs={}
    for refname in ("reference.exr","reference_check.exr"):
        reference=read_arrays(root/refname)["image"]
        stats={m:[] for m in METHODS}
        for row in prepared:
            images=row["images"]
            br=hdr_tail_breakdown(reference,images["Raw"],{k:v for k,v in images.items() if k!="Raw"})["masks"]["reference_brightest"]["methods"]
            for name in METHODS:
                err=compare_images(reference,images[name]);grad=detail_fidelity(reference,images[name])
                stats[name].append({
                    "rmse":err["rmse_linear"],"mae":err["mae_linear"],
                    "edge_rmse":grad["edge_gradient_rmse"],
                    "bright_rmse":br[name]["rmse_inside"],
                    "outside_bright_rmse":br[name]["rmse_outside"]})
        refs[refname]={name:{key:float(np.mean([x[key] for x in stats[name]])) for key in stats[name][0]} for name in METHODS}
    ref1=read_arrays(root/"reference.exr")["image"]
    ref2=read_arrays(root/"reference_check.exr")["image"]
    return {"experiment":"E0029","scene_sha":EXPECTED_SHA,
            "seeds":len(folders),"input_spp":metadata["samples"],"reference_spp":metadata["reference_samples"],
            "resolution":metadata["resolution"],
            "reference_disagreement_rmse":compare_images(ref1,ref2)["rmse_linear"],
            "emission_stats":[{"seed":r["seed"],**r["emission"]} for r in prepared],
            "reference_metrics":refs,
            "parameters":{"scale":.25,"max_raw":[.5,1.0],"constant":"mean same-seed Emission100 weight"},
            "caveat":"Same creator as prior Terraced, finite references, no broader production validation. Frozen E0027 recipe not tuned."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyze(a.directory.resolve())
    write_report(a.output,result)
    print("E0029_METADATA",json.dumps({k:v for k,v in result.items() if k!="reference_metrics"}))
    for ref,values in result["reference_metrics"].items():
        print("E0029_REF",ref)
        for method in METHODS:
            print("E0029_RESULT",json.dumps({"method":method,**values[method]}))
if __name__=="__main__":main()
