"""Compare isolated OIDN filters across Blender versions; no ranking or claims of parity."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scripts.compare_sid_standard_numeric import rgba,metrics

def compare(src,legacy,port,dest):
    dest.mkdir(parents=True,exist_ok=True)
    old=json.loads((legacy/"manifest.json").read_text())
    new=json.loads((port/"manifest.json").read_text())
    fixture=json.loads((src/"input_manifest.json").read_text())
    if old["flavor"]!="legacy" or new["flavor"]!="port" or old["cases"]!=new["cases"]:
        raise ValueError("Different OIDN cases")
    passthrough={}
    for name in old["input_sha256"]:
        if name not in new["input_sha256"]:
            raise ValueError("Missing input: "+name)
        digest=hashlib.sha256((src/(name+".exr")).read_bytes()).hexdigest()
        if not (digest==fixture["files"][name]==old["input_sha256"][name]
                ==new["input_sha256"][name]):
            raise ValueError("Input hash mismatch "+name)
        lhs,rhs=rgba(legacy/("raw_"+name+".exr")),rgba(port/("raw_"+name+".exr"))
        passthrough[name]=metrics(lhs,rhs)
    valid=all(m["max_abs"]<=0.001 for m in passthrough.values())
    region=np.max(rgba(src/"emission.exr")[...,:3],axis=-1)>1
    if not region.any():
        raise ValueError("HDR region absent")
    cases={}
    maps={}
    for name in old["cases"]:
        lhs,rhs=rgba(legacy/(name+".exr")),rgba(port/(name+".exr"))
        if lhs.shape!=rhs.shape or lhs.shape!=(64,96,4):
            raise ValueError("Result shape mismatch "+name)
        cases[name]={
            "rgb":metrics(lhs[...,:3],rhs[...,:3]),
            "alpha":metrics(lhs[...,3:],rhs[...,3:]),
            "rgb_emissive_region":metrics(lhs[...,:3],rhs[...,:3],region),
        }
        maps[name+"_rgb_delta"]=np.asarray(rhs[...,:3]-lhs[...,:3],dtype=np.float32)
    report={
        "test":"M3.7 isolated OIDN cross-version, same EXRs",
        "legacy_blender":old["blender"],"port_blender":new["blender"],
        "input_passthrough_valid":valid,"passthrough":passthrough,
        "settings":old["cases"],"blender5_oidn_settings":new["blender5_oidn_settings"],
        "measurements":cases,
        "warning":"Differences include Blender/OIDN version and settings changes; not evidence of porting bug alone.",
        "not_proven":["OIDN version equality","Pixel-equivalent SID","Quality superiority"],
    }
    (dest/"comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(dest/"difference_maps.npz",**maps)
    print(json.dumps({"input_passthrough_valid":valid,"measurements":cases},indent=2))
    if not valid:
        raise ValueError("Inputs differ before OIDN")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("input","legacy","port","output"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    compare(a.input,a.legacy,a.port,a.output)
