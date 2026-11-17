# E0044 — Validar si OIDN actual conserva los detalles que fallaban en Blender 5.0.1

Fecha: 2026-11-16. Estado en este commit: protocolo y código, **resultados pendientes de CI**.

**Objetivo ACD:** buscar una pérdida específica de detalles geométricos arquitectónicos con OIDN 5.2.4 antes de crear otro algoritmo. Si el comportamiento ya se corrigió en Blender, no intervenir.

## Revisión de anterioridad y justificación de una sola repetición

- [E0016](E0016.md) ya midió el fixture procedural `detail_target` en Blender 5.0.1, 320x240, 24 spp ×3, refs1024×2. OIDN / Standard RMSE 0.0608849 y error de gradientes 0.0721193 (primera referencia); High/Super empeoraron. **No repetir variantes High/Super, ni ajustar Emission50**.
- En marzo de 2026 Blender fusionó [PR 154988](https://projects.blender.org/blender/blender/pulls/154988), revisión de la escritura de los pases de denoising (umbrales de rugosidad especular y relación especular/difusa suavizados). El resultado previo de 5.0.1 **no basta** para atribuir fallas a Blender 5.2.4, que ya incluye la modificación.
- [Intel OIDN](https://www.openimagedenoise.org/documentation.html) ya incluye guías albedo/normal prefiltradas y seguimiento de hits especulares; no proponer como idea original algo que su API resuelve.
- [E0043](E0043.md) descartó combinaciones de guías como mejora candidata y descubrió IES faltante en la escena Italian Flat. E0044 usa únicamente geometría/materiales generados por código y sin ningún archivo externo.

## Ensayo predefinido

- Software: **Blender 5.2.4 LTS oficial**, SHA-256 del archivo de distribución verificado contra el manifiesto oficial.
- Fixture *sin dependencias*: `tests/scene_detail_target.py` con 52 lamas, juntas de azulejos, vidrio, metal y microbump; resolución **320×240**. Un input noisy de **24 spp / semilla 539**; dos referencias **1024 spp** (8819 y 8922). CPU. Empleo de igual RenderLayer/AOV y `CompositorNodeDenoise` Accurate/High/HDR con Albedo y Normal. Se desactiva adaptive sampling para que el spp sea explícito; el addon estable no se toca.
- Solo **Raw vs OIDN compositor**, sin High/Super, SID4, CLI ni variantes de emisión. Verificar igualdad de Raw con Combined multilayer y metadatos.
- Métricas frente a cada referencia: RMSE HDR lineal, error de gradientes asinh RGB (fidelidad de bordes), ratio de contraste de borde, referencia-referencia; **rejilla fija 4×3 de 80x80** de regiones independientes; reporte descriptivo de dónde OIDN reduce fuerza de borde. Los tiles son geométricos e independientes, pero el criterio de borde usa la referencia y sigue siendo una métrica proxy.
- Publicar una lámina 1:1 y métricas JSON en Git. EXR + AOV crudos en artefacto temporal 14 días. No publicar como mejoras del denoiser las discrepancias inter-versión, porque Blender 5.0.1 y 5.2.4 no comparten exactamente la misma entrada Monte Carlo.

## Condición de decisión

**Continuar** hacia hipótesis causal y eventual intervención solo si se observa un fallo de detalle claro en la escena actual, consistente con ambas referencias y significativamente superior al desacuerdo entre referencias, revisado también en visualización 1:1.

**Descartar la línea** si solo aparecen ratios de contraste menores sin mayor error atribuible, si el fallo ya está explicado/solucionado en Cycles, o si la incertidumbre de las referencias impide afirmar algo. No hacer más renders ni crear modelos nuevos para forzar una mejora. Un hallazgo de una escena sintética solo habilita una investigación, no la integración de ACD.

El coste de este diagnóstico es un input y dos referencias; no es un benchmark a escala de entrega.