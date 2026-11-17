# E0039 — Identidad de guías Blender compositor vs AOV

## 2026-11-13 — E0039: identidad de guías comprobable

- E0038 confirmó que la versión 2.5.0 vs 2.5.1 aporta RMSE ~2e-6, mientras CLI vs Blender sigue ~0.04035 en guías prefiltradas: divergencia sin explicar.
- El código de Blender 5.2.4 node_composite_denoise.cc usa OIDN RT y filtros auxiliares separados; para comprobar si son idénticas las señales, E0039 exportará en el mismo render los sockets Noisy Image, Denoising Albedo y Denoising Normal y comparará contra EXR multilayer, sin usar referencias para ranking. También invalida un supuesto si esas guías no coinciden.
- Cambio de blender_compare_smoke.py limitado a bandera opt-in ACD_E0039_CAPTURE_SOCKETS; flujo estándar intacto. Workflow E0039 dispara y publica reportes si pasa.

Puerta: RMSE y máximo absoluto del mismo render 5.2.4 128x96 16spp, sockets exactos vs EXR. No se evalúa calidad ni comparaciones entre versiones. OIDN compositor source: https://github.com/blender/blender/blob/v5.2.4/source/blender/nodes/composite/nodes/node_composite_denoise.cc .
