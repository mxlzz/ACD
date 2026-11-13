# E0043 — Diagnóstico de daño de detalle por guías de OIDN (Blender 5.2.4)

**Preinscrito antes del run:** 13-11-2026. Su objetivo es localizar fallos en imágenes reales, **no crear o validar una nueva técnica de denoising**.

## Revisión de anterioridad y criterio de no duplicación

- [Documentación oficial Intel OIDN](https://www.openimagedenoise.org/documentation.html): guías albedo/normal mejoran detalles, el prefiltrado de guías ruidosas es conocido, y la utilidad de la primera superficie en reflejos/transmisión es limitada. Ya se proponen guías de hits posteriores. Por tanto no atribuir originalidad a la simple inclusión/exclusión de guías.
- [Código Blender 5.2.4 Cycles properties](https://github.com/blender/blender/blob/v5.2.4/intern/cycles/blender/addon/properties.py): RGB, RGB+Albedo y RGB+Albedo+Normal; prefilter NONE/FAST/ACCURATE. No reinventar controles ya implementados.
- [ACD E0013](E0013.md): Standard=OIDN y High/Super regresivos en casos históricos. [E0033](E0033.md): Emission50 falló la generalización. [E0035–E0039](E0039.md): rutas de API/guías auditadas, sin resolver igualdad de CLI. [E0042](E0042.md): Italian Flat references 128 spp y dispersión no convergida (RMSE entre refs ≈0.05549).
- Esta prueba es **una única ablation diagnóstica de 3 configuraciones ya existentes**. Si no identifica errores localizados claramente distinguibles de la variabilidad de referencias, se descarta y no se continúa optimizando configuraciones.

## Protocolo congelado

- Fuente Italian Flat © Flavio Della Tommasa, Blender Demo Cycles CC-BY, SHA256 `0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25`; se descarga únicamente en runner, no redistribuir .blend.
- Blender **5.2.4 LTS**, cámara **Cam Kitchen Table**, Cycles CPU, 640×400, 32 spp, seed **539**, denoising interno OFF, adaptive OFF. Un único render produce las cuatro salidas **Raw, OIDN RGB-only, OIDN Albedo, OIDN Albedo+Normal**. Cada denoiser: **High, Accurate, HDR**. Mismo `CompositorNodeRLayers.Image` como color y sockets `Denoising Albedo/Normal` de ese mismo render. No modificar escena original.
- Referencias **ya renderizadas**: EXACTAMENTE `ref_640x400_128spp_seed8819.exr` y `ref_640x400_128spp_seed8922.exr` de E0042 run [43497486691](https://github.com/mxlzz/ACD/actions/runs/43497486691), verificadas por SHA256 de manifiesto. No nuevos renders de referencias. No usar refs para construir candidatos.
- Evaluar RMSE lineal HDR global de cada candidato contra las 2 refs y gradiente de detalle (misma métrica existente), error referencia contra referencia; además grilla predefinida de 4×4 regiones (160×100) y acuerdo de dirección entre las dos refs al comparar `OIDN Albedo+Normal` contra `OIDN RGB`. Visualizar las cuatro salidas y las dos refs con misma transformación diagnóstica (NO Blender OCIO). No usar diferencia mínima de RMSE como prueba de calidad.
- **Criterio de éxito exploratorio (no promoción):** hallar una región de geometría/materiales interpretables donde la diferencia atribuible a guías tiene dirección consistente respecto de ambas refs y el margen no es trivial frente al desacuerdo de referencias. Además inspeccionar visualmente a escala 1:1 antes de formular mecanismo. Caso contrario **descartar como candidato**, sin reajustar parámetros ni lanzar otra prueba sobre la misma escena.
- **Limitación crítica:** 128spp ref1 vs ref2 difieren significativamente. Esto NO proporciona verdad de referencia convergente, ni efecto causal universal ni validez estadística por tener una sola semilla ruidosa. NO sacar conclusiones generalizables ni integrar el addon. Si el efecto es pequeño, no escalar spp automáticamente; diseñar primero un caso sintético con referencia más estable.

## Costes y salida

Un solo nuevo render 640×400 32 spp, 3 filtros compositor del mismo RenderLayer; refs recuperadas del artifact temporal E0042. Guardar JSON y galería PNG permanentemente, EXR temporal 14 días. Sin tests de CI pesados recurrentes, no automatizar tuning. Mantener PR #10 experimental y addon estable inalterado.
