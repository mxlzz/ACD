# E0059 — Cross-reference error de borde sobre Cozy (preinscripción 16-11-2026)

**Objetivo rector:** E0054 observó una ganancia de borde OIDN ~0.74-0.75 pero Raw ~0.78-0.79; la mayor parte de la atenuación no es imputable exclusivamente al denoiser. E0054 refs512spp discrepan RMSE0.077947, 0.845 veces el error nativo. NO justificar sharpen ni filtro nuevo desde esa amplitud.

**Pregunta nueva y falsable:** ¿empeora OIDN el error de *gradiente* frente a la propia entrada Raw sobre bordes definidos SIN utilizar la referencia que evalúa? Es una regresión local contra Raw, no una comparación con un ACD nuevo y no demuestra superioridad perceptual.

**Datos:** E0054 run43930780340, original Cozy Kitchen © Nicole Morena CC BY-SA, Blender5.2.4, crop512×512 de cámara virtual1920, interior (76,76,360,360), seeds de entrada 539/911/1337 a24spp, refs8819/8922 a512spp. Recuperar artefacto de siete días, verificar hash SHA256 de todos los Raw/OIDN/refs/AOV conforme a E0054_RESULTS.json, metadata exacta y certificado de Raw/AOV ya medido. No volver a renderizar.

**Diseño cross-reference:** (1) seleccionar solo por gradiente asinh de luminancia scene-linear de *ref1*: 20% de diferencias adyacentes H/V no nulas más fuertes (cuantil 0.80); (2) medir RMSE de gradientes Raw y OIDN contra ref2, que NO interviene en selección; (3) repetir al revés ref2→ref1. En ambos sentidos 3 seeds, regiones congeladas central360² y crop completo. RGB HDR RMSE respecto a ref de evaluación por separado. Las variantes comparten Raw por seed, medido en E0054. Rechazar nonfinite/desalineado/ausencia de EXR.

**Pantalla de regresión, no inferencia final:** se activa solo si OIDN tiene RMSE gradiente *mayor* al Raw en ambas direcciones, las tres semillas y las dos regiones. Una pantalla negativa rechaza la tesis de regresión global *contra Raw en este criterio*, no la posibilidad de suavizado físico localizado en otra escena. La pantalla positiva requiere confirmación en bordes semánticos, convergencia de referencias y escena de otro autor. Las refs son finitas y pueden compartir sesgo; elegir por una implica sesgo de selección incluso si se valida sobre la otra.

**Stop:** no hacer nuevos filtros, no aumentar samples, no relajar criterios a posteriori. Archivar datos y decisión; decidir la siguiente inversión de cómputo con E0058 (cámara nueva con diversidad medible) y licencias en cuenta. La escena Surat tiene derechos arquitectónicos no aclarados, solo verificaciones internas. PR #10 permanece draft, addon producción intacto.
