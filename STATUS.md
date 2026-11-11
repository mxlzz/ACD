# M2 — External .blend scene benchmark and regional analysis

**Project plan:** [docs/ROADMAP.md](docs/ROADMAP.md). **Scientific foundations and hypotheses:** [docs/research_foundations.md](docs/research_foundations.md). These are reference documents; the status below records actual implementation and evidence.

Updated: 2026-11-11. Branch dev/acd-m2-real-scenes-regions, draft PR #4 stacked on M1 PR #3.

## Auditoría Cycles v5.0.1: guías de hits especulares (11-11-2026)

- El código de Cycles v5.0.1 **ya espera a rebotes posteriores cuando domina la contribución especular** antes de registrar características de denoising; no siempre utiliza el primer hit.
- E0012 prueba que cambiar conexiones de guías afecta la calidad, pero no identifica el mecanismo de degradación. No implementar ciegamente guías de «segundo hit» sin comprobar qué información ya registra el renderer.
- Fuente técnica y próximos controles: docs/cycles_guide_source_audit.md; tareas concretas [Issue #6](https://github.com/mxlzz/ACD/issues/6). La hipótesis H-01 se acota a la **correspondencia entre cada subpase y las guías usadas**.

## E0012 — Ablación de Albedo/Normal por subpase (11-11-2026)

- E0012 ejecutado y aprobado en Blender 5.0.1: 10 ramas de denoising sobre lobby de vidrio/metal, 128×96, 24 spp, 3 entradas y 2 referencias. Run https://github.com/mxlzz/ACD/actions/runs/43086458932.
- High sin guías intermedias bajó RMSE global 0,194924 → 0,180170, pero Standard guiado (0,174651) y Standard sin guías (0,173501) fueron mejores. High mejoró transmisión con guías retiradas; Super mostró un compromiso distinto y empeoró globalmente sin guías.
- La «guía Normal sin Albedo» en el Denoise de Blender es **ignorada por diseño**: las salidas fueron idénticas a las variantes sin guías. Se prohibió producir estos duplicados; informes históricos todavía pueden leerse. Fuente oficial y cifras en docs/experiments/E0012.md.
- **No se promovió ninguna variante** al addon. Próxima hipótesis H-01: auditar qué hits representan los AOV de Cycles, y evaluar guías de reflexión/refracción específicas en datasets de escenas no vistas.

## E0010 / E0011 — Ejecuciones completas (11-11-2026)

- E0010: la repetición completa de E0008 PASÓ, con 3 entradas diferentes y máscara regional idéntica (SHA-256; 66 píxeles). El RMSE en la región emisiva se redujo 0,2758194 → 0,2717647, pero las regresiones de MAE y RMSE global impiden activarlo por defecto. Run 43085166506.
- E0011: segundo escenario **procedural** de lobby con vidrio y metal. Blender 5.0.1, 128×96, 24 spp, 3 entradas y dos referencias de 1024 spp. Standard RMSE 0,1746515; High 0,1949242; Super 0,2014348. En máscaras glossy/transmisión Standard superó a Super en las tres entradas. Run 43085451268.
- Los dos workflows intensivos quedaron como **manuales** después de validarlos. Los reportes completos están en docs/experiments/E0010.md y E0011.md, con JSON numérico E0011_metrics.json.
- Las referencias no están certificadas como convergidas; E0011 no equivale a una segunda escena profesional externa. Próximo paso: ablar guías de Albedo/Normal por señal y reunir más escenas externas.

## M2.1 — Validación de la integridad de las comparaciones (2026-11-11)

- Incorporado `mask_sha256`: digest versionado del tamaño y la pertenencia exacta de cada píxel a la ROI. Los informes nuevos incluyen el hash; el agregador rechaza ROI con igual área/definición pero ubicación diferente y exige regenerar informes antiguos sin huella. Tests unitarios y OpenEXR de regresión agregados.
- Incorporado `acd_lab/reference_audit.py`: mide la discrepancia entre dos referencias de muestras finitas respecto del error del render ruidoso, detecta referencias casi idénticas y alerta cuando su diferencia es considerable. **No** certifica independencia ni convergencia (ambas se informan como no demostradas). Incluido en `compare-batch`.
- Corregida la semántica del diagnóstico multisemilla: `input_diversity_heuristic_passed` solo certifica el umbral heurístico de **diferencia entre imágenes**. `sampling_independence_proven` permanece `false`; ya no se usa el nombre engañoso `independent_seeds_verified`.
- Las pruebas verifican también dos referencias EXR, normalización del diagnóstico y máscaras distintas con el mismo número de píxeles. Evidencia y limitaciones técnicas: `docs/experiments/E0009.md`.
- Estado actual: verificaciones Python y Blender headless de la rama, pero **no** se ejecutó de nuevo el pipeline E0008 completo con el agregador actualizado ni una segunda escena profesional. M2.1 sigue abierto: https://github.com/mxlzz/ACD/issues/5

## Sampling-validity finding — E0007 (2026-11-11)
- Official Classroom: in independent Blender processes at 96x54, 16 spp, Classic TABULATED_SOBOL, changing Cycles seed 539 -> 911 only changed 4/5184 pixels (RGB RMSE ~1.04e-6); setting sample_offset 0 -> 16 changed only 8/5184 pixels. Source: GitHub Actions 43069937939.
- Switching Classic to BLUE_NOISE altered the image strongly (RGB RMSE 0.16825), but changing seed 539 -> 911 *within BLUE_NOISE* again produced virtually identical images (relative RMSE 1.32e-9). Source: run 43071018867.
- **Interpretation:** In this specific Classroom/Blender 5.0.1 setup, nominal seed changes do not generate meaningfully distinct noisy images. Cause is not established. This is a methodological blocker; do not treat extra seed labels as independent samples.
- Implemented automated per-pair diversity checks and prevented multi-seed mean rankings from being treated as validated unless raw samples pass image-diversity screening. This is a necessary check, not a proof of statistical independence.
- Classroom E0005/E0006 remain useful *single-input comparative ablations*; the allegedly independent seed-derived reference is not validated as independent sampling. The prior numeric improvements cannot yet be generalized.
- See docs/experiments/E0007.md. Heavy Classroom and seed probes are manual-only after debugging.

- E0007 controlled procedural interior: seeds 539 and 911 produce meaningfully different unfiltered 16-spp renders in independent Blender processes (pair RMSE / signal RMS 0.2655), unlike Classroom. Evidence: https://github.com/mxlzz/ACD/actions/runs/43071534950
- Classroom workflow now intentionally uses one noisy input only, without invalid multi-seed averages. Heavy benchmark and seed-probe workflows are manual-only.

## E0008 — emission preservation with verified diverse noisy inputs
- Procedural emissive interior, 128x96, 24 spp, three distinguishable raw noisy seeds and two 1024-spp unfiltered references.
- Baseline emission mask: 66 pixels (0.54% of image). Standard emission-region RMSE mean 0.275820 vs emission-preserved 0.271765 (~1.47% reduction), improvement only 2/3 seeds.
- However, emission-region MAE mean worsens 0.185852 -> 0.206836 (~11.29%), and global RMSE mean worsens 0.091558 -> 0.091715. No default algorithm change justified.
- Results and source runs: docs/experiments/E0008.md and E0008_metrics.json.
- Fixed a glob bug where seed_aggregate.json was treated as a seed folder; numerical CI and Blender smoke tests passed after the correction. Heavy emission workflow is now manual-only.

## Implemented and checked
- Local runner: scripts/run_scene_benchmark.py. Loads an existing .blend without saving, supports chosen frame/resolution, noisy/reference spp and seeds, optional existing reference, and CPU/CUDA/OPTIX selection.
- Experiment provenance: source scene SHA256, scene name, selected view layer, Blender version, color management settings, frame, samples, seed and device recorded.
- Raw multilayer EXR exported from the same noisy render as Standard/High/Super; it contains Composite and ViewLayer parts. Region analysis selects the actual ViewLayer stored in metadata.
- Explicit spatial ROI and relative AOV radiance-contribution masks, HDR regional metrics, signed error maps (not material ID segmentation).
- Real headless Blender 5.0.1 external .blend integration test PASSED, including byte-identical .blend checksum, AOV parsing and ROI report. Evidence: https://github.com/mxlzz/ACD/actions/runs/43057833000
- Python/EXR test suite passed on this branch. Blender 5.3 node API smoke also passed, but Blender 5.3 composited rendering is unverified on cloud runners lacking EGL.
- Fixed synthetic OpenEXR test fixtures requiring contiguous NumPy channel buffers.

- E0005: first real official Classroom (CC0) rendered and analyzed. At 384x216 / 32 spp vs 256 spp reference: Standard RMSE 0.043961, High 0.044847, Super 0.052703, Raw 0.072410. AOV closure RMSE 3.55e-8. In the emission-dominated 1.4% subset, raw RMSE 0.035607 vs Standard 0.060156. See docs/experiments/E0005.md and CI run 43058679034.
- E0006: Classroom emission-preservation results were recorded, but the independence of the reference/input sampling was not validated; see docs/experiments/E0006.md and E0007.md.

## Remaining validation
- Actual professional-sized scenes at 1080p+, multiple input seeds, convergence-tested reference.
- RTX 4050 OPTIX run on Windows.
- Material-specific quality in reflections/transmission, HDR-FLIP or reviewed crops.
- Full pass closure and alpha behavior with complex Blender shaders.
- No universal superiority or verified commercial SID 5.3 equivalence.

## Next gates
1. Evaluate official Classroom (CC0), Barcelona Pavilion (CC-BY), or a licensed production .blend outside Git. Keep scene assets out of the repository.
2. Inspect reflected/transmitted ROIs and compare 3+ noisy seeds to two high-spp references when practical.
3. Test guided versus unguided denoising only where the region metrics justify it.
4. Leave expensive renders manual/local; preserve stable addon apart from experiments.

## Earlier project state

# Persistent project state — ACD

Updated: 2026-11-11
Base M0 merged to main by PR #1.
M1 development: PR #3, branch dev/acd-m1-exr-evaluation. Related issue #2.

## Verified
- GitHub Actions Python core+lab checks passed.
- Blender 5.0.1: addon nodes constructed; render test passed.
- Blender 5.3: addon node construction passed; composited rendering remains unverified in the cloud runner because of missing EGL dependencies.
- OpenEXR 3.3+ support: tests with synthetic EXR passes passed.
- Blender-generated raw multi-layer EXR ingested successfully (run 43048580433).
- For the 48×40, 8 spp factory scene: raw beauty vs AOV recomposition max absolute difference 8.26e-8.
- Same Cycles noisy render successfully processed via Raw, Standard, High, Super branches (run 43048979372).
- First reference run: 16 spp seed 539 against 256 spp seed 8819. Standard RMSE 0.002668, Raw 0.002796, High 0.006526, Super 0.018854. See docs/experiments/E0001.md.
- Removing the final OIDN from High/Super barely changes RMSE; the raw compositing graph reproduces raw with RMSE ~1e-8.
- Blender 5.0.1 guided AOV denoising ablation: High RMSE 0.005879 without guides vs 0.006526 with; Super 0.008978 vs 0.018854. Neither beats Standard 0.002668 (run 43050200840).

- E0002: 48x40 architectural interior, 16 spp vs two 4096 spp references: High RGB RMSE 0.150261, Standard 0.154318, Super 0.158825, Raw 0.302980. High ranks first against both, but MAE and log-luminance metrics favor other methods. The reference-to-reference RMSE is 0.041418: not converged. Full details: docs/experiments/E0002.md.
- Added automated log1p luminance RMSE, per-pixel p95 error and metric-specific rankings to avoid relying on global linear RMSE alone.
- Follow-up 96x80 at 32 spp and two 4096 spp references configured as an evaluation job.

- E0003 (run 43051674524): 96x80, 32 spp, same noisy input, two 4096 spp independent references. Super RGB RMSE 0.085272, Standard 0.089322, High 0.090164. Super also improves MAE, log-luminance RMSE and p95 pixel RMSE relative to Standard in this trial. Unguided Super RGB RMSE 0.081339, but guided Super leads on MAE and log-luminance. The two references differ (RMSE 0.03941). More seeds/scenes required; see docs/experiments/E0003.md.
- Note: comparison order changed from E0002 to E0003; image size and input spp changed together, so no single cause is established.

- E0004: 96x80 interior repeated with four noisy seeds (539, 911, 1337, 2026) and shared two 4096-spp references (run 43052249917). Mean RGB RMSE: Standard 0.078680, Super 0.080243, High 0.082621. However Super has lower mean MAE (0.030957 vs Standard 0.033328) and lower p95 pixel error (0.105689 vs 0.114824). Unguided High and Super have lower mean RMSE (0.076094 and 0.077236). No universal winner. See docs/experiments/E0004.md.
- The expensive architectural multi-seed battery is now manual workflow_dispatch, not a default PR check, to avoid wasteful repeated CPU render runs.

## Unverified, pending
- Blender 5.3 actual composited render on machine with working graphics runtime.
- Equivalence to released SID 5.3 and performance on practical interiors.
- Convergence-checked reference and multiple independent input seeds.
- Material-specific quality improvements, HDR perceptual metrics, and RTX performance.

## Immediate next gates
1. E0004 multi-seed experiment completed. Next: isolate resolution vs sample budget as single-variable changes, add scenes and reference convergence checks.
2. Inspect per-pass residual maps to isolate where distortion is introduced.
3. Benchmark three test scenes and several seeds/spp budgets.
4. Move beyond generic OIDN stacking only when a measurable benefit appears.

## Policy
No merge of experimental M1 as a production denoiser unless empirical and API tests substantiate it. Keep the source research and licensing record in GitHub.
