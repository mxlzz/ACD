# E0047 — ¿La pérdida de detalle resoluble se concentra tras el vidrio?

Preinscripción: 2026-11-16, antes del postprocesado. **No hay renders ni filtros nuevos.**

## Antecedentes y criterio de foco

- E0044 en 320px usaba lamas con período <2px (E0045: sub-Nyquist); E0046 sobre el mismo modelo llevó el período a ~8–10px, crop de 512px sobre sensor de 1920x1440 y centro320px. [E0046](E0046.md) guardó Raw, OIDN, dos referencias512spp y EXR con guías.
- En la [galería E0046](../../benchmarks/results/detail_crop_e0046/e0046_cropped_slats_1to1.png) se observan lamas directas identificables, mientras que el patrón detrás del vidrio delantero aparece más suavizado. **Observación visual tentativa**, no prueba de causalidad ni de detalle verdadero.
- [OIDN documentation](https://www.openimagedenoise.org/documentation.html) y el código Cycles 5.2.4 ya conocen guías Albedo/Normal que pueden seguir reflejos y albedo ponderado por rugosidad. No se atribuye novedad al seguimiento de rayos ni se reimplementa.
- Problema específico: ¿se atenúan gradientes periódicos en la zona superpuesta al vidrio respecto del patrón directamente visible, aun cuando dos referencias finitas retienen parte de esos gradientes?

## Método y controles

- **Reutilizar exclusivamente** el artifact E0046 de [run 43883209135](https://github.com/mxlzz/ACD/actions/runs/43883209135); SHA256 de todos los EXRs igual a `docs/experiments/E0046_RESULTS.json`. No volver a ejecutar Cycles.
- Dos regiones **predefinidas de 80×160 px en coordenadas del interior320** (sumar96 a cada eje para encontrar las coordenadas de los EXR512): `glass_overlap`=[8,96,80,160] y `uncovered_slats`=[232,96,80,160]. La primera está dentro de la proyección del panel `Glass overlay in front of slats` y la segunda fuera, conforme E0045 y caja (centro -0.4,1.96,1.52; tamaño 1.63x.027x1.29). **No son materiales/iluminación equivalentes ni un experimento de intervención en vidrio:** solo screening espacial de pérdida de gradiente. No ocultar la máscara ni ajustar rectángulos después de ver la métrica.
- Por región: RMSE HDR Raw/OIDN contra cada ref, `detail_fidelity` y ratio de contraste y error de gradiente, diferencia ref-ref; **correlación del gradiente horizontal de la luminancia asinh entre referencias** (para verificar que las franjas son más estables que el ruido) y entre OIDN y la media de refs. Producir comparativas de las regiones y visualización separada de Albedo/Normal originales (sin considerarlas ground truth).
- Éxito diagnóstico preliminar: gradientes de refs coherentes (correlación positiva robusta), contraste de OIDN sistemáticamente menor en región tras vidrio comparado con región sin vidrio y consistente en ambas refs, sin discrepancia de referencia suficiente para invalidar la comparación. Éxito **no implica** algoritmo nuevo o causalidad. Si la hipótesis no se sostiene, **descartar sin tuning**.
- Cualquier experimento posterior (E0048) requerirá preinscribir un cambio causal en un parámetro de Cycles *ya existente* (p. ej. follow-reflections) conservando ruido beauty emparejado, y confirmar que efectivamente cambia solo la guía y no otros pases; nada de mezclas arbitrarias.

## Límites

Las dos referencias tienen 512spp y error entre sí 0.07922 en el centro completo de E0046, **no son convergidas**. OIDN vio solo 512px más margen96 y pueden existir efectos de borde. Los dos ROIs difieren en oclusión, fondo, iluminación y materiales. La métrica de gradientes no es perceptual. Salida de E0047 = hipótesis de fallo local o descarte, no promoción de ACD.

Archivar JSON+PNG en Git permanentemente. EXR temporal en Actions.