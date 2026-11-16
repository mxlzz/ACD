"""E0046 — architectural slat contrast at production pixel density.

Blender full-frame 1920x1440, actual 512x512 crop (with pixel-perfect
camera FOV), evaluate 320x320 interior only. Existing native OIDN vs Raw.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays, write_report

RECT=[928,320,512,512]
INNER=[96,96,320,320]
METHODS=("Raw","NATIVE_COMP_OIDN")

def sha(file):
    h=hashlib.sha256()
    with file.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def evaluate(images,refs):
    if len(refs)!=2:raise ValueError("Two references required")
    if set(images)!=set(METHODS):raise ValueError("Expected only Raw and native OIDN")
    if any(rgb(a).shape!=(512,512,3) for a in [*images.values(),*refs]):
        raise ValueError("Crop must physically have exactly 512x512 pixels")
    if any(not np.isfinite(rgb(a)).all() for a in [*images.values(),*refs]):
        raise ValueError("NaN or Inf in image")
    x,y,w,h=INNER
    sl=(slice(y,y+h),slice(x,x+w))
    centered={k:rgb(v)[sl] for k,v in images.items()}
    reference=[rgb(a)[sl] for a in refs]
    measurements={
        method:{
            f"ref{i+1}":{
                "color":compare_images(ref,im),
                "detail":detail_fidelity(ref,im)
            } for i,ref in enumerate(reference)
        } for method,im in centered.items()
    }
    quadrants=[]
    for j in range(2):
        for i in range(2):
            crop=(slice(j*160,(j+1)*160),slice(i*160,(i+1)*160))
            refsm=[a[crop] for a in reference]
            oidn=centered["NATIVE_COMP_OIDN"][crop]
            raw=centered["Raw"][crop]
            quadrants.append({
                "xywh_relative_interior":[i*160,j*160,160,160],
                "reference_pair_rmse":compare_images(refsm[0],refsm[1])["rmse_linear"],
                "native_rmse":[compare_images(ref,oidn)["rmse_linear"] for ref in refsm],
                "raw_rmse":[compare_images(ref,raw)["rmse_linear"] for ref in refsm],
                "native_edge_ratio":[detail_fidelity(ref,oidn)["edge_contrast_ratio"] for ref in refsm],
                "native_edge_rmse":[detail_fidelity(ref,oidn)["edge_gradient_rmse"] for ref in refsm],
            })
    return {
        "full_interior_metrics":measurements,
        "reference_pair_difference":compare_images(reference[0],reference[1]),
        "quadrants":quadrants,
        "crop_xywh":RECT,"evaluation_interior_xywh":INNER,
        "convergence_proven":False,
        "denoiser_border_effects_eliminated":False,
        "warnings":[
            "512spp references are finite and might be noisy/correlated.",
            "OIDN receives cropped image; 96px margin reduces but cannot prove absence of receptive-field border effects.",
            "Edge-gradient strength is not proof of true geometry reconstruction."
        ]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--directory",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    root=args.directory
    meta=json.loads((root/"metadata.json").read_text())
    crop=meta.get("e0046_crop")
    if (not meta["blender"].startswith("5.2.4")
        or meta["scene"]!="detail_target"
        or meta["resolution"]!=[1920,1440]
        or meta["seed"]!=539 or meta["samples"]!=24
        or meta["reference_seed"]!=8819
        or meta["reference_samples"]!=512 or not meta["second_reference"]
        or not meta["capture_aov"]
        or meta["cycles"]["use_denoising"] is not False
        or meta["cycles"]["use_adaptive_sampling"] is not False
        or not crop or crop["top_left_origin_rect"]!=RECT
        or crop["evaluation_interior_xywh"]!=INNER):
        raise ValueError("E0046 camera/border/sampling contract violated")
    imgs={name:rgb(read_arrays(root/f"acd_compare_{name}.exr")["image"]) for name in METHODS}
    refs=[rgb(read_arrays(root/name)["image"]) for name in ("reference.exr","reference_check.exr")]
    aov=read_arrays(root/"raw_multilayer.exr",layer=meta["view_layer"])
    if np.max(np.abs(imgs["Raw"]-rgb(aov["image"])))>1e-5:
        raise ValueError("Raw and same-seed multilayer AOV not identical")
    if not {"denoising_albedo","denoising_normal"}.issubset(aov):
        raise ValueError("Guides absent from source EXR")
    d=evaluate(imgs,refs)
    args.output.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    x,y,w,h=INNER
    rows=[
        ("Raw 24spp",imgs["Raw"]),
        ("OIDN 5.2.4",imgs["NATIVE_COMP_OIDN"]),
        ("Ref 512spp A",refs[0]),
        ("Ref 512spp B",refs[1])
    ]
    gallery=Image.new("RGB",(2*w+36,2*(h+30)+24),(26,26,26))
    pen=ImageDraw.Draw(gallery)
    for n,(name,array) in enumerate(rows):
        px=12+(n%2)*(w+12)
        py=12+(n//2)*(h+30+12)
        patch=Image.fromarray(display_rgb(array[y:y+h,x:x+w]))
        gallery.paste(patch,(px,py+28))
        pen.text((px+4,py+6),name,fill=(248,248,248))
    gallery.save(args.output/"e0046_cropped_slats_1to1.png",optimize=True)
    result={
        "experiment":"E0046",
        "classification":"real Blender 5.2.4 targeted crop, physically resolvable slat pitch",
        "source_metadata":meta,
        "output_sha256":{p.name:sha(p) for p in sorted(root.glob("*.exr"))},
        "geometry_projection":"E0045 full-frame slat pitch min7.825px at 1920px width",
        **d,
        "not_a_quality_ranking":True,
        "algorithm_modified":False,
        "next_decision":"Investigate optical path behind glass only on visibly coherent losses exceeding reference uncertainty; else stop rather than tuning."
    }
    write_report(args.output/"E0046_RESULTS.json",result)
    print("E0046_CROPPED_FIDELITY",json.dumps({
        "blender":meta["blender"],
        "ref_pair_rmse":d["reference_pair_difference"]["rmse_linear"],
        "oidn_rmse":[d["full_interior_metrics"]["NATIVE_COMP_OIDN"][f"ref{i}"]["color"]["rmse_linear"] for i in (1,2)],
        "oidn_edge_ratio":[d["full_interior_metrics"]["NATIVE_COMP_OIDN"][f"ref{i}"]["detail"]["edge_contrast_ratio"] for i in (1,2)]},sort_keys=True))

if __name__=="__main__":main()
