"""Direct OIDN CLI 2.3.3 vs 2.5.1 same-input/same-flags comparator."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, time
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays, write_report
from acd_lab.pfm import read_pfm


def args_for(binary, color, alb, nrm, out):
    return [str(binary), "-d", "cpu", "--hdr", str(color), "--alb", str(alb),
            "--nrm", str(nrm), "-q", "high", "-o", str(out)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as file:
        for part in iter(lambda: file.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()


def compare_versions(root, oidn233, oidn251):
    rows=[]
    for folder in [root]+sorted(root.glob("seed_*")):
        if not folder.is_dir(): continue
        p=folder/"oidn251"
        color,alb,nrm=[p/(name+".pfm") for name in ("color","albedo","normal")]
        for required in (color,alb,nrm,folder/"reference.exr",p/"output.pfm"):
            if not required.is_file(): raise FileNotFoundError(required)
        results={}
        for label,binary in (("oidn233",oidn233),("oidn251",oidn251)):
            out=p/(label+"_fresh_output.pfm")
            tic=time.perf_counter()
            run=subprocess.run(args_for(binary,color,alb,nrm,out),
                               stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                               check=True,text=True)
            results[label]={"image":read_pfm(out),"sha256":sha256(out),
                            "duration_sec":time.perf_counter()-tic,
                            "log":run.stdout[-2200:]}
        # Re-running the same official 2.5.1 executable must reproduce its
        # earlier output before comparisons are made.
        repeated=np.max(np.abs(results["oidn251"]["image"]-read_pfm(p/"output.pfm")))
        if not np.isfinite(repeated) or repeated>1e-5:
            raise ValueError(f"OIDN 2.5.1 repeat not deterministic: {repeated}")
        ref=read_arrays(folder/"reference.exr")["image"]
        row={"seed_folder":str(folder.relative_to(root)),
             "same_input_sha256":{str(x.name):sha256(x) for x in (color,alb,nrm)},
             "oidn251_repeat_max_abs":float(repeated)}
        for label in ("oidn233","oidn251"):
            v=results[label]
            row[label]={"rmse":compare_images(ref,v["image"])["rmse_linear"],
                        "detail":detail_fidelity(ref,v["image"]),
                        "output_sha256":v["sha256"],
                        "duration_sec":v["duration_sec"],"log":v["log"]}
        row["output_pair_difference"]=compare_images(results["oidn233"]["image"],
                                                     results["oidn251"]["image"])
        second=folder/"reference_check.exr"
        if second.is_file():
            ref2=read_arrays(second)["image"]
            row["second_ref"]={label:{
                "rmse":compare_images(ref2,results[label]["image"])["rmse_linear"],
                "detail":detail_fidelity(ref2,results[label]["image"]),
            } for label in ("oidn233","oidn251")}
        rows.append(row)
    return {"version_233_bin_sha256":sha256(oidn233),
            "version_251_bin_sha256":sha256(oidn251),
            "flags":"-d cpu --hdr <same color> --alb <same guide> --nrm <same guide> -q high",
            "warnings":"Fixed finite-spp references; differences may reflect weights/build/quality changes, not universal superiority; no independent sampling proof.",
            "rows":rows}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--directory",type=Path,required=True)
    ap.add_argument("--oidn233",type=Path,required=True)
    ap.add_argument("--oidn251",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    r=compare_versions(a.directory.resolve(),a.oidn233.resolve(),a.oidn251.resolve())
    write_report(a.output,r)
    print("OIDN_VERSION_PAIR",json.dumps([{"seed":x["seed_folder"],
        "oidn233_rmse":x["oidn233"]["rmse"],
        "oidn251_rmse":x["oidn251"]["rmse"],
        "oidn233_edge_rmse":x["oidn233"]["detail"]["edge_gradient_rmse"],
        "oidn251_edge_rmse":x["oidn251"]["detail"]["edge_gradient_rmse"],
        "direct_output_rmse":x["output_pair_difference"]["rmse_linear"],
        "repeat_delta":x["oidn251_repeat_max_abs"]} for x in r["rows"]],indent=2))

if __name__=="__main__":main()
