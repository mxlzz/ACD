"""E0035: small compatibility/data contract, not a denoiser quality comparison."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from acd_lab.core import compare_images, rgb
from acd_lab.io import read_arrays, write_report


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def analyze(root: Path, capabilities: Path) -> dict:
    metadata = json.loads((root / "metadata.json").read_text())
    api = json.loads(capabilities.read_text())
    if metadata["blender"] != api["blender"]:
        raise ValueError("API scan and render must use the same Blender version")
    if (metadata["samples"], metadata["reference_samples"], metadata["resolution"]) != (16, 64, [128, 96]):
        raise ValueError("Unexpected E0035 sampling/resolution")
    if metadata["scene"] != "detail_target" or metadata["native_compositor_oidn"] is None:
        raise ValueError("Wrong scene or no native compositor OIDN")
    if metadata["cycles"]["use_denoising"] is not False or not metadata["capture_aov"]:
        raise ValueError("Cycles-internal denoising must remain OFF; AOVs required")
    required = {"Image", "Albedo", "Normal", "Prefilter", "Quality", "HDR"}
    if not required.issubset(api["denoise_inputs"]) or api["node_type"] != "CompositorNodeDenoise":
        raise ValueError("Compositor denoise API does not satisfy known contract")
    def load(name):
        return read_arrays(root / ("acd_compare_" + name + ".exr"))["image"]
    raw, native = load("Raw"), load("NATIVE_COMP_OIDN")
    standard, high, super_ = load("STANDARD"), load("HIGH"), load("SUPER")
    ref = read_arrays(root / "reference.exr")["image"]
    layer = read_arrays(root / "raw_multilayer.exr", layer=metadata["view_layer"])
    if not {"image", "denoising_albedo", "denoising_normal"}.issubset(layer):
        raise ValueError("Missing same-seed beauty/denoising guides")
    raw_delta = float(np.max(np.abs(rgb(raw) - rgb(layer["image"]))))
    if raw_delta > 1e-5:
        raise ValueError("Raw/multilayer beauty mismatch")
    return {
        "experiment": "E0035", "classification": "real Blender 128x96 compatibility smoke, not a quality ranking",
        "blender": metadata["blender"], "api": api,
        "resolution": metadata["resolution"], "samples": 16, "reference_samples": 64,
        "seed": metadata["seed"], "raw_multilayer_max_abs_delta": raw_delta,
        "standard_vs_native_compositor_rmse": compare_images(native, standard)["rmse_linear"],
        "standard_vs_native_compositor_max_abs_delta": float(np.max(np.abs(rgb(native) - rgb(standard)))),
        "exploratory_rmse_vs_unconverged_reference": {
            name: compare_images(ref, item)["rmse_linear"] for name, item in (
                ("Raw", raw), ("OIDN_compositor", native), ("ACD_Standard", standard),
                ("ACD_High", high), ("ACD_Super", super_))
        },
        "sha256_exr": {p.name: sha256(p) for p in sorted(root.glob("*.exr"))},
        "cycles_internal_output_compared": False,
        "limits": "64 spp reference unconverged. 5.2 and 5.3 noisy beauty/AOV can differ: do not attribute cross-version RMSE changes to OIDN.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--capabilities", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.directory, args.capabilities)
    write_report(args.output, result)
    print("ACD_E0035_CONTRACT", json.dumps({
        "blender": result["blender"],
        "raw_delta": result["raw_multilayer_max_abs_delta"],
        "standard_native_delta": result["standard_vs_native_compositor_rmse"],
        "cycles_internal_compared": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
