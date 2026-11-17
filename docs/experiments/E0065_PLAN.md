# E0065 — Lone Monk: residuo nativo OIDN sobre arquitectura a densidad de entrega

**Preinscrito 2026-11-16, antes de cualquier denoising de esta región.** La finalidad rectora de ACD sigue siendo superar de manera demostrable el denoiser OIDN de Blender en *fidelidad física de detalle arquitectónico*, sin elevar ruido, error HDR ni coste innecesario. E0059 descartó que una pérdida de amplitud en sí sola justifique sharpen. Este ensayo investiga **un error residual de baseline** sobre otra escena, no inventa aún otro filtro.

## Procedencia/selección sin fuga de resultados

Lone Monk, Carlo Bergonzini / Monorender, demo oficial Blender Cycles CC BY; archivo original actualizado, exactamente 33.452.252 bytes, SHA256 eea2bbfb3f9271050f523c8351fca40f2f559ce84b42b0143e949ecdb4594c3b; cámara original daylight/cam.001, escena guardada a 1440×1080 (4:3). Auditoría funcional E0062 PASS; E0063 comprobó variación Raw entre semillas; E0064 realizó únicamente un render Raw/PNG original sin denoise de 960×720 / 8spp, SHA256 22ab1cf8ebfd76078d5bd3f1e84ebe8ac9e812c1797eb1e0216a342cfb1a16b7, 16,73s CPU.

**Imagen observada E0064:** claustro románico con portal central, cornisa/pedimento y columnas entre arcadas. El rasgo se seleccionó por geometría arquitectónica visible, **antes** de generar o mirar cualquier salida filtrada o referencia de E0065. No volver a mover el recorte por ganar una métrica.

## Geometría fijada

Full virtual **1920×1440**, mismo FOV y proporción que la cámara original, no una modificación de lente. Realizar crop de Cycles border arriba-izquierda **(700,430,512,512)**, sin renderizar todo el frame; guardia de contexto **64 píxeles** en los cuatro lados. ROI de evaluación interior **(64,64,384,384)** en coordenadas de imagen ya recortada. Dos subregiones semánticas predefinidas, también dentro de ese interior: cornisa/pedimento (64,64,384,160) y columnas/arco (64,224,384,224). Calcular también crop completo como control. Imagen de encuadre E0064 y coordenadas son únicas fuentes para esta selección; la profundidad visual/semántica no se infiere de una máscara de gradientes de referencia.

## Protocolo de costo y fidelidad

Render Blender **5.2.4 LTS**, Cycles CPU, adaptive OFF, denoising interno OFF, misma geometría, materiales, cámara y luces; tres Raw **24spp** de seeds 539, 911, 1337, y **dos referencias finitas 512spp** seeds 8819/8922. Nodo compositor OIDN native High/Accurate/HDR con AOV Albedo/Normal de exactamente el mismo RenderLayer; addon STANDARD como verificación de identidad (NO nueva técnica). No SID5, no High/Super, no variar guías, no modificar addon ni guardar .blend.

Checks fail-closed: fuente/cámara/aspecto/hash/spp/seed, crop 512² y ROI 384², float RGB finito, guías originales presentes, Raw passthrough igual a beauty multilayer <=1e-5, STANDARD = native compositor OIDN <=1e-5, todas las noisy seeds distintas, referencias distintas, elapsed CPU wall >0. Toda discrepancia aborta y queda en logs. Artifacts EXR solo siete días, JSON+hash y panel de contacto 1:1 con atribución CC BY permanentes.

**Métricas preregistradas:** por cada región física fija, RMSE HDR scene-linear entre las dos referencias, RMSE Raw/OIDN contra **cada referencia** por las tres semillas, RMSE de gradientes de luminancia asinh scene-linear entre refs y OIDN, error de gradiente sin umbrales reoptimizados, variación entre referencias dividida por error nativo OIDN, CPU wall real. Contacto visual 1:1 Raw/OIDN/RefA/RefB con un mismo transfer de diagnóstico (no equivale a Blender OCIO/AgX). Reportar referencia insuficiente si discrepancia relativa sigue siendo grande (pantalla pragmática <0,50 refref/native, no prueba de convergencia). Comparación con imagen Raw es solo contexto de nivel de ruido, NO criterio para decir que OIDN destruye detalle real.

## Decisión después del run

Si referencias demasiado distintas o render demasiado caro: **STOP**, sin nuevo filtro. Si el residuo de OIDN aparece estable entre refs y semillas: verificar físicamente su patrón (junta, perfil de moldura o columna), luego comparar contra aumentar samples Cycles a coste equivalente y contra métodos ya publicados antes de idear candidato. Esta escena fue vista al seleccionar ROI: **desarrollo**, no holdout ciego. Reservar otra escena de autor independiente para generalización. PR #10 draft, producto estable intacto. Un archivo con licencia libre permite experimentación, pero no sustituye referencias convergidas.
