# E0012 — Prueba de guías por componente (protocolo)

Configurado: 2026-11-11. El protocolo fue registrado durante la ejecución inicial del workflow, antes de inspeccionar los resultados. Resultados y conclusiones deben agregarse en un archivo independiente; no reescribir retroactivamente criterios tras observar las métricas.

## Pregunta

¿La pérdida de fidelidad de High/Super en el lobby de E0011 proviene parcialmente de usar guías de Normal y Albedo del hit visible para filtrar contribuciones distintas (reflejos y transmisión)?

Esta es una **hipótesis** basada en ablations E0001/E0002 y literatura sobre denoising condicionado por tipo de señal; los resultados E0011 por sí solos no establecen causalidad.

## Control experimental

- Escena procedural y referencias: exactamente la configuración E0011, Blender 5.0.1, 128×96, 24 spp por entrada, nominales 539/911/1337 y dos referencias 1024 spp, mismas luces, geometría y política de compositing.
- Métodos principales: Standard, High, Super.
- Ablación del método Standard: sin Albedo ni Normal, para distinguir el valor general de las guías.
- Ablaciones High/Super en **los filtros de contribución**, manteniendo intactas las conexiones del denoiser final: ambas guías, ninguna, solamente Albedo y solamente Normal.
- Los métodos High_no_guides y Super_no_guides históricos (que quitaban también guías del filtro final) no participan en este conjunto. No confundir esas definiciones.
- Todas las ramas de un seed comparten un mismo RenderLayer y un presupuesto igual de muestras.
- Máscaras AOV: glossy y transmission, determinadas desde un EXR común, exactitud espacial verificada con SHA-256. No son máscaras de ID de material.

## Criterios de lectura

1. Métrica primaria exploratoria: media de RMSE RGB en luz lineal de tres entradas para imagen completa y dos regiones de radiancia.
2. Métricas de apoyo: MAE, p95 por píxel y error de luminancia transformada. Valorar compromisos, sin optimizar exclusivamente RMSE.
3. El control de diversidad por imagen es requisito previo pero no certifica independencia estadística.
4. Evaluar discrepancia entre referencias y estabilidad de orden frente a ambas; no asumir convergencia.
5. Una sola escena pequeña y pocas semillas no permiten promover una variante al addon estable aunque aparezca una mejora.

## Resultado esperado

Se desconoce. Una mejora de High/Super tras quitar una guía sería evidencia de que las guías afectan su rendimiento en esta escena, **no** evidencia suficiente de por qué ni de superioridad general. Un fallo de alguna configuración (por ejemplo, Normal sin Albedo) debe documentarse como restricción de la API de Blender/OIDN, no ocultarse.

Workflow: https://github.com/mxlzz/ACD/actions/workflows/glass-guide-ablation.yml

Artifacts de EXR en Actions: retención 7 días. Conservar aquí las métricas, ajustes, hashes y referencias antes de su expiración.
