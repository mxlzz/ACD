"""E0047 -- Glass-overlap vs uncovered slat diagnostic from unchanged E0046 EXRs.

No new render, model, denoiser or learned parameter. Two predeclared ROIs
on 320x320 INTERIOR: glass [8,96,80,160], uncovered [232,96,80,160].
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from acd_lab.io import read_arrays,write_report
from acd_lab.core import rgb,compare_images
from acd_lab.detail import detail_fidelity

FULL_INTERIOR=(96,96,320,320)
ROIS={"glass_overlap":(8,96,80,160),"uncovered_slats":(232,96,80,160)}
FILES={
    "raw":"acd_compare_Raw.exr",
    "oidn":"acd_compare_NATIVE_COMP_OIDN.exr",
    "ref1":"reference.exr",
    "ref2":"reference_check.exr",
    "aov":"raw_multilayer.exr",
}

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""):h.update(part)
    return h.hexdigest()

def corr_h_luma(a,b):
    """Pearson correlation of horizontal asinh(scene-linear) luma gradients."""
    if rgb(a).shape!=rgb(b).shape:raise ValueError("Mismatched images")
    weights=np.array([.2126,.7152,.0722])
    la=np.arcsinh(rgb(a)@weights)
    lb=np.arcsinh(rgb(b)@weights)
    ga=np.diff(la,axis=1).ravel()
    gb=np.diff(lb,axis=1).ravel()
    ca,cb=ga-ga.mean(),gb-gb.mean()
    norm=float(np.linalg.norm(ca)*np.linalg.norm(cb))
    return float(np.dot(ca,cb)/norm) if norm>1e-12 else None

def analyze_arrays(images):
    if set(images)!={"raw","oidn","ref1","ref2","albedo","normal"}:
        raise ValueError("Missing exact frozen E0046 input set")
    if any(rgb(v).shape!=(512,512,3) for v in images.values()):
        raise ValueError("E0047 must consume 512x512 EXRs")
    data={}
    for name,(x,y,w,h) in ROIS.items():
        sx,sy=FULL_INTERIOR[0]+x,FULL_INTERIOR[1]+y
        mask=(slice(sy,sy+h),slice(sx,sx+w))
        p={key:rgb(value)[mask] for key,value in images.items()}
        refs=[p["ref1"],p["ref2"]]
        variants={}
        for candidate in ("raw","oidn"):
            variants[candidate]={
                f"ref{i+1}":{
                    "linear":compare_images(ref,p[candidate]),
                    "detail":detail_fidelity(ref,p[candidate])
                }for i,ref in enumerate(refs)
            }
        def rms_gradient(arr):
            a=np.arcsinh(rgb(arr))
            dx=np.diff(a,axis=1)
            return float(np.sqrt(np.mean(dx**2)))
        data[name]={
            "relative_inner_xywh":[x,y,w,h],
            "absolute_exr_xywh":[sx,sy,w,h],
            "method_scores":variants,
            "ref_ref_rmse":compare_images(*refs)["rmse_linear"],
            "ref_horizontal_luma_gradient_corr":corr_h_luma(*refs),
            "oidn_vs_refmean_horizontal_luma_gradient_corr":
                corr_h_luma(p["oidn"],(refs[0]+refs[1])/2),
            "ref_horizontal_gradient_rms":[rms_gradient(v) for v in refs],
            "oidn_horizontal_gradient_rms":rms_gradient(p["oidn"]),
            "albedo_horizontal_gradient_rms":rms_gradient(p["albedo"]),
            "normal_horizontal_gradient_rms":rms_gradient(p["normal"]),
        }
    return data

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",required=True,type=Path)
    parser.add_argument("--source-json",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    source=json.loads(a.source_json.read_text())
    m=source["source_metadata"]
    if (source["experiment"]!="E0046" or not m["blender"].startswith("5.2.4")
        or source["crop_xywh"]!=[928,320,512,512]
        or source["evaluation_interior_xywh"]!=list(FULL_INTERIOR)
        or m["samples"]!=24 or m["reference_samples"]!=512
        or m["seed"]!=539 or m["reference_seed"]!=8819 or m["second_reference_seed"]!=8922):
        raise ValueError("Not frozen E0046 result source")
    files={}
    for key,name in FILES.items():
        fp=a.directory/name
        if not fp.is_file() or sha(fp)!=source["output_sha256"][name]:
            raise ValueError("E0046 SHA-256 input mismatch: "+name)
        files[key]=fp
    raw=read_arrays(files["raw"])["image"]
    layer=read_arrays(files["aov"],layer=m["view_layer"])
    if not {"image","denoising_albedo","denoising_normal"}.issubset(layer):
        raise ValueError("Missing denoising guides")
    if float(np.max(np.abs(rgb(raw)-rgb(layer["image"]))))>1e-5:
        raise ValueError("Raw beauty AOV not identical")
    images={
        "raw":raw,
        "oidn":read_arrays(files["oidn"])["image"],
        "ref1":read_arrays(files["ref1"])["image"],
        "ref2":read_arrays(files["ref2"])["image"],
        "albedo":layer["denoising_albedo"],
        "normal":layer["denoising_normal"],
    }
    data=analyze_arrays(images)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    a.output.mkdir(parents=True,exist_ok=True)
    panels=("raw","oidn","ref1","ref2","albedo","normal")
    # Two areas side-by-side; 6 signals in rows, source-native resolution 80x160
    scale=2
    sheet=Image.new("RGB",(2*(80*scale+16)+16,6*(160*scale+24+12)+16),(27,27,27))
    draw=ImageDraw.Draw(sheet)
    for col,(region,(x,y,w,h)) in enumerate(ROIS.items()):
        sx,sy=FULL_INTERIOR[0]+x,FULL_INTERIOR[1]+y
        for row,name in enumerate(panels):
            patch=rgb(images[name])[sy:sy+h,sx:sx+w]
            if name=="normal":
                patch=(patch+1)*.5
                preview=np.uint8(np.clip(patch*255+.5,0,255))
            else:
                preview=display_rgb(patch)
            tile=Image.fromarray(preview).resize((w*scale,h*scale),Image.Resampling.NEAREST)
            ix=16+col*(w*scale+16)
            iy=16+row*(h*scale+36)
            sheet.paste(tile,(ix,iy+24))
            draw.text((ix,iy+5),region[:8]+" "+name,fill=(247,247,247))
    sheet.save(a.output/"e0047_roi_comparison.png",optimize=True)
    report={
        "experiment":"E0047","source_run":43883209135,"source_commit":None,
        "source_e0046":"docs/experiments/E0046_RESULTS.json",
        "no_new_render":True,"no_new_filter":True,
        "prespecified_regions":{k:list(v) for k,v in ROIS.items()},
        "same_noisy_input":True,"source_guide_original":True,
        "regions":data,
        "reference_convergence_proven":False,
        "causal_glass_effect_proven":False,
        "warning":"Glass and uncovered ROIs have different content/light/materials. Correlated gradients can show candidate lost signal but not prove glass caused it. 512 spp finite refs and 96px OIDN crop margin.",
    }
    write_report(a.output/"E0047_RESULTS.json",report)
    print("E0047_PASS_DIAGNOSIS",json.dumps({
        k:{"ref_gradient_corr":v["ref_horizontal_luma_gradient_corr"],
           "oidn_refmean_gradient_corr":v["oidn_vs_refmean_horizontal_luma_gradient_corr"],
           "oidn_edge_ratio_ref1":v["method_scores"]["oidn"]["ref1"]["detail"]["edge_contrast_ratio"],
           "oidn_edge_ratio_ref2":v["method_scores"]["oidn"]["ref2"]["detail"]["edge_contrast_ratio"],
           "ref_disagreement":v["ref_ref_rmse"]} for k,v in data.items()},sort_keys=True))
if __name__=="__main__":main()
