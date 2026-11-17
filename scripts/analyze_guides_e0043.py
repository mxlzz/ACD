"""E0043 — predeclared 4x4 tiles and two finite references, no tuning."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images,rgb
from acd_lab.io import read_arrays,write_report

NAMES=("Raw","OIDN_RGB","OIDN_Albedo","OIDN_Both")
REF_SEEDS=(8819,8922)
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
    return h.hexdigest()
def locate(root,name):
    match=list(root.rglob(name))
    if len(match)!=1:raise ValueError("Missing or ambiguous "+name+": "+str(len(match)))
    return match[0]
def compare(images, refs):
    if any(rgb(v).shape != (400,640,3) or not np.isfinite(rgb(v)).all()
           for v in list(images.values())+list(refs.values())):
        raise ValueError("Wrong dimensions or nonfinite EXRs")
    full={n:{key:compare_images(ref,v) for key,ref in refs.items()} for n,v in images.items()}
    referr=compare_images(refs["ref8819"],refs["ref8922"])
    tiles=[]
    for yi in range(4):
        for xi in range(4):
            y0,y1=yi*100,(yi+1)*100
            x0,x1=xi*160,(xi+1)*160
            diffs={}
            for n,im in images.items():
                diffs[n]={k:compare_images(ref[y0:y1,x0:x1],im[y0:y1,x0:x1])["rmse_linear"]
                          for k,ref in refs.items()}
            refspread=compare_images(refs["ref8819"][y0:y1,x0:x1],
                                     refs["ref8922"][y0:y1,x0:x1])["rmse_linear"]
            deltas={k:diffs["OIDN_Both"][k]-diffs["OIDN_RGB"][k] for k in refs}
            # This is a screening flag, NOT a detection of a real visual failure.
            clear=all(v>0 for v in deltas.values()) and min(deltas.values()) > 0.1*refspread
            tiles.append({"grid_xy":[xi,yi],"xywh":[x0,y0,160,100],
                          "rmse_per_method_per_ref":diffs,
                          "reference_disagreement_rmse":refspread,
                          "full_guides_minus_rgb_only_rmse_delta":deltas,
                          "screen_for_guide_regression":bool(clear)})
    return {"global_errors":full,"reference_pair_disagreement":referr,
            "tiles":tiles,"tentative_guide_regression_tiles":
                [t["grid_xy"] for t in tiles if t["screen_for_guide_regression"]]}
def analyze(source,refroot,manifest42,output):
    m=json.loads((source/"e0043_manifest.json").read_text())
    refsmeta=json.loads(manifest42.read_text())
    if m["experiment"]!="E0043" or m["resolution"]!=[640,400] or m["seed"]!=539 or m["samples"]!=32 or not m["single_render"]:
        raise ValueError("Wrong new experiment")
    if (refsmeta["experiment"]!="E0042" or refsmeta["camera"]!=m["camera"]
        or not refsmeta["source"].startswith("Italian Flat")
        or any(row["resolution"]!=[640,400] for row in refsmeta["renders"])):
        raise ValueError("Reference provenance mismatch")
    images={}
    for n in NAMES:
        file=source/("e0043_"+n+".exr")
        if sha(file)!=m["files"][n]["sha256"]:raise ValueError("New output hash mismatch "+n)
        images[n]=rgb(read_arrays(file)["image"])
    refs={}
    for seed in REF_SEEDS:
        entry=next((x for x in refsmeta["renders"] if x["spp"]==128 and x["seed"]==seed),None)
        if entry is None:raise ValueError("Ref missing")
        path=locate(refroot,entry["file"])
        if sha(path)!=entry["file_sha256"]:raise ValueError("Reference hash mismatch "+str(seed))
        refs["ref"+str(seed)]=rgb(read_arrays(path)["image"])
    data=compare(images,refs)
    output.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    panel_names=["Raw","OIDN_RGB","OIDN_Albedo","OIDN_Both","ref8819","ref8922"]
    panel_arrays={**images,**refs}
    width,height=640,400
    sheet=Image.new("RGB",(3*width+48,2*(height+35)+36),(24,24,24))
    pen=ImageDraw.Draw(sheet)
    for i,name in enumerate(panel_names):
        col,row=i%3,i//3
        x=12+col*(width+12);y=12+row*(height+35+12)
        sheet.paste(Image.fromarray(display_rgb(panel_arrays[name])),(x,y+32))
        pen.text((x+3,y+9),name,fill=(240,240,240))
    sheet.save(output/"e0043_guides_1to1.png",optimize=True)
    result={"experiment":"E0043","source":m,"reference_source_run":43497486691,
            "reference_source":"E0042 two finite 128spp seeds 8819/8922",
            "prior_art_known":"OIDN recommends albedo/normal and prefilt; existing Blender exposes RGB, RGB+Albedo, RGB+Albedo+Normal. This is diagnosis only.",
            **data,"visual":"e0043_guides_1to1.png",
            "convergence_proven":False,"new_algorithm_tested":False,
            "decision_gate":"Investigate only a visually meaningful, predeclared tile failing with both references and margin against reference disagreement; otherwise stop this line.",
            "missing_external_ies":"IES_profiles/three-lobe-vee.ies",
            "scene_lighting_fidelity_validated":False,
            "limitation":"Single 32 spp and finite 128 spp refs cannot rank quality. All Italian Flat renders logged missing external IES profile. Original architectural illumination is not reproduced faithfully; experimental images are diagnostic only."}
    write_report(output/"e0043_results.json",result)
    print("E0043_GUIDE_SCREEN",json.dumps({"flagged":data["tentative_guide_regression_tiles"],
        "reference_rmse":data["reference_pair_disagreement"]["rmse_linear"],
        "global":{n:{ref:row["rmse_linear"] for ref,row in d.items()} for n,d in data["global_errors"].items()}},sort_keys=True))
    return result
def main():
    p=argparse.ArgumentParser()
    for name in ("source","refs","manifest42","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    analyze(a.source,a.refs,a.manifest42,a.output)
if __name__=="__main__":main()
