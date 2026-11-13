"""E0030 same-display diagnostic crops of frozen Emission50 on independent Island.

References select all ROIs: candidates cannot influence what gets shown.
This is display-compressed diagnostic, not Blender OCIO or perceptual evaluation.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.emission_guide import emission_guided_blend
from acd_lab.io import read_arrays, write_report
from scripts.analyze_cozy_e0020 import choose_reference_rois,display_rgb

SHA="0fceb72489873a1ebbdf8210c435713e5fee1b3c58ffa4105187023f6896b701"

def analyze(root:Path,output:Path):
    from PIL import Image,ImageDraw
    data=json.loads((root/"metadata.json").read_text())
    if data.get("source_blend_sha256")!=SHA or not data.get("second_reference"):
        raise ValueError("Wrong frozen Island source or missing reference")
    ref1=read_arrays(root/"reference.exr")["image"]
    ref2=read_arrays(root/"reference_check.exr")["image"]
    raw=read_arrays(root/"acd_compare_Raw.exr")["image"]
    native=read_arrays(root/"acd_compare_NATIVE_COMP_OIDN.exr")["image"]
    high=read_arrays(root/"acd_compare_HIGH.exr")["image"]
    sup=read_arrays(root/"acd_compare_SUPER.exr")["image"]
    layers=read_arrays(root/"raw_multilayer.exr",layer=data["view_layer"])
    if "emission" not in layers: raise ValueError("Missing actual Cycles emission pass")
    e50,s50=emission_guided_blend(raw,native,layers["emission"],scale=.25,max_raw_fraction=.5)
    e100,s100=emission_guided_blend(raw,native,layers["emission"],scale=.25,max_raw_fraction=1.)
    # Position 1: highest mean signed-reference luminance, no method outputs.
    ref=(np.asarray(rgb(ref1),dtype="f8")+np.asarray(rgb(ref2),dtype="f8"))*.5
    luma=ref @ np.array([.2126,.7152,.0722])
    size=80
    h,w=luma.shape
    iy,ix=np.unravel_index(np.argmax(luma),luma.shape)
    highlight=(max(0,min(w-size,int(ix)-size//2)),
               max(0,min(h-size,int(iy)-size//2)),size,size)
    # Positions 2-4: strongest RGB detail from mean refs, non-overlapping.
    detail=choose_reference_rois(ref1,ref2,size=size,count=3)
    coords=[highlight]+[x for x in detail if x != highlight]
    names=["reference_brightest"]+[f"reference_detail_{i}" for i in range(1,len(coords))]
    ordered=[("Reference 1",ref1),("Raw",raw),("OIDN",native),
             ("Emission50",e50),("Emission100",e100),
             ("ACD High",high),("ACD Super",sup),("Reference 2",ref2)]
    output.mkdir(parents=True,exist_ok=True)
    crops=[]
    for idx,(name,(x,y,cw,ch)) in enumerate(zip(names,coords),1):
        magnify=3;margin=10;head=25
        canvas=Image.new("RGB",(len(ordered)*(cw*magnify+margin)+margin,
                                ch*magnify+margin*2+head),(30,30,30))
        drawer=ImageDraw.Draw(canvas)
        for pos,(label,image) in enumerate(ordered):
            patch=Image.fromarray(display_rgb(image[y:y+ch,x:x+cw]))
            patch=patch.resize((cw*magnify,ch*magnify),Image.Resampling.NEAREST)
            px=margin+pos*(cw*magnify+margin)
            canvas.paste(patch,(px,head+margin))
            drawer.text((px+2,7),label,fill=(238,238,238))
        fname=f"island_e0030_{idx}_{name}.png"
        canvas.save(output/fname)
        crops.append(fname)
    # Error on the exact same crop, finite refs. Not selection of a winning ROI.
    local=[]
    for tag,(x,y,cw,ch) in zip(names,coords):
        patch=lambda arr:arr[y:y+ch,x:x+cw]
        entry={"tag":tag,"bbox":[x,y,cw,ch]}
        for method,img in ordered:
            if method.startswith("Reference"):continue
            entry[method]={
                "rmse_first":compare_images(patch(ref1),patch(img))["rmse_linear"],
                "rmse_second":compare_images(patch(ref2),patch(img))["rmse_linear"],
            }
        local.append(entry)
    report={"experiment":"E0030","scene_sha256":SHA,"render_run_id":43309302172,
            "roi_selection":"maximum luminance of mean finite-spp references and reference-only gradient regions",
            "coords_px":coords,"crops":crops,"local_rmse":local,
            "emission_inference_weights":{"half":s50,"full":s100},
            "source_license":"MIT, Yunus Emre Karaman",
            "display":"shared linear RGB max(0,x)/(1+max(0,x)) ^(1/2.2), equal for every panel; NOT Blender OCIO",
            "caveat":"Finite refs, 320px aliasing, non-color-managed illustrative crops; visual inspection required before product claim."}
    write_report(output/"analysis.json",report)
    print("ACD_E0030_VISUAL_ROI",json.dumps({"crops":crops,"coords":coords,"local_rmse":local},sort_keys=True))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    analyze(a.directory.resolve(),a.output.resolve())
if __name__=="__main__":main()
