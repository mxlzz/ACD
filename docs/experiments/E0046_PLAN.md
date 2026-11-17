# E0046 — Muestra a densidad de imagen de 1920 px, sin render completo

**Preinscrito antes de ejecutar:** 2026-11-16. Parte de B3: localizar un fallo genuino de OIDN en lamas arquitectónicas físicamente resolubles.

## Motivo y anterioridad

E0044 sobre Blender 5.2.4 halló contraste de bordes OIDN ~0.686 frente a referencias; E0045 demostró que las 52 lamas estaban proyectadas a 1.30–1.68 px por período en 320px de ancho, **por debajo de Nyquist ideal**. Continuar comparando filtros a esa escala podría confundir información subpixel con error del denoiser.

Intel OIDN ya utiliza albedo/normal y Blender 5.1 suavizó las discontinuidades de sus guías. E0046 no prueba una modificación: comprueba **si sigue existiendo una pérdida de contraste relevante cuando la geometría sí está representada en varios píxeles**.

## Fixture congelado y control

- `tests/scene_detail_target.py`, sin texturas o IES externos; Blender 5.2.4 LTS oficial con hash verificado; cámara y geometría originales inalteradas.
- Resolución de cámara **1920×1440**, FOV idéntico al del benchmark anterior. Render border con `use_crop_to_border=True`; solo se calculan los píxeles dentro del rectángulo de imagen **x928:y320:512×512** (origen superior izquierdo). El centro evaluado es **x+96:y+96:320×320** para evitar bordes de mosaico sin contexto.
- Input noisy **24 spp, seed539**; referencias **512 spp, seeds8819/8922**, adaptive OFF y denoising interno OFF. Todos los filtros comparten el mismo RenderLayer por seed. Únicamente **Raw y OIDN compositor Accurate/High/HDR** con sus guías originales. El addon ACD de producto queda intacto.
- La separación de lamas dentro del crop es ~8–10 px en la imagen virtual de 1920px, vs ~1.3–1.7 px a 320. **Esto habilita evaluar líneas**, no demuestra que la referencia512 haya convergido.
- Verificar que los EXR sean verdaderamente **512×512**, que los buffers Raw y Combined multilayer sean idénticos, que los parámetros y el crop coincidan y que las referencias sean diferentes. Si la imagen devuelve resolución distinta o la cámara/FOV cambian, **fallo de contrato**, no interpretar métricas.
- Analizar solo el centro 320×320. Comparar RMSE scene-linear y error de gradientes asinh RGB, ratio contraste y referencia-referencia. Subdividir ese centro en cuatro ROIs no solapados 160×160; el resultado determina si hay una región de detalle a investigar.
- Guardar PNG cuatro vías (Raw, OIDN, ref1/ref2), mismo display diagnóstico no OCIO/AgX, JSON, hashes y limitaciones. EXR temporal 14 días.

## Decisión congelada

1. Si hay pérdida visual clara de geometría resoluble, consistente en ambas refs y el ruido de referencia no domina, avanzar a un experimento causal sobre **la guía detrás del vidrio**, no a otra mezcla genérica de Raw/OIDN.
2. Si OIDN recupera la geometría suficientemente, o si 512 spp no separa el error del ruido residual, no inventar un algoritmo ni subir spp automáticamente; documentar resultado y solicitar un caso real de fallo verificable.
3. Una mejora general solo se considera después de comparar varios seeds, múltiples escenas independientes y coste adicional; E0046 no valida el addon ni el rendimiento a 1920px de imagen completa.

**Riesgo admitido:** el nodo OIDN ve únicamente un crop 512² y no la imagen entera. Se excluye un margen interior de 96px para reducir, sin demostrar que elimina, el efecto del campo receptivo del denoiser.