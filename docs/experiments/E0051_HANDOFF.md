# E0051 — Puerta científica antes de proponer otro algoritmo

**Decisión 16-11-2026:** cerrar ensayos de configuración nativa. El objetivo central sigue siendo superar a OIDN en conservación **fiel** de detalles arquitectónicos a escala de entrega y con coste justificado.

**Evidencia y anterioridad:**
- [E0048](E0048.md), run43893867618: mismo Raw exacto. La opción preexistente Cycles `denoising_pass_follow_reflections=True` produce menor RMSE tras vidrio (0.07040 vs 0.07580 al desactivarla), también mejor global 0.06840 vs 0.07744. Ya documentado por OIDN y Blender; **no es innovación ACD**.
- [E0049](E0049.md), run43894800865: desactivar ponderación de albedo por rugosidad cambió Raw (máximo absoluto 0.077223). Rechazada inferencia causal directa.
- [E0050](E0050.md), run43895999901: con Raw idéntico cargado de EXR, replay del OIDN con guías originales difirió de la salida original (máximo absoluto 0.034577 > criterio 0.0001). No se puede afirmar que el swap de guías mejore el pipeline nativo. El resultado del swap (RMSE entre outputs ~0.01065) **no** mide superioridad visual.
- E0045 corrigió detalle sub-Nyquist, E0046/47 identificaron lamas tras vidrio atenuadas (~50% contraste de borde frente a ~91% en lamas directas), pero referencias 512spp no convergentes, ROI distintas y una escena sintética observada.
- No repetir variantes High/Super/Emission50 ni toggles de OIDN/Cycles conocidos. Documentación de anterioridad: https://www.openimagedenoise.org/documentation.html y https://github.com/blender/blender/blob/v5.2.4/intern/cycles/blender/addon/properties.py .

**Siguiente entrada indispensable:** un fallo real reproducible en escena arquitectónica completa. Preferencia: el archivo `Prueba ACD.blend` que se había compartido en otro chat; no está accesible en los archivos de la sesión actual. Debe incluir recursos empaquetados, archivos IES externos, bibliotecas enlazadas y permisos de uso. Alternativa: EXR lineales Raw/OIDN y dos referencias Cycles con misma cámara y regiones específicas donde se pierda detalle.

**Reanudación cuando exista la entrada:** (1) fuente, SHA, licencia, cámara y dependencias verificadas; smoke CPU 192px×4spp; (2) recorte a densidad 1080/1920 con detalle físicamente representable; (3) OIDN y cualquier variante sobre Raw idéntico, referencias con incertidumbre suficiente; (4) localizar error residual que OIDN/Cycles no resuelven y comprobar anterioridad; (5) solo entonces prueba de nueva corrección falsable, validación en holdout y coste vs aumentar spp. La fuente privada no se subirá al repo público sin autorización.

No entrenamiento/fork/merge ahora; PR#10 draft y addon estable intactos. El bloqueo es de **evidencia representativa**, no de capacidad de ejecutar otra acción.
