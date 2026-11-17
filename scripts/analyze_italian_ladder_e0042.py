"""E0042 evaluate finite reference spread at 640px and create viewable gallery."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images, rgb
from acd_lab.io import read_arrays, write_report

SAMPLES=(32,64,128)
SEEDS=(8819,8922)

def evaluate_arrays(pairs):
    result={}
    prior=None
    for s in SAMPLES:
        if s not in pairs: raise ValueError("Missing sample level")
        a,b=(rgb(x) for x in pairs[s])
        if a.shape!=b.shape or a.shape[:2]!=(400,640):
            raise ValueError("Reference shape not pinned")
        if not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError("Nonfinite HDR input")
        difference=compare_images(a,b)
        spread=float(difference["rmse_linear"])
        result[str(s)]={"interseed_metrics":difference,"exact_match":bool(np.array_equal(a,b)),
                        "spread_ratio_to_previous":spread/prior if prior is not None and prior>0 else None}
        prior=spread
    return result

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def analyze(root,out):
    meta=json.loads((root/"e0042_manifest.json").read_text())
    if (meta["source_sha256"]!="0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25"
        or meta["camera"]!="Cam Kitchen Table" or meta["resolution"]!=[640,400]
        or meta["denoising"] is not False or meta["adaptive_sampling"] is not False):
        raise ValueError("E0042 source/protocol invalid")
    expected={(s,p) for s in SAMPLES for p in SEEDS}
    actual={(row["spp"],row["seed"]) for row in meta["entries"]}
    if expected!=actual or len(meta["entries"])!=len(expected):
        raise ValueError("Incomplete/duplicate E0042 render grid")
    all_images={}
    pairs={}
    for spp in SAMPLES:
        arrays=[]
        for seed in SEEDS:
            row=next(r for r in meta["entries"] if r["spp"]==spp and r["seed"]==seed)
            file=root/row["file"]
            if digest(file)!=row["file_sha256"]:
                raise ValueError("EXR digest changed for "+file.name)
            value=read_arrays(file)["image"]
            arrays.append(value)
            all_images[(spp,seed)]=value
        pairs[spp]=tuple(arrays)
    scores=evaluate_arrays(pairs)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    target=out/"gallery"
    target.mkdir(parents=True,exist_ok=True)
    w,h=640,400
    border,labelheight=12,32
    sheet=Image.new("RGB",(3*(w+border)+border,2*(h+labelheight+border)+border),(27,27,27))
    draw=ImageDraw.Draw(sheet)
    for idx,spp in enumerate(SAMPLES):
        for row,seed in enumerate(SEEDS):
            patch=Image.fromarray(display_rgb(all_images[(spp,seed)]))
            x=border+idx*(w+border)
            y=border+row*(h+labelheight+border)
            sheet.paste(patch,(x,y+labelheight))
            draw.text((x+3,y+8),f"{spp} spp / seed {seed}",fill=(240,240,240))
    sheet.save(target/"italian_reference_ladder.png",optimize=True)
    data={
        "experiment":"E0042","source":"Italian Flat / CC-BY / original not distributed",
        "blender":meta["blender"],"camera":meta["camera"],
        "spp":list(SAMPLES),"seeds":list(SEEDS),
        "reference_pairs":scores,"renders":meta["entries"],
        "cpu_total_wall_seconds":float(sum(r["wall_seconds"] for r in meta["entries"])),
        "peak_process_rss_kb":max(r["process_peak_rss_kb"] for r in meta["entries"]),
        "viewer":"gallery/italian_reference_ladder.png",
        "viewer_transfer":"Shared HDR diagnostic transform from existing ACD display_rgb, NOT Blender OCIO/AgX",
        "reference_convergence_proven":False,
        "quality_evaluation_performed":False,
        "caveat":"Two seeds per sample level insufficient to prove sample stream independence, unbiasedness or convergence. The 128 spp images are not ground truth; no denoiser rankings."
    }
    write_report(out/"e0042_results.json",data)
    print("ACD_E0042_PAIRS",json.dumps({
        k:v["interseed_metrics"]["rmse_linear"] for k,v in scores.items()},sort_keys=True))
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    analyze(args.directory,args.output)

if __name__=="__main__":main()
