# E0051 — Puerta científica antes de proponer otro algoritmo

**Decisión 16-11-2026:** cerrar ensayos de configuración nativa. El objetivo central sigue siendo superar a OIDN en conservación **fiel** de detalles arquitectónicos a escala de entrega y con coste justificado.

**Evidencia y anterioridad:**
- [E0048](E0048.md), run43893867618: mismo Raw exacto. La opción preexistente Cycles `denoising_pass_follow_reflections=True` produce menor RMSE tras vidrio (0.07040 vs 0.07580 al desactivarla), también mejor global 0.06840 vs 0.07744. Ya documentado por OIDN y Blender; **no es innovación ACD**.
- [E0049](E0049.md), run43894800865: desactivar ponderación de albedo por rugosidad cambió Raw (máximo absoluto 0.077223). Rechazada inferencia causal directa.
- [E0050](E0050.md), run43895999901: con Raw idéntico cargado de EXR, replay del OIDN con guías originales difirió de la salida original (máximo absoluto 0.034577 > criterio 0.0001). No se puede afirmar que el swap de guías mejore el pipeline nativo. El resultado del swap (RMSE entre outputs ~0.01065) **no** mide superioridad visual.
- E0045 corrigió detalle sub-Nyquist, E0046/47 identificaron lamas tras vidrio atenuadas (~50% contraste de borde frente a ~91% en lamas directas), pero referencias 512spp no convergentes, ROI distintas y una escena sintética observada.
- No repetir variantes High/Super/Emission50 ni toggles de OIDN/Cycles conocidos. Documentación de anterioridad: https://www.openimagedenoise.org/documentation.html y https://github.com/blender/blender/blob/v5.2.4/intern/cycles/blender/addon/properties.py .

**Siguiente condición indispensable:** un fallo reproducible en una escena arquitectónica completa con recursos resueltos, licencia comprobada, Raw/AOV compatibles y referencias suficientemente fiables. **No se exige que sea una escena propia**: usar primero el corpus libre auditado, según [B1_PUBLIC_CORPUS_RESTART](B1_PUBLIC_CORPUS_RESTART.md). `Prueba ACD.blend` queda como entrada privada opcional, no bloqueante. Otra alternativa son EXR lineales Raw/OIDN y dos referencias Cycles de la misma escena y cámara.

**Reanudación cuando exista la entrada:** (1) fuente, SHA, licencia, cámara y dependencias verificadas; smoke CPU 192px×4spp; (2) recorte a densidad 1080/1920 con detalle físicamente representable; (3) OIDN y cualquier variante sobre Raw idéntico, referencias con incertidumbre suficiente; (4) localizar error residual que OIDN/Cycles no resuelven y comprobar anterioridad; (5) solo entonces prueba de nueva corrección falsable, validación en holdout y coste vs aumentar spp. La fuente privada no se subirá al repo público sin autorización.

No entrenamiento/fork/merge ahora; PR#10 draft y addon estable intactos. El bloqueo es de **evidencia representativa**, no de capacidad de ejecutar otra acción.

## Verificación de acceso a fuente original (16-11-2026)

Se localizó un registro privado de `Prueba ACD.blend` en la biblioteca asociada al proyecto (166.912.086 bytes; 12-11-2026). **Solo se recuperó el metadato**, no el contenido binario: el intento de obtener una copia de trabajo devolvió «This Project file does not have an authorized raw-byte materialization path». En consecuencia, no se ha abierto con Blender, no se ha comprobado su integridad ni se ha observado su contenido. No afirmar que la escena esté disponible para ejecutar benchmarks.

**Solo si se elige esta fuente privada:** volver a adjuntar el `.blend` en el chat activo o facilitar un enlace de descarga autorizado al archivo completo. Si la escena depende de imágenes, bibliotecas o IES externos, adjuntar también esas dependencias o empaquetarlas previamente. Mantener la escena privada; no publicarla en GitHub. Una vez disponible, seguir la puerta de aceptación y el protocolo de comparación definidos arriba. Sin nuevos renders ni cambios al addon a partir de la mera existencia del metadato.

**Corrección de auditoría:** en la descripción archivada de E0049 aparecía `follow=False` por un error del generador de informes; el workflow fija únicamente `ACD_E0049_ROUGHNESS_WEIGHTING=0` y el script de Blender exige `follow_reflections=True`. Se corrigió la interpretación documental, sin alterar los resultados numéricos ni repetir el experimento.
