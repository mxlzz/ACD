"""Compare isolated compositor math and alpha conversion independently of OIDN."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scripts.compare_sid_standard_numeric import rgba,metrics

INPUTS=("noisy","diffuse_direct","diffuse_indirect","diffuse_color","emission","alpha")
OPERATORS=("add_diffuse","mul_diffuse","add_emission_hdr","recombine_alpha")

def compare(src,old_dir,new_dir,dest):
    dest.mkdir(parents=True,exist_ok=True)
    src_meta=json.loads((src/"input_manifest.json").read_text())
    old=json.loads((old_dir/"manifest.json").read_text())
    new=json.loads((new_dir/"manifest.json").read_text())
    if old["flavor"]!="legacy" or new["flavor"]!="port" or not old["no_oidn"] or not new["no_oidn"]:
        raise ValueError("Invalid operator probe")
    controls={}
    for name in INPUTS:
        digest=hashlib.sha256((src/(name+".exr")).read_bytes()).hexdigest()
        if not (digest==src_meta["files"][name]==old["input_sha256"][name]
                ==new["input_sha256"][name]):
            raise ValueError("EXR sha mismatch: "+name)
        source=rgba(src/(name+".exr"))
        raw_old=rgba(old_dir/("raw_"+name+".exr"))
        raw_new=rgba(new_dir/("raw_"+name+".exr"))
        if not (source.shape==raw_old.shape==raw_new.shape==(64,96,4)):
            raise ValueError("Source size mismatch: "+name)
        controls[name]=metrics(raw_old,raw_new)
    valid=all(control["max_abs"]<=0.001 for control in controls.values())
    ops={}
    maps={}
    for name in OPERATORS:
        lhs,rhs=rgba(old_dir/(name+".exr")),rgba(new_dir/(name+".exr"))
        if lhs.shape!=rhs.shape or lhs.shape!=(64,96,4):
            raise ValueError("Output size mismatch: "+name)
        ops[name]={"rgb":metrics(lhs[...,:3],rhs[...,:3]),
                   "alpha":metrics(lhs[...,3:],rhs[...,3:])}
        maps[name+"_rgb"]=np.asarray(rhs[...,:3]-lhs[...,:3],dtype=np.float32)
        maps[name+"_alpha"]=np.asarray(rhs[...,3:]-lhs[...,3:],dtype=np.float32)
    report={
        "experiment":"M3.6 no-OIDN compositor math comparison",
        "blender_original":old["blender"],"blender_port":new["blender"],
        "source_inputs_equal":valid,"passthrough":controls,
        "operations":ops,
        "hypothesis":"If difference persists without OIDN, compositor port API may contribute.",
        "not_proven":["Full SID High/Super parity","OIDN equivalence","General color-management parity"],
    }
    (dest/"comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(dest/"difference_maps.npz",**maps)
    print(json.dumps({"source_inputs_equal":valid,"operations":ops},indent=2))
    if not valid:
        raise ValueError("Raw inputs drift across Blender versions")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("input","legacy","port","output"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    compare(a.input,a.legacy,a.port,a.output)
