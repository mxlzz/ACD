"""E0059: cross-reference edge scoring on frozen E0054 Cozy EXRs, no rerender.

Reference A selects gradient pairs, independent reference B scores candidates;
then swap A/B. Avoid selecting and scoring with the same finite-spp reference.
Not ground truth; repeated scene is NOT held-out algorithm validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

from acd_lab.core import rgb, compare_images
from acd_lab.io import read_arrays, write_report
from scripts.analyze_cozy_consensus_e0052 import SEEDS
from scripts.cozy_crop_e0053 import INNER
from scripts.analyze_cozy_hires_e0054 import validate_meta

ROIS={"detail_2_interior":INNER,"full_render_crop":(0,0,512,512)}
METHODS=("Raw","NATIVE_COMP_OIDN")
WEIGHTS=np.array([.2126,.7152,.0722])


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):digest.update(chunk)
    return digest.hexdigest()


def gradients(a):
    luma=np.arcsinh(rgb(a) @ WEIGHTS)
    return np.concatenate([np.diff(luma,axis=1).ravel(),
                           np.diff(luma,axis=0).ravel()])


def crossfit_region(select_ref,heldout_ref,candidates,rect,quantile=.8):
    a,b=rgb(select_ref),rgb(heldout_ref)
    if a.shape!=b.shape:raise ValueError("Reference shapes differ")
    if not 0<quantile<1:raise ValueError("Invalid quantile")
    x,y,w,h=rect
    if x<0 or y<0 or w<2 or h<2 or x+w>a.shape[1] or y+h>a.shape[0]:
        raise ValueError("ROI outside source")
    def patch(array):
        arr=rgb(array)
        if arr.shape!=a.shape:raise ValueError("Candidate dimensions mismatch")
        return arr[y:y+h,x:x+w]
    source=gradients(patch(a))
    check=gradients(patch(b))
    positive=np.abs(source[source!=0])
    threshold=float(np.quantile(positive,quantile)) if positive.size else None
    mask=(np.abs(source)>=threshold) & (np.abs(source)>0) if threshold is not None else np.zeros_like(source,dtype=bool)
    count=int(mask.sum())
    # Selection uses source only, not heldout or model output.
    stats={"reference_selection_quantile":quantile,
           "selected_pair_count":count,
           "source_gradient_threshold":threshold,
           "heldout_reference_disagreement_rmse":float(np.sqrt(np.mean((source[mask]-check[mask])**2))) if count else None}
    for seed,methods in sorted(candidates.items()):
        row={}
        for name in METHODS:
            if name not in methods:raise ValueError("Missing exact method "+name)
            cand=gradients(patch(methods[name]))
            row[name]={
                "heldout_gradient_rmse":float(np.sqrt(np.mean((cand[mask]-check[mask])**2))) if count else None,
                "heldout_linear_rgb_rmse":compare_images(patch(b),patch(methods[name]))["rmse_linear"]
            }
        stats[str(seed)]=row
    flags=[]
    for seed in SEEDS:
        a1=stats[str(seed)]["NATIVE_COMP_OIDN"]["heldout_gradient_rmse"]
        a2=stats[str(seed)]["Raw"]["heldout_gradient_rmse"]
        flags.append(bool(count and a1>a2))
    stats["oidn_worse_than_raw_in_all_three_seeds"]=bool(len(flags)==3 and all(flags))
    stats["oidn_worse_per_seed"]=flags
    return stats


def analyze(root,manifest):
    if manifest.get("experiment")!="E0054" or manifest.get("blender")!="5.2.4 LTS":
        raise ValueError("Wrong E0054 manifest")
    meta=json.loads((root/"metadata.json").read_text())
    validate_meta(meta)
    if not manifest["same_seed_raw_AOV_and_native_baseline_verified"]:
        raise ValueError("E0054 same-input identity not previously verified")
    hashes=manifest["hashes"]
    def load_verified(folder,name,expected):
        path=folder/name
        if not path.is_file() or sha(path)!=expected:
            raise ValueError("E0054 SHA mismatch "+str(path))
        if name=="raw_multilayer.exr":return None
        value=rgb(read_arrays(path)["image"])
        if value.shape!=(512,512,3):raise ValueError("Expected exact 512px output")
        return value
    refs=[]
    for name in ("reference.exr","reference_check.exr"):
        refs.append(load_verified(root,name,hashes["references"][name]))
    images={}
    for seed in SEEDS:
        folder=root if seed==539 else root/f"seed_{seed}"
        images[seed]={name:load_verified(folder,f"acd_compare_{name}.exr",
                         hashes[str(seed)][f"acd_compare_{name}.exr"])
                      for name in METHODS}
        load_verified(folder,"raw_multilayer.exr",hashes[str(seed)]["raw_multilayer.exr"])
        if compare_images(images[seed]["Raw"],images[seed]["NATIVE_COMP_OIDN"])["rmse_linear"]<1e-6:
            raise ValueError("OIDN output indistinguishable from Raw")
    results={}
    for region,rect in ROIS.items():
        a=crossfit_region(refs[0],refs[1],images,rect)
        b=crossfit_region(refs[1],refs[0],images,rect)
        results[region]={"select_ref_8819_evaluate_8922":a,
                         "select_ref_8922_evaluate_8819":b,
                         "consistent_oidn_gradient_regression_screen":bool(
                           a["oidn_worse_than_raw_in_all_three_seeds"]
                           and b["oidn_worse_than_raw_in_all_three_seeds"])}
    return {
        "experiment":"E0059","source_experiment":"E0054",
        "source_run":43930780340,
        "source_blender":meta["blender"],
        "scene":"Cozy Kitchen, Nicole Morena, CC BY-SA",
        "source_sha256":meta["source_blend_sha256"],
        "input_seeds":list(SEEDS),"input_spp":24,
        "references":[8819,8922],"reference_spp":512,
        "same_raw_per_method_verified_from_E0054":True,
        "input_integrity_rechecked":True,
        "new_cycles_render":False,"new_denoiser":False,
        "reference_convergence_proven":False,
        "algorithms_compared":["Raw","NATIVE_COMP_OIDN"],
        "method":"Select top 20% nonzero asinh-luma gradients from first finite reference only; score heldout second, and swap roles. No denoiser outputs used in selection.",
        "regions":results,
        "global_oidn_gradient_regression_screen":bool(all(
            r["consistent_oidn_gradient_regression_screen"] for r in results.values())),
        "warning":"Reference A and B remain noisy and can share bias; cross-fitting reduces selection leakage but does not establish true edges, perceptual fidelity or algorithm superiority. Raw is not a new denoiser; OIDN removing raw noise can outperform it while still suppressing some true edges.",
        "decision":"Do not propose a correction from edge amplitude alone. Only if consistent heldout gradient regression appears, inspect physical edges and reference uncertainty. New algorithm needs independent author holdout and cost comparison."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--source-manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=analyze(a.directory,json.loads(a.source_manifest.read_text()))
    a.output.mkdir(parents=True,exist_ok=True)
    write_report(a.output/"E0059_RESULTS.json",report)
    lines=[
        "# E0059 — Cross-reference validation of Cozy detail attenuation",
        "",
        "Uses unchanged E0054 real Blender5.2.4 EXRs: 24spp ×3 noisy seeds and two 512spp references. No Cycles rendering, no new denoiser or tuning.",
        "A reference selects high-gradient pixels, the other scores OIDN and exact same-seed Raw; roles swapped. Selection independent of heldout reference and denoiser output.",
        "",
        "| Frozen ROI | Reference used to select | Pairs | OIDN worse than Raw in all 3 seeds? | Mean gradient RMSE Raw / OIDN |",
        "|---|---|---:|---|---|"
    ]
    for name,region in report["regions"].items():
        for direction,k in (("8819→8922","select_ref_8819_evaluate_8922"),
                            ("8922→8819","select_ref_8922_evaluate_8819")):
            r=region[k]
            avg=lambda method:sum(r[str(s)][method]["heldout_gradient_rmse"] for s in SEEDS)/3 if r["selected_pair_count"] else None
            metric=f"{avg('Raw'):.5f} / {avg('NATIVE_COMP_OIDN'):.5f}" if r["selected_pair_count"] else "n/a"
            lines.append(f"| {name} | {direction} | {r['selected_pair_count']} | {r['oidn_worse_than_raw_in_all_three_seeds']} | {metric} |")
    lines+=[
        "",
        "Overall same-seed paired comparison is only a screen. A negative result cannot exclude local OIDN smoothing; a positive result cannot prove lost physical detail while the references are unconverged.",
        "Cross-fit avoids directly evaluating on the reference that selected the edge set; noisy selected gradients and limited sample independence remain.",
        "**Decision:** "+report["decision"],
        "[Input hashes, all per-seed metrics and gates](E0059_RESULTS.json)."
    ]
    (a.output/"E0059.md").write_text("\n".join(lines)+"\n")
    print("E0059_RESULT",json.dumps({
        "regression_screen":report["global_oidn_gradient_regression_screen"],
        "regions":{n:{key:v["oidn_worse_than_raw_in_all_three_seeds"]
                      for key,v in r.items() if isinstance(v,dict)}
                   for n,r in report["regions"].items()}
    },sort_keys=True))


if __name__=="__main__":main()
