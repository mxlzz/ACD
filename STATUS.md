# M2 — External .blend scene benchmark and regional analysis

Updated: 2026-11-11. Branch dev/acd-m2-real-scenes-regions, draft PR #4 stacked on M1 PR #3.

## Implemented and checked
- Local runner: scripts/run_scene_benchmark.py. Loads an existing .blend without saving, supports chosen frame/resolution, noisy/reference spp and seeds, optional existing reference, and CPU/CUDA/OPTIX selection.
- Experiment provenance: source scene SHA256, scene name, selected view layer, Blender version, color management settings, frame, samples, seed and device recorded.
- Raw multilayer EXR exported from the same noisy render as Standard/High/Super; it contains Composite and ViewLayer parts. Region analysis selects the actual ViewLayer stored in metadata.
- Explicit spatial ROI and relative AOV radiance-contribution masks, HDR regional metrics, signed error maps (not material ID segmentation).
- Real headless Blender 5.0.1 external .blend integration test PASSED, including byte-identical .blend checksum, AOV parsing and ROI report. Evidence: https://github.com/mxlzz/ACD/actions/runs/43057833000
- Python/EXR test suite passed on this branch. Blender 5.3 node API smoke also passed, but Blender 5.3 composited rendering is unverified on cloud runners lacking EGL.
- Fixed synthetic OpenEXR test fixtures requiring contiguous NumPy channel buffers.

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
