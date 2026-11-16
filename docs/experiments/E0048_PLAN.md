# E0048 — Diagnóstico causal de Denoising Pass Reflections (16-11-2026)

**Pregunta:** E0047 mostró ratio de bordes de ~0.50 tras vidrio frente a ~0.91 en lamas descubiertas, pero las regiones tienen distintos materiales/iluminación y las referencias 512spp no convergieron. ¿El seguimiento de reflejos en guías de Cycles contribuye a esa pérdida?

**Estado del arte:** Intel OIDN documenta guías albedo/normal y seguimiento de hits posteriores a reflexiones/refracciones; Blender 5.2.4 ya incluye la opción `ViewLayer.cycles.denoising_pass_follow_reflections` con valor predeterminado True. Fuentes: https://www.openimagedenoise.org/documentation.html y https://github.com/blender/blender/blob/v5.2.4/intern/cycles/blender/addon/properties.py . No se reclama novedad algorítmica.

**Prueba única y fijada:** reutilizar por SHA EXR de E0046 run43883209135: Raw seed539 24spp, nodo compositor OIDN High/Accurate/HDR, dos refs seed8819/8922 512spp, Blender 5.2.4 CPU, crop512×512 con campo visual 1920×1440 (rect [928,320,512,512]). Realizar **un solo nuevo render de 24spp seed539** en el mismo fixture, sin modificar geometría ni cámara, con el único cambio `denoising_pass_follow_reflections=False`. Copiar ref1 de E0046 para evitar referencias nuevas; usar ref1 y ref2 existentes al analizar.

**Puertas de descarte:** (1) Exigir Raw pixel a pixel idéntico (tolerancia max absoluta 1e-5) entre renders; si cambia, no atribuir diferencia a guías. (2) Si no cambian AOV albedo/normal, detener hipótesis. (3) Solo entonces medir OIDN output contra ambas refs en ROIs fijas de E0047, glass=[104,192,80,160], uncovered=[328,192,80,160] y centro320×320. Reportar RMSE y detail_fidelity y efecto sobre guías. Cualquier mejora debe sobrevivir refs y no empeorar otros sectores. *Ref refs no convergidas*, por lo que prueba causal local ≠ mejora de calidad demostrada.

No hay nueva arquitectura de denoiser ni entrenamiento. El addon estable permanece intacto y PR#10 en draft. No continuar tuning si resultado no es inequívoco.
