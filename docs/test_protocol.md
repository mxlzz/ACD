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
