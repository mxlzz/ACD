"""E0053 8spp + 32spp x2 feasibility pilot: validate only; never rank."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from acd_lab.io import read_arrays,write_report
from acd_lab.core import rgb,compare_images
from scripts.cozy_crop_e0053 import contract,SOURCE_SHA

FILES=("acd_compare_Raw.exr","acd_compare_NATIVE_COMP_OIDN.exr",
       "raw_multilayer.exr","reference.exr","reference_check.exr")

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""): h.update(chunk)
    return h.hexdigest()

def analyze(root):
    meta=json.loads((root/"metadata.json").read_text())
    expected={
        "scene":"external", "scene_name":"Main", "source_blend_sha256":SOURCE_SHA,
        "resolution":[1920,1808], "samples":8, "reference_samples":32,
        "seed":539, "reference_seed":8819, "second_reference":True,
        "capture_aov":True, "extra_input_seeds":[],
    }
    for k,v in expected.items():
        if meta.get(k)!=v: raise ValueError(f"E0053 source mismatch {k}: {meta.get(k)!r}")
    if not str(meta.get("blender","")).startswith("5.2.4"):
        raise ValueError("Blender must be 5.2.4")
    if meta.get("e0053_crop")!=contract(1920,1808):
        raise ValueError("E0053 crop metadata mismatch")
    array={p:rgb(read_arrays(root/p)["image"]) for p in FILES if p!="raw_multilayer.exr"}
    if any(a.shape!=(512,512,3) for a in array.values()):
        raise ValueError("Rendered crop is not exact 512x512")
    multi=read_arrays(root/"raw_multilayer.exr",layer=meta["view_layer"])
    if not {"image","denoising_albedo","denoising_normal"}.issubset(multi):
        raise ValueError("Denoiser AOVs missing")
    maxraw=float(np.max(np.abs(array["acd_compare_Raw.exr"]-rgb(multi["image"]))))
    if maxraw>1e-5:raise ValueError(f"Raw vs multilayer mismatch {maxraw}")
    refspread=compare_images(array["reference.exr"],array["reference_check.exr"])["rmse_linear"]
    if refspread<1e-8:raise ValueError("Reference pair is identical; check seed handling")
    elapsed=int((root/"wall_seconds.txt").read_text().strip())
    if elapsed<=0:raise ValueError("Missing positive render wall seconds")
    return {
        "experiment":"E0053", "classification":"Blender 5.2.4 real public scene high-density crop feasibility",
        "source":"Cozy Kitchen Nicole Morena", "license":"CC BY-SA",
        "source_sha256":SOURCE_SHA, "blender":meta["blender"],
        "virtual_full_frame":meta["resolution"], "crop":meta["e0053_crop"],
        "same_seed_raw_AOV_max_abs":maxraw, "AOV_available":True,
        "noisy_samples":8,"reference_samples":32,"reference_seeds":[8819,8922],
        "reference_pair_rmse":refspread,
        "raw_vs_oidn_output_rmse_NOT_quality":compare_images(
            array["acd_compare_Raw.exr"],array["acd_compare_NATIVE_COMP_OIDN.exr"])["rmse_linear"],
        "elapsed_wall_seconds_including_scene_load_and_output":elapsed,
        "source_output_sha256":{p:sha(root/p) for p in FILES},
        "reference_convergence_proven":False,"quality_ranking_allowed":False,
        "new_denoiser":False,"addon_modified":False,
        "decision":"FUNCTIONAL / COST PILOT ONLY: insufficient 32 spp refs for quality."
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    r=analyze(a.directory)
    a.output.mkdir(parents=True,exist_ok=True)
    write_report(a.output/"E0053_RESULTS.json",r)
    text=[
        "# E0053 — Cozy Kitchen detail_2 at virtual 1920px image density",
        "", "Functional/cost smoke. Source Nicole Morena CC BY-SA, Blender 5.2.4.",
        "Real Cycles source geometry/camera, 1920x1808 FOV, only 512x512 render-border crop.",
        "Input8spp seed539 and two 32spp references seeds8819/8922; AOV verified.",
        "",
        f"- Full pipeline wall seconds: **{r['elapsed_wall_seconds_including_scene_load_and_output']}**",
        f"- Raw vs same-render EXR beauty max absolute: **{r['same_seed_raw_AOV_max_abs']}**",
        f"- Finite 32spp interreference RMSE: **{r['reference_pair_rmse']:.6f}**",
        "- The reference pair is far too noisy to score OIDN. No winner, new model or addon changes.",
        "- Source E0021 ROI was already observed and its mapping was rounded; not a heldout test.",
        "- Estimate future render cost with separately observed pilot timings, not linear guesses about full-HD performance.",
        "", "[JSON with hashes and crop contract](E0053_RESULTS.json).",""
    ]
    (a.output/"E0053.md").write_text("\n".join(text))
    print("E0053_PASS_FUNCTIONAL",json.dumps({"wall":r["elapsed_wall_seconds_including_scene_load_and_output"],
        "raw_delta":r["same_seed_raw_AOV_max_abs"],"interreference_rmse":r["reference_pair_rmse"]}))

if __name__=="__main__":main()
