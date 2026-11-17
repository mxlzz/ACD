"""E0065: real full-scale architectural detail residual diagnostic, fixed E0064 ROI.

No learned/posthoc denoiser or sharpening. Same noisy Cycles RenderLayer per
seed for Raw, addon STANDARD and native compositor OIDN; two finite 512spp
references do NOT establish ground truth. Metrics on *fixed physical ROIs*.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import statistics
from pathlib import Path
import numpy as np
from acd_lab.io import read_arrays, write_report
from acd_lab.core import rgb, compare_images
from scripts.lone_monk_crop_e0065 import contract, SOURCE_SHA, SOURCE_PREVIEW_SHA, REGIONS

SEEDS=(539,911,1337)
METHODS=("Raw","STANDARD","NATIVE_COMP_OIDN")
REFS=("reference.exr","reference_check.exr")
EXPECTED={
    "scene":"external","scene_name":"daylight",
    "source_blend_sha256":SOURCE_SHA,
    "resolution":[1920,1440], "samples":24,
    "reference_samples":512,"seed":539,
    "extra_input_seeds":[911,1337],
    "reference_seed":8819,"second_reference":True,
    "capture_aov":True,"e0065_crop":contract(1920,1440),
}


def hashfile(p):
    d=hashlib.sha256()
    with p.open("rb") as stream:
        for ch in iter(lambda:stream.read(1024*1024),b""):
            d.update(ch)
    return d.hexdigest()


def inspect_meta(meta):
    for key,value in EXPECTED.items():
        if meta.get(key)!=value:
            raise ValueError(f"E0065 metadata mismatch {key}: {meta.get(key)!r}")
    if not str(meta.get("blender","")).startswith("5.2.4"):
        raise ValueError("E0065 requires Blender 5.2.4")
    if not meta.get("native_compositor_oidn"):
        raise ValueError("Missing native OIDN baseline")
    if meta.get("cycles",{}).get("use_adaptive_sampling") is not False:
        raise ValueError("Adaptive sampling must be OFF for reference protocol")
    if meta.get("cycles",{}).get("use_denoising") is not False:
        raise ValueError("Cycles internal denoising must be OFF")


def load(path):
    val=rgb(read_arrays(path)["image"])
    if val.shape!=(512,512,3) or not np.isfinite(val).all():
        raise ValueError(f"E0065 wrong shape or nonfinite EXR: {path}")
    return val


def gradients(v):
    lum=rgb(v)@np.array([.2126,.7152,.0722],dtype=np.float64)
    encoded=np.arcsinh(lum)
    return np.concatenate([np.diff(encoded,axis=0).ravel(),
                           np.diff(encoded,axis=1).ravel()])


def rmse(v,w):
    return float(np.sqrt(np.mean((np.asarray(v,dtype=np.float64)-
                                  np.asarray(w,dtype=np.float64))**2)))


def evaluate_region(name,region,refs,by_seed):
    x,y,w,h=region
    if x<0 or y<0 or x+w>512 or y+h>512:
        raise ValueError("ROI exceeds true crop")
    sl=(slice(y,y+h),slice(x,x+w))
    a,b=[r[sl] for r in refs]
    ref_pair=compare_images(a,b)["rmse_linear"]
    g1,g2=gradients(a),gradients(b)
    ref_gradient=rmse(g1,g2)
    scores={}
    for seed in SEEDS:
        scores[str(seed)]={}
        for name_of_method in METHODS:
            pixel=by_seed[seed][name_of_method][sl]
            g=gradients(pixel)
            scores[str(seed)][name_of_method]={
                "rmse_linear_refA":compare_images(pixel,a)["rmse_linear"],
                "rmse_linear_refB":compare_images(pixel,b)["rmse_linear"],
                "gradient_rmse_asinh_refA":rmse(g,g1),
                "gradient_rmse_asinh_refB":rmse(g,g2),
                "gradient_amplitude_rms":float(np.sqrt(np.mean(g**2))),
            }
    native_errors=[
        scores[str(seed)]["NATIVE_COMP_OIDN"][key]
        for seed in SEEDS for key in ("rmse_linear_refA","rmse_linear_refB")
    ]
    gradient_errors=[
        scores[str(seed)]["NATIVE_COMP_OIDN"][key]
        for seed in SEEDS for key in ("gradient_rmse_asinh_refA","gradient_rmse_asinh_refB")
    ]
    mean_native=statistics.fmean(native_errors)
    mean_grad=statistics.fmean(gradient_errors)
    return {
        "region_name":name,"fixed_roi_xywh":list(region),
        "reference_pair_rmse_linear":ref_pair,
        "reference_pair_gradient_rmse_asinh":ref_gradient,
        "native_oidn_mean_linear_rmse_to_finite_refs":mean_native,
        "native_oidn_mean_gradient_rmse_to_finite_refs":mean_grad,
        "reference_spread_over_native_linear_error":ref_pair/max(mean_native,1e-12),
        "reference_gradient_spread_over_native_gradient_error":ref_gradient/max(mean_grad,1e-12),
        "relative_reference_spread_screen_lt_0_50":bool(ref_pair/max(mean_native,1e-12)<.50),
        "scores_per_seed":scores,
    }


def analyze(root):
    meta=json.loads((root/"metadata.json").read_text())
    inspect_meta(meta)
    refs=[load(root/p) for p in REFS]
    if compare_images(refs[0],refs[1])["rmse_linear"]<1e-8:
        raise ValueError("Reference images identical: invalid nominal seed streams")
    inputs,sha={},{}
    sha["references"]={p:hashfile(root/p) for p in REFS}
    max_raw,max_baseline=0.,0.
    for seed in SEEDS:
        folder=root if seed==539 else root/f"seed_{seed}"
        images={method:load(folder/f"acd_compare_{method}.exr") for method in METHODS}
        raw=read_arrays(folder/"raw_multilayer.exr",layer=meta["view_layer"])
        if not {"image","denoising_albedo","denoising_normal"}.issubset(raw):
            raise ValueError(f"Missing source Albedo/Normal AOV seed{seed}")
        same=np.max(np.abs(images["Raw"]-rgb(raw["image"])))
        if not np.isfinite(same) or same>1e-5:
            raise ValueError(f"Raw multilayer mismatch {seed}: {same}")
        max_raw=max(max_raw,float(same))
        native=np.max(np.abs(images["STANDARD"]-images["NATIVE_COMP_OIDN"]))
        if not np.isfinite(native) or native>1e-5:
            raise ValueError(f"STANDARD baseline differs native {seed}: {native}")
        max_baseline=max(max_baseline,float(native))
        sha[str(seed)]={p:hashfile(folder/p) for p in
                        ("raw_multilayer.exr",)+tuple(f"acd_compare_{m}.exr" for m in METHODS)}
        inputs[seed]=images
    for a,b in ((539,911),(539,1337),(911,1337)):
        if compare_images(inputs[a]["Raw"],inputs[b]["Raw"])["rmse_linear"]<1e-6:
            raise ValueError("Noisy inputs not materially different; repeat seed audit")
    sec=int((root/"wall_seconds.txt").read_text().strip())
    if sec<=0:
        raise ValueError("Missing real wall time")
    regions={name:evaluate_region(name,rect,refs,inputs)
             for name,rect in REGIONS.items()}
    return {
        "experiment":"E0065",
        "source_scene":"Official Lone Monk, Carlo Bergonzini / Monorender, CC BY",
        "original_source_sha256":SOURCE_SHA,
        "original_unfiltered_preview_sha256":SOURCE_PREVIEW_SHA,
        "preview_selected_semantic_feature":"central stone portal with cornice, pediment, columns and arch",
        "blender":meta["blender"],
        "roi_contract":meta["e0065_crop"],
        "noisy_spp":24,"noisy_seeds":list(SEEDS),
        "reference_spp":512,"reference_seeds":[8819,8922],
        "actual_wall_seconds":sec,
        "raw_same_render_max_abs":max_raw,
        "standard_vs_native_max_abs":max_baseline,
        "same_noisy_Raw_for_every_method":True,
        "reference_convergence_proven":False,
        "reference_statistical_independence_proven":False,
        "reference_visual_ground_truth_established":False,
        "quality_superiority_tested":False,
        "new_denoiser":False,
        "architecture_holdout":False,
        "regions":regions,"source_output_sha256":sha,
        "decision":"Descriptive baseline residual on an architectural ROI fixed before viewing denoised output. Finite references do not prove physical ground truth. No algorithm/fork/merge before inspecting residuals and reference uncertainty; next benchmark must include extra-spp control and independent author holdout."
    },inputs,refs


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    data,by_seed,refs=analyze(a.directory)
    a.output.mkdir(parents=True,exist_ok=True)
    write_report(a.output/"E0065_RESULTS.json",data)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    x,y,w,h=REGIONS["portal_architecture"]
    pic=Image.new("RGB",(2*w+36,2*(h+32)+20),(35,35,35))
    draw=ImageDraw.Draw(pic)
    frames=[
        ("Raw 24spp seed539",by_seed[539]["Raw"]),
        ("Native compositor OIDN 24spp seed539",by_seed[539]["NATIVE_COMP_OIDN"]),
        ("Reference 512spp seed8819",refs[0]),
        ("Reference 512spp seed8922",refs[1]),
    ]
    for i,(label,img) in enumerate(frames):
        ox=12+(i%2)*(w+12)
        oy=10+(i//2)*(h+32)
        draw.text((ox,oy+2),label,fill=(245,245,245))
        pic.paste(Image.fromarray(display_rgb(img[y:y+h,x:x+w])),(ox,oy+22))
    pic.save(a.output/"E0065_1to1.png",optimize=True)
    r=data["regions"]["portal_architecture"]
    notes=[
        "# E0065 — Lone Monk: physically identified stone portal, native OIDN finite-reference residual",
        "",
        "Official Blender Cycles demo, Carlo Bergonzini / Monorender CC BY. Blender5.2.4 CPU.",
        "Portal/cornice/columns visible on original-camera E0064 unfiltered 8spp preview; "
        "fixed crop at virtual1920x1440 before observing OIDN outputs.",
        "Three independent-seed 24spp noisy RenderLayers share Raw/AOV with OIDN; "
        "two 512spp reference renders are finite, NOT certified converged.",
        "",
        "![Same-input Raw/OIDN and two finite references](../../benchmarks/results/lone_monk_e0065/E0065_1to1.png)",
        "",
        f"- Full 5-render CPU workflow elapsed wall: {data['actual_wall_seconds']} seconds.",
        f"- Same-sample Raw EXR beauty/AOV max absolute: {data['raw_same_render_max_abs']}.",
        f"- Standard branch/native compositor OIDN max absolute: {data['standard_vs_native_max_abs']}.",
        f"- Portal center, reference/reference HDR RMSE: {r['reference_pair_rmse_linear']:.6f}.",
        f"- Portal center, mean native OIDN vs both finite refs HDR RMSE: {r['native_oidn_mean_linear_rmse_to_finite_refs']:.6f}.",
        f"- Ref/reference spread divided by OIDN/reference error: {r['reference_spread_over_native_linear_error']:.3f}.",
        f"- Reference pair asinh-gradient RMSE: {r['reference_pair_gradient_rmse_asinh']:.6f}.",
        f"- Native OIDN mean asinh-gradient RMSE to refs: {r['native_oidn_mean_gradient_rmse_to_finite_refs']:.6f}.",
        "",
        "| Fixed semantic region | Ref/Ref HDR RMSE | Native/finite-ref RMSE | Relative uncertainty |",
        "|---|---:|---:|---:|",
    ]
    for name,reg in data["regions"].items():
        notes.append(f"| {name} | {reg['reference_pair_rmse_linear']:.6f} | "
                     f"{reg['native_oidn_mean_linear_rmse_to_finite_refs']:.6f} | "
                     f"{reg['reference_spread_over_native_linear_error']:.3f} |")
    notes += [
        "",
        "**Interpretation:** These quantify residual and reference uncertainty, not a correctable "
        "OIDN-specific bias or ACD win. The source has already been observed; not a holdout. "
        "No hand-picked mask from OIDN, no altered native settings, no algorithm.",
        "A positive residual does not imply denoising makes a physical edge worse; "
        "noise, finite references, spectral/nonlinear features and renderer variance remain.",
        "Only if the physical detail residual exceeds reference uncertainty convincingly, "
        "inspect paired error maps and test against added Cycles spp at equal cost before "
        "postprocess research. Otherwise stop the idea.",
        "",
        "[Immutable method/metadata/hashes and per-seed metrics](E0065_RESULTS.json).",""
    ]
    (a.output/"E0065.md").write_text("\n".join(notes))
    print("E0065_REAL_PORTAL_DIAGNOSTIC",json.dumps({
        "seconds":data["actual_wall_seconds"],
        "reference_pair":r["reference_pair_rmse_linear"],
        "native_error":r["native_oidn_mean_linear_rmse_to_finite_refs"],
        "reference_relative":r["reference_spread_over_native_linear_error"]
    },sort_keys=True))


if __name__=="__main__":
    main()
