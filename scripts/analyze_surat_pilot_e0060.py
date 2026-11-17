"""E0060 source-verified tiny Surat interior Raw/OIDN/reference cost pilot.

No quality claim; 64spp finite references. The model's own CC0 contribution
doesn't clear third-party rights of the represented architectural design.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from acd_lab.io import read_arrays,write_report
from acd_lab.core import compare_images,rgb

ZIP_SHA="721e77b401fba0fa5c3b9df13b09279c6d05781af865f2b63945e7e032e991a8"
INPUTS=("acd_compare_Raw.exr","acd_compare_NATIVE_COMP_OIDN.exr",
        "reference.exr","reference_check.exr","raw_multilayer.exr")

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as stream:
        for b in iter(lambda:stream.read(1048576),b""):h.update(b)
    return h.hexdigest()

def validate(meta,source_sha):
    expected={
        "scene":"external","scene_name":"Scene","active_camera":"CAM Office",
        "source_blend_sha256":source_sha,
        "resolution":[256,144],"samples":8,
        "reference_samples":64,"seed":539,"reference_seed":8819,
        "second_reference":True,"second_reference_seed":8922,
        "extra_input_seeds":[],"capture_aov":True,
    }
    for k,v in expected.items():
        if meta.get(k)!=v:raise ValueError(f"E0060 invalid {k}: {meta.get(k)!r}")
    if not str(meta.get("blender","")).startswith("5.2.4"):
        raise ValueError("Wrong Blender version")
    if meta["cycles"]["use_denoising"] or meta["cycles"]["use_adaptive_sampling"]:
        raise ValueError("Native internal denoise/adaptive must be OFF")
    if not meta.get("native_compositor_oidn"):
        raise ValueError("Native compositor OIDN missing")

def analyze(root,source_zip,source_sha):
    if not source_zip.is_file() or source_zip.stat().st_size!=166627773 or sha(source_zip)!=ZIP_SHA:
        raise ValueError("Wrong published source archive")
    meta=json.loads((root/"metadata.json").read_text())
    validate(meta,source_sha)
    imgs={}
    hashes={}
    for name in INPUTS:
        p=root/name
        hashes[name]=sha(p)
        if name!="raw_multilayer.exr":
            data=rgb(read_arrays(p)["image"])
            if data.shape!=(144,256,3):raise ValueError("Expected native256x144 pilot shape")
            imgs[name]=data
    multi=read_arrays(root/"raw_multilayer.exr",layer=meta["view_layer"])
    if not {"image","denoising_albedo","denoising_normal"}.issubset(multi):
        raise ValueError("Original AOV guides missing")
    delta=float(np.max(np.abs(imgs["acd_compare_Raw.exr"]-rgb(multi["image"]))))
    if delta>1e-5:raise ValueError("Raw/AOV mismatch")
    pair=compare_images(imgs["reference.exr"],imgs["reference_check.exr"])["rmse_linear"]
    if pair<1e-8:raise ValueError("No measurable reference difference")
    wall=int((root/"wall_seconds.txt").read_text().strip())
    if wall<=0:raise ValueError("Missing time")
    return {
        "experiment":"E0060","source":"Surat Diamond Bourse model release v1.0.1",
        "archive_sha256":ZIP_SHA,"source_blend_sha256":source_sha,
        "contributor_model_cc0_only":True,"underlying_architecture_rights_cleared":False,
        "scene":"Scene","camera":"CAM Office","blender":meta["blender"],
        "resolution":[256,144],"noisy_spp":8,"reference_spp":64,
        "input_seed":539,"reference_seeds":[8819,8922],
        "raw_beauty_AOV_max_abs":delta,
        "reference_pair_rmse":pair,
        "original_albedo_normal_guides_available":True,
        "total_wall_seconds_including_load_and_write":wall,
        "file_sha256":hashes,"new_denoiser":False,
        "reference_convergence_proven":False,"quality_ranking_allowed":False,
        "render_or_model_redistributed":False,
        "decision":"Feasibility only: do not infer OIDN detail fidelity or compare to other scenes with finite64spp references. Assess scene suitability, rights and cost before high-resolution source independent validation."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--source-zip",required=True,type=Path)
    p.add_argument("--source-sha256",required=True)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=analyze(args.directory,args.source_zip,args.source_sha256)
    args.output.mkdir(parents=True,exist_ok=True)
    write_report(args.output/"E0060_RESULTS.json",report)
    lines=[
        "# E0060 — Surat CAM Office, small reference feasibility and cost",
        "",
        "Blender5.2.4, public model contribution CC0 but architectural design rights not cleared.",
        "Camera CAM Office original; single 256x144 8spp noisy input; 64spp×2 references, native compositor OIDN and original Raw share one RenderLayer. No images/model are redistributed.",
        "",
        "- Total CPU rendering + loading and file writes: "+str(report["total_wall_seconds_including_load_and_write"])+" seconds",
        "- Raw vs same-render beauty AOV max abs: "+str(report["raw_beauty_AOV_max_abs"]),
        "- RMSE between finite 64spp references: "+str(report["reference_pair_rmse"]),
        "",
        "No denoiser quality ranking, no ground truth convergence, no ACD algorithm or addon change.",
        "This scene cannot serve as public holdout until underlying architectural rights are resolved. "
        "Pilot resolution cannot substantiate detail at final delivery scale.",
        "",
        "[Exact source and output hashes](E0060_RESULTS.json)."
    ]
    (args.output/"E0060.md").write_text("\n".join(lines)+"\n")
    print("E0060_ONLY_FEASIBILITY",json.dumps({
        "wall_seconds":report["total_wall_seconds_including_load_and_write"],
        "raw_aov_delta":delta if False else report["raw_beauty_AOV_max_abs"],
        "ref_pair_rmse":report["reference_pair_rmse"]},sort_keys=True))

if __name__=="__main__":main()
