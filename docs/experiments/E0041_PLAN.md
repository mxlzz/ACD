# E0041 — Plan preinscrito de divergencia por muestras y presupuesto

## 2026-11-13 — B2 E0041 low-cost finite-reference and timing pilot

- Source Italian Flat CC-BY already audited SHA256 `0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25`. E0040 7 cameras completed [run 43494967820](https://github.com/mxlzz/ACD/actions/runs/43494967820) and [gallery](benchmarks/results/italian_flat_e0040/README.md). Each 4 spp 320×200 render ~27s CPU; camera chosen **Cam Kitchen Table** on architectural content, before benchmark metrics.
- E0041 pre-registered: two seeds 8819/8922 at 8,16,32 spp and 320×200; one 640×400 8spp cost check. No denoiser, no training, no high-res/costly reference, not proof of convergence. Source download SHA checked, only EXR in 14-day Actions artifact; numerical outputs permanent. Results pending execution.

**Aceptación:** 7 renders con seeds predeterminadas y AOV de denoising OFF; evaluar RMSE entre pares por spp y ratio de tiempos 640/320, registrar SHA, cámara y metadatos. Si el tiempo escala mal o 32 spp sigue ruidoso, no aprobar 1920x1080/1024spp automáticamente. No comparar algoritmos, no declarar convergencia. Referencia de cámaras E0040.
