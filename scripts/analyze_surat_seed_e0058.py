"""E0058: interior-camera same-scene noisy-seed variation, no denoiser."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from scripts.analyze_classroom_seed_e0056 import score
from acd_lab.io import read_arrays,write_report

ZIP_SHA="721e77b401fba0fa5c3b9df13b09279c6d05781af865f2b63945e7e032e991a8"
SOURCE_BYTES=166627773
CAMERA="CAM Office"
SEEDS=(539,911)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()

def validate_metadata(meta,seed):
    if (meta.get("active_scene")!="Scene" or meta.get("active_camera")!=CAMERA
        or meta.get("requested_seed")!=seed
        or meta.get("sample_offset")!=0
        or meta.get("sampling_pattern")!="TABULATED_SOBOL"
        or meta.get("scene_variant")!="external"):
        raise ValueError(f"E0058 source/camera/sampler mismatch seed {seed}")
    selected=[x for x in meta["settings_all_scenes"] if x["name"]=="Scene"]
    if len(selected)!=1 or selected[0]["samples"]!=16 or selected[0]["seed"]!=seed:
        raise ValueError("E0058 samples or seed mismatch")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--source-zip",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    if a.source_zip.stat().st_size!=SOURCE_BYTES or sha(a.source_zip)!=ZIP_SHA:
        raise ValueError("Wrong source ZIP; no quality test")
    images=[]
    details={}
    for seed in SEEDS:
        stem=f"surat_seed{seed}"
        meta=json.loads((a.directory/f"{stem}.json").read_text())
        validate_metadata(meta,seed)
        path=a.directory/f"{stem}.exr"
        images.append(read_arrays(path)["image"])
        details[str(seed)]={"sha256":sha(path),"metadata":meta}
    metrics=score(*images)
    report={
        "experiment":"E0058","source":"Surat Diamond Bourse v1.0.1, CC0 contributor model only",
        "source_zip_sha256":ZIP_SHA,"source_zip_bytes":SOURCE_BYTES,
        "underlying_architecture_rights_cleared":False,
        "scene":"Scene","camera":CAMERA,"blender":"5.2.4",
        "input_seeds":list(SEEDS),"samples":16,"resolution":[96,54],
        "sampler":"TABULATED_SOBOL","reference_rendered":False,
        "denoiser_run":False,"new_algorithm":False,
        "source_or_render_redistributed":False,
        "raw_seed_variation":metrics,"source_metadata":details,
        "proven_independent_noise":False,
        "heldout_scene_accepted":False,
        "decision":("Raw varies in this internal camera; candidate for further technical validation. "
                    "Need reference convergence and rights review before any external holdout."
                    if metrics["measurably_distinct"] else
                    "STOP: Interior camera does not show sufficient seed variation; "
                    "reject for multiseed quality benchmark."),
    }
    a.output.mkdir(parents=True,exist_ok=True)
    write_report(a.output/"E0058_RESULTS.json",report)
    text=[
        "# E0058 — Surat interior camera: reproducibility gate only",
        "",
        "Original contributor's CC0 model, underlying architectural rights unresolved. "
        "Source ZIP SHA256 pinned, no model or images redistributed.",
        "Blender 5.2.4 CPU, CAM Office, 96×54 at 16spp; two separate processes, seeds539/911.",
        "",
        f"- Raw interseed RMSE: {metrics['rmse']:.9f}",
        f"- Relative RMSE to raw signal RMS: {metrics['relative_rmse']:.9f}",
        f"- Changed pixels >1e-6: {metrics['changed_pixels_above_1e_minus_6']}/5184",
        "- Measurable variation: "+str(metrics["measurably_distinct"]),
        "",
        "**Decision:** "+report["decision"],
        "A nonzero difference is NOT statistical independence, denoiser quality, "
        "HDR convergence or legal clearance. No reference, OIDN or ACD filtering tested.",
        "",
        "[Input manifest and results](E0058_RESULTS.json)."
    ]
    (a.output/"E0058.md").write_text("\n".join(text)+"\n")
    print("E0058_ONLY_RAW_VARIATION",json.dumps(metrics,sort_keys=True))

if __name__=="__main__":main()
