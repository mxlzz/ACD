"""Read E0023 original EXRs and diagnose signed HDR highlight bias.

NO new render. No changes to OIDN or ACD. Highlight ROI uses only the
corresponding high-spp reference, never the denoised candidates.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from acd_lab.hdr_tail import highlight_signed_bias
from acd_lab.io import read_arrays, write_report

SOURCE_SHA = "37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84"
METHODS = ("STANDARD", "HIGH", "SUPER", "NATIVE_COMP_OIDN")


def analyze(root: Path) -> dict:
    meta=json.loads((root / "metadata.json").read_text())
    if meta["source_blend_sha256"] != SOURCE_SHA or not meta.get("second_reference"):
        raise ValueError("Requires exact Terraced E0023 source and two references")
    refs=("reference.exr", "reference_check.exr")
    folders=[root]+sorted(x for x in root.glob("seed_*") if x.is_dir())
    rows=[]
    for refname in refs:
        ref=read_arrays(root/refname)["image"]
        for folder in folders:
            raw=read_arrays(folder/"acd_compare_Raw.exr")["image"]
            outputs={name:read_arrays(folder/f"acd_compare_{name}.exr")["image"]
                     for name in METHODS}
            detail=highlight_signed_bias(ref,raw,outputs)
            rows.append({
                "reference":refname,
                "seed":folder.name if folder!=root else "seed_539",
                "mask_sha256":detail["mask_sha256"],
                "pixel_count":detail["selected_pixel_count"],
                "methods":detail["methods"],
            })
    return {
        "experiment":"E0025",
        "source_run":43291659387,
        "source_sha256":SOURCE_SHA,
        "reference_count":len(refs),
        "input_seed_count":len(folders),
        "rows":rows,
        "warning":"Reference-selected bright ROI. Descriptive finite-spp signed luminance, not proof of emission, filter mechanism or quality. This fixture has been examined; not blind."
    }


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--directory",type=Path,required=True)
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    data=analyze(args.directory.resolve())
    write_report(args.output,data)
    for ref in ("reference.exr","reference_check.exr"):
        subset=[x for x in data["rows"] if x["reference"]==ref]
        print("ACD_SIGNED_HIGHLIGHT",ref)
        for method in ("Raw",*METHODS):
            m=[r["methods"][method] for r in subset]
            print(json.dumps({
                "method":method,
                "mean_reference_luma":sum(x["reference_mean_luminance"] for x in m)/len(m),
                "mean_candidate_luma":sum(x["candidate_mean_luminance"] for x in m)/len(m),
                "mean_signed_delta":sum(x["mean_signed_luminance_delta"] for x in m)/len(m),
                "mean_abs_delta":sum(x["mean_absolute_luminance_delta"] for x in m)/len(m),
                "mean_ratio":sum(x["candidate_to_reference_sum_ratio"] for x in m)/len(m),
                "fraction_below":sum(x["fraction_below_reference"] for x in m)/len(m),
                "fraction_above":sum(x["fraction_above_reference"] for x in m)/len(m)
            },sort_keys=True))


if __name__=="__main__":
    main()
