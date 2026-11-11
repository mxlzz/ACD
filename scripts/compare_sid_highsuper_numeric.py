"""Cross-version High/Super OIDN/alpha/HDR diagnostics, using all frozen AOVs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scripts.compare_sid_standard_numeric import rgba,metrics

def compare(src,legacy,port,dest):
    dest.mkdir(parents=True,exist_ok=True)
    fixture=json.loads((src/"input_manifest.json").read_text())
    old=json.loads((legacy/"manifest.json").read_text())
    new=json.loads((port/"manifest.json").read_text())
    assert old["mode"]==new["mode"] and old["mode"] in ("HIGH","SUPER")
    assert (old["flavor"],new["flavor"])==("legacy","port")
    assert old["upstream_commit"]==new["upstream_commit"]
    assert set(old["input_sha256"])==set(new["input_sha256"])==set(fixture["files"])
    controls={}
    for name in sorted(fixture["files"]):
        source=src/(name+".exr")
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if not (digest==fixture["files"][name]==old["input_sha256"][name]
                ==new["input_sha256"][name]):
            raise ValueError("Input hash mismatch: "+name)
        origin=rgba(source)
        a=rgba(legacy/("raw_"+name+".exr"))
        b=rgba(port/("raw_"+name+".exr"))
        if not (origin.shape==a.shape==b.shape==(64,96,4)):
            raise ValueError("Input passthrough shape mismatch: "+name)
        controls[name]={"legacy_vs_port":metrics(a,b),
                        "legacy_vs_source":metrics(origin,a),
                        "port_vs_source":metrics(origin,b)}
    input_ok=all(data["legacy_vs_port"]["max_abs"]<=0.001 for data in controls.values())
    a,b=rgba(legacy/"sid.exr"),rgba(port/"sid.exr")
    if a.shape!=b.shape or a.shape!=(64,96,4):
        raise ValueError("Final SID shape differs")
    emission=rgba(src/"emission.exr")
    alpha=rgba(src/"noisy.exr")[...,3]
    bright=np.max(emission[...,:3],axis=-1)>1
    translucent=alpha<0.999
    if not bright.any() or not translucent.any():
        raise ValueError("Missing diagnostic regions")
    diffs={
        "rgb_full":metrics(a[...,:3],b[...,:3]),
        "alpha_full":metrics(a[...,3:],b[...,3:]),
        "rgb_emissive":metrics(a[...,:3],b[...,:3],bright),
        "rgb_translucent":metrics(a[...,:3],b[...,:3],translucent),
        "alpha_translucent":metrics(a[...,3:],b[...,3:],translucent),
    }
    report={
        "test":"M3.5 High/Super real SID vs port on same AOV EXRs",
        "mode":old["mode"],"legacy_blender":old["blender"],"port_blender":new["blender"],
        "input_passthrough_valid":input_ok,
        "passthrough":controls,
        "roi":{"emissive_pixels":int(bright.sum()),"translucent_pixels":int(translucent.sum())},
        "cross_version":diffs,
        "not_proven":["Backend OIDN equivalence","Pixel equivalence","Visual quality superiority"],
    }
    (dest/"comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(dest/"difference_maps.npz",rgb_delta=np.asarray(b[...,:3]-a[...,:3],
                            dtype=np.float32),alpha_delta=np.asarray(b[...,3:]-a[...,3:],
                            dtype=np.float32),emissive_mask=bright,translucent_mask=translucent)
    print(json.dumps({"mode":old["mode"],"input_passthrough_valid":input_ok,
                      "cross_version":diffs},indent=2))
    if not input_ok:
        raise ValueError("Compositor raw AOV mismatch; SID deltas uninterpretable")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("input","legacy","port","output"):
        p.add_argument("--"+key,type=Path,required=True)
    ar=p.parse_args()
    compare(ar.input,ar.legacy,ar.port,ar.output)
