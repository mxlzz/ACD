"""E0038: OIDN 2.5.0 vs 2.5.1 isolated on same E0037 PFM inputs.

Blender 5.2.4 and 5.3.0 source pins OIDN_VERSION 2.5.0.
Same CLI options, device CPU, high, same three PFM guides, version only.
No ground truth reference and no perceptual ranking.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time
import numpy as np
from acd_lab.core import compare_images, rgb
from acd_lab.io import read_arrays, write_report
from acd_lab.pfm import read_pfm
from scripts.analyze_oidn_standalone_e0037 import commands, digest, only, source_arrays


def version_case(binary, e37_root, e35_root, e35_json, original, version, output):
    stored = original["cases"][version]
    first = only(e37_root, "color.pfm") if False else None
    relative = version.replace(".", "_")
    from37 = e37_root / relative
    if not from37.is_dir():
        raise ValueError(f"E0037 source directory absent: {from37}")
    work = output / relative
    work.mkdir(parents=True, exist_ok=True)
    original_pfms={}
    for n in ("color","albedo","normal"):
        src = from37 / (n+".pfm")
        if not src.is_file() or digest(src) != stored["source_sha256"][n]:
            raise ValueError(f"E0037 source PFM checksum mismatch {version}/{n}")
        shutil.copyfile(src, work / (n+".pfm"))
        original_pfms[n] = read_pfm(src)
    arrays, native, _ = source_arrays(e35_root, e35_json, version)
    for n in original_pfms:
        if not np.array_equal(original_pfms[n], arrays[n]):
            raise ValueError("Source PFM differs from SHA-controlled E0035 EXR")
    result={}
    for mode in ("raw_aux","accurate_like"):
        from251 = from37 / (mode+".pfm")
        if not from251.is_file() or digest(from251) != stored[mode]["sha256_output"]:
            raise ValueError("E0037 2.5.1 output checksum mismatch")
        steps=[]
        for cmd in commands(binary,mode,work):
            tic=time.perf_counter()
            proc=subprocess.run(cmd,check=True,capture_output=True,text=True)
            steps.append({"args":cmd[1:],
                          "wall_seconds":time.perf_counter()-tic,
                          "log_tail":(proc.stdout+"\n"+proc.stderr)[-1000:]})
        output250=read_pfm(work/(mode+".pfm"))
        output251=read_pfm(from251)
        if output250.shape != native.shape or not np.isfinite(output250).all():
            raise ValueError("2.5.0 output invalid")
        result[mode]={
            "oidn250_vs_251":compare_images(output250,output251),
            "oidn250_vs_blender_compositor":compare_images(output250,native),
            "oidn251_vs_blender_compositor":compare_images(output251,native),
            "oidn250_max_abs_vs_blender":float(np.max(np.abs(output250-native))),
            "oidn250_sha256":digest(work/(mode+".pfm")),
            "oidn251_sha256":digest(from251),
            "commands":steps,
        }
    return {"version":version,"original_blender":stored["blender"],
            "modes":result,"same_pfm_verified":True}


def main():
    parser=argparse.ArgumentParser()
    for label in ("oidn250","original37","archive37","source52","source53","archive35","output"):
        parser.add_argument("--"+label,type=Path,required=True)
    args=parser.parse_args()
    record37=json.loads(args.archive37.read_text())
    record35=json.loads(args.archive35.read_text())
    if record37.get("experiment")!="E0037" or record35.get("source_run")!=43480823352:
        raise ValueError("Wrong original experiment")
    args.output.mkdir(parents=True,exist_ok=True)
    cases={
        v:version_case(args.oidn250,args.original37,args.source52 if v=="5.2.4" else args.source53,
                       record35,record37,v,args.output)
        for v in ("5.2.4","5.3.0")
    }
    report={
        "experiment":"E0038",
        "oidn_250_bin_sha256":digest(args.oidn250),
        "oidn_251_bin_sha256":record37["oidn_binary_sha256"],
        "original_e0037_source_run":record37["source_run"],
        "versions":cases,
        "interpretation":"Fixed input/flags comparison across two official standalone OIDN versions. Both tested against Blender compositor output; no ground truth and no evidence of relative visual quality. Source Blender release build CMake pins OIDN 2.5.0, but runtime patch/ISA equivalence not assumed.",
    }
    write_report(args.output/"e0038_results.json",report)
    print("ACD_E0038_VERSION_ISOLATION",json.dumps({
        v:{mode:{
            "250vs251":cases[v]["modes"][mode]["oidn250_vs_251"]["rmse_linear"],
            "250vsBlender":cases[v]["modes"][mode]["oidn250_vs_blender_compositor"]["rmse_linear"]
        } for mode in ("raw_aux","accurate_like")} for v in cases},sort_keys=True))


if __name__=="__main__":main()
