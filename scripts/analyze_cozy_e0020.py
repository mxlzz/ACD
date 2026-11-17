"""Offline analysis of previously rendered E0020 EXRs. No Cycles rerender.

All ROI/crop choices depend only on two finite-spp references. Method outputs
cannot influence ROI selection. Crops use a shared illustrative display map,
not Blender's OCIO transform; inspect linear error metrics for conclusions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

from acd_lab.core import rgb, compare_images
from acd_lab.detail import detail_fidelity
from acd_lab.io import read_arrays, write_report
from acd_lab.region_cli import compare_regions_from_files

METHODS=("Raw","STANDARD","HIGH","SUPER","NATIVE_COMP_OIDN")
SHA="5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395"


def choose_reference_rois(first: np.ndarray, second: np.ndarray, *,
                          size: int=80, count: int=3) -> list[tuple[int,int,int,int]]:
    """Return non-overlapping, high-gradient patches based only on references.

    Uses half-pixel-neighbor color gradient on an asinh-compressed *mean of
    both references*. Dense noise may still inflate scores; 512spp not ground truth.
    """
    a=rgb(first).astype(np.float64)
    b=rgb(second).astype(np.float64)
    if a.shape != b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("ROI selection requires aligned finite references")
    h,w=a.shape[:2]
    size=min(size,h,w)
    if size<4: raise ValueError("ROI requires at least 4x4 pixels")
    merged=np.arcsinh((a+b)*.5)
    scores=np.zeros((h,w),np.float64)
    dif_x=np.linalg.norm(merged[:,1:]-merged[:,:-1],axis=2)
    dif_y=np.linalg.norm(merged[1:]-merged[:-1],axis=2)
    scores[:,1:]+=dif_x
    scores[1:,:]+=dif_y
    # Grid candidates with overlapping proposal windows; chosen windows do NOT
    # overlap. Count can be lower than requested for small images.
    step=max(1,size//3)
    topxs=sorted(set([*range(0,w-size+1,step),w-size]))
    topys=sorted(set([*range(0,h-size+1,step),h-size]))
    candidates=[(float(np.mean(scores[y:y+size,x:x+size])),x,y)
                for y in topys for x in topxs]
    candidates.sort(key=lambda r:(-r[0],r[2],r[1]))
    picked=[]
    for _,x,y in candidates:
        if any(not (x+size<=xx or xx+size<=x or y+size<=yy or yy+size<=y)
               for xx,yy,_,_ in picked):
            continue
        picked.append((x,y,size,size))
        if len(picked)>=count: break
    return picked


def display_rgb(array: np.ndarray):
    """Fixed sRGB-like diagnostic preview, not a color-managed verdict."""
    r=np.clip(rgb(array).astype(np.float64),0,None)
    compressed=r/(1+r)
    return np.uint8(np.clip(np.power(compressed,1/2.2)*255+.5,0,255))


def analyze(root: Path, output: Path) -> dict:
    from PIL import Image, ImageDraw

    meta=json.loads((root/"metadata.json").read_text())
    if meta.get("source_blend_sha256") != SHA:
        raise ValueError("E0020 input source hash is not the pinned Cozy Kitchen fixture")
    if meta.get("second_reference") is not True:
        raise ValueError("Two references are required for unbiased crop selection")
    output.mkdir(parents=True,exist_ok=True)
    ref1=read_arrays(root/"reference.exr")["image"]
    ref2=read_arrays(root/"reference_check.exr")["image"]
    coords=choose_reference_rois(ref1,ref2,size=80,count=3)
    h,w=rgb(ref1).shape[:2]
    rois={"regions":[
        {"name":f"detail_{i+1}",
         "rect_norm":[x/w,y/h,(x+rw)/w,(y+rh)/h]}
        for i,(x,y,rw,rh) in enumerate(coords)]}
    (output/"reference_rois.json").write_text(json.dumps(rois,indent=2)+"\n")
    regional=compare_regions_from_files(
        root,passes_file=root/"raw_multilayer.exr",
        regions_file=output/"reference_rois.json"
    )
    write_report(output/"region_metrics_fixed.json",regional)
    missing=[n for n in METHODS if not (root/f"acd_compare_{n}.exr").exists()]
    if missing:raise FileNotFoundError("Missing candidate EXRs: "+repr(missing))
    candidates={name:read_arrays(root/f"acd_compare_{name}.exr")["image"] for name in METHODS}
    pass_ref={"first":ref1,"second":ref2}
    metrics={}
    for label,reference in pass_ref.items():
        metrics[label]={name:{
            "rmse_linear":compare_images(reference,candidate)["rmse_linear"],
            "edge_gradient_rmse":detail_fidelity(reference,candidate)["edge_gradient_rmse"]
        } for name,candidate in candidates.items()}
    ranks={ref_name:sorted(METHODS,key=lambda name:entry[name]["rmse_linear"])
           for ref_name,entry in metrics.items()}
    # Preview SAME fixed tonemapping, zoom 3x without resampling for every panel.
    ordered=[("First reference",ref1),("OIDN",candidates["NATIVE_COMP_OIDN"]),
             ("ACD High",candidates["HIGH"]),("ACD Super",candidates["SUPER"]),
             ("Raw",candidates["Raw"]),("Second reference",ref2)]
    out_crops=[]
    for index,(x,y,cw,ch) in enumerate(coords,1):
        scale=3
        margin=14
        label_height=27
        canvas=Image.new("RGB",(len(ordered)*(cw*scale+margin)+margin,
                                 ch*scale+2*margin+label_height),
                         (29,29,29))
        drawer=ImageDraw.Draw(canvas)
        for item,(label,image) in enumerate(ordered):
            cut=Image.fromarray(display_rgb(image[y:y+ch,x:x+cw]))
            cut=cut.resize((cw*scale,ch*scale),resample=Image.Resampling.NEAREST)
            px=margin+item*(cw*scale+margin)
            canvas.paste(cut,(px,label_height+margin))
            drawer.text((px+2,6),label,fill=(240,240,240))
        name=f"reference_selected_crop_{index}.png"
        canvas.save(output/name)
        out_crops.append(name)
    report={
        "experiment":"E0020","source_sha256":SHA,
        "source_license":"Cozy Kitchen Nicole Morena CC BY-SA; derivative crops also CC BY-SA with attribution",
        "source_render_run":"https://github.com/mxlzz/ACD/actions/runs/43287450449",
        "resolution":meta["resolution"],"samples":meta["samples"],
        "ref_spp":meta["reference_samples"],"seeds":[meta["seed"],*meta["extra_input_seeds"]],
        "region_selection":"asinh RGB gradients of mean of two references; never candidate-derived",
        "coords_px":coords,
        "rank_by_rmse_against_each_reference":ranks,
        "metrics_against_each_reference":metrics,
        "region_metrics_path":"region_metrics_fixed.json",
        "preview_files":out_crops,
        "preview_caveat":"Shared simple compress+gamma display approximation, nearest neighbor 3x, NOT Blender OCIO/color-accurate, not perceptual proof.",
        "scientific_caveat":"512-spp references differ materially, correlated samples/convergence unverified; crops do not replace validation."
    }
    write_report(output/"roi_analysis.json",report)
    def show(v): return f"{v:.7f}" if v is not None and math.isfinite(v) else "n/a"
    lines=[
        "# E0020 — Cozy Kitchen, benchmark de calidad y recortes (2026-11-12)",
        "",
        "- **Fuente:** [Cozy Kitchen de Nicole Morena](https://github.com/mxlzz/ACD/blob/dev/acd-v2-oidn-detail-eval/benchmarks/scenes/cozy_kitchen.blend), licencia **CC BY-SA**; SHA256 `"+SHA+"`.",
        "- **Ejecución real:** [GitHub Actions #43287450449](https://github.com/mxlzz/ACD/actions/runs/43287450449). Blender 5.0.1 Cycles, escena Main / CAM-wide, 320×240, 24 spp ×3 seeds, referencias 512 spp ×2. Mismo RenderLayer/AOV para todos los métodos.",
        "- **Datos:** [resumen original del run](https://github.com/mxlzz/ACD/actions/runs/43287450449/artifacts/13974609975) (caduca a 14 días); [EXR originales](https://github.com/mxlzz/ACD/actions/runs/43287450449/artifacts/13975167835) (caducan a 7 días).",
        "- **Auditoría:** diversidad heurística de noisy seeds superada. Referencias entre sí difieren RMSE lineal **0.0610477**, ~**24.51 %** del error del render crudo respecto a referencia media, muy próximo al umbral exploratorio del 25 %. No hay prueba de convergencia. El ranking contra ambas referencias **no es idéntico**.",
        "",
        "| Método | RMSE contra ref 1 | RMSE contra ref 2 | Borde contra ref 1 | Borde contra ref 2 |",
        "|---|---:|---:|---:|---:|"
    ]
    for n in METHODS:
        x=metrics["first"][n];y=metrics["second"][n]
        lines.append(f"| {n} | {show(x['rmse_linear'])} | {show(y['rmse_linear'])} | {show(x['edge_gradient_rmse'])} | {show(y['edge_gradient_rmse'])} |")
    lines+=["",
        f"- **Ranking ref 1 (única seed 539):** `{ranks['first']}`. **Ranking ref 2:** `{ranks['second']}`. Este orden individual no sustituye los promedios de tres semillas registrados en el run.",
        "- **ROI de alto gradiente** elegidas solo por las dos referencias: "+json.dumps(coords)+" en píxeles (x,y,ancho,alto), origen superior izquierdo. Reporte espacial incluye OIDN nativo luego de corregir su omisión en `region_cli`.",
        "- **Vista previa:** crop PNG de cada ROI en `benchmarks/results/cozy_e0020/`. Todas las versiones usan la misma curva aproximada para visualización y ampliación 3x sin interpolación; **no** equivale a gestión de color OCIO ni validación perceptual.",
        "- **Diagnóstico actual:** ACD Standard reproduce salida OIDN nativa a precisión del benchmark; High/Super no mejoran de forma consistente el RMSE ni el error de gradiente y Super aumenta el contraste aparente. No se ha demostrado conservación de detalle adicional auténtico.",
        "- **Siguiente prueba:** mejorar convergencia de referencias y/o subir resolución, más regiones semánticas/materiales y una escena retenida de test antes de investigar filtros adaptativos. No entrenar red ni fusionar addon estable.",
        ""
    ]
    (output/"E0020.md").write_text("\n".join(lines),encoding="utf-8")
    print("E0020_ROI_ANALYSIS",json.dumps({
        "rois":coords,"ranking_ref1":ranks["first"],
        "ranking_ref2":ranks["second"],
        "native_region_present":("NATIVE_COMP_OIDN" in
                                 (regional["regions"].get("whole_image",{}).get("metrics") or {})),
        "crops":out_crops
    },indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    analyze(a.directory.resolve(),a.output.resolve())


if __name__=="__main__": main()
