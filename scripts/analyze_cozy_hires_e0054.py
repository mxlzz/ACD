"""E0054: real Blender 5.2.4 Cozy detail_2 same-Raw 24spp vs 512spp refs.

No ACD improvement method is tested. Positive edge screens identify possible
native OIDN residuals, not proof of hallucination/loss or a product gain.
"""
import argparse, hashlib, json, statistics
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images, rgb
from acd_lab.io import read_arrays, write_report
from scripts.cozy_crop_e0053 import contract, SOURCE_SHA, INNER
from scripts.analyze_cozy_consensus_e0052 import inspect_region, SEEDS

METHODS=("Raw","STANDARD","NATIVE_COMP_OIDN")


def validate_meta(meta):
    expected={
        "scene":"external", "scene_name":"Main", "source_blend_sha256":SOURCE_SHA,
        "resolution":[1920,1808], "samples":24, "reference_samples":512,
        "seed":539, "extra_input_seeds":[911,1337],
        "reference_seed":8819, "second_reference":True, "capture_aov":True,
        "e0053_crop":contract(1920,1808)
    }
    for field,want in expected.items():
        if meta.get(field)!=want:
            raise ValueError(f"E0054 metadata violates {field}: {meta.get(field)!r}")
    if not str(meta.get("blender","")).startswith("5.2.4"):
        raise ValueError("Unexpected Blender engine/version")
    if not meta.get("native_compositor_oidn"):
        raise ValueError("Native OIDN compositor absent")


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""):h.update(part)
    return h.hexdigest()


def load_rgb(path):
    value=rgb(read_arrays(path)["image"])
    if value.shape!=(512,512,3):
        raise ValueError(f"Unexpected EXR crop dimensions: {path} {value.shape}")
    return value


def evaluate(root):
    meta=json.loads((root/"metadata.json").read_text())
    validate_meta(meta)
    refs=[load_rgb(root/"reference.exr"), load_rgb(root/"reference_check.exr")]
    hashes={"references":{name:sha(root/name) for name in
                           ("reference.exr","reference_check.exr")}}
    by_seed={}
    for seed in SEEDS:
        folder=root if seed==539 else root/f"seed_{seed}"
        images={method:load_rgb(folder/f"acd_compare_{method}.exr") for method in METHODS}
        maxsame=float(np.max(np.abs(images["STANDARD"]-images["NATIVE_COMP_OIDN"])))
        if maxsame>1e-5:raise ValueError(f"Same-Raw Standard vs OIDN mismatch seed {seed}: {maxsame}")
        aov=read_arrays(folder/"raw_multilayer.exr",layer=meta["view_layer"])
        if not {"image","denoising_albedo","denoising_normal"}.issubset(aov):
            raise ValueError(f"Missing original denoiser guides seed {seed}")
        maxraw=float(np.max(np.abs(images["Raw"]-rgb(aov["image"]))))
        if maxraw>1e-5:raise ValueError(f"Raw/AOV mismatch seed {seed}: {maxraw}")
        by_seed[seed]=images
        hashes[str(seed)]={p:sha(folder/p) for p in
                            ("acd_compare_Raw.exr","acd_compare_STANDARD.exr",
                             "acd_compare_NATIVE_COMP_OIDN.exr","raw_multilayer.exr")}
    for seed in (911,1337):
        if compare_images(by_seed[539]["Raw"],by_seed[seed]["Raw"])["rmse_linear"]<1e-6:
            raise ValueError("Input seeds have no measurable variation")
    center=inspect_region(refs[0],refs[1],by_seed,INNER)
    full=inspect_region(refs[0],refs[1],by_seed,(0,0,512,512))
    x,y,w,h=INNER
    sl=(slice(y,y+h),slice(x,x+w))
    pair=compare_images(refs[0][sl],refs[1][sl])["rmse_linear"]
    native_rmse=[center["scores"][str(seed)]["NATIVE_COMP_OIDN"][f"rmse_ref{i}"]
                 for seed in SEEDS for i in (1,2)]
    mean_native=statistics.fmean(native_rmse)
    if pair<1e-8:raise ValueError("Reference pair unexpectedly identical")
    elapsed=int((root/"wall_seconds.txt").read_text().strip())
    if elapsed<=0:raise ValueError("Missing positive wall time")
    return {
        "experiment":"E0054","source":"Cozy Kitchen © Nicole Morena CC BY-SA",
        "source_sha256":SOURCE_SHA,"blender":meta["blender"],
        "source_output_resolution":meta["resolution"],"actual_render_crop":meta["e0053_crop"],
        "samples":24,"input_seeds":list(SEEDS),"reference_samples":512,
        "reference_seeds":[8819,8922],
        "same_seed_raw_AOV_and_native_baseline_verified":True,
        "reference_pair_rmse_in_center":pair,
        "mean_native_rmse_to_two_refs_in_center":mean_native,
        "reference_disagreement_relative_to_native_rmse":pair/max(mean_native,1e-12),
        "mean_native_rmse_per_ref":[statistics.fmean(
            center["scores"][str(seed)]["NATIVE_COMP_OIDN"][f"rmse_ref{i}"]
            for seed in SEEDS) for i in (1,2)],
        "center":center,"full_crop":full,"elapsed_wall_seconds":elapsed,
        "hashes":hashes,
        "new_denoiser":False,"reference_convergence_proven":False,
        "perceptual_quality_established":False,
        "valid_generalization_to_unseen_scene":False,
        "conclusion":"DESCRIPTIVE only. Two finite references and one already-observed stylized scene do not establish quality superiority; select next independent representative scene or improve reference confidence before new algorithm."
    },by_seed,refs


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result,inputs,refs=evaluate(a.directory)
    a.output.mkdir(parents=True,exist_ok=True)
    write_report(a.output/"E0054_RESULTS.json",result)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    x,y,w,h=INNER
    panels=[("Raw24spp",inputs[539]["Raw"]),("Native OIDN24spp",inputs[539]["NATIVE_COMP_OIDN"]),
            ("Ref512 A",refs[0]),("Ref512 B",refs[1])]
    canvas=Image.new("RGB",(2*w+42,2*(h+34)+20),(29,29,29))
    draw=ImageDraw.Draw(canvas)
    for i,(name,data) in enumerate(panels):
        px=12+(i%2)*(w+12)
        py=12+(i//2)*(h+34)
        canvas.paste(Image.fromarray(display_rgb(data[y:y+h,x:x+w])),(px,py+24))
        draw.text((px+3,py+3),name,fill=(246,246,246))
    canvas.save(a.output/"E0054_1to1.png",optimize=True)
    ratio=result["reference_disagreement_relative_to_native_rmse"]
    center=result["center"]
    gains=[center["scores"][str(s)]["NATIVE_COMP_OIDN"]["projected_edge_gain"] for s in SEEDS]
    lines=[
        "# E0054 — Cozy detail_2 at virtual 1920px: actual OIDN and two finite references",
        "", "Source: Nicole Morena, Cozy Kitchen CC BY-SA; Blender5.2.4, CPU.",
        "Noisy 24spp ×3 seeds and 512spp ×2 independent reference seeds; "
        "true 512² crop at native 1920px camera density, centered 360².",
        "All denoisers use same Raw per seed. No original ACD algorithm tested.",
        "",
        "![Raw, OIDN, two references on the same diagnostic transfer](../../benchmarks/results/cozy_e0054/E0054_1to1.png)",
        "",
        f"- Wall seconds, including all five Cycles renders and file writes: {result['elapsed_wall_seconds']}",
        f"- Reference1 vs reference2 HDR RMSE (central ROI): {result['reference_pair_rmse_in_center']:.6f}",
        f"- Native OIDN mean HDR RMSE against both finite refs: {result['mean_native_rmse_to_two_refs_in_center']:.6f}",
        f"- Reference disagreement / OIDN error ratio: {ratio:.3f}; ratio alone is not convergence proof.",
        f"- Common-reference edge mask pairs: {center['selected_reference_consensus_pairs']}",
        f"- OIDN projected edge gain, 3 noisy seeds: {', '.join(f'{v:.3f}' if v is not None else 'n/a' for v in gains)}",
        f"- Pre-registered attenuation screen on center: {center['persistent_attenuation_screen']}.",
        "",
        "All ROI and masks derived from two finite references; E0021 detail_2 was already observed, "
        "and cannot be heldout. The reference pair can share bias. The crop excludes outer 76px "
        "but denoiser receptive-field border effects are not eliminated by proof.",
        "Preview has a shared diagnostic transfer, not Blender OCIO/AgX. The test does "
        "not demonstrate an improvement over OIDN or independent generalization.",
        "",
        "[Exact hashes and per-seed results](E0054_RESULTS.json).",""
    ]
    (a.output/"E0054.md").write_text("\n".join(lines))
    print("E0054_RESULT",json.dumps({
        "wall":result["elapsed_wall_seconds"],"pair_rmse":result["reference_pair_rmse_in_center"],
        "oidn_mean_rmse":result["mean_native_rmse_to_two_refs_in_center"],
        "ratio":ratio,"pairs":center["selected_reference_consensus_pairs"],
        "gain":gains,"screen":center["persistent_attenuation_screen"]
    },sort_keys=True))


if __name__=="__main__":main()
