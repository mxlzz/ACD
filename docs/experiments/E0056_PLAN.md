# E0056 — Reexaminar bloqueo de Classroom CC0 en Cycles 5.2.4

Investigación central: corpus de escenas reales para comparar fidelidad con OIDN moderno. Classroom, obra de Christophe Seux publicada por Blender como CC0, sería útil por arquitectura interior y materiales; E0007 halló que dos seeds diferentes casi no alteraban la salida Raw en Blender 5.0.1, por lo que NO se permite validar promedios independientes con esa escena.

Hipótesis delimitada: en Blender 5.2.4 LTS, la misma escena y el patrón de muestreo original podrían producir realizaciones distintas entre seeds 539 y 911. Si no, Classroom sigue excluida; no es obligatorio corregir Cycles para continuar ACD.

Protocolo invariable E0007: ZIP oficial https://download.blender.org/demo/test/classroom.zip, SHA256 0f0ecc58d45f12b2f4272a53e2d8e69135518e16e956b118f10c20d8dcf5e6, tamaño 70.279.690 bytes; verificar ZIP antes de extraer, no redistribuir. Auditar con audit_public_scene.py. Dos procesos Blender aislados, misma cámara y escena, CPU Cycles, 96x54, 16spp, adaptive OFF, denoising OFF, sample_offset0, sampling_pattern TABULATED_SOBOL, seeds539 y 911. Los EXR son Raw lineales.

Medición predeclarada: RMSE lineal, delta máximo, píxeles modificados por más de 1e-6, RMSE inter-seed dividido por RMS señal. Umbral diagnóstico ya existente: >=1e-4 relativo; si menor, no hay diversidad medible. Ninguna comparación denoiser, ni reference 512 spp, ni algoritmo nuevo. Registrar metadatos de sampling por escena/view layer y hashes de las salidas.

Interpretación: si E0056 encuentra cambio, eso solo prueba variación, NO independencia estadística ni fidelidad de referencia; exigir pruebas multisemilla y AOV completos antes de usar Classroom en holdout. Si todavía hay identidad casi total, STOP y buscar escena libre alternativa. Si el patrón TABULATED_SOBOL ya no existe o la escena tiene recursos faltantes, resultado inconcluso por incompatibilidad; no improvisar otro patrón. E0054 Cozy es desarrollo, referencias finitas. No modificar addon ni hacer modelos nuevos.
