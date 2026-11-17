"""E0064: provenance and scene-only preview verification, no denoiser scoring."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from acd_lab.io import write_report
from scripts.lone_monk_contract_e0064 import SOURCE_SHA, SCENE, CAMERA, SAMPLES, SEED, sha256, frame_size


def analyze(root:Path)->dict:
    meta=json.loads((root/"framing_metadata.json").read_text())
    w,h=frame_size(*meta["original_source_resolution"])
    expected={
        "experiment":"E0064", "source_sha256":SOURCE_SHA,
        "original_active_scene":SCENE, "original_camera":CAMERA,
        "render_resolution":[w,h], "render_samples":SAMPLES,
        "render_seed":SEED, "render_compositor_disabled":True,
        "denoiser_disabled":True, "new_algorithm":False,
        "quality_result":False, "image_missing_count":0,
        "linked_library_count":0
    }
    for key,want in expected.items():
        if meta.get(key)!=want:
            raise ValueError(f"Framing contract mismatch {key}: {meta.get(key)!r}, expected {want!r}")
    if not str(meta.get("blender_version","")).startswith("5.2.4"):
        raise ValueError("Unexpected Blender version")
    path=root/"framing.png"
    with Image.open(path) as img:
        img.load()
        if img.format!="PNG" or img.size!=(w,h):
            raise ValueError("Wrong actual PNG size/format")
        arr=np.asarray(img.convert("RGB"),dtype=np.float32)/255.0
    luma=arr@np.array([.2126,.7152,.0722])
    quantiles=np.quantile(luma,[.01,.50,.99])
    spread=float(quantiles[2]-quantiles[0])
    if not np.isfinite(arr).all() or not np.isfinite(spread):
        raise ValueError("Nonfinite preview")
    return {
        "experiment":"E0064","source_sha256":SOURCE_SHA,
        "license":"CC BY, Carlo Bergonzini / Monorender",
        "source_camera":CAMERA,"source_scene":SCENE,
        "source_resolution":meta["original_source_resolution"],
        "preview_resolution":[w,h],
        "preview_samples":SAMPLES,"preview_seed":SEED,
        "preview_render_wall_seconds":meta["cycles_cpu_wall_seconds"],
        "preview_sha256":sha256(path),"preview_bytes":path.stat().st_size,
        "luma_p01_p50_p99":[round(float(x),6) for x in quantiles],
        "luma_98pct_range":round(spread,6),
        "usable_framing_preview":spread>.06,
        "raw_exr_produced":False,"denoiser_evaluated":False,
        "new_algorithm":False,"reference_available":False,
        "representative_roi_selected":False,"quality_claim_allowed":False,
        "next_gate":"Inspect architectural features in original camera preview. Preregister ROI prior to higher-spp reference or native OIDN benchmark."
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    a=parser.parse_args()
    d=analyze(a.directory)
    a.output.mkdir(parents=True,exist_ok=True)
    write_report(a.output/"E0064_RESULTS.json",d)
    md=[
        "# E0064 — Lone Monk original camera framing and render cost",
        "",
        "Carlo Bergonzini / Monorender, CC BY, official Blender Cycles demo. Blender 5.2.4.",
        "Only a source-camera 8spp preview; no denoiser, reference or ACD method tested.",
        "",
        "![Framing scene preview](../../benchmarks/results/lone_monk_e0064/framing.png)",
        "",
        f"- Source image dimensions: {d['source_resolution']}; original camera cam.001 unchanged.",
        f"- Preview: {d['preview_resolution']} at {SAMPLES}spp seed {SEED}.",
        f"- Cycles render seconds: {d['preview_render_wall_seconds']}.",
        f"- Luminance quantiles of display RGB: {d['luma_p01_p50_p99']}.",
        f"- Usable framing screen: {d['usable_framing_preview']}.",
        f"- SHA256: {d['preview_sha256']}.",
        "",
        "This image only establishes the existence/placement of physically relevant architectural features.",
        "Any ROI must be preregistered on original camera coordinate system BEFORE denoiser output.",
        "This is a development scene, not a blind holdout. Quality ranking is forbidden.",
        "",
        "[Provenance and metrics](E0064_RESULTS.json).",""
    ]
    (a.output/"E0064.md").write_text("\n".join(md))
    print("E0064_FRAMING_SCREEN",json.dumps({
        "resolution":d["preview_resolution"],"seconds":d["preview_render_wall_seconds"],
        "luma_spread":d["luma_98pct_range"],"usable":d["usable_framing_preview"]
    }))


if __name__=="__main__":
    main()
