"""E0037: OIDN 2.5.1 CPU with frozen E0035 beauty and denoising AOVs.

Contract comparison only, without a converged reference.
Accurate-like is a three-step OIDN RT approximation of Blender Accurate,
not a claim that Blender uses identical weights, pre/post-processing or ISA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.io import read_arrays, write_report
from acd_lab.pfm import read_pfm, write_pfm

RUN = 43480823352
NAMES = ("acd_compare_Raw.exr", "acd_compare_NATIVE_COMP_OIDN.exr", "raw_multilayer.exr")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(2 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def only(root, name):
    matches = sorted(Path(root).rglob(name))
    if len(matches) != 1:
        raise ValueError(f"Expected unique {name}, found {len(matches)}")
    return matches[0]


def commands(binary, mode, folder):
    cmd = [str(binary), "-d", "cpu"]
    color = str(folder / "color.pfm")
    alb = str(folder / "albedo.pfm")
    nrm = str(folder / "normal.pfm")
    if mode == "raw_aux":
        return [cmd + ["--hdr", color, "--alb", alb, "--nrm", nrm,
                       "-q", "high", "--threads", "4", "-o", str(folder / "raw_aux.pfm")]]
    if mode == "accurate_like":
        out_alb = str(folder / "filtered_albedo.pfm")
        out_nrm = str(folder / "filtered_normal.pfm")
        return [
            cmd + ["--alb", alb, "-q", "high", "--threads", "4", "-o", out_alb],
            cmd + ["--nrm", nrm, "-q", "high", "--threads", "4", "-o", out_nrm],
            cmd + ["--hdr", color, "--alb", out_alb, "--nrm", out_nrm,
                   "--clean_aux", "-q", "high", "--threads", "4",
                   "-o", str(folder / "accurate_like.pfm")],
        ]
    raise ValueError("Unknown mode")


def source_arrays(source, permanent, version):
    meta = json.loads(only(source, "metadata.json").read_text())
    prior = permanent["reports_by_version"][version]
    if (meta["blender"] != prior["blender"] or not meta["blender"].startswith(version)
        or meta["resolution"] != [128, 96] or meta["seed"] != 539
        or meta["samples"] != 16 or prior["standard_vs_native_compositor_rmse"] != 0
        or prior["raw_multilayer_max_abs_delta"] != 0):
        raise ValueError("Not the frozen E0035 source contract")
    for name in NAMES:
        if digest(only(source, name)) != prior["sha256_exr"][name]:
            raise ValueError("E0035 input hash mismatch: " + name)
    raw = rgb(read_arrays(only(source, NAMES[0]))["image"])
    native = rgb(read_arrays(only(source, NAMES[1]))["image"])
    layer = read_arrays(only(source, NAMES[2]), layer=meta["view_layer"])
    if not {"image", "denoising_albedo", "denoising_normal"}.issubset(layer):
        raise ValueError("Missing E0035 denoising guides")
    arrays = {"color": raw, "albedo": rgb(layer["denoising_albedo"]),
              "normal": rgb(layer["denoising_normal"])}
    if raw.shape != (96, 128, 3) or native.shape != raw.shape:
        raise ValueError("Wrong source image size")
    if any(arr.shape != raw.shape or not np.isfinite(arr).all() for arr in [native,*arrays.values()]):
        raise ValueError("Inconsistent/nonfinite input")
    mismatch = float(np.max(np.abs(raw - rgb(layer["image"]))))
    if mismatch != 0:
        raise ValueError("Raw vs multilayer input mismatch")
    return arrays, native, meta


def evaluate(source, permanent, binary, output, version):
    arrays, native, meta = source_arrays(source, permanent, version)
    work = output / version.replace(".", "_")
    work.mkdir(parents=True, exist_ok=True)
    for name, data in arrays.items():
        path = work / (name + ".pfm")
        write_pfm(path, data)
        if not np.array_equal(read_pfm(path), data):
            raise ValueError("PFM roundtrip failed for " + name)
    result = {}
    for mode in ("raw_aux", "accurate_like"):
        steps = []
        for cmd in commands(binary, mode, work):
            start = time.perf_counter()
            finished = subprocess.run(cmd, capture_output=True, text=True, check=True)
            steps.append({"command": cmd[1:],
                          "wall_seconds": time.perf_counter() - start,
                          "stdout_tail": (finished.stdout + "\n" + finished.stderr)[-1200:]})
        path = work / (mode + ".pfm")
        output_rgb = rgb(read_pfm(path))
        if output_rgb.shape != native.shape or not np.isfinite(output_rgb).all():
            raise ValueError("Invalid standalone output")
        result[mode] = {
            "difference_from_native_compositor": compare_images(native, output_rgb),
            "max_absolute_difference": float(np.max(np.abs(native - output_rgb))),
            "sha256_output": digest(path),
            "command_steps": steps,
        }
    return {"blender": meta["blender"], "input_seed": meta["seed"],
            "source_sha256": {key:digest(work / (key+".pfm")) for key in arrays},
            "raw_aux": result["raw_aux"], "accurate_like": result["accurate_like"],
            "prefilter_vs_unfiltered": compare_images(
                read_pfm(work/"raw_aux.pfm"), read_pfm(work/"accurate_like.pfm"))}


def main():
    ap=argparse.ArgumentParser()
    for arg in ("oidn", "archive", "source52", "source53", "output"):
        ap.add_argument("--"+arg, type=Path, required=True)
    args=ap.parse_args()
    reference=json.loads(args.archive.read_text())
    if reference.get("source_run") != RUN:
        raise ValueError("Unexpected source run")
    binary=args.oidn.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    cases={
        "5.2.4":evaluate(args.source52,reference,binary,args.output,"5.2.4"),
        "5.3.0":evaluate(args.source53,reference,binary,args.output,"5.3.0")
    }
    data={"experiment":"E0037", "source_run":RUN,
          "oidn_release":"2.5.1", "oidn_binary_sha256":digest(binary),
          "cases":cases, "source_spp":16, "resolution":[128,96],
          "reference_convergence_proven":False,
          "caveat":"Single-seed same-input output differences, not denoiser quality or CPU speed ranking. Accurate-like may differ from actual Blender OIDN preprocessing and version."}
    write_report(args.output/"e0037_results.json",data)
    print("E0037_CLI_COMPLETED",json.dumps({
        version:{mode:cases[version][mode]["difference_from_native_compositor"]["rmse_linear"]
                 for mode in ("raw_aux", "accurate_like")}
        for version in cases},sort_keys=True))


if __name__=="__main__":
    main()
