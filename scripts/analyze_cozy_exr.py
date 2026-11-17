"""Shared E0020/E0021 ROI report: identical output/cropping policy across seeds.

Reference-only selection, descriptive HDR/error metrics; never use candidate
images to locate crops. Keep same display conversion for each method. EXR must
be generated using controlled scene/layer settings and pinned Cozy Kitchen SHA.
"""
from __future__ import annotations
import argparse
import json
import statistics
from pathlib import Path

import numpy as np

from acd_lab.core import compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays, write_report
from acd_lab.region_cli import compare_regions_from_files
from scripts.analyze_cozy_e0020 import choose_reference_rois, display_rgb, SHA, METHODS


def summarize_all_seeds(root: Path, references: dict[str,np.ndarray]):
    folders=[root]+sorted(x for x in root.glob("seed_*") if x.is_dir())
    score={}
    for label,reference in references.items():
        score[label]={}
        for method in METHODS:
            vals=[]
            for folder in folders:
                image=read_arrays(folder/f"acd_compare_{method}.exr")["image"]
                vals.append({
                    "rmse_linear":compare_images(reference,image)["rmse_linear"],
                    "edge_gradient_rmse":detail_fidelity(reference,image)["edge_gradient_rmse"]
                })
            score[label][method]={
                "mean_rmse_linear":statistics.fmean(x["rmse_linear"] for x in vals),
                "mean_edge_gradient_rmse":statistics.fmean(x["edge_gradient_rmse"] for x in vals),
                "per_seed":vals
            }
    return score


def analyze(root: Path, output: Path, *, experiment: str, run_id: int, roi_size: int=96):
    from PIL import Image, ImageDraw

    meta=json.loads((root/"metadata.json").read_text(encoding="utf-8"))
    if meta.get("source_blend_sha256") != SHA:
        raise ValueError("Expected tracked Cozy Kitchen source SHA")
    if meta.get("second_reference") is not True:
        raise ValueError("Two independent reference seeds required")
    reference={
        "first":read_arrays(root/"reference.exr")["image"],
        "second":read_arrays(root/"reference_check.exr")["image"]
    }
    coords=choose_reference_rois(reference["first"],reference["second"],size=roi_size,count=3)
    h,w=reference["first"].shape[:2]
    output.mkdir(parents=True,exist_ok=True)
    roi={"regions":[{
        "name":f"reference_detail_roi_{i+1}",
        "rect_norm":[x/w,y/h,(x+rw)/w,(y+rh)/h]
    } for i,(x,y,rw,rh) in enumerate(coords)]}
    (output/"reference_rois.json").write_text(json.dumps(roi,indent=2)+"\n")
    region=compare_regions_from_files(
        root,passes_file=root/"raw_multilayer.exr",
        regions_file=output/"reference_rois.json"
    )
    write_report(output/"region_metrics.json",region)
    if "NATIVE_COMP_OIDN" not in region["regions"]["whole_image"]["metrics"]:
        raise AssertionError("Native OIDN omitted from ROI baseline")
    scores=summarize_all_seeds(root,reference)
    ranked={name:sorted(METHODS,key=lambda m:scores[name][m]["mean_rmse_linear"])
            for name in reference}
    first={name:read_arrays(root/f"acd_compare_{name}.exr")["image"] for name in METHODS}
    methods=[("Ref 1",reference["first"]),("OIDN",first["NATIVE_COMP_OIDN"]),
             ("ACD High",first["HIGH"]),("ACD Super",first["SUPER"]),
             ("Raw",first["Raw"]),("Ref 2",reference["second"])]
    previews=[]
    for i,(x,y,cw,ch) in enumerate(coords,1):
        scale=3
        gap=14
        label_height=27
        image=Image.new("RGB",(len(methods)*(cw*scale+gap)+gap,
                                ch*scale+label_height+2*gap),(29,29,29))
        draw=ImageDraw.Draw(image)
        for j,(label,src) in enumerate(methods):
            crop=Image.fromarray(display_rgb(src[y:y+ch,x:x+cw]))
            crop=crop.resize((cw*scale,ch*scale),resample=Image.Resampling.NEAREST)
            start=gap+j*(cw*scale+gap)
            image.paste(crop,(start,gap+label_height))
            draw.text((start,6),label,fill=(240,240,240))
        filename=f"reference_detail_crop_{i}.png"
        image.save(output/filename)
        previews.append(filename)
    audit=json.loads((root/"metrics.json").read_text())
    quality=audit.get("reference_quality_diagnostic") or {}
    agg=json.loads((root/"seed_aggregate.json").read_text())
    report={
        "experiment":experiment,
        "render_run_id":run_id,
        "source_scene_sha256":SHA,
        "license":"Cozy Kitchen by Nicole Morena — CC BY-SA; derived previews preserve attribution",
        "blender":meta["blender"],
        "source_original_resolution":meta.get("source_original_resolution"),
        "resolution":meta["resolution"],
        "source_original_pixel_aspect":meta.get("source_original_pixel_aspect"),
        "samples":meta["samples"],
        "reference_samples":meta["reference_samples"],
        "seed_diversity_heuristic_passed":agg.get("input_diversity_heuristic_passed"),
        "reference_disagreement_rmse":(audit.get("independent_reference_difference") or {}).get("rmse_linear"),
        "reference_disagreement_over_raw_error":quality.get("reference_disagreement_over_raw_error"),
        "convergence_proven":quality.get("convergence_proven"),
        "reference_ranking_per_seed_averages":ranked,
        "methods_vs_both_references":scores,
        "roi_selection":"Top asinh-RGB gradient windows of mean first+second reference, no method data",
        "rois_px":coords,
        "roi_metrics_path":"region_metrics.json",
        "visualization":"non-OCIO diagnostic compress+gamma mapping; 3x nearest-neighbor crops",
        "previews":previews,
        "warning":"Finite-spp reference not necessarily converged; reference-derived gradients may reflect reference noise; do not assert perceptual victory."
    }
    write_report(output/"analysis.json",report)

    def fmt(x):return f"{x:.7f}" if x is not None else "n/a"
    lines=[
        f"# {experiment} — Cozy Kitchen: comparación de detalle y referencias (2026-11-12)",
        "",
        f"- **Run de render:** [#{run_id}](https://github.com/mxlzz/ACD/actions/runs/{run_id}) (CPU, Blender {meta['blender']}).",
        f"- **Fuente:** Cozy Kitchen de Nicole Morena, CC BY-SA; SHA256 `{SHA}`.",
        f"- **Imagen original:** `{meta.get('source_original_resolution')}`, imagen de ensayo `{meta['resolution']}`; **24 spp ×3 semillas**, dos referencias **{meta['reference_samples']} spp**.",
        f"- Heurística de diversidad de semillas: **{agg.get('input_diversity_heuristic_passed')}**. Diferencia entre referencias, RMSE: **{fmt(report['reference_disagreement_rmse'])}**; proporción sobre ruido original: **{fmt(report['reference_disagreement_over_raw_error'])}**.",
        f"- **Convergencia probada:** {quality.get('convergence_proven')}. Diferencia entre referencias y seed no prueban por sí solas independencia.",
        "",
        "| Método | RMSE medio ref 1 | RMSE medio ref 2 | Error bordes ref 1 | Error bordes ref 2 |",
        "|---|---:|---:|---:|---:|"
    ]
    for method in METHODS:
        a=scores["first"][method];b=scores["second"][method]
        lines.append("| "+method+" | "+" | ".join(map(fmt,[
            a["mean_rmse_linear"],b["mean_rmse_linear"],
            a["mean_edge_gradient_rmse"],b["mean_edge_gradient_rmse"]
        ]))+" |")
    lines+=["",
        f"- **Ranking (medias de 3 seeds) ref1:** `{ranked['first']}`. **Ref2:** `{ranked['second']}`. Si el orden cambia solo entre métodos numéricamente equivalentes, no interpretar como cambio de superioridad.",
        f"- **Recortes 1:1 ampliados ×3 (solo primera seed):** `{previews}`, regiones elegidas solo desde ambas referencias: `{coords}`. No representan el encuadre completo.",
        "- Los recortes son derivados **CC BY-SA** con autoría Nicole Morena; transformada de pantalla común aproximada, no OCIO de Blender. El reporte regional contiene OIDN nativo y ACD sobre máscaras idénticas.",
        "- **Interpretación prudente:** a baja resolución OIDN puede suavizar detalles reales. Un ratio de contraste superior no prueba fidelidad: requiere menor error de gradiente HDR y comparación perceptual con convergencia mejor.",
        "- **Siguiente puerta:** interpretar regiones y referencias convergentes; repetir en al menos otra escena profesional/pública retenida antes de ajustar algoritmo. No comparar SID5 comercial si no fue ejecutado.",
        ""
    ]
    (output/f"{experiment}.md").write_text("\n".join(lines),encoding="utf-8")
    print("ACD_COZY_REFERENCES_AND_CROPS",json.dumps({
        "experiment":experiment,
        "resolution":report["resolution"],
        "source_original_resolution":report["source_original_resolution"],
        "ref_pair_rmse":report["reference_disagreement_rmse"],
        "ref_pair_over_raw":report["reference_disagreement_over_raw_error"],
        "rank_ref1":ranked["first"],"rank_ref2":ranked["second"],
        "rois":coords,"crops":previews,
        "scores":{method:{
            "rmse_ref1":scores["first"][method]["mean_rmse_linear"],
            "rmse_ref2":scores["second"][method]["mean_rmse_linear"],
            "edge_ref1":scores["first"][method]["mean_edge_gradient_rmse"],
            "edge_ref2":scores["second"][method]["mean_edge_gradient_rmse"]
        } for method in METHODS}
    },indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--experiment",choices=("E0020","E0021"),required=True)
    p.add_argument("--render-run",type=int,required=True)
    p.add_argument("--roi-size",type=int,default=96)
    a=p.parse_args()
    analyze(a.directory.resolve(),a.output.resolve(),
            experiment=a.experiment,run_id=a.render_run,roi_size=a.roi_size)


if __name__=="__main__":main()
