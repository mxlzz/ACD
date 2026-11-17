"""E0036 cross-output comparison on a single actual Cycles RenderLayer."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from acd_lab.core import compare_images, rgb
from acd_lab.io import read_arrays, write_report


def scores(raw, internal, compositor):
    a,b,c = (rgb(x) for x in (raw,internal,compositor))
    if a.shape != b.shape or a.shape != c.shape:
        raise ValueError("E0036 RGB outputs must have identical dimensions")
    return {
        "raw_vs_internal": compare_images(a,b),
        "raw_vs_compositor": compare_images(a,c),
        "internal_vs_compositor": compare_images(b,c),
        "internal_compositor_max_abs_diff": float(np.max(np.abs(b-c))),
        "internal_compositor_exact_match": bool(np.array_equal(b,c)),
        "no_ground_truth_used": True,
    }


def analyze(root):
    meta=json.loads((root/"e0036_metadata.json").read_text())
    if meta["raw_from_same_layers"] is not True or meta["cycles_scene_use_denoising"] is not True:
        raise ValueError("Not a common Cycles render with internal denoising enabled")
    read=lambda name:read_arrays(root/("acd_e0036_"+name+".exr"))["image"]
    result=scores(read("Raw"),read("CyclesInternal"),read("CompositorOIDN"))
    return {"experiment":"E0036","blender":meta["blender"],"shared_render":True,
            "input_seed":meta["seed"],"sampling":meta["samples"],
            "native_internal_setting":meta["cycles_scene_denoiser"],
            "compositor_setting":meta["compositor"],"metrics":result,
            "source_metadata":meta,
            "caveat":"Single-render difference isolates implementations on one noise realization; without a converged reference no quality winner or speed comparison."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data=analyze(a.directory)
    write_report(a.output,data)
    print("ACD_E0036_ANALYSIS",json.dumps({"blender":data["blender"],
        "raw_vs_internal":data["metrics"]["raw_vs_internal"]["rmse_linear"],
        "raw_vs_compositor":data["metrics"]["raw_vs_compositor"]["rmse_linear"],
        "internal_vs_compositor":data["metrics"]["internal_vs_compositor"]["rmse_linear"],
        "exact_match":data["metrics"]["internal_compositor_exact_match"]},sort_keys=True))


if __name__=="__main__": main()
