"""M3.8: compare OIDN quality/HDR ablations to historical Blender output.

Matching historical pixels is NOT the same as higher visual fidelity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scripts.compare_sid_standard_numeric import metrics,rgba

BASES=("guided_fast","guided_accurate","emission_accurate","alpha_accurate")
QUALITIES=("high","balanced","fast")
HDRS=(1,0)
INPUTS=("noisy","normal","albedo","alpha","emission")

def key(base,quality,hdr):
    return f"{base}__{quality}__h{int(hdr)}"

def summarize(src,old_dir,new_dir,out_dir):
    out_dir.mkdir(parents=True,exist_ok=True)
    fixture=json.loads((src/"input_manifest.json").read_text())
    old=json.loads((old_dir/"manifest.json").read_text())
    new=json.loads((new_dir/"manifest.json").read_text())
    if old["flavor"]!="legacy" or new["flavor"]!="port":
        raise ValueError("Wrong Blender flavors")
    passthrough={}
    for name in INPUTS:
        digest=hashlib.sha256((src/(name+".exr")).read_bytes()).hexdigest()
        if not (digest==fixture["files"][name]
                ==old["input_sha256"][name]==new["input_sha256"][name]):
            raise ValueError("Input SHA mismatch: "+name)
        a=rgba(old_dir/("raw_"+name+".exr"))
        b=rgba(new_dir/("raw_"+name+".exr"))
        if a.shape!=b.shape or a.shape!=(64,96,4):
            raise ValueError("Passthrough shape differs: "+name)
        passthrough[name]=metrics(a,b)
    passthrough_ok=all(m["max_abs"]<=.001 for m in passthrough.values())

    roi=np.max(rgba(src/"emission.exr")[...,:3],axis=-1)>1
    if not roi.any():
        raise ValueError("HDR fixture region absent")
    records=[]
    maps={}
    for base in BASES:
        for hdr in HDRS:
            previous_key=key(base,"legacy",hdr)
            if previous_key not in old["filters"]:
                raise ValueError("Legacy case missing: "+previous_key)
            previous=rgba(old_dir/(previous_key+".exr"))
            match={}
            for quality in QUALITIES:
                current_key=key(base,quality,hdr)
                if current_key not in new["filters"]:
                    raise ValueError("Port case missing: "+current_key)
                current=rgba(new_dir/(current_key+".exr"))
                if current.shape!=previous.shape or current.shape!=(64,96,4):
                    raise ValueError("Output dimensions mismatch: "+current_key)
                rgb=metrics(previous[...,:3],current[...,:3])
                alpha=metrics(previous[...,3:],current[...,3:])
                hdr_rgb=metrics(previous[...,:3],current[...,:3],roi)
                match[quality]={"rgb":rgb,"alpha":alpha,"rgb_emission_roi":hdr_rgb}
                maps[current_key+"_rgb_delta"]=np.asarray(
                    current[...,:3]-previous[...,:3],dtype=np.float32)
            closest=min(QUALITIES,key=lambda q:match[q]["rgb"]["rmse"])
            baseline=match["high"]["rgb"]["rmse"]
            records.append({
                "filter":base,"HDR":bool(hdr),
                "metrics_vs_blender36":match,
                "closest_to_blender36_in_rgb_rmse":closest,
                "closest_to_high_delta":float(match[closest]["rgb"]["rmse"]-baseline),
                "note":"closest historical output is NOT best reconstruction quality",
            })

    # Deliberate within-version comparisons to isolate actual effects
    # without incorrectly attributing changes to an altered source EXR.
    within={}
    for base in BASES:
        for hdr in HDRS:
            high=rgba(new_dir/(key(base,"high",hdr)+".exr"))
            for quality in ("balanced","fast"):
                other=rgba(new_dir/(key(base,quality,hdr)+".exr"))
                within[key(base,quality,hdr)]=metrics(high[...,:3],other[...,:3])
        for quality in QUALITIES:
            on=rgba(new_dir/(key(base,quality,1)+".exr"))
            off=rgba(new_dir/(key(base,quality,0)+".exr"))
            within[f"{base}__{quality}__hdr_toggle"]=metrics(on[...,:3],off[...,:3])

    result={
        "experiment":"M3.8 controlled OIDN Quality/HDR options, pinned input EXRs",
        "blender_legacy":old["blender"],"blender_port":new["blender"],
        "oidn_semantic_version_from_runtime":"unknown; consult build artifacts",
        "input_passthrough_valid":passthrough_ok,
        "passthrough":passthrough,"matrix":records,
        "within_blender5_differences":within,
        "limitations":["different OIDN versions possible","Quality unavailable on Blender 3.6",
                       "synthetic fixture, no Cycles convergence","no pixel-equivalence required",
                       "closer to historic pixels does not imply better quality"],
    }
    (out_dir/"comparison.json").write_text(json.dumps(result,indent=2)+"\n")
    np.savez_compressed(out_dir/"difference_maps.npz",**maps)
    compact=[{"filter":r["filter"],"hdr":r["HDR"],
              "rmse":{q:round(r["metrics_vs_blender36"][q]["rgb"]["rmse"],7)
                      for q in QUALITIES},
              "closest":r["closest_to_blender36_in_rgb_rmse"]}
             for r in records]
    print("M3.8 MATRIX COMPARISON",json.dumps({
        "input_passthrough_valid":passthrough_ok,"records":compact,
        "within_port":{k:round(v["rmse"],7) for k,v in within.items()}
    },indent=2))
    if not passthrough_ok:
        raise ValueError("Input drift invalidates OIDN comparison")
    return result

def main():
    p=argparse.ArgumentParser()
    for name in ("input","legacy","port","output"):
        p.add_argument("--"+name,type=Path,required=True)
    args=p.parse_args()
    summarize(args.input,args.legacy,args.port,args.output)

if __name__=="__main__":
    main()
