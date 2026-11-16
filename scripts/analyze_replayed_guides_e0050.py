"""E0050: proof that compositor replay matches native before guide-swap inference."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from acd_lab.io import read_arrays,write_report
from acd_lab.core import compare_images,rgb
from acd_lab.detail import detail_fidelity

ROI={"glass_overlap":(104,192,80,160),"uncovered_slats":(328,192,80,160),"interior":(96,96,320,320)}
def hashfile(f):
    h=hashlib.sha256()
    with f.open("rb") as stream:
        for part in iter(lambda:stream.read(1024*1024),b""):h.update(part)
    return h.hexdigest()
def assess(a,b,c,original_oidn,refs):
    rawmax=float(np.max(np.abs(rgb(a)-rgb(b))))
    baseline_max=float(np.max(np.abs(rgb(c)-rgb(original_oidn))))
    output={"raw_passthrough_max_abs":rawmax,
            "baseline_native_replay_max_abs":baseline_max,
            "raw_passthrough_verified":rawmax<=1e-5,
            "native_replay_verified":baseline_max<=1e-4,
            "scores":{}}
    if not output["raw_passthrough_verified"]:
        output["decision"]="STOP: compositor altered noisy RGB, invalid input identity"
    elif not output["native_replay_verified"]:
        output["decision"]="STOP: offline native-guide replay not equivalent to original compositor"
    else:
        output["decision"]="Valid same-noisy compositor guide swap; finite-reference evaluation only"
    return output
def main():
    p=argparse.ArgumentParser()
    for field in ("old","alternative","comparison","result46","result49","output"):
        p.add_argument("--"+field,type=Path,required=True)
    args=p.parse_args()
    base=json.loads(args.result46.read_text())
    alt=json.loads(args.result49.read_text())
    if base["experiment"]!="E0046" or alt["experiment"]!="E0049":
        raise ValueError("Wrong source experiments")
    for name in ("acd_compare_Raw.exr","raw_multilayer.exr","acd_compare_NATIVE_COMP_OIDN.exr","reference.exr","reference_check.exr"):
        fp=args.old/name
        if hashfile(fp)!=base["output_sha256"][name]:raise ValueError("Original SHA mismatch "+name)
    for name,expect in alt["source_hashes"].items():
        fp=args.alternative/name
        if hashfile(fp)!=expect:raise ValueError("Alternative SHA mismatch "+name)
    def read(file):return rgb(read_arrays(file)["image"])
    raw=read(args.old/"acd_compare_Raw.exr")
    replay_raw=read(args.comparison/"e0050_RawReplayed.exr")
    replay_base=read(args.comparison/"e0050_NativeGuidesReplay.exr")
    replay_alt=read(args.comparison/"e0050_AlternativeGuides.exr")
    original_oidn=read(args.old/"acd_compare_NATIVE_COMP_OIDN.exr")
    refs={"ref1":read(args.old/"reference.exr"),"ref2":read(args.old/"reference_check.exr")}
    out=assess(raw,replay_raw,replay_base,original_oidn,refs)
    out["replay_vs_swap_rmse"]=compare_images(replay_base,replay_alt)
    if out["raw_passthrough_verified"] and out["native_replay_verified"]:
        out["scores"]={}
        for label,im in (("native_guides",replay_base),("alternative_guides",replay_alt)):
            out["scores"][label]={}
            for region,(x,y,w,h) in ROI.items():
                out["scores"][label][region]={
                    key:{"linear":compare_images(ref[y:y+h,x:x+w],im[y:y+h,x:x+w]),
                         "detail":detail_fidelity(ref[y:y+h,x:x+w],im[y:y+h,x:x+w])}
                    for key,ref in refs.items()}
    args.output.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    sheet=Image.new("RGB",(668,748),(25,25,25))
    pen=ImageDraw.Draw(sheet)
    for i,(label,im) in enumerate((("native guides replay",replay_base),("alternative roughness guides",replay_alt),("ref512 A",refs["ref1"]),("ref512 B",refs["ref2"]))):
        x=12+332*(i%2);y=12+366*(i//2)
        sheet.paste(Image.fromarray(display_rgb(im[96:416,96:416])),(x,y+28))
        pen.text((x+5,y+5),label[:38],fill=(245,245,245))
    sheet.save(args.output/"E0050_replayed_guides.png",optimize=True)
    data={"experiment":"E0050","source_runs":[43883209135,43894800865],
          "no_new_cycles_scene_render":True,
          "reference_convergence_proven":False,"new_denoiser":False,
          "metrics":out}
    write_report(args.output/"E0050_RESULTS.json",data)
    print("E0050_REPLAY_VERIFICATION",json.dumps({
        "raw_passthrough":out["raw_passthrough_max_abs"],
        "native_vs_replay":out["baseline_native_replay_max_abs"],
        "decision":out["decision"]}))
if __name__=="__main__":main()
