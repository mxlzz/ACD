# E0058 — Validación de diversidad de ruido en cámara interior, escena Surat (16-11-2026)

E0057 verificó funcionalmente una escena de arquitectura de 4.717 objetos y 105 materiales, 18 cámaras, sin recursos faltantes (run 43936110361); aún NO admite usarla como holdout público: los derechos sobre el diseño real son desconocidos, aunque la contribución del modelador sea CC0. Ninguna fuente ni render derivado se redistribuirán.

Hipótesis puntual: en esta escena completa, la cámara original CAM Office genera Raw físicamente distinto con semillas de Cycles 539 y 911. Si no, se rechaza para inferencias multisemilla (al igual que Classroom E0056); si sí, continúa como *candidato técnico*, no como holdout admitido.

Fuente inmutable: ZIP del release v1.0.1, 166.627.773 bytes y SHA256 721e77b401fba0fa5c3b9df13b09279c6d05781af865f2b63945e7e032e991a8. Blender5.2.4, scene Scene y cámara CAM Office, procedencia de cámara indicada en los scripts públicos de arquitectura del mismo autor. Dos procesos Blender independientes, render CPU Cycles 96x54, 16 spp, adaptive OFF, denoising OFF, TABULATED_SOBOL, offset0. No modificación/salvado del .blend.

Preinscripción: require archivo exacto y cámara original, metadata escena/semilla/patrón/cantidad, EXR RGB finite correct shape, comparar RMSE lineal, RMSE relativo RMS señal, píxeles cambiados >1e-6, umbral existente >=1e-4. Fail closed en asset corrupto/cámara ausente/render/API distinto. Guardar metadata y SHA de EXR, no imágenes ni EXR en repositorio público. Una diferencia medible NO prueba independencia estadística, referencias convergidas, relevancia visual ni mejora de ACD.

Keep-on-track: solo puerta B1/B2 de aptitud de corpus, NO comparador ni cambio de denoiser. Si falla, descartar, no insistir ni inventar muestras. Si supera, la próxima prueba útil es evaluar convergencia de referencias en escena de otro autor y separar contribución de Raw vs OIDN, con derechos resueltos antes de divulgar resultados visuales. PR #10 draft, stable addon intacto.
