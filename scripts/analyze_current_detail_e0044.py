"""E0044 — current OIDN architectural-detail diagnosis, NOT a new filter.

One Blender 5.2.4 24-spp noisy input; 2 independent 1024-spp
references. Compare Raw vs native compositor OIDN and predeclared
non-overlapping 4x3 tiles. Results are descriptive, not visual quality proof.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import hashlib
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays, write_report

METHODS=("Raw","NATIVE_COMP_OIDN")
EXPECTED_VERSION="5.2.4"

def score_arrays(images, references):
    a,b=(rgb(x) for x in references)
    if a.shape!=(240,320,3) or b.shape!=a.shape:
        raise ValueError("References must be 320x240")
    if set(images)!=set(METHODS):
        raise ValueError("Only native OIDN vs Raw, no other candidate")
    if any(rgb(v).shape!=a.shape for v in images.values()):
        raise ValueError("Output shapes differ from references")
    whole={
        name:{f"ref{index+1}":{
            "color":compare_images(ref,image),
            "detail":detail_fidelity(ref,image)}
            for index,ref in enumerate((a,b))}
        for name,image in images.items()
    }
    tiles=[]
    for y in range(3):
        for x in range(4):
            sl=(slice(y*80,(y+1)*80),slice(x*80,(x+1)*80))
            refs=(a[sl],b[sl])
            native=rgb(images["NATIVE_COMP_OIDN"])[sl]
            raw=rgb(images["Raw"])[sl]
            rows=[]
            for ref in refs:
                native_d=detail_fidelity(ref,native)
                raw_d=detail_fidelity(ref,raw)
                rows.append({
                    "native_hdr_rmse":compare_images(ref,native)["rmse_linear"],
                    "raw_hdr_rmse":compare_images(ref,raw)["rmse_linear"],
                    "native_edge_gradient_rmse":native_d["edge_gradient_rmse"],
                    "raw_edge_gradient_rmse":raw_d["edge_gradient_rmse"],
                    "native_edge_contrast_ratio":native_d["edge_contrast_ratio"]})
            tiles.append({
                "xywh":[x*80,y*80,80,80],
                "ref_disagreement_rmse":compare_images(refs[0],refs[1])["rmse_linear"],
                "against_refs":rows,
                "requires_visual_review":(
                    all(r["native_edge_contrast_ratio"] is not None
                        and r["native_edge_contrast_ratio"]<0.75
                        for r in rows)
                ),
            })
    return {
        "reference_disagreement":compare_images(a,b),
        "whole_image":whole,
        "tiles":tiles,
        "potential_low_edge_contrast_tiles":[r["xywh"] for r in tiles
                                             if r["requires_visual_review"]],
        "selection_is_predeclared":True,
        "warnings":[
            "Edge contrast below 0.75 is a screening threshold, not proof of blur or ground-truth geometry.",
            "Reference gradients include 1024-spp sampling noise; independence and convergence unproven.",
            "Do not infer version causality from E0016: source ray samples and denoising passes may differ."
        ]
    }

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for p in iter(lambda:f.read(1024*1024),b""):h.update(p)
    return h.hexdigest()

def run(root,output):
    m=json.loads((root/"metadata.json").read_text())
    if (not m["blender"].startswith(EXPECTED_VERSION)
        or m["scene"]!="detail_target"
        or m["resolution"]!=[320,240]
        or m["seed"]!=539 or m["samples"]!=24
        or m["reference_seed"]!=8819
        or m["reference_samples"]!=1024
        or m["second_reference"] is not True
        or m["cycles"]["use_adaptive_sampling"] is not False
        or m["cycles"]["use_denoising"] is not False
        or m["capture_aov"] is not True):
        raise ValueError("E0044 source/config contract failed")
    images={n:rgb(read_arrays(root/f"acd_compare_{n}.exr")["image"]) for n in METHODS}
    first=rgb(read_arrays(root/"reference.exr")["image"])
    second=rgb(read_arrays(root/"reference_check.exr")["image"])
    aov=read_arrays(root/"raw_multilayer.exr",layer=m["view_layer"])
    if float(np.max(np.abs(images["Raw"]-rgb(aov["image"]))))>1e-5:
        raise ValueError("Noisy Raw not equal to captured multilayer beauty")
    if not {"denoising_normal","denoising_albedo"}.issubset(aov):
        raise ValueError("Denoising guides missing")
    measurements=score_arrays(images,(first,second))
    result={
        "experiment":"E0044","classification":"targeted real Blender5.2.4 detail failure diagnostic",
        "metadata":m,"current_blender":m["blender"],"methods":list(METHODS),
        "source":"fully procedural 52 slats + tile joints + glass + microbump, no external assets",
        "old_e0016_descriptive_baseline":{"blender":"5.0.1","oidn_hdr_rmse":0.0608849,
            "oidn_edge_gradient_rmse":0.0721193,
            "warning":"different source renders and different seeds aggregate: do not measure backend quality delta"},
        **measurements,
        "source_exr_sha256":{p.name:sha(p) for p in root.glob("*.exr")},
        "new_algorithm_tested":False,
        "convergence_proven":False,
    }
    output.mkdir(parents=True,exist_ok=True)
    write_report(output/"E0044_RESULTS.json",result)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    ordered=[
        ("24spp Raw",images["Raw"]),
        ("OIDN native 5.2.4",images["NATIVE_COMP_OIDN"]),
        ("1024spp reference 1",first),
        ("1024spp reference 2",second),
    ]
    out=Image.new("RGB",(2*320+36,2*(240+30)+24),(24,24,24))
    draw=ImageDraw.Draw(out)
    for i,(name,im) in enumerate(ordered):
        x=12+(i%2)*(320+12)
        y=12+(i//2)*(240+30+12)
        out.paste(Image.fromarray(display_rgb(im)),(x,y+28))
        draw.text((x+3,y+8),name,fill=(245,245,245))
    out.save(output/"e0044_reference_comparison.png",optimize=True)
    print("E0044_DETAIL_DIAGNOSTIC",json.dumps({
        "blender":m["blender"],
        "reference_spread":result["reference_disagreement"]["rmse_linear"],
        "oidn_ref_rmse":[result["whole_image"]["NATIVE_COMP_OIDN"][f"ref{n}"]["color"]["rmse_linear"] for n in (1,2)],
        "edge_ratio":[result["whole_image"]["NATIVE_COMP_OIDN"][f"ref{n}"]["detail"]["edge_contrast_ratio"] for n in (1,2)],
        "regions_for_visual_review":len(result["potential_low_edge_contrast_tiles"])},sort_keys=True))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.directory,a.output)
if __name__=="__main__":main()
