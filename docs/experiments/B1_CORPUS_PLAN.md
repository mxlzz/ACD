# B1 — Corpus: inventario y aceptación de una escena arquitectónica realista

**Preinscrito 2026-11-13; primer candidato: Barcelona Pavilion.**

- Fuente oficial: [Blender Demo Files](https://www.blender.org/download/demo-files/), sección Cycles, Barcelona Pavillion, **eMirage**, **CC-BY (versión no especificada en el catálogo)**. Descarga histórica publicada en Blender: https://download.blender.org/demo/test/pabellon_barcelona_v1.scene_.zip . Se conservará licencia y atribución por separado; NO redistribuir el .blend hasta verificar sus contenidos y condiciones.
- Razonamiento: escena arquitectónica realista de autor distinto a Cozy Kitchen / Modern Hall / Island y Terraced Houses; candidata a observar juntas/reflejos, materiales y vidrio. El tamaño indicado en el catálogo es aprox. 24 MB, pero debe verificarse **contenido ZIP, recursos y cámara** antes de caracterizarla.
- Clasificación **desarrollo/calibración**, no holdout. Al inspeccionarla deja de ser una escena ciega. Reservar futuras escenas de otro autor/estilo para test fuera de muestra.
- [Workflow](../../.github/workflows/acd-b1-barcelona-smoke.yml): descargar ZIP sin publicarlo, registrar SHA256 y número/tamaño de entradas, controlar zip-slip, extraer en /tmp, localizar un .blend exacto, rechazar dependencias faltantes, abrir con Blender 5.2.4 --disable-autoexec, render Cycles CPU 192×192 **4 spp** sin denoising y conservar solo metadatos y PNG de smoke. No usar este smoke como medición de denoising ni compararlo con OIDN. Archivo fuente permanece fuera de Git y de los artifacts.
- **Aceptación:** SHA ZIP, estructura documentada, dependencias resolubles, cámara/materiales, Cycles smoke exitoso. Si no, registrar rechazo y pasar a otro candidato sin inventar texturas ni alterar escena.
- Si pasa, fijar SHA en un segundo commit y diseñar B2 piloto 512–960px con escalera de 128/256/512 spp antes de plantear 1920px y referencias múltiples. El coste de 1920 y muchas muestras solo se aprueba tras una estimación obtenida de render de prueba. Comparar coste temporal frente a aumentar spp.
- Otras fuentes públicas **no inspeccionadas aún**: Blender Cycles Italian Flat (Flavio Della Tommasa, CC-BY, 368 MB), Flat Archviz (Marek Moravec, 368 MB) y Classroom (Christophe Seux, CC0), esta última condicionada por anomalía de seeds de E0007. La disponibilidad de un enlace no significa aprobación de licencia/recursos o aptitud para nuestro test.

**Estado al crear:** no hay descarga del ZIP validada, cámara/render ni benchmark B1.


## B1 Barcelona — fallo de textura y control de relink (2026-11-13)

- [Run 43493237120](https://github.com/mxlzz/ACD/actions/runs/43493237120): ZIP 24,661,092 bytes, 24 entradas, SHA256 0a85bf512329f1780563069512b934d679a6c543eeb1a4ec4f60cddeab706697; BLEND 8,485,449 bytes SHA256 92162db8cabcd03641c53df95554b604b494ba74a76a099c7e06637e9379120a. Blender 5.2.4 lo abrió pero auditor rechazó antes de render por Mies-BCN_M11.jpg no resuelto; **no existe validación de render**.
- Corrección de aceptación: registrar todos los paths ZIP y aplicar solo si hay **una única coincidencia por basename en la misma extracción verificada**, relink de textura temporal en memoria; el original .blend permanece intacto. Si no hay coincidencia exacta, sigue fallando el smoke y se descartará. Sin datos de calidad ni modificación del addon.


## 2026-11-13 — B1 Barcelona descartada, Italian Flat preinscrito

- Barcelona [run 43493720883](https://github.com/mxlzz/ACD/actions/runs/43493720883) (reintento): confirmados ZIP y .blend íntegros, pero la imagen llamada Mies-BCN_M11.jpg tiene ruta original water bump.jpg, **no presente** en los 24 paths ZIP. Reasignar el archivo de foto Mies a ese mapa de bump sería inventar un recurso; rechazo como fixture reproducible. No se renderizó.
- Nuevo candidato: Italian Flat, Flavio Della Tommasa, CC-BY (versión no indicada), Blender demo Cycles fuente oficial https://download.blender.org/demo/cycles/flat-archiviz.blend (367,972,724 bytes publicados). Mayor tamaño que anteriores; solo smoke 192² 4spp, no referencia ni benchmark, y nunca subir original .blend. Workflow lanza check de dependencias, cámara, hash y Cycles CPU. Resultado **pendiente**.
