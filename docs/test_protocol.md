# ACD experiment protocol — M0

This is the original baseline protocol, retained for provenance. Updated gate priorities and the sampling-diversity blocker found in E0007 are in [ROADMAP.md](ROADMAP.md), [research_foundations.md](research_foundations.md), and [experiments/E0007.md](experiments/E0007.md).

No numerical or perceptual superiority is asserted until this protocol has been executed.

## Scenes
1. Interior indirect lighting, subtle textures and smooth gradients.
2. Reflective metal, polished floor and transmissive glass.
3. Night interior with small artificial lights and difficult indirect transport.

## For every scene
- Record Blender exact version, Cycles settings, resolution, camera, OCIO view transform, hardware and render time.
- Generate noisy images at 64, 128 and 256 samples using independently chosen seeds, plus an independently converged reference at >=4096 samples if practical.
- Preserve raw linear multi-layer OpenEXR, including normals, albedo, diffuse/glossy/transmission direct-indirect-color, emission, environment, alpha and volumes when used.
- Check raw AOV reconstruction BEFORE denoising; record residual and explicitly mark missing terms.
- Use identical noisy input for native OIDN, native OptiX, SID-style High, SID-style Super, and each ablation (e.g. final denoiser on/off).
- Compare at same resolution, with no hidden resize, color transform or sharpening.

## Metrics
- Linear RMSE, MAE, relative RMSE, and signed residual maps.
- PSNR only with the same explicitly declared range for comparisons.
- HDR-FLIP/perceptual comparisons as a future adapter; don't equate PSNR with visual quality.
- Compare crops at native resolution for lost texture, reflection fidelity, altered energy and fireflies.
- Record wall-time and peak RAM/VRAM when known.
- Repeat on multiple seeds; a one-off attractive crop is not sufficient.

## Gates
M0: Python lab unit tests + Blender 5 construction smoke.
M1: EXR ingest and accurate AOV pass mapping + scene fixtures.
M2: objective baseline tests on the three scenes.
M3: adaptive fusion experiments with out-of-scene validation.
M4+: upscale, photo, optional trained selection model.


## M2.1 laboratory checks (2026-11-11 addendum)

- EXR candidate comparisons now include a **reference-pair diagnostic**:
  per-reference RMSE, pairwise reference disagreement, and disagreement
  normalized by the noisy baseline's error.
- A pair of numerically different references does **not** certify
  independent Monte Carlo sampling. Two near-identical references may
  indicate a converged scene *or* correlated/identical sampling. The
  diagnostic explicitly refuses to certify either convergence or independence.
- A reference pair with difference comparable to the denoising improvement
  requires more reference samples or a different test configuration. Relative
  warning threshold 0.25 is a *heuristic*, not a scientific hard threshold.
- Regional comparisons may be aggregated only when mask fingerprints
  (position-by-position membership) match. Same name, ROI definition,
  area, and coverage are insufficient.
- Distinct noisy EXRs are evidence of variation, not proof of sampling
  independence; the lab uses \`input_diversity_heuristic_passed\` and
  \`sampling_independence_proven: false\` to avoid overstating certainty.
- Existing E0001–E0008 reports are historic snapshots. Their original
  filenames and computed metrics are kept, but files without the new
  fingerprint cannot be safely aggregated by the new code.


## V2 — conservación de detalle, 2026-11-12

`acd_lab.detail.detail_fidelity` agrega métricas **descriptivas** sobre diferencias RGB de píxeles adyacentes tras `asinh` por canal (apto para valores HDR negativos, sin truncar los valores originales). Las máscaras de borde son el percentil superior del 20 % de las diferencias *positivas* en la referencia, las zonas planas el 50 % inferior de todas las parejas. Selección **solo a partir de referencia**, nunca de salida candidata; los empates pueden ampliar cobertura. Se computan parejas horizontal/vertical, y en ROI ambos extremos deben pertenecer a la máscara para evitar falsa vecindad al aplanar regiones.

- `edge_gradient_rmse` / `edge_gradient_mae`: error de gradiente en bordes definidos por referencia (menor = mejor).
- `edge_contrast_ratio`: razón de intensidad de gradiente candidato / referencia en esos bordes; **no es una puntuación de calidad**, puede subir por halo/sharpen/noise. Debe interpretarse junto al error.
- `flat_gradient_rmse`: gradientes falsos o alterados en parejas planas de referencia (menor = mejor).
- Cuando no hay bordes o parejas elegibles, las métricas afectadas son `null`; no inventar valor cero ni ranking. La referencia finita puede contener ruido y definir bordes incorrectos. No hay prueba de equivalencia con métricas HDR perceptuales ni sensibilidad validada en escenas profesionales.
- Batch: `measurements[method].detail` y `rank_by_edge_gradient_rmse`; regiones: `regions[name].metrics[method].detail`; agregado de semillas: `detail_methods`. En agregado, ranking de detalle solo si la auditoría de diversidad de inputs pasa la heurística, y no acredita independencia ni convergencia.
- Benchmark real: priorizar 1:1 crops, dos referencias con discrepancia aceptable, varios seeds, escenas withheld y métricas globales; no promover variante por una única puntuación.
