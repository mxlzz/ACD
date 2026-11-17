# E0063 — Lone Monk: control de variación real entre semillas (preinscrito, 16-11-2026)

**Pregunta acotada:** ¿dos procesos Blender independientes producen ruido Raw efectivamente distinto en la nueva escena arquitectónica oficial de Lone Monk? En Classroom E0056 la mayor parte de los píxeles era idéntica, pese a variar el seed. Sin esta puerta no se admiten promedios multisemilla.

**Fuente fijada E0062:** Lone Monk, Carlo Bergonzini/Monorender CC BY, demo oficial Cycles, escena original `daylight`, cámara `cam.001`, fuente 33.452.252 bytes, SHA256 `eea2bbfb3f9271050f523c8351fca40f2f559ce84b42b0143e949ecdb4594c3b`. Auditoría E0062 funcional, sin imágenes ni IES faltantes. Usar únicamente el mismo binario; si cambia el hash, abortar y auditar nuevamente.

**Protocolo:** Blender 5.2.4 CPU, 96×54, 16 spp, adaptive OFF, denoising OFF, patrón TABULATED_SOBOL, offset0. Dos procesos Blender separados (no solo dos invocaciones `bpy.ops.render`), semillas 539 y 911. No mover cámara, geometría, materiales ni guardar la fuente.

**Requisitos:** metadata activa `daylight`/`cam.001`, 16spp, patrón y seed correctos, EXR scene-linear 96×54 finitos, identidades SHA256 de fuente y salida, RMSE relativo de imágenes Raw y píxeles que cambiaron >1e-6. El umbral heredado de detección es 1e-4 relativo; su superación solo prueba diferencia medible, **no independencia estadística** ni convergencia.

**Puerta:** PASS si hay cambio significativo de Raw sin alterar la fuente. FAIL si las imágenes son virtualmente idénticas o alguna comprobación falla. Archivar ambas respuestas, sin imágenes/EXR en GitHub, ni cambio de addon.

**Keep on track:** después de PASS no repetir otros smokes de 96px por inercia; el próximo experimento útil deberá usar rasgos arquitectónicos físicamente resolubles a densidad de entrega y referencias con discrepancia suficientemente acotada, para localizar error residual atribuible a OIDN y comparar costo de aumentar spp. E0063 no constituye benchmark de denoising ni test holdout. PR #10 draft y addon estable sin cambios.
