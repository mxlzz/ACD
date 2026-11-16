"""E0056 Classroom CC0: sampling seed variation on Blender 5.2.4.

Reproduces E0007 controlled 96x54/16spp seed test on a newer Blender.
A nonzero difference is necessary, never sufficient for seed independence.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.io import read_arrays, write_report
from acd_lab.seed_audit import verify_sample_variation

ZIP_SHA = "0f0ecc58d45f12b2f4272a53e2d8e69135518e16e956b118f10c20d8dcf5e6"
SEEDS = ((539,"seed539_offset0"),(911,"seed911_offset0"))


def sha(path):
    d=hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda:stream.read(1048576),b""):d.update(part)
    return d.hexdigest()


def score(a,b):
    a,b=rgb(a),rgb(b)
    if a.shape!=(54,96,3) or b.shape!=a.shape:
        raise ValueError("E0056 expected exact 96x54 pixel dimensions")
    variation=verify_sample_variation(a,b)
    delta=np.max(np.abs(a-b),axis=2)
    return {
        "rmse":compare_images(a,b)["rmse_linear"],
        "max_abs":float(delta.max()),
        "changed_pixels_above_1e_minus_6":int((delta>1e-6).sum()),
        "pixel_count":int(delta.size),
        "relative_rmse":variation["pair_rmse_over_signal_rms"],
        "measurably_distinct":variation["meaningfully_different"],
        "independent_samples_proven":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--directory",required=True,type=Path)
    ap.add_argument("--source-zip",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    if sha(args.source_zip)!=ZIP_SHA:
        raise ValueError("Unexpected official Classroom ZIP checksum")
    meta=[]
    images=[]
    hashes={}
    for seed,name in SEEDS:
        j=json.loads((args.directory/(name+".json")).read_text())
        if (j.get("requested_seed")!=seed or j.get("sample_offset")!=0 or
            j.get("sampling_pattern")!="TABULATED_SOBOL" or
            j.get("scene_variant")!="external"):
            raise ValueError("Wrong E0056 independent-process sampler metadata "+name)
        p=args.directory/(name+".exr")
        images.append(read_arrays(p)["image"])
        hashes[name]=sha(p)
        meta.append(j)
    output=score(*images)
    report={
        "experiment":"E0056",
        "purpose":"Reprobe E0007 Classroom seed anomaly on Blender 5.2.4",
        "source":"Christophe Seux Classroom, official Blender demo, CC0",
        "source_zip_sha256":ZIP_SHA,
        "source_bytes":args.source_zip.stat().st_size,
        "rendering":"two separate Blender5.2.4 processes, Cycles CPU, 96x54, 16spp",
        "sampler":"TABULATED_SOBOL",
        "input_seeds":[539,911],
        "sample_offset":0,
        "source_metadata":meta,
        "source_hashes":hashes,
        "test":output,
        "reference_rendered":False,
        "denoiser_run":False,
        "algorithm_modified":False,
        "decision":(
            "Sampler varies in this configuration; now test AOV/independent reference seed and representative noise levels before using Classroom"
            if output["measurably_distinct"] else
            "STOP: Classroom raw outputs still effectively identical under different seeds; do not use as multiseed validation"
        ),
        "warning":"Measured variation does not prove independent Monte Carlo sequences or source correctness. This test may not isolate Blender version if other sampler settings differ from E0007.",
    }
    args.output.mkdir(parents=True,exist_ok=True)
    write_report(args.output/"E0056_RESULTS.json",report)
    lines=[
        "# E0056 — Classroom CC0: sampling variation Blender 5.2.4 vs E0007",
        "",
        "Original Classroom © Christophe Seux, CC0. Exact ZIP SHA256 verified. Two separate Blender processes, same camera/frame and 96×54 at 16 spp, seed539 and seed911, TABULATED_SOBOL and sample_offset0. No denoiser run.",
        "",
        f"- Inter-seed linear RMSE: {output['rmse']:.10f}",
        f"- Relative RMSE to input signal RMS: {output['relative_rmse']:.10f}",
        f"- Changed pixels above 1e-6: {output['changed_pixels_above_1e_minus_6']}/{output['pixel_count']}",
        "- Measurably distinct by existing 1e-4 ratio smoke threshold: "+str(output["measurably_distinct"]),
        "",
        "**Decision:** "+report["decision"],
        "Even measurable variation is not proof of sample independence, and there are no converged references or ACD quality results.",
        "[Original E0007 anomaly](E0007.md); [new data/hashes](E0056_RESULTS.json).",
    ]
    (args.output/"E0056.md").write_text("\n".join(lines)+"\n")
    print("E0056_CLASSROOM_SEED_RESULT",json.dumps(output,sort_keys=True))


if __name__=="__main__":
    main()
