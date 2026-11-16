"""E0048: fail-closed native Cycles guide reflection toggle on matched Raw."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from acd_lab.core import rgb,compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays,write_report

ROIS={"glass_overlap":(104,192,80,160),"uncovered_slats":(328,192,80,160),"interior":(96,96,320,320)}
FILES={"raw":"acd_compare_Raw.exr","oidn":"acd_compare_NATIVE_COMP_OIDN.exr","aov":"raw_multilayer.exr"}

def digest(f):
    h=hashlib.sha256()
    with Path(f).open("rb") as stream:
        for block in iter(lambda:stream.read(1048576),b""):h.update(block)
    return h.hexdigest()

def load(root,meta,expected=None):
    files={key:root/name for key,name in FILES.items()}
    for path in files.values():
        if not path.is_file():raise ValueError("Missing "+str(path))
        if expected and digest(path)!=expected[path.name]:raise ValueError("Wrong frozen source SHA: "+str(path))
    ml=read_arrays(files["aov"],layer=meta["view_layer"])
    if not {"image","denoising_albedo","denoising_normal"}<=set(ml):
        raise ValueError("Denoising AOV incomplete")
    arr={"raw":rgb(read_arrays(files["raw"])["image"]),
         "oidn":rgb(read_arrays(files["oidn"])["image"]),
         "albedo":rgb(ml["denoising_albedo"]),"normal":rgb(ml["denoising_normal"])}
    if any(x.shape!=(512,512,3) for x in arr.values()):raise ValueError("Wrong crop shape")
    if np.max(np.abs(arr["raw"]-rgb(ml["image"])))>1e-5:
        raise ValueError("Noisy beauty differs from multilayer")
    return arr

def compare(a,b,refs):
    max_raw=float(np.max(np.abs(a["raw"]-b["raw"])))
    result={"raw_max_abs":max_raw,"raw_identical":max_raw<=1e-5,
            "causal_interpretation_allowed":False,"guide_effect":{},"scores":{}}
    if not result["raw_identical"]:
        result["decision"]="STOP: Raw changed; no same-input causal inference"
        return result
    for guide in ("albedo","normal"):
        result["guide_effect"][guide]=compare_images(a[guide],b[guide])
    if all(x["rmse_linear"]<=1e-5 for x in result["guide_effect"].values()):
        result["decision"]="STOP: Cycles guide toggle has no measurable effect here"
        return result
    result["causal_interpretation_allowed"]=True
    for name,im in (("follow_true",a["oidn"]),("follow_false",b["oidn"])):
        result["scores"][name]={}
        for area,(x,y,w,h) in ROIS.items():
            result["scores"][name][area]={
                k:{"linear":compare_images(ref[y:y+h,x:x+w],im[y:y+h,x:x+w]),
                   "detail":detail_fidelity(ref[y:y+h,x:x+w],im[y:y+h,x:x+w])}
                for k,ref in refs.items()}
    result["oidn_output_difference"]=compare_images(a["oidn"],b["oidn"])
    result["decision"]="DIAGNOSTIC only: native guide setting changed output, inspect against both finite references"
    return result

def main():
    p=argparse.ArgumentParser()
    for k in ("original","switched","manifest","output"):
        p.add_argument("--"+k,required=True,type=Path)
    args=p.parse_args()
    original=json.loads(args.manifest.read_text())
    oldmeta=original["source_metadata"]
    newmeta=json.loads((args.switched/"metadata.json").read_text())
    for meta in (oldmeta,newmeta):
        if (not meta["blender"].startswith("5.2.4") or meta["scene"]!="detail_target"
            or meta["resolution"]!=[1920,1440] or meta["samples"]!=24 or meta["seed"]!=539
            or meta["e0046_crop"]["top_left_origin_rect"]!=[928,320,512,512]):
            raise ValueError("Fixed E0046/E0048 contract mismatch")
    if newmeta.get("e0048_follow_reflections") is not False:
        raise ValueError("Follow-reflections switch was not applied")
    a=load(args.original,oldmeta,original["output_sha256"])
    b=load(args.switched,newmeta)
    refs={}
    for key,file in (("ref1","reference.exr"),("ref2","reference_check.exr")):
        path=args.original/file
        if digest(path)!=original["output_sha256"][file]:raise ValueError("Wrong reference SHA")
        refs[key]=rgb(read_arrays(path)["image"])
    metrics=compare(a,b,refs)
    args.output.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    sheet=Image.new("RGB",(668,748),(25,25,25))
    draw=ImageDraw.Draw(sheet)
    for i,(name,img) in enumerate((("follow True",a["oidn"]),("follow False",b["oidn"]),
                                   ("reference 1",refs["ref1"]),("reference 2",refs["ref2"]))):
        px=12+332*(i%2);py=12+366*(i//2)
        sheet.paste(Image.fromarray(display_rgb(img[96:416,96:416])),(px,py+28))
        draw.text((px+5,py+6),name,fill=(245,245,245))
    sheet.save(args.output/"E0048_comparison.png",optimize=True)
    data={"experiment":"E0048","source_run":43883209135,"algorithm_new":False,
          "intervention":"native Cycles denoising_pass_follow_reflections True to False",
          "reference_converged":False,"metrics":metrics,
          "new_sha256":{k:digest(args.switched/name) for k,name in FILES.items()}}
    write_report(args.output/"E0048_RESULTS.json",data)
    print("E0048_RESULT",json.dumps({"raw_max":metrics["raw_max_abs"],
          "allowed":metrics["causal_interpretation_allowed"],"decision":metrics["decision"]}))

if __name__=="__main__":main()
