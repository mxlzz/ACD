# E0042 — Preinscripción referencia 640px

## 2026-11-13 — B2 E0042 640px reference pilot (run pending)

- E0041 [run 43496312451](https://github.com/mxlzz/ACD/actions/runs/43496312451) **success**: Italian Flat Cam Kitchen Table (320×200, seeds8819/8922) interseed RMSE 8spp 0.24900, 16spp 0.17253, 32spp 0.11853, approx 1/sqrt(spp) behavior. CPU 30–34s/render with major fixed cost; 640x400 8spp 33.319s vs 320x200 8spp 30.166s. Process peak RSS ~10,968,480 KB. These references still noisy and not converged.
- E0042 predeclares 640×400, 32/64/128 spp × two independent seeds, no denoiser, locked SHA/source/camera. Render costs, actual interseed RMSE and 1:1 reference gallery preserved. **Results not claimed before workflow success.** No 1080p or test-set overfitting.

Control: 640×400 con 32/64/128 spp y dos seeds. Rechazar si cambia SHA256 de archivo fuente o falta alguno de los seis EXR. Registrar diferencias de semilla y tiempos, con visuales que comparten transferencia diagnóstica, no OCIO. No hay datos de denoiser ni prueba de convergencia. Nunca usar E0042 como holdout, ya observado.
