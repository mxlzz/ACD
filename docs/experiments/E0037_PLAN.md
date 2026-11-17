# E0037 — OIDN CLI 2.5.1 con guías congeladas

## 2026-11-13 — E0037 preinscripción y método

- Objetivo: comparar OIDN standalone 2.5.1 sobre los datos reales ya congelados de E0035 (16 spp, 128×96, dos versiones) sin re-renderizar ni atribuir calidad. Se exige SHA256 exacto de Raw, compositor y multilayer, verificación de PFM float32 e identidad de AOV.
- Dos modos: raw_aux (OIDN RT high/HDR guías originales, cleanAux=false) vs accurate_like (OIDN RT high prefilter solo albedo, luego normal, luego beauty con cleanAux=true). La guía de OIDN indica este prefiltrado; no se asume paridad exacta con el compositor Blender y no se mide verdad de referencia.
- A registrar: RMSE directo respecto a compositor por misma versión, mayor diferencia, SHA256, flags de CPU y walltime por subprocess con overhead. Resultado todavía no obtenido; workflow separado en próximo commit. No tocar addon.

Origen: [E0035_RESULTS.json](E0035_RESULTS.json), [run 43480823352](https://github.com/mxlzz/ACD/actions/runs/43480823352). Documentación oficial: https://www.openimagedenoise.org/documentation.html . Binario release Apache-2.0; comprobar SHA256 tar 743c3e2aff8c220d5d70fe6cb970fb3d36f2702d2693c61d1d148e404cf37cd6. Cualquier diferencia aquí es entre outputs sin ground truth convergente. No confundir walltime del CLI con costo nativo Blender. Artifacts fuente vencen 2026-11-27.
