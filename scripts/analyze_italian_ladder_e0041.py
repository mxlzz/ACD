"""E0041 diagnostics of independent finite-spp reference disagreement.

Two sources per sample count measure inter-seed spread. They do not prove
Monte Carlo independence, unbiasedness or convergence to truth.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np

from acd_lab.core import compare_images, rgb
from acd_lab.io import read_arrays, write_report

SPP=(8,16,32)
SEEDS=(8819,8922)


def summarize_pairs(pairs:dict[int,tuple[np.ndarray,np.ndarray]]):
    result={}
    previous=None
    for spp in SPP:
        if spp not in pairs:raise ValueError("Missing sample count")
        x,y=(rgb(a) for a in pairs[spp])
        if x.shape!=y.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("Misaligned or nonfinite reference matrices")
        if x.shape[:2] != (200,320):
            raise ValueError("Incorrect pre-registered resolution")
        discrepancy=compare_images(x,y)
        rmse=float(discrepancy["rmse_linear"])
        result[str(spp)]={
            "interseed_difference":discrepancy,
            "identical_references":bool(np.array_equal(x,y)),
            "ratio_to_previous_spp":rmse/previous if previous is not None and previous>0 else None,
        }
        previous=rmse
    return result


def analyze(root):
    manifest=json.loads((root/"e0041_render_manifest.json").read_text())
    if (manifest.get("source_sha256")!="0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25"
        or manifest.get("camera_name")!="Cam Kitchen Table"
        or manifest.get("adaptive_sampling") is not False
        or manifest.get("denoising") is not False):
        raise ValueError("Wrong E0041 source/camera/protocol")
    entries=manifest["results"]
    expected={(w,h,spp,seed) for w,h,spp,seed in
        [(320,200,spp,seed) for spp in SPP for seed in SEEDS] + [(640,400,8,8819)]}
    actual={(x["resolution"][0],x["resolution"][1],x["samples"],x["seed"]) for x in entries}
    if expected!=actual or len(entries)!=len(expected):
        raise ValueError("Wrong or duplicate E0041 render grid")
    pairs={}
    for spp in SPP:
        images=[]
        for seed in SEEDS:
            entry=next(x for x in entries if x["resolution"]==[320,200]
                       and x["samples"]==spp and x["seed"]==seed)
            image=read_arrays(root/entry["file"])["image"]
            images.append(image)
        pairs[spp]=tuple(images)
    spread=summarize_pairs(pairs)
    def seconds(w,h,spp,seed):
        return next(x["render_and_write_wall_seconds"] for x in entries
                    if x["resolution"]==[w,h] and x["samples"]==spp and x["seed"]==seed)
    ratio=seconds(640,400,8,8819)/seconds(320,200,8,8819)
    return {
        "experiment":"E0041","source":manifest["source"],"source_sha256":manifest["source_sha256"],
        "camera":manifest["camera_name"],"blender":manifest["blender"],
        "sampling_method":"Cycles independent seeds 8819/8922, adaptive OFF, CPU, no denoising",
        "reference_interseed_by_spp":spread,
        "render_manifest":manifest["results"],
        "resolution_time_ratio_640x400_vs_320x200_at_8spp":float(ratio),
        "independent_sampling_proven":False,"reference_convergence_proven":False,
        "quality_ranking_performed":False,
        "interpretation":"Interseed RMSE should generally decrease with higher spp, but non-monotonicity and correlation are possible. This finite low-res pilot cannot certify convergence or extrapolate render cost accurately to 1080p."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=analyze(args.directory)
    write_report(args.output,result)
    print("ACD_E0041_SPREAD",json.dumps({
        "rmse":{k:result["reference_interseed_by_spp"][k]["interseed_difference"]["rmse_linear"]
                for k in ("8","16","32")},
        "pixel_scaling_ratio":result["resolution_time_ratio_640x400_vs_320x200_at_8spp"],
    },sort_keys=True))


if __name__=="__main__":main()
