"""Run official OIDN 2.5.1 CPU CLI on EXR beauty/albedo/normal for every seed."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, time
from pathlib import Path
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays, write_report
from acd_lab.pfm import read_pfm, write_pfm

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def evaluate(root: Path, binary: Path) -> dict:
    metadata=json.loads((root/"metadata.json").read_text())
    if not metadata.get("capture_aov") or not metadata.get("native_compositor_oidn"):
        raise ValueError("Capture AOVs and native compositor OIDN baseline are required")
    rows=[]
    for folder in [root]+sorted(root.glob("seed_*")):
        if not folder.is_dir(): continue
        multilayer=folder/"raw_multilayer.exr"
        raw_file=folder/"acd_compare_Raw.exr"
        native_file=folder/"acd_compare_NATIVE_COMP_OIDN.exr"
        ref_file=folder/"reference.exr"
        for f in (multilayer,raw_file,native_file,ref_file):
            if not f.is_file(): raise FileNotFoundError(f)
        aov=read_arrays(multilayer,layer=metadata["view_layer"])
        for key in ("image","denoising_albedo","denoising_normal"):
            if key not in aov: raise ValueError(f"Missing AOV {key}")
        raw=rgb(read_arrays(raw_file)["image"])
        if raw.shape != rgb(aov["image"]).shape: raise ValueError("Raw shape differs")
        beauty_delta=float(np.max(np.abs(raw-rgb(aov["image"]))))
        if beauty_delta>1e-5: raise ValueError(f"Raw not identical to AOV beauty: {beauty_delta}")
        work=folder/"oidn251"
        work.mkdir(exist_ok=True)
        color,alb,nrm,out=[work/p for p in ("color.pfm","albedo.pfm","normal.pfm","output.pfm")]
        write_pfm(color,raw)
        write_pfm(alb,aov["denoising_albedo"])
        write_pfm(nrm,aov["denoising_normal"])
        pfm_delta=float(np.max(np.abs(rgb(read_pfm(color))-raw)))
        if pfm_delta>1e-5: raise ValueError(f"PFM changed input: {pfm_delta}")
        cmd=[str(binary),"-d","cpu","--hdr",str(color),"--alb",str(alb),"--nrm",str(nrm),"-q","high","-o",str(out)]
        start=time.perf_counter()
        p=subprocess.run(cmd,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        elapsed=time.perf_counter()-start
        standalone=read_pfm(out)
        native=read_arrays(native_file)["image"]
        reference=read_arrays(ref_file)["image"]
        row={"seed_folder":str(folder.relative_to(root)), "multilayer_sha256":sha(multilayer),
             "color_pfm_sha256":sha(color), "albedo_pfm_sha256":sha(alb),
             "normal_pfm_sha256":sha(nrm), "output_pfm_sha256":sha(out),
             "max_abs_raw_vs_aov":beauty_delta, "max_abs_raw_vs_pfm":pfm_delta,
             "wall_seconds":elapsed, "cli_log":p.stdout[-2500:],
             "native":{"error":compare_images(reference,native),"detail":detail_fidelity(reference,native)},
             "standalone251":{"error":compare_images(reference,standalone),"detail":detail_fidelity(reference,standalone)},
             "direct_difference":compare_images(native,standalone)}
        second=folder/"reference_check.exr"
        if second.is_file():
            second_ref=read_arrays(second)["image"]
            row["second_ref"]={"native":compare_images(second_ref,native),
                               "standalone251":compare_images(second_ref,standalone),
                               "native_detail":detail_fidelity(second_ref,native),
                               "standalone_detail":detail_fidelity(second_ref,standalone)}
        rows.append(row)
    return {"oidn_version":"v2.5.1 official binary", "binary_sha256":sha(binary),
            "scene":metadata["scene"],"blender_version":metadata["blender"],
            "parameters":{"device":"cpu","quality":"high","hdr":True,"albedo":True,
                          "normal":True,"cleanAux":False},
            "warning":"Native compositor Accurate prefilter may differ from CLI defaults. References finite and seed independence unproven; comparison not universal quality.", "rows":rows}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--directory",type=Path,required=True)
    ap.add_argument("--oidn",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    result=evaluate(a.directory.resolve(),a.oidn.resolve())
    write_report(a.output,result)
    print("OIDN251",json.dumps([{"seed":r["seed_folder"],
        "native_rmse":r["native"]["error"]["rmse_linear"],
        "standalone_rmse":r["standalone251"]["error"]["rmse_linear"],
        "native_edge_rmse":r["native"]["detail"]["edge_gradient_rmse"],
        "standalone_edge_rmse":r["standalone251"]["detail"]["edge_gradient_rmse"],
        "native_vs_standalone_rmse":r["direct_difference"]["rmse_linear"]} for r in result["rows"]],indent=2))

if __name__=="__main__":main()
