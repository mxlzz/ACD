"""Diagnose withheld night scene using its original EXR artifacts (no rerender).

Source is licensed MIT by Yunus Emre Karaman. This fixture has been observed,
so the result is exploratory and not a future untouched test.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from acd_lab.io import read_arrays, write_report
from acd_lab.error_concentration import error_concentration
from acd_lab.region_cli import compare_regions_from_files
from scripts.analyze_cozy_exr import summarize_all_seeds
from scripts.analyze_cozy_e0020 import choose_reference_rois, display_rgb, METHODS

EXPECTED_SHA = "37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84"


def analyze(root: Path, output: Path) -> dict:
    from PIL import Image, ImageDraw

    metadata=json.loads((root/"metadata.json").read_text())
    if metadata.get("source_blend_sha256") != EXPECTED_SHA:
        raise ValueError("Wrong pinned MIT exterior source SHA")
    if not metadata.get("second_reference"):
        raise ValueError("Need two independent high-spp references")
    output.mkdir(parents=True, exist_ok=True)
    ref1=read_arrays(root/"reference.exr")["image"]
    ref2=read_arrays(root/"reference_check.exr")["image"]
    scores=summarize_all_seeds(root,{"ref1":ref1,"ref2":ref2})
    ranking={ref:sorted(METHODS,key=lambda m:scores[ref][m]["mean_rmse_linear"])
             for ref in ("ref1","ref2")}
    coords=choose_reference_rois(ref1,ref2,size=80,count=3)
    h,w=ref1.shape[:2]
    roi={"regions":[{"name":f"detail_{i+1}",
                     "rect_norm":[x/w,y/h,(x+ww)/w,(y+hh)/h]}
                    for i,(x,y,ww,hh) in enumerate(coords)]}
    (output/"reference_rois.json").write_text(json.dumps(roi,indent=2)+"\n")
    region=compare_regions_from_files(root,passes_file=root/"raw_multilayer.exr",
                                       regions_file=output/"reference_rois.json")
    write_report(output/"region_metrics.json",region)
    if "NATIVE_COMP_OIDN" not in region["regions"]["whole_image"]["metrics"]:
        raise AssertionError("Native baseline missing in regional comparisons")

    images={name:read_arrays(root/f"acd_compare_{name}.exr")["image"] for name in METHODS}
    concentrate={name:error_concentration(ref1,image) for name,image in images.items()}
    aov={}
    for key in ("aov_emission","aov_glossy","aov_transmission","aov_environment"):
        entry=region["regions"].get(key)
        if entry is None or entry.get("metrics") is None:
            continue
        aov[key]={
            "coverage":entry["coverage"],
            "methods":{name:{"rmse_linear":entry["metrics"][name]["rmse_linear"],
                             "mae_linear":entry["metrics"][name]["mae_linear"]}
                       for name in METHODS if name in entry["metrics"]}
        }

    ordered=[("Reference 1",ref1),("Native OIDN",images["NATIVE_COMP_OIDN"]),
             ("ACD High",images["HIGH"]),("ACD Super",images["SUPER"]),
             ("Raw",images["Raw"]),("Reference 2",ref2)]
    previews=[]
    for index,(x,y,cw,ch) in enumerate(coords,1):
        scale=3
        gap=14
        canvas=Image.new("RGB",(len(ordered)*(cw*scale+gap)+gap,
                                 ch*scale+2*gap+27),(29,29,29))
        draw=ImageDraw.Draw(canvas)
        for j,(label,arr) in enumerate(ordered):
            inset=Image.fromarray(display_rgb(arr[y:y+ch,x:x+cw]))
            inset=inset.resize((cw*scale,ch*scale),Image.Resampling.NEAREST)
            xx=gap+j*(cw*scale+gap)
            canvas.paste(inset,(xx,gap+27))
            draw.text((xx+1,6),label,fill=(245,245,245))
        name=f"reference_selected_crop_{index}.png"
        canvas.save(output/name)
        previews.append(name)

    batch=json.loads((root/"metrics.json").read_text())
    quality=batch.get("reference_quality_diagnostic") or {}
    aggregate=json.loads((root/"seed_aggregate.json").read_text())
    data={
        "experiment":"E0023","fixture":"Terraced Houses",
        "creator":"Yunus Emre Karaman","license":"MIT",
        "original_source_sha256":EXPECTED_SHA,
        "render_run_id":43291659387,
        "resolution":metadata["resolution"],"original_resolution":metadata.get("source_original_resolution"),
        "samples":metadata["samples"],"reference_samples":metadata["reference_samples"],
        "seed_diversity_passed":aggregate.get("input_diversity_heuristic_passed"),
        "reference_disagreement_rmse":(batch.get("independent_reference_difference") or {}).get("rmse_linear"),
        "reference_disagreement_over_raw":quality.get("reference_disagreement_over_raw_error"),
        "scores_vs_both_refs_three_seeds":scores,
        "rankings":ranking,
        "error_concentration_first_seed_vs_ref1":concentrate,
        "aov_region_first_seed_vs_ref1":aov,
        "reference_selected_rois_px":coords,
        "previews":previews,
        "uncertainty":"Finite references, raw and denoiser have opposite RMSE/MAE ranking; no causal attribution.",
        "holdout_policy":"Already observed; not a pristine heldout for subsequent model selection."
    }
    write_report(output/"analysis.json",data)
    def fmt(v):
        return "n/a" if v is None or not math.isfinite(v) else f"{v:.7f}"

    lines=[
        "# E0023 — Terraced Houses: validación externa nocturna y anomalía RMSE",
        "",
        "- Fuente: Terraced Houses, Yunus Emre Karaman, licencia MIT; copia sin modificar y LICENSE en benchmarks/scenes.",
        "- Render verificado: GitHub Actions https://github.com/mxlzz/ACD/actions/runs/43291659387",
        f"- Blender 5.0.1 Cycles {metadata['resolution']}, tres entradas de {metadata['samples']} spp, dos referencias de {metadata['reference_samples']} spp.",
        f"- Referencias difieren RMSE {fmt(data['reference_disagreement_rmse'])}; razón sobre error raw {fmt(data['reference_disagreement_over_raw'])}; diversidad heurística {data['seed_diversity_passed']}. No prueba convergencia o independencia.",
        "",
        "| Método | RMSE ref1 (promedio 3 seeds) | RMSE ref2 | Error gradiente ref1 | Error gradiente ref2 | SSE peor 1 % (seed 539) |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for name in METHODS:
        a=scores["ref1"][name]
        b=scores["ref2"][name]
        fraction=concentrate[name]["fraction_squared_error_in_top_pixels"]
        lines.append(f"| {name} | {fmt(a['mean_rmse_linear'])} | {fmt(b['mean_rmse_linear'])} | {fmt(a['mean_edge_gradient_rmse'])} | {fmt(b['mean_edge_gradient_rmse'])} | {fmt(fraction)} |")
    lines.extend([
        "",
        f"- Ranking RMSE ref1: {ranking['ref1']}. Ref2: {ranking['ref2']}. No inferir calidad perceptual de un ranking único.",
        f"- Regiones elegidas exclusivamente de ambas referencias: {coords}. Recortes de primera seed (curva simple no OCIO): {previews}.",
        "",
        "## Pases energéticos (AOV; solo primera seed vs ref1)",
        "Son regiones de contribución relativa, no máscaras de objetos. Se usa el mismo ROI para todos los métodos."
    ])
    for key,entry in aov.items():
        lines.append(f"- {key}, cobertura {entry['coverage']:.4f}: "+
                     ", ".join(name+" RMSE "+fmt(v["rmse_linear"])
                               for name,v in entry["methods"].items()))
    lines.extend([
        "",
        "**Interpretación:** El render Raw gana en RMSE pero pierde en MAE y error de gradientes. La concentración de SSE puede explicar por qué difieren las métricas, pero no atribuye por sí sola la causa a emisión, reflejos o algoritmo. Ver mapas y recortes; no entrenar o ajustar sobre esta escena observada.",
        "",
        "Esta escena ya se examinó y por tanto dejó de ser un test ciego estrictamente reservado para cualquier candidato futuro. Será necesario otro conjunto de evaluación final no observado.",
        ""
    ])
    (output/"E0023.md").write_text("\n".join(lines))
    print("E0023_ANALYSIS",json.dumps({
        "rankings":ranking,
        "top1_sse":{name:concentrate[name]["fraction_squared_error_in_top_pixels"] for name in METHODS},
        "aov":aov,
        "rois":coords,
        "ref_disagreement":data["reference_disagreement_rmse"]
    },indent=2))
    return data


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    analyze(args.directory.resolve(),args.output.resolve())


if __name__ == "__main__":
    main()
