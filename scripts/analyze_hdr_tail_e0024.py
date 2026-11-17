"""Postprocess already-rendered Terraced Houses EXR with identical HDR masks."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from acd_lab.hdr_tail import hdr_tail_breakdown
from acd_lab.io import read_arrays, write_report

FIXTURE_SHA = "37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84"
METHODS = ("STANDARD", "HIGH", "SUPER", "NATIVE_COMP_OIDN")


def analyze(root: Path) -> dict:
    meta = json.loads((root / "metadata.json").read_text())
    if meta["source_blend_sha256"] != FIXTURE_SHA:
        raise ValueError("Wrong source scene for E0024")
    if not meta["second_reference"]:
        raise ValueError("E0024 requires two high-spp references")
    records = []
    folders = [root] + sorted(x for x in root.glob("seed_*") if x.is_dir())
    for reference_name in ("reference.exr", "reference_check.exr"):
        reference = read_arrays(root / reference_name)["image"]
        for folder in folders:
            raw = read_arrays(folder / "acd_compare_Raw.exr")["image"]
            methods = {m: read_arrays(folder / f"acd_compare_{m}.exr")["image"]
                       for m in METHODS}
            r = hdr_tail_breakdown(reference, raw, methods)
            masks = {}
            for key, mask in r["masks"].items():
                masks[key] = {
                    "selection": mask["mask_origin"],
                    "mask_count": mask["pixel_count"],
                    "mask_hash": mask["mask_coordinate_hash"],
                    "methods": {method: {
                        "rmse_full": v["rmse_full"],
                        "mae_full": v["mae_full"],
                        "rmse_inside": v["rmse_inside"],
                        "rmse_outside": v["rmse_outside"],
                        "sse_fraction_inside": v["sse_fraction_inside"],
                        "mae_outside": v["mae_outside"]
                    } for method, v in mask["methods"].items()}
                }
            records.append({
                "seed": folder.name if folder != root else "seed_539",
                "reference": reference_name,
                "masks": masks,
            })
    out = {
        "experiment": "E0024",
        "source_sha": FIXTURE_SHA,
        "original_render_run": 43291659387,
        "seed_count": len(folders),
        "reference_count": 2,
        "mask_fraction": .01,
        "records": records,
        "warning": (
            "Diagnostic only: the raw-error-selected mask favors the raw image; "
            "reference brightest is finite-spp HDR. Already-observed scene: "
            "not an untouched validation set for future changes."
        ),
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--directory", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    data = analyze(args.directory.resolve())
    write_report(args.output, data)
    for reference in ("reference.exr", "reference_check.exr"):
        group = [x for x in data["records"] if x["reference"] == reference]
        for mask in ("reference_brightest", "raw_largest_errors"):
            print("ACD_HDR_TAIL", reference, mask)
            for method in ("Raw", *METHODS):
                x = [e["masks"][mask]["methods"][method] for e in group]
                print(json.dumps({
                    "method": method,
                    "mean_rmse_full": sum(y["rmse_full"] for y in x)/len(x),
                    "mean_rmse_inside": sum(y["rmse_inside"] for y in x)/len(x),
                    "mean_rmse_outside": sum(y["rmse_outside"] for y in x)/len(x),
                    "mean_sse_fraction_inside": sum(y["sse_fraction_inside"] for y in x)/len(x)
                },sort_keys=True))


if __name__ == "__main__":
    main()
