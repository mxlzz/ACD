# B1 / E0061 — Control estratégico: no confundir disponibilidad con aptitud (2026-11-16)

## Pregunta central y decisión
ACD quiere **mejorar de forma verificable la fidelidad de detalle arquitectónico de OIDN en Blender**, conservando ruido residual/HDR y coste competitivo. La disponibilidad de escenas y la cantidad de experimentos no son indicadores de progreso. E0059 ha rechazado una regresión de error de gradiente OIDN frente a Raw en los tests predefinidos sobre Cozy (no descarta pérdida física local). E0060 confirma solo factibilidad de Surat: 256x144, 8 spp, referencias 64 spp, RMSE inter-referencia 0.110399 y tiempo total 35s. Nada justifica todavía un algoritmo nuevo ni referencias masivas.

## Auditoría de fuentes con evidencia
- **Cozy Kitchen, Nicole Morena CC BY-SA:** escena de desarrollo ya investigada y no holdout. E0054 detalle a densidad de 1920px mostró referencia/referencia RMSE 0.077947 frente a OIDN/ref ~0.092270 (alta incertidumbre relativa); E0059 no encontró regresión Raw-relativa de gradiente según su test. No repetir High/Super ni alterar contraste sin nueva causa comprobada.
- **Surat Diamond Bourse (modelador CC0, diseño real con derechos pendientes):** E0057/58/60 validan funcionalidad, recursos y ruido con semillas distintas en CAM Office. Solo uso técnico interno; NO publicar derivados ni tratarlo como holdout aceptado. E0060 a 256px es prueba de capacidad, no de detalle representable.
- **Classroom, Christophe Seux CC0:** E0056 repitió la anomalía de seeds (solo 4/5184 pixeles cambiaron a >1e-6); excluido de tests multisemilla en el ajuste actual.
- **living-room-3 convertida:** auditoría B1 rechazada por tres texturas faltantes y derechos de conversión sin verificar.
- **House of Chores (Blender Studio CC BY):** catálogo oficial público, pero el proyecto se creó para probar Grease Pencil 3 y se renderiza en EEVEE; no es una escena física de Cycles para verificar denoise de path tracing. No invertir en descargar 238 MB para nuestra pregunta.
- **Room Replica (Weiping Yan):** Blender/Cycles interior con source en GitHub y software MIT; el README advierte expresamente que algunas texturas extraídas de fotos no están cubiertas por MIT/CC0 y que puede haber marcas de terceros. No es material íntegramente libre y verificable para corpus redistribuible.
- **Blender3DArchitect (Filipe Lima Botelho):** declara ocho escenas archviz completas CC0 optimizadas para Cycles (9–62MB ZIP); su entrega pública requiere registro a newsletter. Candidata sustantivamente apropiada si se obtiene enlace autorizado y se verifica licencia de los archivos originales, checksum y dependencias. No inventar URL ni pedir acceso en nombre del usuario.

Referencias: https://www.blender.org/download/demo-files/ ; https://www.blender3darchitect.com/free-scenes/ ; https://github.com/appleweiping/room-replica . Evidencia experimental y límites detallados en docs/experiments/E0054.md, E0059.md, E0060.md y B1_LIVING_ROOM3_AUDIT.md.

## Puerta para el próximo experimento
1. **Corpus:** buscar prioritariamente una nueva escena archviz completa en Cycles, de otro autor, licencia explícita para los assets, reproducible sin texturas/IES ausentes y sin barreras de descarga. No llamar holdout a una escena usada para selección/calibración.
2. **Costo y precisión antes de hipótesis:** verificar frame/cámara, seed real, referencia-referencia, y detalles físicamente resolubles a una densidad de entrega; el test sobre 256px no es evidencia para juntar píxeles o conservar texturas finas.
3. **Innovación falsable:** estudiar un tipo de error *residual atribuible a OIDN* frente a un control mejor que Raw ruidoso, por ejemplo alta-spp con incertidumbre cuantificada; probar que guías/variantes nativas y métodos previos no lo resolvieron. Antes de crear candidato, registrar función de pérdida, control constante, presupuesto y división por escenas.
4. **Decisión:** no programar automáticamente nuevos tests 8/64spp de otras escenas, nuevos filtros de nitidez, ports StatMC/ProDen ni merges hasta que la próxima ejecución responda una pregunta que E0054–E0060 no respondieron. Un stop documentado evita gasto inútil.

**Estado:** checkpoint de investigación, sin renders ni tests de calidad nuevos. PR #10 sigue draft; producto estable y resultados anteriores sin alteraciones. 