## 2026-11-13 — B0b E0036 real smoke initiated (pending results)

- Workflow [.github/workflows/acd-e0036-cycles-internal.yml](.github/workflows/acd-e0036-cycles-internal.yml) agregado y disparado: Blender oficial 5.2.4 LTS verificado, Cycles 16 spp, una sola ejecución, RLayers Noisy Image/Imagen denoised interna/CompositorOIDN, mismo albedo y normal. Métricas RMSE entre outputs, sin ground truth ni ranking. No requiere escena o intervención privada.
- Si falla, conservar mensaje real y reparar causa; no interpretar como diferencia de calidad. Resultados pendientes en Actions.

---

## 2026-11-13 — B0b/E0036: estudio con idéntico RenderLayer diseñado

- Implementados tests/blender_cycles_internal_e0036.py y scripts/analyze_cycles_internal_e0036.py. En una sola ejecución Cycles, se activa denoising integrado OIDN y se obtienen tres EXR del mismo nodo Render Layers: Raw/Noisy Image, CyclesInternal/Image y CompositorOIDN con Accurate/High/HDR + albedo/normal. Por tanto se eliminan diferencias entre seeds/renders al comparar ambas rutas. Fixtures procedurales 128×96, 16spp, sin ground truth; solo se informará **diferencia entre outputs**, no ranking de calidad.
- Tests sintéticos comprueban identidad, detección de diferencias y rechazo de dimensión. Workflow por crear/ejecutar tras este commit. No modificar ni forzar expectativas de igualdad: diferentes preprocesamientos pueden dar imágenes distintas.

---


## 2026-11-13 — E0035 archive corrected: nested artifact layout

- Run [43481397097](https://github.com/mxlzz/ACD/actions/runs/43481397097) retrieved both E0035 artifacts and validated report versions, then failed reading EXR because Actions upload preserved `acd-e0035-render/` subfolder rather than placing raw EXR at archive root. Not a rendering/algorithm error. Fix by locating exactly one file recursively per name and rejecting ambiguous artifacts. Re-run without Blender/denoiser.

---

## 2026-11-13 — E0035 real success; archival validation triggered

- [Run 43480823352](https://github.com/mxlzz/ACD/actions/runs/43480823352) dos jobs **success**. Blender oficiales 5.2.4 LTS (build cd5dc428cce1) y 5.3.0 (02f0899d78e3), verificación SHA256/tiny Cycles 128×96, 16 spp, misma beauty raw/AOV delta=0, Standard vs OIDN compositor delta=0 en cada versión. Ninguna de estas cifras indica calidad real.
- Se agregó pipeline E0035 archive que recupera EXR/reportes **ya generados** y mide diferencias pixel/guías entre versiones, publica JSON pequeño en docs/experiments. **Su ejecución pendiente**. El denoiser integrado de Cycles todavía no fue evaluado; pasar a B0b después de registrar deltas.

---

## 2026-11-13 — E0035 primer smoke abortado por biblioteca faltante en runner

- [Actions run 43480476666](https://github.com/mxlzz/ACD/actions/runs/43480476666): **ambos jobs fallaron** tras pasar tests, SHA256 oficial, Blender --version y enumeración API. En el paso de render se produjo abort 134 con mensaje **libEGL.so.1: cannot open shared object file**; Blender 5.3 además advirtió que el backend Vulkan no se inicializaba. Esto indica una dependencia runtime del runner, no prueba de defecto del denoiser ni de incompatibilidad del addon.
- Corrección limitada a CI: instalar libegl1/libgl1-mesa-dri/libopengl0/libxkbcommon0 y verificar ldconfig antes de render; repetir igual fixture/configuración. No modificar el método, reference spp o addon. Resultado del segundo intento pendiente.

---

## 2026-11-13 — E0035 control de versiones iniciado

- Workflow E0035 incorporado con matriz Blender 5.2.4 LTS y 5.3.0 de archivos oficiales + hash, API compositor/Cycles y render ligero con misma beauty y AOV dentro de cada job.
- Push de workflow dispara primera corrida; siguientes solo manual o cambio explícito a este workflow. Resultado **pendiente de GitHub Actions**, no benchmark de calidad ni comprobación Cycles-internal. Addon estable intacto.

---


## 2026-11-13 — B0a/E0035: contrato reproducible implementado (ejecución pendiente)

- Código nuevo: tests/blender_cycles_capabilities_e0035.py registra sockets/propiedades de denoise de la versión real, scripts/summarize_blender_compat_e0035.py comprueba fuente RAW igual al beauty AOV de la misma seed y compara Standard con OIDN compositor, tests/test_blender_compat_e0035.py rechaza mezclar informes de diferentes versiones. 
- Clasificación: **tests de contrato**, no calidad visual. Resolución 128×96, noisy16spp, referencia64spp (no convergida). Cycles-internal todavía sin ejecutar. Próximo workflow E0035 matrices 5.2.4 LTS/5.3.0 y checksums oficiales.

---

## 2026-11-13 — Reorientación B0–B4 aprobada para implementación

- Programa rector: [B0–B4](docs/ACD_V2_REORIENTATION_2026-11-13.md). Prioridad inmediata: B0a (compatibilidad Blender 5.2.4 LTS + 5.3.0 y auditoría de diferencias de rutas OIDN). Se conserva 5.0.1 como control histórico; las variantes High/Super/Emission50 no se siguen optimizando.
- Los resultados reales y la ejecución de E0035 **todavía no están verificados** en este commit de decisión; el próximo commit implementa workflow y contrato. Addon estable y PR #10 draft sin merge.

---

## 2026-11-13 — Índice permanente de imágenes del laboratorio
- E0034 [run 43451534590](https://github.com/mxlzz/ACD/actions/runs/43451534590) success; commit de archivo f20d2a854f61e0681ffd6a659f0565b15269c124; resultados E0033 exactos y PNG E0034 versionados. Nuevo índice benchmarks/results/README.md integra Modern Hall, Island, Cozy Kitchen E0020/E0021 y Terraced; enlaza licencias, full/crops y diferencia entre PNG permanentes y artifacts EXR temporales. README principal enlaza el índice. No hubo nuevo render ni cambio al addon.

---


## 2026-11-13 — E0034 publication staging correction
- E0034 run 43451223536 generated the postprocessed PNG and verified original E0033 EXRs, but the git-add phase was blocked again by the broad nested-ignore rule for docs/experiments. No new render or scientific results. Fix the root ignore mismatch with an explicit documentation exception and force-stage both numeric JSON and tracked report, while retaining broad exclusions for .blend/.exr assets. This is a packaging fix, not algorithm adjustment.

---


## E0033 run completed — numerical result, Git archiving issue (2026-11-13)

- Run: https://github.com/mxlzz/ACD/actions/runs/43416607737 . Blender 5.0.1 rendered all three 24-spp seeds, two 1024-spp references and the lab produced scores. The final git-add failed because the ignore rule experiments/ covers docs/experiments/, but 149 MB of EXRs/JSON were uploaded as artifact 14034252923, expiring 2026-11-27. This is a publication error, NOT a rendering/denoiser failure.
- First/second ref global HDR RMSE OIDN 0.02223804 / 0.02215599; frozen Emission50 0.02230239 / 0.02221500, worse in both. ACD High 0.02371872 / 0.02366157; ACD Super 0.03184713 / 0.03176431. First-ref edge RMSE OIDN 0.03445690 vs Emission50 0.03455458 (regression); top 1% reference brightness RMSE OIDN 0.01197959 vs Emission50 0.00643289 (localized improvement).
- Reference-to-reference RMSE 0.02153122 (similar scale to denoised error). No reference convergence proven, and no universal ranking should be inferred. Emission50 FAILED to improve global quality on an independent artist/scene and must not be promoted or tuned against this now-observed scene.
- E0034 is a postprocess-only recovery workflow: exact JSON + EXRs from the existing run, source-only ROI selection and nonoverlapping crops, fixed display transfer, archive PNG in Git. Its run is not yet verified at this commit. Addon stable unchanged.

---

## 2026-11-13 — E0032 compatibilidad superada; E0033 benchmark congelado

- [Run E0032 #43415697217](https://github.com/mxlzz/ACD/actions/runs/43415697217) **success**: Modern Hall cuteday source SHA256 b35b6694eb231d0d4d5d9ee9bbe63122218183fd519a05c7d5db0e62cbdaeca1, 5,793,896 B, 22 materiales, 32 mallas, 1 cámara, 3 imágenes empaquetadas / 4 imágenes, ningún archivo externo faltante, Cycles Blender5.0.1 192²×4spp completado; fuente externa efímera NO subida a ACD. Conversión y derechos de redistribución independientes aún sin resolver.
- E0033 diseñado con mismos coeficientes E0027 y control de mezcla constante, 512px, 24spp×3 y refs1024×2, números y pruebas de borde/HDR guardables permanentemente. **No reportar números antes de ejecución.** Workflow autoiniciado por incorporación y CI Python.
- E0031 continúa rechazado por texturas faltantes; ACD stable addon no modificado.

---

## 2026-11-13 — E0031 fuente rechazada, E0032 smoke independiente preparado

- E0031 [GH Actions 43414866242](https://github.com/mxlzz/ACD/actions/runs/43414866242): hash, tamaño y licencia MIT pasaron; abrió Blender5.0.1 pero falló el control funcional por `lapajne.jpg` y `lapajne.jpg.001` ausentes (y advertencia de archivo pre-2.50). **Sin render ni .blend versionado**, sin mediciones ACD. Rechazado sin sustituir recursos.
- E0032: nueva fuente arquitectónica de autor NewSee2l035, conversión Mitsuba→Blender de Modern Hall/Bitterli, GitHub `cuteday/scenes_blender` commit 4271a72, blob 6c60f72, 5,793,896 B. Origen CC BY 3.0, licencia de conversión a revisar antes de redistribuir. Workflow lee fuente externa sin incluirla en repo y exige hash, Blender5 cámara/materiales/texturas, render 192px 4spp; quality benchmark no iniciado. No cambia addon ni coeficientes Emission50.
- La comprobación Python/trazabilidad del commit precedente [run 43414877028](https://github.com/mxlzz/ACD/actions/runs/43414877028) pasó. CI verde no mide calidad de denoise.

---

## 2026-11-13 — E0030 revisión visual y E0031 nueva fuente independiente

- E0030: se inspeccionaron los 4 paneles archivados y sus métricas de dos referencias; la fusión Emission50 conserva una ganancia local HDR en luces intensas, pero no demuestra superioridad perceptual. **Limitación confirmada:** la ROI brightest solapa la detail_1 3354/6400 píxeles (52.4%), aunque las tres ROI de detalle son disjuntas entre sí. Se conserva E0030 sin reetiquetar cuatro vistas como cuatro regiones independientes. Ver informe E0030 revisado.
- E0031: se seleccionó Living Room ©2014 Jure Sorn MIT, autor distinto, archivo .blend original 7,328,212 B en gto76/living-room, commit a36bac4 y blob 51374a6. Añadido workflow para verificar integridad/licencia, faltantes y render Cycles Blender5 de 192px 4spp antes de copiar binario a repo; **smoke pendiente al commit**. Si falla compatibilidad/dependencias, no incorporar el fichero. No se ejecutó aún prueba de calidad ni se tocó addon.
- Puerta: 512px+ y 2 referencias sobre fuente nueva ya validada, con parámetros E0027 congelados y ROI disjuntas para un benchmark manual. No entrenar/forkear ni promover Emission50 mientras persistan regresiones de bordes y falta de diversidad profesional.

---

## E0030 visual diagnostics prepared (2026-11-12)

- Reference-selected multi-panel crops with fixed diagnostic transfer and MIT attribution prepared from E0029 Island original EXRs (no rerender), 4 ROIs including brightest and gradients; computes local RMSE both references for Raw/OIDN/Emission50/Emission100/High/Super. Workflow publishes derived PNG and JSON under benchmarks/results/island_e0030 only after successful postprocess. Results pending. Do not infer perceptual superiority without inspecting images.

---

## E0029: nueva escena confirma disminución HDR con regresión de borde leve (2026-11-12)

- GH run #43309302172 success y 21 tests; Low-Poly Island 320x272, 24 spp x3, refs512 spp x2, discrepancia refs RMSE 0.0112732 (~18% Raw). Parámetros Emission50 congelados desde E0027. OIDN nativo RMSE 0.065539 vs Emission50 0.053347 (**-18.6%**), pero edge error 0.039348 vs 0.039621 (+0.70%). Segunda ref confirma. No hubo tuning por esta escena ni se integró addon.
- Informe numérico permanente [E0029](docs/experiments/E0029.md), workflow caro ahora manual. Island comparte autor/estilo low-poly con Terraced, referencias no convergidas demostrablemente. Próximo: inspectar crops 1:1 en zonas emisivas y buscar escena/autor verdaderamente independiente antes de declarar éxito general.

---

## E0029 — New-scene frozen Emission AOV test staged (2026-11-12)

- E0028 GH Actions #43308643155 success; source Low-Poly Island SHA256 0fceb72489873a1ebbdf8210c435713e5fee1b3c58ffa4105187023f6896b701, MIT, 2.62MB, Blender5 smoke passed. Import workflow disabled after publication.
- E0029 workflow prepared to apply identical E0027 emission blend scale .25 with max Raw weights .5/1 to the newly introduced island scene, 24spp x3 and 512spp refs x2. No quality result at commit. All references only used for scoring; original addon untouched.

---

## E0028 — tercera escena pública MIT seleccionada, sin resultados de denoiser (2026-11-12)

- Encontrado `emrelab/blender-projects/low-poly-island/envanto-tutariol.blend` de Yunus Emre Karaman, MIT, 2,621,405 bytes, git blob `e540ffeae1f063393d644bd4af3a0a27f732fe5c`, source commit fijo `36c46d3b49ea872f6039e07a5e4769b5f9443654`. Escena distinta de Terraced y Cozy, cabin sobre isla con vidrio, lámparas y materiales; comparte autor de Terraced (no independiente de estilo).
- E0028 crea workflow de importación que comprueba hash/mit/license, abre Blender5 sin autoexec, ejecuta smoke CPU de 4 spp y **solo si pasa** publica binario y SHA en GitHub; **ejecución pendiente al commit**. Parámetros E0027 (.25, maxMix 50/100) congelados antes de usar escena; ningún entrenamiento ni modificación del addon.

---

## E0027 observado — guiado por Emission AOV mejora RMSE, requiere prueba nueva (2026-11-12)

- [Run #43307378645](https://github.com/mxlzz/ACD/actions/runs/43307378645) **success, 11 tests**, mismos EXR E0021/E0023, 3 seeds×2refs. [E0027](docs/experiments/E0027.md): AOV_EMISSION50 (mezcla Raw local máx .5) Cozy RMSE 0.083196 vs OIDN0.083393, edge0.089395 vs0.089698; Terraced RMSE0.122200 vs OIDN0.167785 y MAE0.01765 vs0.02107, pero edge sube 0.06795→0.07210. AOV_EMISSION100 mejora RMSE nocturno aún más (0.1130), pero empeora mucho edge (0.08098). Control mezcla global al peso medio no recupera esa mejora. Fuente emisiva: 0.0408% píxeles Cozy, 4.49% Terraced.
- **Decisión:** candidata AOV es plausible pero no puede promoverse por error de bordes y falta de validación ciega. Probar exactamente mismos coeficientes/escala en una tercera escena pública sin observar previamente sus resultados. E0027 workflow a manual tras completar. No hay nuevo addon ni modificación del núcleo OIDN.

---

## E0027 — ablation específica Cycles Emission AOV preparada (2026-11-12)

- E0026 descartó gating Raw por brillo como método general pese a buena mejora nocturna: degrada Cozy. E0027 prueba un indicador más específico disponible en el render **sin oracle:** `Emission` AOV de cada seed, peso suave de mezcla Raw/OIDN según energía de emisión, escala fija 0.25 y fracción máxima Raw .5/1.0; control mezcla uniforme del mismo peso medio y comparación con variante genérica E0026.
- Código `acd_lab/emission_guide.py`, tests e informe predeclarado [E0027](docs/experiments/E0027.md). Workflow recupera EXR de Cozy E0021/Terraced E0023 sin rerender, dos referencias y tres seeds; documenta cobertura del pase y score HDR/gradientes. **CI y resultados pendientes al commit**. No toca addon ni fork OIDN.

---

## E0026 ejecutado — descartar gating Raw como solución general (2026-11-12)

- [Run #43306559564](https://github.com/mxlzz/ACD/actions/runs/43306559564) **success, 16 tests**, reutiliza EXR E0021/E0023 sin render. [Informe E0026](docs/experiments/E0026.md) almacena dos refs x3 seeds: Cozy OIDN RMSE 0.08339 vs RAW_BRIGHT50 0.09781, RAW_BRIGHT100 0.13909; Terraced OIDN 0.16778 vs RAW_BRIGHT50 0.12253, RAW_BRIGHT100 0.10936. El algoritmo mejora claramente exterior nocturno pero degrada mucho interior: **no generaliza**. Errores de gradientes también se deterioran fuertemente en Cozy.
- Decisión: **NO integrar** la variante y **NO optimizar post hoc** sus percentiles / pesos contra mismas escenas. E0026 workflow a manual; paquete experimental permanece disponible para investigación y casos negativos. Siguiente hipótesis: AOV Emission de Cycles como guía de clase física, no brillo crudo genérico, siempre con controles y sin referencia en inferencia. No hay ventaja general probada.

---

## E0026 — primer candidato adaptativo *input-only* preparado, sin tocar Blender (2026-11-12)

- [E0025](docs/experiments/E0025.md) reportó que OIDN reduce ligeramente la media energética en highlights (-0.85% aprox), pero produce error absoluto espacial mucho mayor que Raw. Para explorar preservación de extremos sin oracle se creó `acd_lab/highlight_blend.py` y tests: selección únicamente por percentiles de luminancia **Raw**, smoothstep 97%–99.5%, fusión local máxima 50% o 100% con OIDN; controles fijos 10% y 50% Raw globales.
- Comparación E0026 planeada en **dos escenas ya observadas**, Cozy Kitchen E0021 y Terraced Houses E0023, usando sus EXR originales (sin rerender), 3 semillas ×2 referencias; métricas RMSE lineal, MAE, gradientes, errores dentro/fuera de highlights definidos solo por referencia para scoring. No se han ajustado parámetros contra referencias ni liberado addon. **CI/workflow pendientes al commit; ningún resultado todavía**.
- Los resultados no equivalen a test held-out, ni demuestran superioridad hasta disponer de tercera escena nueva. Si falla se descarta el método sin retocar selectivamente percentiles.

---

## E0025 verificado — OIDN sesgo mixto en highlights (2026-11-12)

- [Run 43305700278](https://github.com/mxlzz/ACD/actions/runs/43305700278) **success**, 10 tests. [E0025](docs/experiments/E0025.md): en top1% brillo de referencia, OIDN promedio ratio energía 0.99147 y delta lum -0.19294 (ref2 ratio 0.99088), pero 56% de píxeles sobre ref, abs error 0.799 vs Raw 0.338. High ratio 1.00395/abs0.728 y Super 1.00542/abs0.746. Error espacial mixto, no basta reajustar exposición global, no prueba causalidad de emisión. Prueba sin rerender a partir de E0023, tres seeds y dos referencias finitas.
- Siguiente: ablation **postproceso sin guías de referencia** usando solo luminosidad de Raw para mezcla localizada frente a mezcla constante, evaluar exactamente mismos parámetros en Cozy Kitchen y exterior nocturno. E0025 workflow pasa a manual tras éxito. Aún sin algoritmo validado ni mejora publicable.

---

## E0025 — sesgo HDR firmado, preparación sin nuevo render (2026-11-12)

- E0024 confirmó gran SSE en top1% luminosidad de referencia, pero no dirección. Se añadió `highlight_signed_bias` y pruebas para detectar atenuación o amplificación de energía en máscaras SOLO de referencia; contiene ratio de suma de luminancias, delta firmado, fracción sobre/bajo ref para mismos píxeles/métodos. Workflow nuevo consume artifacts E0023 y escribe JSON 3 semillas ×2 refs. **CI y ejecución pendientes**, no se ha concluido ninguna causa; aun sin datos para entrenar/cambiar algoritmo.
- E0024 pasó 7 tests, run #43305087148, reporte permanente [E0024](docs/experiments/E0024.md). E0021 y E0023 permanecen líneas de base de calidad.

---

## E0024 verificado — error HDR concentrado en luces, no causalidad (2026-11-12)

- [Run #43305087148](https://github.com/mxlzz/ACD/actions/runs/43305087148) **success**, 7 tests; mismo EXR E0023 3 seeds ×2 refs. [E0024](docs/experiments/E0024.md): en top1% píxeles de mayor luminancia (solo referencia), RMSE medio Raw=0.7151 vs OIDN nativo=1.4207, High=1.2794, Super=1.2843. Fuera del 1%, OIDN=0.08967 mejora Raw=0.09701 y High=0.09479. Top luminosidad concentra ~71.7% del SSE nativo vs 35.5% Raw. Segunda referencia ratifica patrón. No confirma si OIDN atenúa o aumenta iluminación, ni efecto exclusivamente emisión; 512 spp no son convergencia probada.
- E0020 320px se archivó como redundante frente a E0021 512px y dejó workflow **manual**, así como E0024 que ya completó. Siguiente diagnóstico E0025 de sesgo de luminancia firmado sin nuevos renders; F5 todavía sin base suficiente. No se tocó addon ni el motor del denoiser.

---

## E0024 — reejecución tras fix de prueba (2026-11-12)

- Se amplió el trigger **únicamente** del workflow E0024 a test/analizador específicos para ejecutar la versión corregida sin rehacer renders; se mantiene manual y no dispara por docs. Se conserva evidencia del fallo original y aserción ya corregida. Nuevo run pendiente.

---

## E0024 — corrección de aserción de test (2026-11-12)

- [Run #43304804793](https://github.com/mxlzz/ACD/actions/runs/43304804793) falló en **un único regex de test**, no en fórmula: `acd_lab.core.rgb` rechaza NaN antes del validador local con mensaje `raw: found NaN or infinite values`, mientras el test esperaba literalmente `Nonfinite`. Se ajustó la expresión del test al mensaje efectivo (sin reducir validación). 6/7 tests E0024 pasaron; script sobre EXR todavía no corrió. Nuevo run pendiente.

---

## E0024 — diagnóstico sobre EXR existentes, no repetir E0020 (2026-11-12)

- Al recuperar la historia completa de la rama, se constató que **E0020 fue seguido por E0021** (Cozy Kitchen 512×482, tres seeds, dos referencias 1024 spp; OIDN nativo supera High/Super en RMSE y gradientes) y **E0023** (Terraced Houses exterior nocturno, RMSE nativo mayor que Raw pero menor MAE y error de bordes). No tomar el piloto 320px añadido nuevamente como experimento nuevo; su workflow se pasa a **manual** y se conserva por reproducibilidad.
- Nuevo instrumento E0024 `acd_lab/hdr_tail.py` + tests sintéticos: máscaras comunes de píxeles HDR más luminosos según referencia y de errores raw más altos; SSE/RMSE/MAE dentro/fuera; selección *reference-only* y *raw-reference* explícita con advertencia de sesgo. Workflow consume artifacts reales E0023 (sin render) y compara tres seeds/dos refs. **Pendiente de ejecución al commit**.
- Aún no se ha desarrollado algoritmo nuevo ni habilitado F5. Se requiere diagnosticar si errores HDR localizados justifican estudiar preservación de emisión/varianza con método reproducible y sin sobreajuste a escena examinada.

---

## E0020 — benchmark real sobre Cozy Kitchen preparado (2026-11-12)

- `acd-v2-cozy-pilot.yml` crea piloto de Cycles Blender5.0.1 en la escena pública E0019 a 320px ancho, 24 spp x3 seeds, dos refs independientes 512 spp, mismos inputs nativos/ACD Standard/High/Super, EXR/AOV raw por seed; informe en [E0020](docs/experiments/E0020.md).
- **Al registrar este commit el workflow aún no ha corrido**. No hay evidencia de que nuestras métricas de detalle ganen o de convergencia de 512 spp. Se conserva la escena original, sin tocar addon estable; outputs temporales, números esenciales a registrar permanentemente.
- Prueba de integración real previa [E0019](docs/experiments/E0019.md) pasó con render smoke a 4 spp. Si este piloto falla, corregir bug real y conservar fallo; no iniciar F5 sin evidencia.

---

## E0023 postproceso cuantitativo preparado sin nuevos renders (2026-11-12)

- Nuevo script analyze_terraced_e0023.py reusa métricas de 3 semillas/2 referencias del laboratorio, añade distribución de error HDR en peor 1%, ROI de AOV emisión/glossy/transmission/environment y tres recortes seleccionados solo por referencias. Se compara nativo, Raw y High/Super. Licencia y crédito MIT del fixture preservados.
- Workflow acd-e0023-analyze-exr.yml recuperará EXR del run 43291659387 y publicará E0023.md, previews y JSON **solo después de superar tests y cálculos**. En este commit no se dispone de diagnóstico final del origen de RMSE. La escena nocturna ya observada no es test ciego para ajustes posteriores.

---

## E0023 — Instrumento de concentración de errores HDR añadido (2026-11-12)

- Resultados verificados E0023 [run 43291659387](https://github.com/mxlzz/ACD/actions/runs/43291659387): Raw RMSE 0.1201359 frente OIDN comp 0.1677849; pero Raw MAE 0.0281466 frente OIDN 0.0210728 y error de bordes Raw 0.1210943 vs OIDN 0.0679478. Ref spread/raw 17.01%; multiseed heurística aprobó, no independencia científica.
- Nuevo `acd_lab.error_concentration` cuantifica qué proporción del error cuadrático HDR aportan el peor 1 % de píxeles, más valor máximo/p99, con tests de outlier y error uniforme. **Implementado pero no corrido sobre E0023 al commit**. Permite investigar la discrepancia RMSE/MAE sin afirmar causa antes de medir.
- E0021 Cozy Kitchen a 512×482 con dos refs de 1024 spp está archivado con ROI/crops en [E0021](docs/experiments/E0021.md). No mejora ACD High/Super.
- Precaución: E0023 ya se observó y por ello pierde pureza como test completamente ciego para futuros candidatos; requiere otra escena no observada en F5.

---

## E0021 — Post-análisis de mayor resolución preparado (2026-11-12)

- [Run real #43289852695](https://github.com/mxlzz/ACD/actions/runs/43289852695) **success**: Blender5.0.1 Cozy Kitchen 512×482, 24spp ×3, 1024spp refs ×2, mismo RenderLayer/AOV. Nativo/Standard RMSE media 0.0833928, High 0.0860779, Super 0.0971167; error bordes 0.0896975/0.0902929/0.0962214. Las referencias entre sí difieren 0.0355077 RMSE o 13.5268% del error raw, menor que E0020 24.51%; rankings entre refs coherentes.
- Workflow `acd-e0021-cozy-analyze.yml` recuperará estos EXR exactos y computará medias contra ambas refs para 3 semillas + ROI nativo corregido y tres recortes. Publicará E0021 y derived CC BY-SA en GitHub. **Al registrar este commit el análisis y su publicación aún no están verificados.**
- E0023 sobre segunda escena retenida sigue separado. Protocolo: seguir sin tocar algoritmo hasta cotejar resultados con referencias y escena retenida.

---

## Ahorro de CI real — Runtime Blender manual (2026-11-12)

- Se constató que `.github/workflows/acd-blender-runtime-bundle.yml` se reejecutaba en cada cambio del PR #10 aunque el código de Blender no cambiaba, generando ~374 MB de artifact de duración 1 día por commit. **Se reemplazó el trigger pull_request por workflow_dispatch manual**, preservando el workflow para descargar Blender cuando haga falta. El quality gate Python permanece automático.
- E0021 Cozy Kitchen mayor resolución/ref 1024 spp y E0023 exterior retenido continúan ejecutándose en GitHub Actions; este commit no interrumpe ni duplica ambos tests, pues usan workflows distintos.
- Cambio en configuración CI, no denoiser. Quality del commit pendiente.

---

## E0022 verificado y E0023 prueba retenida preparada (2026-11-12)

- [E0022 run #43291261400](https://github.com/mxlzz/ACD/actions/runs/43291261400) **success**, `terraced_houses.blend` 3,044,256 bytes, SHA256 `37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84`, MIT de Yunus Emre Karaman, fijado commit fuente. Abrió y renderizó Blender5.0.1 Cycles CPU 192²×4 spp sin activos faltantes. [E0022](docs/experiments/E0022.md).
- Se creó workflow E0023 de **test retenido**, 320 de ancho con relación de aspecto original, 24spp×3 seeds, refs 512spp×2; métodos OIDN comp, ACD Standard/High/Super. Compara sin modificar el algoritmo. Añadida prueba de SHA/licencia y reporte genérico reutilizado para distinta escena.
- **Estado al commit:** prueba de calidad E0023 aún pendiente, mientras E0021 Cozy Kitchen refs mejoradas sigue en ejecución. No incluir resultados de held-out en desarrollo ni tomar decisiones hasta verificar su calidad de referencias.

---

## E0022 — Segunda fuente pública MIT seleccionada como test retenido (2026-11-12)

- Fuente candidata: [Terraced Houses](https://github.com/emrelab/blender-projects/tree/36c46d3b49ea872f6039e07a5e4769b5f9443654/terraced-houses) de Yunus Emre Karaman, licencia MIT explicita para .blend, 3,044,256 bytes, commit fuente fijado, git blob SHA1 conocido. Exterior nocturno con emisión en ventanas y farolas, diferencia sustantiva respecto de Cozy Kitchen. Autor declara tutoriales no registrados, se conserva caveat.
- Workflow `acd-import-terraced-houses.yml` verifica fuente/integridad/Blender5 Cycles 192px 4 spp antes de publicar; `scripts/audit_public_scene.py` parametrizado por variables de entorno sin alterar auditoría anterior. **Estado en commit:** importación y render todavía sin verificar.
- Objetivo: fixture retenido para evaluación de generalización, no optimización. No equivale a una escena profesional de texturas finas. E0021 continúa en ejecución por separado.

---

## E0021 — Postprocesamiento de dos referencias preparado sin nuevos renders (2026-11-12)

- Se añadió `scripts/analyze_cozy_exr.py` para E0020/E0021: 3 ROI elegidas por gradiente de ambas refs solamente; JPG/PNG comparativos con curva común; informe de métricas **promediadas sobre las tres seeds respecto de ambas referencias** (no solo seed539), incluyendo OIDN nativo en máscaras AOV; captura resolución original y de ensayo. No interfiere con la corrida E0021 que ya está ejecutándose.
- Este commit deja el script y tests; ejecución E0021 aún pendiente. No se ejecutará un segundo Cycles render para generar crops. `scripts/analyze_cozy_e0020.py` permanece como historial de E0020.

---

## E0021 — Control de mayor resolución y convergencia de referencias (2026-11-12)

- E0020 se verificó y sus [ROI/3 crops + informe](docs/experiments/E0020.md) se versionaron efectivamente en commit `4825a4afc57991e7c4be42a044925d38f67fc5e1`, [run de postproceso #43289259037](https://github.com/mxlzz/ACD/actions/runs/43289259037) success; no rerender. F3 `NATIVE_COMP_OIDN` presente en ROI.
- Nuevo ensayo E0021: Blender5.0.1 Cozy Kitchen a **ancho máximo 512, alto derivado de aspecto original**, 24spp ×3 seeds y referencias 1024spp ×2; ACD Standard/High/Super frente a nativo. Introduce `--max-width` sin mutar el original, guarda `source_original_resolution` y pixel aspect en metadata. Un solo job manual/push-path, no rerenders innecesarios.
- **Estado al commit:** código y tests, nuevo workflow y resultados aún no verificados. Prioridad: comprobar nueva discrepancia entre refs, comparación global y detalles y revisar si los beneficios perceptuales ameritan hipótesis F5. No inferir convergencia por spp altos solamente.

---

## E0020 post-proceso completó cálculos, publicación bloqueada por gitignore (2026-11-12)

- [Run #43288965340](https://github.com/mxlzz/ACD/actions/runs/43288965340) generó recortes y reporte regional desde los EXR originales **sin rerender**: tres ROI 80×80 seleccionadas solo de referencias; `NATIVE_COMP_OIDN` recuperado en reporte de regiones. Comparación de cinco métodos contra cada referencia arroja mismo orden sustantivo en la seed primaria (Standard/OIDN idénticos, después High, Super, Raw).
- El paso de publicación falló por `.gitignore` que omite `docs/experiments` para archivos nuevos (como había ocurrido con .blend). Los análisis existen en [artifact #13975528472](https://github.com/mxlzz/ACD/actions/runs/43288965340/artifacts/13975528472); se corrige `git add -f` **solo para E0020.md y tres PNG/JSON concretos**, preservando reglas generales. Nuevo run pendiente; no declarar permanencia de reportes aún.

---

## E0020 post-análisis sin rerender — preparación (2026-11-12)

- [Benchmark #43287450449](https://github.com/mxlzz/ACD/actions/runs/43287450449) **success**: Cozy Kitchen 320×240, 24 spp ×3 semillas y referencias 512 spp ×2. Heurística diversidad seeds pasó; refs discrepan RMSE 0.0610477, 24.51 % del error raw, **casi** el umbral exploratorio 25 %; ranking con ref2 no fue exactamente igual. Global RMSE media Native/Standard 0.1058435, High 0.1072723, Super 0.1286238. Borde: Native/Standard 0.1252201, High 0.1272333, Super 0.1324044. Son solo medidas contra refs finitas.
- F3 defecto corregido aparte: ROI antes omitía NATIVE_COMP_OIDN. Workflow nuevo descargará EXR originales de este run, reanalizará (sin rerender) con nativo en regiones, seleccionará crops en base a ambas referencias y archivará informe permanente E0020+3 imágenes+coordenadas/JSON en GitHub **solo si passes**. Última validación del workflow todavía pendiente.
- No iniciar F5; primero identificar naturaleza de discrepancia entre referencias y evaluar visualmente crops; posteriormente considerar 1024–2048 spp referencias/escena de prueba a mayor resolución.

---

## F3 — Corrección del comparador de regiones nativo (2026-11-12)

- Hallazgo durante E0020: `acd_lab.region_cli.compare_regions_from_files` filtraba método `NATIVE_COMP_OIDN` del diagnóstico espacial aunque se incluía en batch global. Se incorporó baseline nativo y SID4 cuando estén presentes, además de test sobre lectura real EXR.
- El [run E0020](https://github.com/mxlzz/ACD/actions/runs/43287450449) arrancó en commit anterior (3cda34e); sus métricas regionales **no** incluirán OIDN nativo hasta reprocesarlas. Global batch sí lo mide. **No se desencadena un segundo render costoso por este cambio.**
- El fix y nuevos tests quedan pendientes de CI. Reanalizar los EXR E0020 de forma independiente solo si los artifacts pueden recuperarse sin alterar inputs.

---

## E0020 — Benchmark Cozy Kitchen con referencias y semillas preparado (2026-11-12)

- Se agregó `acd-e0020-cozy-pilot.yml` como job único: fixture público SHA fijo, Blender5.0.1 CPU, 320×240, **24 spp ×3 semillas (539, 911, 1337)**, **512 spp ×2 refs** (8819 y 8922), Standard/High/Super/comp-OIDN (además Raw), EXR con AOV y diagnóstico por región. Workflow automático solo cuando cambie su propio fichero; posterior desactivar disparo por push para no gastar minutos repetidos.
- Añadido `scripts/summarize_e0020.py` para emitir métricas compactas legibles (RMSE, MAE, gradientes, ratio contraste), control de diversidad y discrepancia de refs; no afirma mejora por métrica única. Validación de `tests/test_e0020_summary.py` pendiente CI.
- Runner de escena externa invoca Blender con `--disable-autoexec` (archivo de terceros), sin modificar el original. Tests del comando actualizados.
- **La ejecución real en este commit todavía no está confirmada.** Si falla, registrar causa. Tras piloto juzgar validez de refs; ampliar resolución/spp solo con hipótesis y cuota disponibles. No fusionar addon estable.

---

## E0019 completado — Cozy Kitchen pública e íntegra en GitHub (2026-11-12)

- **Hecho verificado:** [workflow #43285518302](https://github.com/mxlzz/ACD/actions/runs/43285518302) success y commit automático `b63204749a95109eb5e913d6f4a1c4607cb7ddac`; [archivo .blend](benchmarks/scenes/cozy_kitchen.blend) **realmente versionado** con 7,685,702 bytes, SHA256 `5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395`, fuente oficial Blender 3.5 splash *Cozy Kitchen*, Nicole Morena, CC BY-SA. [E0019](docs/experiments/E0019.md) y manifest auditado.
- **Validación Blender real:** 5.0.1 CPU, cámara `CAM-wide`, 2 cámaras, 1077 objetos, 175 materiales, 0 imágenes externas faltantes y 0 bibliotecas .blend enlazadas; Cycles 192x192 ×4 spp sin denoising renderizado exitosamente. Esto no demuestra fidelidad OIDN ni vence referencias.
- **Seguridad/permisos:** el workflow de importación ahora es una comprobación manual de solo lectura, sin permisos write; SHA del fixture pasa a test Python automático. La escena privada del usuario no se distribuyó.
- **Siguiente paso:** corrida controlada a 512², 3 seeds ×2 refs, ACD Standard/High/Super vs OIDN compositor, graduar resolución y crops; mantener referencia convergente. No entrenar o fork antes de defecto reproducible.

---

## E0019 — Cozy Kitchen validada, bloqueo de gitignore en publicación (2026-11-12)

- [Workflow 43285264648](https://github.com/mxlzz/ACD/actions/runs/43285264648) ejecutó Blender5.0.1 **con éxito**: escena `Main`, cámara activa `CAM-wide`, 2 cámaras, 1077 objetos, 1058 meshes, 175 materiales, 6 imágenes (4 packed), 0 texturas faltantes, 0 librerías externas, render de prueba Cycles CPU 192×192 ×4 spp OK. Fuente oficial 7,685,702 B. El original permaneció sin cambios.
- Publicación posterior falló porque `.gitignore` omite `*.blend`; se corrigió la etapa de `git add` con **`-f` únicamente en `benchmarks/scenes/cozy_kitchen.blend`**. No eliminar el ignore global ni permitir otros .blend por accidente. Reintento pendiente. Este commit todavía no contiene el binario.

---

## E0019 — Validación de fuente: corrección de premisa de cabecera (2026-11-12)

- Primer intento [workflow 43285007004](https://github.com/mxlzz/ACD/actions/runs/43285007004) **failure en paso de descarga**, probablemente por comprobación inadecuada de magic uncomprimido `BLENDER` en .blend (puede estar comprimido); descarga HTTP 200 de ~7.3 MiB. No se abrió Blender ni se publicó archivo. Se corrigió el protocolo: conservar validación de tamaño y documentar bytes iniciales, después dejar a Blender verificar el archivo realmente. Nuevo run pendiente; no inferir defecto de la escena.

---

## E0019 — Fuente pública compacta seleccionada (2026-11-12)

- Se seleccionó **Cozy Kitchen**, Blender 3.5 splash by Nicole Morena, **7,685,702 bytes**, licencia declarada **CC BY-SA**, fuente Blender Foundation, archiviz/interior con objetos y materiales. Documentado en [E0019](docs/experiments/E0019.md) y [benchmarks/scenes/README.md](benchmarks/scenes/README.md).
- Se agregó workflow controlado de importación: descarga oficial, verificación de tamaño/cabecera, apertura Blender 5.0.1 sin autoexec, revisión cámara/texturas/libraries y render funcional CPU 192x192 4 spp. **Este commit solo crea el workflow; ejecución y publicación de binario quedan pendientes de comprobar**. Si pasa, el workflow crea un commit binario con SHA256 y también actualiza los tres archivos de trazabilidad por protocolo. `Prueba ACD.blend` del usuario sigue privado.
- Siguiente: comprobar ejecución, SHA, CI y que archivo .blend está efectivamente en GitHub; correr luego benchmark real de detalle solo con referencia validada, no inferir calidad del smoke.

---

## E0018 — Escena real recibida (2026-11-12)

- Archivo Prueba ACD.blend recibido y auditado estáticamente. Cycles 1920×1080, 137 objetos, 86 materiales, cinco cámaras (activa Camera.003), 121/122 imágenes empaquetadas. SHA256 e inventario en [E0018](docs/experiments/E0018.md).
- Usuario autoriza pruebas. **No se publica el archivo original:** contiene paths de red de trabajo y referencias a assets BlenderKit sujetos a licencias individuales; además excede el límite habitual GitHub de 100 MB. Compartir solo código y resultados sin rutas sensibles.
- La lectura de DNA y bloques completó; **Blender no se abrió ni renderizó** en esta etapa. Se prepara runtime Blender5.0.1 portable para ejecutar en entorno local sin descarga directa; el workflow todavía no está verificado.
- Próximo: inspección bpy sin autoexec, smoke Cycles, regiones y multi-seed con dos referencias, sin alterar original.

---
## E0017 validado — cierre del ciclo automático actual (2026-11-12)

- [ISA fixed-input run #43237525190](https://github.com/mxlzz/ACD/actions/runs/43237525190) **success dos jobs**, [E0017](docs/experiments/E0017.md): mismo PFM por SHA en AMD EPYC 7763 AVX2 vs EPYC9V45 AVX-512; los dos OIDN CLI v2.3.3/v2.5.1 son idénticos *dentro* de cada CPU, pero entre CPUs su output difiere RGB RMSE 7.41e-7 (max abs 3.48e-5). La causa de discrepancias mayores E0015 no está aislada. No atribuir diferencias a AMX sin medición.
- F1 gobernanza/documentación completa en PR #10 draft e Issue #9. F2 runtime CLI/versión verificadas, quedando control estricto prefilter/compositor e ISA. F3 tests de detalle y escena sintética verificados E0016, pero no hay escena profesional 1080p con referencia adecuada. F4 revisión repos ProDen/StatMC/StatER hecha, sin port. F5/F6 sin habilitación científica.
- **Decisión de eficiencia de CI:** el workflow pesado histórico M3.9, piloto independiente OIDN y diagnostico ISA pasan a `workflow_dispatch` manual; solo quality gate permanece automático en cada PR. Razón: cualquier push a PR #10 reejecutaba todos los workflows a pesar de no modificar su código, consumiendo minutos y repitiendo datos ya verificados. Se mantienen disponibles y reproducibles, sin borrar scripts ni artifacts existentes.
- **Pendiente que requiere escena externa:** una escena .blend arquitectónica autorizada y con recursos empaquetados (o dataset público realmente representativo), idealmente detalles finos, vidrio, reflejos, vegetación, iluminación artificial. No incorporar escena propietaria al repo público. Hasta entonces, no diseñar un 'denoiser mejor' basándose solo en fixture sintético.
- En este commit calidad CI **aún pendiente**; confirmar antes de dar estado final.

---

## E0016 verificado / CPU ISA bajo investigación (2026-11-12)

- [Run #43235485653](https://github.com/mxlzz/ACD/actions/runs/43235485653) **3 jobs success** incluyendo `detail_target` 320×240; [quality #43235484414](https://github.com/mxlzz/ACD/actions/runs/43235484414) **90 tests**. [E0016](docs/experiments/E0016.md) almacena comparación y caveats. En detail_target OIDN nativo RGB RMSE medio 0.0608849 y error gradiente 0.0721193, frente ACD High 0.0613499/0.0721533 y Super 0.0632406/0.0726432. Super eleva contraste y mejora MAE pero empeora fidelidad de gradiente y RMSE: aparente nitidez no equivale a detalle verdadero.
- Comparación de artifacts E0015/E0016 revela variación de imagen entrada entre workflows aun con mismos seeds y binarios (RGB PFM RMSE 4.96e-5 seed539). La salida OIDN2.5 cambió más entre jobs que OIDN2.3; tiempos e [OIDN changelog AMX-FP16](https://github.com/RenderKit/oidn/blob/v2.5.1/CHANGELOG.md) sugieren **posible dependencia del ISA** (no probada). E0015 se actualiza para no afirmar ventaja v2.3.3 estable.
- Nuevo **ensayo específico de ISA**, SIN Blender, sobre entradas sintéticas idénticas en GH runners 22.04/24.04 con CPU/ISA verboso, hashes de binarios, inputs y outputs. CI/piloto pendientes en este commit; no atribuir diferencias a ISA hasta observar ambas ejecuciones.
- F5/F6 no autorizadas por resultados actuales. Próxima puerta de calidad real: escena arquitectónica autorizada 1080p+ con texturas finas/reflejos y referencias de calidad; alternativa pública bajo licencia verificada. Ningún cambio al addon estable.

---

## E0015 y F3/F4 — Aislamiento de versiones terminado, fixture de detalle preparado (2026-11-12)

- [Run #43234478588](https://github.com/mxlzz/ACD/actions/runs/43234478588) **success, 2 jobs**; [E0015](docs/experiments/E0015.md) archiva resultados por seed: OIDN CLI 2.3.3 y 2.5.1 obtienen salidas idénticas Glass Lobby (RMSE mutuo 0 en 3/3); en interior emisivo cambian ligeramente (RMSE mutuo ~0.00221) y 2.3.3 tiene RMSE global menor en las 3 semillas. Misma PFM/flags/CPU; no implica ranking general ni diferencia de calidad perceptual.
- [F4 fuentes y dependencias](docs/EXTERNAL_DENOISER_PRIOR_ART.md) auditadas por README: ProDen requiere SURE/modelo/pesos, StatMC/StatER modifican pbrt-v3 y recogen estadísticas por muestra; no son filtros drop-in para EXR de Blender. No se ha portado código.
- **F3 candidato pendiente de CI real:** `tests/scene_detail_target.py` con 52 lamas, juntas de 26 filas/13 columnas, vidrio, metal y microbump; Blender generator acepta `ACD_SCENE=detail_target`. Matrix de workflow incluye 320×240 para este caso con refs 1024 spp ×2 y tres noisy seeds; medición de gradiente debe validarse en este fixture.
- Se eliminó duplicación temporal de OIDN CLI en workflow histórico M3.9: el workflow V2 autónomo ya se ejecuta correctamente, evitar rerender innecesario. Nueva CI y benchmark **pendientes al commit**, no afirmar que fixture corre.

---

## E0014 — OIDN standalone 2.5.1 comprobado, siguiente aislamiento 2.3.3 vs 2.5.1 (2026-11-12)

- [Run #43233365334](https://github.com/mxlzz/ACD/actions/runs/43233365334) **success ambos jobs**. Informe permanente [E0014](docs/experiments/E0014.md) y artifacts [Glass #13951826448](https://github.com/mxlzz/ACD/actions/runs/43233365334/artifacts/13951826448), [interior #13950773895](https://github.com/mxlzz/ACD/actions/runs/43233365334/artifacts/13950773895).
- RMSE medio 3 seeds: Glass OIDN compositor 0.15562493 vs CLI 2.5.1 0.15612150; Interior compositor 0.07563019 vs CLI 2.5.1 0.08564105. Error gradiente bordes Glass 0.09138522 vs 0.09695046; interior 0.06909926 vs 0.07730485. **Sin ganancia demostrada** en estos fixtures para OIDN 2.5.1 CLI; configuraciones potencialmente distintas, no atribuir a versiones.
- **Ahora preparado:** `oidn_versions_compare.py` compara dos binarios oficiales 2.3.3/2.5.1 sobre mismos PFMs y flags CPU HDR High, prueba repetición 2.5.1; workflow de F2 actualizado. Ejecución nueva pendiente.

---

## F2 — Implementación conectada al workflow existente (2026-11-12)

- [CI Python #43233365339](https://github.com/mxlzz/ACD/actions/runs/43233365339) **success: 89 tests**, incluida conversión PFM y métricas de detalle; comprobador de trazabilidad aprobó. Esto **no** es ejecución de Blender/OIDN standalone.
- El nuevo workflow `acd-v2-oidn-251-pilot.yml` no apareció en la lista de runs automáticamente durante el PR; para no depender de un disparo manual imposible de garantizar, se agregó el paso OIDN 2.5.1 al workflow M3.9 existente, que ya está activado por cambios en su archivo. Conserva los ensayos y añade mediciones de la versión externa sobre iguales beauty/AOV.
- **Nueva ejecución pendiente al commit.** Inspeccionar si se descargó binario con SHA oficial, si cada seed generó su multilayer y si PFM/native comparten beauty sin delta; abortar si no. No inferir superioridad.

---

## F2 — OIDN 2.5.1 standalone, ejecución experimental preparada (2026-11-12)

- Código nuevo: PFM RGB32 little-endian sin color management, test de roundtrip HDR/orden de filas; `scripts/oidn251_compare.py` ejecuta el binario oficial CPU sobre beauty/albedo/normal exactamente de cada seed y compara frente a compositor OIDN en dos referencias. Export multilayer por semilla activado cuando AOV capture.
- El workflow descarga un binario oficial SHA-256 fijado (digest de GitHub Releases API) y registra SHA de PFM/output, log de proceso, error global y gradiente. Escenas piloto Glass Lobby/interior emisivo a 192×144, 24 spp ×3 y 1024 spp ×2 referencias. Es **nueva comparación de versión**, no repetición de ranking SID.
- **Pendiente en este commit:** CI real y piloto, sin resultados numéricos todavía; no implica equivalencia de políticas de prefilter en Blender y CLI.
- Siguiente: inspeccionar resultados y conservar informe permanente E0014, después aumentar dificultad de escena de detalle.

---

## F3 — Implementación de medición de gradientes (2026-11-12)

- Añadido `acd_lab/detail.py`: gradientes RGB con compresión `asinh`, máscaras de borde definidas exclusivamente por referencia y error en regiones planas. Los métodos no pueden elegir sus propias máscaras. ROI se mide en cuadrícula original, con parejas contiguas válidas, evitando un artefacto previo de vecinos ficticios al aplanar máscaras.
- Integrado en `evaluate_batch`, `assess_regions` y agregado descriptivo de semillas. `edge_contrast_ratio` **no es ranking autónomo**; puede premiar halos. Referencias finitas pueden introducir errores en la máscara.
- Pruebas sintéticas nuevas para fidelidad exacta, blur, oversharpen, ruido plano, región discontinua, borde cromático, HDR negativo y entrada inválida. **CI pendiente al commit; no hay benchmarks de escenas ejecutados en esta etapa.**
- Siguiente: comprobar quality CI y corregir cualquier fallo; usar EXR/Blender reales y comprobar distinción de métodos sobre detalle antes de inferir superioridad.

---

# ACD V2 — OIDN y conservación de detalle

**2026-11-12, F1 — cambio de estrategia iniciado.** Branch `dev/acd-v2-oidn-detail-eval` creada desde commit `9a70736d88af` de PR #4. Issue #9 abierto. Este commit registra [plan V2](docs/ACD_V2_PLAN.md), auditoría estática de OIDN [v2.5.1](docs/OIDN_SOURCE_AUDIT.md), actualización del protocolo y prioridades. **No hay código, tests ni nuevos renders en este commit**; CI aún pendiente. El addon estable y reconstrucción SID no se alteran.

**Evidencia que motiva F1:** [E0013](docs/experiments/E0013.md): Blender5.0.1 Glass Lobby e interior emisivo, Standard y OIDN compositor nativo mismo RMSE medio (~0.14833 y 0.08236), High/Super peor promedio; no mide fidelidad de texturas finas. SID comercial 5.x no está incluido. Classroom multiseed excluido por E0007. No aseverar superioridad general ni descartar recuerdos de conservación de detalle en SID 5.x.

**Siguiente acción:** F3 métricas de detalle *reference-driven* con pruebas sintéticas y conexión al pipeline, junto a F2 comparación de OIDN independiente; disponer luego de escenas mayores. Consulta de PR draft y workflow CI tras commit.

---

# M2 — External .blend scene benchmark and regional analysis

**Project plan:** [docs/ROADMAP.md](docs/ROADMAP.md). **Scientific foundations and hypotheses:** [docs/research_foundations.md](docs/research_foundations.md). These are reference documents; the status below records actual implementation and evidence.

Updated: 2026-11-11. Branch dev/acd-m2-real-scenes-regions, draft PR #4 stacked on M1 PR #3.

## M3.6 — Operadores sin OIDN: prueba real aprobada (2026-11-11)

- [Run 43106813982](https://github.com/mxlzz/ACD/actions/runs/43106813982) **success**, [artifact 13893069815](https://github.com/mxlzz/ACD/actions/runs/43106813982/artifacts/13893069815). Entradas iguales (`source_inputs_equal=true`).
- **Resultados aislados 3.6 vs 5:** ADD, MULTIPLY, ADD con emisión HDR idénticos píxel a píxel en RGB y alfa (RMSE=0). SepRGBA/CombRGBA frente a SetAlpha devuelve RGB idéntico, alfa RMSE=3.84746e-08 y máximo absoluto 5.96046e-08.
- **Inferencia:** estas operaciones y el mapeo de alfa probado no explican las diferencias mucho mayores en High/Super (RGB RMSE 0.065–0.068 y alfa ~0.00387). Esto acota causas hacia OIDN/parametrización/otras ramas, pero no las identifica de manera exhaustiva.
- **Siguiente:** aislar nodos OIDN individuales bajo exactamente las mismas entradas (Fast, Accurate guiado, emisión Accurate sin guías, alfa Accurate guiado).

## M3.9 — Segunda corrida completada y decisión de transición (2026-11-11)

- [Run #43113414513](https://github.com/mxlzz/ACD/actions/runs/43113414513): **ambos jobs success**, `glass_lobby` y `interior_emissive`, tres noisy seeds 24 spp, dos referencias 1024 spp, 160×120. Artifacts [glass 13896374534](https://github.com/mxlzz/ACD/actions/runs/43113414513/artifacts/13896374534), [emisivo 13897536701](https://github.com/mxlzz/ACD/actions/runs/43113414513/artifacts/13897536701).
- **Resultados promediados por tres semillas, RGB RMSE:** Glass Raw 0.31338931, ACD Standard y OIDN compositor nativo 0.14833401, High/SID4 High 0.17022242/0.17022239, Super/SID4 Super 0.17611973/0.17611974. Emisivo Raw 0.24915133, Standard/nativo 0.08236044, emisión preservada 0.08267392, High 0.08670461, Super 0.09241571, SID4 High 0.09496714 y SID4 Super 0.09986059.
- **Auditoría de referencias:** ambas escenas pasan heurística de diversidad y no disparan alerta de spread, con discrepancia ref/raw **0.19417 (Glass)** y **0.20842 (emisivo)**; convergencia e independencia Monte Carlo siguen sin demostrarse.
- **Decisión:** no promover ACD Standard como mejora sobre nodo nativo, ni High/Super ni preservación de emisión; el RMSE agregado de esta última empeora ~0.38 % en interior (ganó solo 1/3 semillas). La coincidencia de métricas no equivale a imagen idéntica: diferencias directas están disponibles en `summary.json`.
- **Hallazgo de disciplina:** E0007 ya había demostrado que Classroom carece de variación de semillas en esta versión: la primera corrida M3.9 replicó innecesariamente un ensayo que debía estar excluido. No repetirlo como prueba multisemilla sin modificar condiciones y verificar imágenes.
- **Fuente de OIDN:** el árbol de código Blender [v3.6.23](https://github.com/blender/blender/blob/v3.6.23/build_files/build_environment/cmake/versions.cmake) especifica `OIDN_VERSION 1.4.3`; Blender5 oficial contiene `libOpenImageDenoise.so.2.3.3` en el runner. No prueba por sí mismo qué DLL concreta cargó el Blender3.6 binario ni causalidad única.
- Informe permanente [E0013](docs/experiments/E0013.md) y protocolo de escena profesional [PRO_SCENE_INPUT.md](docs/PRO_SCENE_INPUT.md).
- **Siguiente puerta:** archivo `.blend` real autorizado/anonimizado, con cámara y texturas empaquetadas; el evaluador local ya existe. Dejar de reiterar el mismo tipo de escena pequeña. PR #4 sigue draft, addon estable intacto.

## M3.9 — Primeras escenas: resultados y control de validez (2026-11-11)

- [Run #43112553045](https://github.com/mxlzz/ACD/actions/runs/43112553045): ambos jobs `success`, pero un job verde significa que produjo medidas, **no** que el conjunto tenga validez estadística. EXR y reportes en [Glass Lobby artifact 13897341205](https://github.com/mxlzz/ACD/actions/runs/43112553045/artifacts/13897341205) y [Classroom artifact 13896727821](https://github.com/mxlzz/ACD/actions/runs/43112553045/artifacts/13896727821).
- **Glass Lobby 160×120, 24 spp contra 384 spp:** Raw RMSE 0.32117; ACD Standard y OIDN nativo compositor **ambos 0.14789017**; SID4 Standard 0.16367653; ACD High y SID4 High ~0.1713718; ACD Super y SID4 Super ~0.1836906. Ambos rankings de referencias coinciden, pero las referencias discrepaban RMSE 0.093295 y `reference_disagreement_over_raw_error=0.31496` (alerta relevante). La diversidad de noisy seeds pasa heurística, independencia no demostrada.
- **Classroom CC0 160×120, 24 spp contra 384 spp:** raw/reference RMSE 0.093205; las dos referencias difieren solo RMSE ~1.65e-6 y noisy seeds 539 vs 911 difieren solo RMSE ~8.43e-7. `input_diversity_heuristic_passed=false` y `almost_identical_reference_images=true`; **benchmark multisemilla inválido para concluir calidad o estabilidad de ranking**. Causa sin identificar; no contabilizar ranking como evidencia de superioridad.
- **Hallazgo de baseline:** ACD Standard y OIDN compositor registran métricas exactamente iguales en ambos casos; eso NO implica mejora frente a nativo. High/Super ACD y SID4 Reference prácticamente coinciden en Glass Lobby. Una comparación directa de pixels para cuantificar redundancia se agrega al siguiente piloto.
- **Siguiente decisión:** descartar Classroom del conjunto con pretensión multisemilla hasta diagnosticar por qué las seeds no cambian la salida. Repetir `glass_lobby` e `interior_emissive` con 1024 spp ×2 referencias, 3 noisy seeds, incluir alternativa `STANDARD_emission_preserved` y diferenciar métricas entre métodos del error relativo a ground truth.
- **Nota:** ni siquiera el siguiente piloto garantiza convergencia o superioridad. No modificar `sid_reference.py` ni producción basándose en rankings de baja resolución.

## M3.9 — Método mejorado y segunda corrida pendiente (2026-11-11)

- El resumen incorpora banderas `input_seed_diversity_passed`, `references_almost_identical`, `large_reference_discrepancy` y `suitable_for_exploratory_quality_ranking`, y diferencias directas de métodos `STANDARD/NATIVE_COMP_OIDN`, `HIGH/SID4_HIGH`, `SUPER/SID4_SUPER`, `STANDARD_emission_preserved/STANDARD`.
- En CI, matriz `glass_lobby` + `interior_emissive`; 160×120, 24 spp, seeds 539/911/1337; referencias 1024 spp, seeds 8819/8922. `ACD_PRESERVE_EMISSION=1` solo como ablación controlada, sin reclamar su ventaja.
- Estado al commit: **CI nueva pendiente**. El experimento Classroom se conserva como evidencia negativa, no se borra ni se oculta.

## M3.8 — Resultado verificado de parámetros OIDN (2026-11-11)

- [Run #43111684409](https://github.com/mxlzz/ACD/actions/runs/43111684409) `success` y [artifact #13896511879](https://github.com/mxlzz/ACD/actions/runs/43111684409/artifacts/13896511879): 8 filtros Blender3.6 y 24 variantes Blender5 con los mismos EXR. Passthrough de entradas validado.
- Blender 5.0.1 incluye Open Image Denoise `libOpenImageDenoise.so.2.3.3`. No se conoce aún el identificador exacto de biblioteca en Blender3.6.23, por lo que no puede atribuirse toda divergencia a una versión concreta.
- HDR=true, RMSE RGB entre versiones: Fast guiado High/Balanced 0.0328543, Quality Fast 0.0427344; Accurate guiado High 0.0306022, Balanced 0.0333146, Fast 0.0443925; emisión sin guías High/Balanced 0.0619173; alfa High 0.0061815.
- Apagar HDR reduce diferencia histórica de emisión a ~0.0021 cuando ambos están HDR=false; **no indica mejor fidelidad**. En Blender5, cambiar HDR true→false altera emisión con RMSE ~0.9046. Mantener HDR para preservar radiancia fuera de 0..1.

## M3.9 — Banco sobre escenas Cycles, pendiente de ejecutar (2026-11-11)

- Nuevo workflow `sid-architectural-pilot.yml` para `glass_lobby` procedimental y Classroom CC0 externo. Render 160×120, 24 spp, dos seeds 539/911 y dos referencias 384 spp (8819 y 8922), todos los candidatos procesan el mismo render.
- Incorpora `NATIVE_COMP_OIDN`, nodo nativo del compositor con Accurate/High/HDR, **no confundir con Cycles denoise interno**. Se compara con ACD y SID4 Reference en el mismo EXR y se archivan métricas, referencias, informes de semillas y outputs.
- **CI aún no verificada.** Las referencias finitas son diagnóstico de calidad relativa, no prueba de convergencia o superioridad. Falta escala de producción y escenas aportadas por usuario.

## M3.8 — Corrección de YAML inválido detectado en Actions (2026-11-11)

- [Run #43111531413](https://github.com/mxlzz/ACD/actions/runs/43111531413) falló **antes de crear jobs**: nombre de workflow mostrado como ruta `.github/workflows/sid-oidn-parameter-matrix.yml`. Motivo identificado en fuente: label del paso `Archive matrix: EXRs...` tenía dos puntos seguidos de espacio sin comillas, invalidando la sintaxis YAML.
- **Cambio:** se entrecomilló el nombre del paso. No se modificaron experimento OIDN, inputs, métricas ni variables de calidad. **CI posterior pendiente**; no atribuir este error a GitHub runner ni al algoritmo.

## M3.8 — Matriz experimental de parámetros OIDN (2026-11-11)

- **Hipótesis activa:** la diferencia RGB entre SID 3.6 y adaptador Blender 5 está presente en nodos OIDN individuales. El estudio M3.7 registró Fast RMSE=0.0328542782, emisión sin guías ROI RMSE=0.2157095979; no se puede atribuir aún a una versión de backend ni a un parámetro particular.
- **Implementación candidata:** `tests/blender_sid_oidn_matrix.py` procesa el mismo fixture EXR con 4 entradas/tipos de filtro. Blender3.6 ejecuta 8 casos (Fast/Accurate, emisión y alfa × HDR true/false); Blender5 ejecuta 24 casos equivalentes (Quality High/Balanced/Fast × HDR true/false), fijando prefilter por caso. Ningún algoritmo ACD se modifica.
- **Control:** SHA y raw passthrough de noisy/normal/albedo/alpha/emission, EXR RGBA 32-bit, métricas RGB y ROI emisiva, cambio intraversión de Quality/HDR, logs de build y archivos OIDN distribuidos con cada Blender. Compara cercanía a salida histórica **sin equipararla a calidad**.
- **Fuentes oficiales de los controles:** manual Blender 3.6 `docs.blender.org/manual/en/3.6/compositing/types/filter/denoise.html`, Blender 5.0 `docs.blender.org/manual/en/5.0/compositing/types/filter/denoise.html`; versión exacta OIDN solo se anotará si es verificable.
- **CI nueva pendiente** al commit; no cerrar M3.8 sin resultados. Próximo paso posterior: integrar SID4 Reference y ACD en comparativa de escenas arquitectónicas procedurales con muestreo controlado y referencias independientes; idealmente después cargar un .blend real facilitado por usuario.

## M3.7 — OIDN individual verificado entre Blender 3.6 y 5.0 (2026-11-11)

- **Evidencia de ejecución:** [Actions #43107260820](https://github.com/mxlzz/ACD/actions/runs/43107260820) `success`; [artifact #13895310157](https://github.com/mxlzz/ACD/actions/runs/43107260820/artifacts/13895310157) con EXR, hash y diferencias firmadas. Se confirmó `input_passthrough_valid=true`.
- **Resultados OIDN aislado, RGB RMSE port Blender 5 vs original Blender 3.6:** Fast guiado **0.0328542782**, Accurate guiado **0.0306021047**, emisión Accurate sin guías **0.0619173071**, alfa como imagen RGB Accurate guiado **0.0061814454**, Diffuse Direct Accurate guiado **0.0042534052**. Región emisiva del filtro de emisión: RGB RMSE **0.2157095979**.
- **Contraste causal controlado:** el filtro Fast independiente produce prácticamente el mismo delta que Standard integral (**0.0328542603**); el filtro aislado de emisión explica plausiblemente buena parte del error localizado de High/Super (ROI emisiva **0.22305557 / 0.23223786**), sin constituir una descomposición aditiva exacta.
- **Precisión sobre alfa:** el canal A de los EXR de OIDN aislado coincide (RMSE=0); para interpretar la rama alfa de High/Super debe compararse el RGB procesado de la imagen escalar de alfa que después se utiliza para recombinación. Su RGB aislado sí difiere (**RMSE 0.00618145**). El error alfa High/Super completo era ~**0.0038727**.
- **Lo descartado en M3.6:** ADD/MULTIPLY y ADD HDR fueron idénticos, recombinación de alfa solo tuvo diferencias ~5.96e-8; la divergencia relevante se observa ya dentro de filtros OIDN individuales.
- **Conclusión limitada:** backend OIDN y parámetros por versión son factores plausibles; todavía no se identificó la versión efectiva ni se ajustó la equivalencia de Quality/HDR. No llamar al port “pixel-identical” ni superior; no modificar el addon estable para perseguir métricas interversiones sin ground truth.
- **Próxima prueba prioritaria M3.8:** establecer y consignar versiones de Blender/OIDN y parámetros/flags de prefiltrado, Quality y HDR; diseñar ablaciones por parámetros del Blender 5 manteniendo el mismo EXR y medir qué delta explica cada cambio. Posteriormente verificar en escenas Cycles reales, muestras y referencias independientes.

## M3.7 — Experimento candidato de OIDN aislado (2026-11-11)

- Código agregado: `tests/blender_sid_oidn_numeric.py`, `scripts/compare_sid_oidn_numeric.py`, workflow `sid-oidn-numeric-parity.yml`. Cinco casos de nodos OIDN sobre los EXR congelados y sus guías, sin mixing de familias; compara RGB/HDR/alfa por filtro.
- **Configuración registrada:** Blender3.6 usa solo `prefilter` como upstream; Blender5 usa socket Prefilter y opciones explícitas Quality=High, HDR=True. No se supone que backend ni controles coincidan.
- **CI posterior al commit pendiente.** Conservar manifest, EXR y mapas firmados. No modificar port estable ni inferir bug por un delta entre backends.

## M3.5 High/Super — primera prueba numérica real aprobada (2026-11-11)

- [Run 43106273482](https://github.com/mxlzz/ACD/actions/runs/43106273482): **success**; [artifact 13894002202](https://github.com/mxlzz/ACD/actions/runs/43106273482/artifacts/13894002202) con 15 AOV de entrada, outputs Blender 3.6 y 5.0, manifests y mapas firmados.
- **Control:** `input_passthrough_valid: true` tanto High como Super; las entradas congeladas se leyeron equivalentes entre versiones (tolerancia máxima absoluta 0.001). No se trata de renders Cycles independientes.
- **Diferencia numérica SID5 port frente a SID3.6 histórico (no ground truth):** High RGB RMSE=0.06531013, MAE=0.01516130, max_abs=2.04866791; Super RGB RMSE=0.06788146, MAE=0.01596297, max_abs=1.89871454.
- **Región emisiva (más sensible):** High RGB RMSE=0.22305557 y Super RGB RMSE=0.23223786. **Alfa global:** High RMSE=0.003872700 y Super RMSE=0.003872709. Todas son diferencias entre implementaciones/versiones, no calidad frente a referencia convergida.
- **Limitación:** los nodos MixRGB históricos y ShaderNodeMix, SepRGBA/CombRGBA y SetAlpha, y las diferentes versiones/controles OIDN todavía pueden explicar parte de la diferencia. La topología estructural previa aprobada no certifica equivalencia de operaciones HDR.
- **Siguiente prueba M3.6:** aislar los operadores compositores **sin ningún OIDN**, bajo los mismos EXR, antes de intentar ajustar el denoiser.

## M3.6 — Comparador de operadores sin OIDN (2026-11-11)

- **Código candidato:** `tests/blender_sid_operator_numeric.py`, `scripts/compare_sid_operators.py`, y workflow `sid-operator-numeric-parity.yml` comparan ADD, MULTIPLY, ADD con emisión HDR y alfa recombinada (MixRGB + Separate/Combine de Blender 3.6 vs ShaderNodeMix + SetAlpha de Blender 5).
- **Prueba de aceptación:** entradas con SHA idénticos, passthrough comparable, salidas EXR finitas y métricas por operador separando RGB y alfa, con mapas firmados. Una diferencia **no** constituye por sí sola fallo de OIDN.
- **Estado:** nueva ejecución no observada aún al commit; no atribuir causas antes de inspeccionar el reporte. El addon SID Reference queda intacto.

## M3.5 High/Super — primer fallo de CI, ejecución modular (2026-11-11)

- [Run 43106081661](https://github.com/mxlzz/ACD/actions/runs/43106081661): instalación y prueba unitaria de AOV `1 passed`; generador EXR falló con `ModuleNotFoundError: No module named 'scripts'` al invocar `python scripts/sid_highsuper_numeric_fixture.py`. No llegó a Blender ni mide diferencia de SID.
- **Corrección mínima:** invocar generador y comparador con `python -m scripts.<módulo>`, que sitúa el root del repositorio en la ruta de importación. El generador, comparador y algoritmo de referencia se mantienen sin cambios.
- **Estado:** pendiente CI posterior al commit; mantener High/Super sin evidencia numérica hasta que termine.

## M3.5 — Standard: primer resultado numérico ejecutado (2026-11-11)

- [Run 43104673773](https://github.com/mxlzz/ACD/actions/runs/43104673773): **success**; [artifact 13893222574](https://github.com/mxlzz/ACD/actions/runs/43104673773/artifacts/13893222574) con archivos originales, portados y mapas de error.
- SHA-256 y passthrough de noisy/albedo/normal idénticos en Blender 3.6.23 y 5.0.1: MAE=RMSE=max_abs=0 en los 6144 píxeles. El protocolo de comparación es válido en este fixture.
- Salida Standard Blender 5 respecto a SID 3.6: RGB RMSE 0.03285426, MAE 0.01902902, máximo absoluto 0.46119857; en píxeles HDR RGB RMSE 0.04103480. Alfa RMSE=0 e igualdad exacta.
- Las diferencias son **entre versiones de Blender/OIDN**, sin referencia ideal ni igualdad comprobada de versiones/ajustes del backend. No atribuir automáticamente a bug del port ni declarar calidad superior.

## M3.5 — High/Super, piloto numérico candidate (2026-11-11)

- Incorporado workflow separado \`sid-highsuper-numeric-parity.yml\`, inputs EXR congelados de 15 AOV, SHA-256 por entrada, ejecuciones del SID histórico Blender 3.6 y port Blender 5, controles passthrough en ambos, mapas de error RGB/HDR/alfa y manifests.
- Fija transmisión/emisión/entorno activados, volumen desactivado; material sintético 96×64. No constituye benchmark de imágenes arquitectónicas.
- **Estado:** aún no ejecutado al momento del commit. No inferir paridad High/Super del éxito Standard. Siguiente: ejecutar CI, verificar 15 controles y medir diferencias; documentar fallas reales.

## M3.5 — CI real, primera falla corregida (2026-11-11)

- [Run #43104453238](https://github.com/mxlzz/ACD/actions/runs/43104453238): generador de entradas/pytest OK; SID público real en Blender 3.6.23 produjo EXR y manifests; el **script del port en Blender 5.0.1** falló antes del render al fijar `node.format.file_format="OPEN_EXR"` con `media_type` por defecto `MULTI_LAYER_IMAGE`. Error concreto: `enum "OPEN_EXR" not found in ('OPEN_EXR_MULTILAYER')`.
- **Diagnóstico:** configuración de OutputFile en harness, no evidencia de bug del SID Reference. El pipeline ya probado de ACD establece `format.media_type="IMAGE"` antes de `file_format="OPEN_EXR"`.
- **Corrección localizada:** en el script M3.5, para Blender 5 se fija media_type IMAGE antes de OPEN_EXR. No se tocan nodos OIDN, entradas ni comparador.
- **Aceptación:** rerun debe generar port/raw+guías/sid y un informe completo. Esta corrección no está verificada aún al commit; mantener M3.5 sin cerrar.

## M3.5 — Refinamiento de controles EXR (2026-11-11)

- **Corrección metodológica antes de observar resultados:** el passthrough ahora se exporta para **los tres buffers** (imagen ruidosa, albedo y normal) en ambos Blenders, no solo para RGB/noisy. El comparador exige máximo error absoluto cross-version de 0.001 en cada buffer; también reporta diferencias respecto del EXR original, sin presuponer que la premultiplicación de alfa de compositor sea un error del denoiser.
- **Error de informe corregido:** `pixels` contaba solamente la altura en comparaciones globales sin máscara. Ahora cuenta los píxeles reales, con regresión en pytest.
- **Prueba posterior a la corrección:** CI numérica aún pendiente; no atribuir diferencias al filtro sin pasar las tres validaciones de entrada.

## M3.5 — Primer banco numérico cross-version, Standard (2026-11-11)

- **Hipótesis comprobable:** medir diferencias entre el SID histórico 4.x (Blender 3.6.23) y la réplica independiente (Blender 5.0.1), sobre tres EXR congelados idénticos (imagen ruidosa HDR y alfa, albedo, normal). No se debe confundir una diferencia de lectura o compositor con un filtro distinto.
- **Implementación candidata:** generador determinista Python/OpenEXR con hashes SHA-256; ejecutor Blender para Standard real/port, control de passthrough sin denoise en ambas versiones, outputs EXR 32-bit y manifiestos; comparador de RGB, HDR, alfa y regiones de transparencia con mapas firmados NPZ. Workflow `sid-numeric-parity.yml` clona upstream temporalmente.
- **Criterios de aceptación previos:** que ambas ejecuciones procesen los mismos bytes, que la comparación de passthrough difiera como máximo 0.001 en valor absoluto, que los outputs sean finitos y que se archiven los EXR y los deltas. **Resultados CI pendientes**; no afirmar aún equivalencia ni error específico de OIDN.
- **Alcance intencional:** Standard únicamente y fixture sintético pequeño 96×64 para depurar el circuito. High/Super, material AOV y escenas reales se abordarán después de inspeccionar resultados, no como parte de una supuesta certificación visual.
- **Siguiente paso:** revisar workflow, corregir fallos observados sin bajar umbrales a ciegas y registrar si el passthrough es confiable antes de interpretar deltas de SID.

## M3.4 — Validación posterior al commit e529c6b (2026-11-11)

- [SID upstream graph #43101708644](https://github.com/mxlzz/ACD/actions/runs/43101708644): **success**, `passed=true`, `errors=[]` para el contrato estructural delimitado. Log `With the provided path, there will be 3 files uploaded`; artifact [sid-upstream-3.6-vs-port-5.0-graph-contracts](https://github.com/mxlzz/ACD/actions/runs/43101708644/artifacts/13890459701) creado correctamente (tres JSON, vencimiento previsto 2026-11-25).
- [Quality gate #43101708666](https://github.com/mxlzz/ACD/actions/runs/43101708666): **success**, incluida comprobación de trazabilidad por commit y test OpenEXR.
- [Blender smoke #43101708862](https://github.com/mxlzz/ACD/actions/runs/43101708862): **success** en Blender 5.0.1 y 5.3.0; en 5.0.1 están los artifacts comparativos SID4 vs ACD, EXR y fixture externo. En 5.3 solo smoke/topología, por condiciones del workflow.
- **Issue #8 deja de bloquear pruebas nuevas.** La causa de la cola anterior no fue identificada; algunas ejecuciones antiguas permanecían `queued` al verificar. No equivale a un incidente de GitHub confirmado.
- **Alcance:** paridad estructural parcial, ejecución del port y generación de muestras, no igualdad de píxeles contra el SID original. Los resultados con 32×24/pequeñas referencias finitas no acreditan calidad superior.
- **Próxima tarea prioritaria M3.5:** comparar SID original en Blender 3.6 frente a SID Reference en Blender 5 bajo mismos buffers EXR, registrando versión/OIDN, mezclas HDR, salida alfa, diferencias numéricas y error residual. Mantener PR #4 en draft.

## M3.4 — CI reanudada; corregida la captura de manifests (2026-11-11)

- **Verificación real anterior al cambio:** [quality gate #43098851163](https://github.com/mxlzz/ACD/actions/runs/43098851163) OK; [Blender smoke #43098851162](https://github.com/mxlzz/ACD/actions/runs/43098851162) OK en 5.0.1/5.3, con comparadores EXR y tests de render de variantes en 5.0.1 (pasos pesados omitidos en 5.3); [upstream SID graph parity #43098851161](https://github.com/mxlzz/ACD/actions/runs/43098851161) OK con `passed=true`, `errors=[]`.
- **Alcance comprobado:** conteos de denoisers y mezclas, factores, prefilters, guías de emisión y alfa en topologías comparadas. No se ha certificado igualdad píxel, equivalencia de backend OIDN ni fidelidad numérica de alfa entre Blender 3.6/5.0.
- **Defecto nuevo de reproducibilidad detectado en logs:** el workflow escribió manifiestos de contrato en `/tmp/acd_sid_legacy_contract.json`, `/tmp/acd_sid_port_contract.json` y `/tmp/sid_contract_comparison.json`, pero el upload buscó rutas diferentes (runner.temp). Avisó `No files were found` y no publicó artifacts, aun con job verde.
- **Corrección en este commit:** cargar los tres archivos desde sus rutas exactas; `if-no-files-found: error` para que futuras pérdidas de evidencia no parezcan CI aprobada. **La nueva ejecución y sus artifacts aún requieren verificación posterior al commit**.
- **Bloqueo previo (Issue #8):** varios runs antiguos siguen `queued` sin jobs; no hay causa confirmada. Al menos tres runs posteriores ya se ejecutaron. No modificar permisos ni afirmar que el incidente esté diagnosticado.
- **Siguiente puerta:** confirmar que el artifact contiene los tres manifiestos; después diseñar y ejecutar una comparación interversión sobre el mismo EXR de entrada, con foco en emisión, alfa, HDR y OIDN, antes de juzgar calidad o fusionar PR #4.

## Bloqueo externo de CI — M3 / Issue #8 (2026-11-11)

- **Hecho observado:** 19 de 25 ejecuciones recientes de GitHub Actions están `queued` sin jobs creados (`total_count=0`), algunas desde las 20:27 UTC, inclusive Python quality gate y Blender smoke conocidos. El control de trazabilidad nuevo y el port SID aún no tienen pruebas físicas aprobadas.
- Runs representativos: quality gate 43096932831; Blender 5 43098499754; comparación SID3.6/port5 43098499807.
- Dos workflows nuevos fallaron sin jobs por expresiones inválidas en `jobs.env`; se corrigió y la ejecución nueva ahora se encuentra en cola. **La causa general de la cola NO está establecida.**
- **Decisión:** no fusionar ni declarar paridad. Mantener el código candidato, los manifests y las pruebas escritos, mientras el usuario revisa Actions/Settings/avisos según [Issue #8](https://github.com/mxlzz/ACD/issues/8).
- Este commit corrige además un bug lógico del comparador: si ambos conteos de Standard eran iguales pero erróneos, la comparación anterior podía no detectarlo. Agregado test regresivo.
- **Próximo paso:** resolver Actions, observar CI real y recién entonces avanzar a comparación SID histórico frente a port Blender 5. No hay justificación para añadir filtros nuevos.

## M3.4 — Comparación estructural con el SID original en Blender 3.6 (2026-11-11)

- **Objetivo:** verificar que la topología y los parámetros de SID Reference coincidan con el addon histórico real, no con una interpretación del código.
- Implementado workflow `sid-upstream-parity.yml`: clona GPL SID commit fijo en runner efímero, lo carga (sin UI/updater) en Blender 3.6.23, inspecciona grupos de nodos y compara contra constructor de Blender 5.0.1.
- Nuevos scripts: `blender_sid_legacy_probe.py`, `blender_sid_reference_snapshot.py`, `compare_sid_contracts.py`; pruebas puras para detección de discrepancia.
- **Estado:** los runs 43098302573 y 43098385953 fallaron sin jobs, por sintaxis/contextos de Actions (uso de `runner.temp` en variables job.env). Se sustituyeron esas variables por rutas absolutas `/tmp/acd_sid_*`. **El resultado corregido aún no está verificado**. No demuestra paridad pixel a pixel ni backend OIDN.
- **Protección de ruta:** se limita a M3. Ninguna implementación experimental nueva ni modificación del addon de producción.

## M3.3 — Comparador SID4 Reference vs ACD, mismo render (2026-11-11)

- Ruta: M3 / Issue #7, paridad antes de optimización. Sin modificaciones del addon de producción.
- El runner experimental acepta `SID4_STANDARD`, `SID4_HIGH` y `SID4_SUPER`, construye el grafo separado y conecta los mismos buffers raw de Cycles usados para Standard/High/Super de ACD.
- `acd_lab/batch.py` incorpora esos EXR de modo opcional (ningún resultado histórico obligatorio cambia) y agrega test OpenEXR sintético.
- Pipeline CI Blender 5.0.1 genera un render pequeño con las seis variantes y una referencia finita. Su salida será un *test de funcionalidad/comparación*, **no una prueba SID 4.0 de paridad interversión**.
- **Verificación real pendiente:** las últimas acciones de GitHub siguen en cola. No se reclaman rendimientos ni equivalencia todavía.
- Próximo paso: usar el EXR de salida para confirmar que los grafos Blender 5 ejecutan de punta a punta y comparar contra SID upstream en Blender compatible.

## M3.2 — Primer port de comportamiento SID a Blender 5 (2026-11-11)

- Objetivo validado antes del cambio: Issue #7 / M3, sin desviación. Implementación independiente, sin copiar código GPL ni modificar ACD estable.
- Nuevos archivos: `addon/sid_reference.py` para grupos de referencia Standard/High/Super y `tests/blender_sid_reference_smoke.py` para comprobar nodos, conexiones, prefilter, guiado de emisión, alfa separado, volumétricos y render.
- El grupo se construye sin asignarlo al compositor del usuario; `prepare_reference_passes` modifica los ajustes de view layer **solo si el llamador lo invoca explícitamente**.
- `ShaderNodeMix` factor 1, sin clamp, para emular `MixRGB` ADD/MULTIPLY histórico. Blender 5 usa `CompositorNodeSetAlpha` en lugar de Separate/Combine RGBA: equivalencia de canal pendiente.
- CI de Blender 5.0.1/5.3 actualizada; **resultados aún pendientes**. La revisión de tests detectó una expectativa numérica errónea en el conteo opcional: High=5 y Super=8 sin transmisión/emisión y con volumen. Corregida antes de interpretar CI.
- Esta implementación no certifica paridad visual ni OIDN cross-version.
- Próximo paso: revisar CI, reparar incompatibilidades documentando cada commit y probar frente al SID histórico.

## M3.1 — Especificación de SID público (2026-11-11)

- Alineación previa: hito M3 / Issue #7, sin desvío; la tarea consiste en congelar comportamiento upstream antes de escribir el port.
- Implementado: [docs/M3_SID_REFERENCE_SPEC.md](docs/M3_SID_REFERENCE_SPEC.md) fija Standard FAST, High/Super Accurate, guías por familia, emisión sin guías, alfa filtrada, volumen, entorno, entradas RenderLayers y factor MixRGB = 1.
- Política: implementar un adaptador nuevo sin copiar código GPL; no se modificó el addon estable, ni se fusionó ninguna rama.
- Verificación: especificación cotejada con archivos Python del SID público y documentación Blender; **no es una prueba Blender ni certifica paridad**.
- Próximo paso M3.2: construir módulo separado y tests de nodos/render con Blender 5.0.1/5.3.

## Control de rumbo y trazabilidad — M3 (2026-11-11)

- **Hito activo confirmado:** M3 / Issue #7. No hay port SID Reference fiel verificado. La prioridad sigue siendo extraer especificación de nodos/enlaces/parámetros del SID público y después implementar paridad en Blender 5.
- **Implementado en este commit:** protocolo obligatorio para revisar alineación antes/después de cada cambio; bitácora de decisiones; verificador por commit integrado a la CI Python. Exige ROADMAP.md, STATUS.md y DECISION_LOG.md modificados juntos en cada commit futuro; la propia introducción del protocolo y el historial anterior están exceptuados.
- **Validación:** tests del verificador añadidos; resultado de CI real aún pendiente de observación.
- **Limitación:** la CI comprueba la presencia de trazabilidad, no decide si la investigación es adecuada ni demuestra equivalencia con SID.
- **Próximo paso:** especificación auditable de SID público, sin alterar el addon estable ni copiar código GPL antes de definir licencias.

## Rectificación de prioridad: SID antes que optimización ACD

- El objetivo original de replicación fiel de SID no se completó. El addon actual es un prototipo independiente inspirado en SID, **no** un port verificado ni una prueba contra el SID original.
- Auditoría directa detectó diferencias concretas: Standard FAST frente a Accurate; emisión sin guías en SID vs con guías en ACD; alfa denoised en SID vs preservada por defecto en ACD; Noisy Image, Mixer y opciones de AOV requieren contraste.
- Repositorio original público GPL-3.0 (commit b4186389cac386eff9d777bb681c0051f8bd9bd2) corresponde al SID histórico; versión comercial 5.3.0 no está publicada en ese código. **No se ha copiado fuente GPL ni modificado el addon estable.**
- Nueva prioridad: **M3 primero (Issue #7)**, especificar grafo original y portar comportamiento en Blender 5.x; mantener M2 como infraestructura y M4/adaptativo en espera. Detalle: docs/sid_parity_gap.md.


## Auditoría Cycles v5.0.1: guías de hits especulares (11-11-2026)

- El código de Cycles v5.0.1 **ya espera a rebotes posteriores cuando domina la contribución especular** antes de registrar características de denoising; no siempre utiliza el primer hit.
- E0012 prueba que cambiar conexiones de guías afecta la calidad, pero no identifica el mecanismo de degradación. No implementar ciegamente guías de «segundo hit» sin comprobar qué información ya registra el renderer.
- Fuente técnica y próximos controles: docs/cycles_guide_source_audit.md; tareas concretas [Issue #6](https://github.com/mxlzz/ACD/issues/6). La hipótesis H-01 se acota a la **correspondencia entre cada subpase y las guías usadas**.

## E0012 — Ablación de Albedo/Normal por subpase (11-11-2026)

- E0012 ejecutado y aprobado en Blender 5.0.1: 10 ramas de denoising sobre lobby de vidrio/metal, 128×96, 24 spp, 3 entradas y 2 referencias. Run https://github.com/mxlzz/ACD/actions/runs/43086458932.
- High sin guías intermedias bajó RMSE global 0,194924 → 0,180170, pero Standard guiado (0,174651) y Standard sin guías (0,173501) fueron mejores. High mejoró transmisión con guías retiradas; Super mostró un compromiso distinto y empeoró globalmente sin guías.
- La «guía Normal sin Albedo» en el Denoise de Blender es **ignorada por diseño**: las salidas fueron idénticas a las variantes sin guías. Se prohibió producir estos duplicados; informes históricos todavía pueden leerse. Fuente oficial y cifras en docs/experiments/E0012.md.
- **No se promovió ninguna variante** al addon. Próxima hipótesis H-01: auditar qué hits representan los AOV de Cycles, y evaluar guías de reflexión/refracción específicas en datasets de escenas no vistas.

## E0010 / E0011 — Ejecuciones completas (11-11-2026)

- E0010: la repetición completa de E0008 PASÓ, con 3 entradas diferentes y máscara regional idéntica (SHA-256; 66 píxeles). El RMSE en la región emisiva se redujo 0,2758194 → 0,2717647, pero las regresiones de MAE y RMSE global impiden activarlo por defecto. Run 43085166506.
- E0011: segundo escenario **procedural** de lobby con vidrio y metal. Blender 5.0.1, 128×96, 24 spp, 3 entradas y dos referencias de 1024 spp. Standard RMSE 0,1746515; High 0,1949242; Super 0,2014348. En máscaras glossy/transmisión Standard superó a Super en las tres entradas. Run 43085451268.
- Los dos workflows intensivos quedaron como **manuales** después de validarlos. Los reportes completos están en docs/experiments/E0010.md y E0011.md, con JSON numérico E0011_metrics.json.
- Las referencias no están certificadas como convergidas; E0011 no equivale a una segunda escena profesional externa. Próximo paso: ablar guías de Albedo/Normal por señal y reunir más escenas externas.

## M2.1 — Validación de la integridad de las comparaciones (2026-11-11)

- Incorporado `mask_sha256`: digest versionado del tamaño y la pertenencia exacta de cada píxel a la ROI. Los informes nuevos incluyen el hash; el agregador rechaza ROI con igual área/definición pero ubicación diferente y exige regenerar informes antiguos sin huella. Tests unitarios y OpenEXR de regresión agregados.
- Incorporado `acd_lab/reference_audit.py`: mide la discrepancia entre dos referencias de muestras finitas respecto del error del render ruidoso, detecta referencias casi idénticas y alerta cuando su diferencia es considerable. **No** certifica independencia ni convergencia (ambas se informan como no demostradas). Incluido en `compare-batch`.
- Corregida la semántica del diagnóstico multisemilla: `input_diversity_heuristic_passed` solo certifica el umbral heurístico de **diferencia entre imágenes**. `sampling_independence_proven` permanece `false`; ya no se usa el nombre engañoso `independent_seeds_verified`.
- Las pruebas verifican también dos referencias EXR, normalización del diagnóstico y máscaras distintas con el mismo número de píxeles. Evidencia y limitaciones técnicas: `docs/experiments/E0009.md`.
- Estado actual: verificaciones Python y Blender headless de la rama, pero **no** se ejecutó de nuevo el pipeline E0008 completo con el agregador actualizado ni una segunda escena profesional. M2.1 sigue abierto: https://github.com/mxlzz/ACD/issues/5

## Sampling-validity finding — E0007 (2026-11-11)
- Official Classroom: in independent Blender processes at 96x54, 16 spp, Classic TABULATED_SOBOL, changing Cycles seed 539 -> 911 only changed 4/5184 pixels (RGB RMSE ~1.04e-6); setting sample_offset 0 -> 16 changed only 8/5184 pixels. Source: GitHub Actions 43069937939.
- Switching Classic to BLUE_NOISE altered the image strongly (RGB RMSE 0.16825), but changing seed 539 -> 911 *within BLUE_NOISE* again produced virtually identical images (relative RMSE 1.32e-9). Source: run 43071018867.
- **Interpretation:** In this specific Classroom/Blender 5.0.1 setup, nominal seed changes do not generate meaningfully distinct noisy images. Cause is not established. This is a methodological blocker; do not treat extra seed labels as independent samples.
- Implemented automated per-pair diversity checks and prevented multi-seed mean rankings from being treated as validated unless raw samples pass image-diversity screening. This is a necessary check, not a proof of statistical independence.
- Classroom E0005/E0006 remain useful *single-input comparative ablations*; the allegedly independent seed-derived reference is not validated as independent sampling. The prior numeric improvements cannot yet be generalized.
- See docs/experiments/E0007.md. Heavy Classroom and seed probes are manual-only after debugging.

- E0007 controlled procedural interior: seeds 539 and 911 produce meaningfully different unfiltered 16-spp renders in independent Blender processes (pair RMSE / signal RMS 0.2655), unlike Classroom. Evidence: https://github.com/mxlzz/ACD/actions/runs/43071534950
- Classroom workflow now intentionally uses one noisy input only, without invalid multi-seed averages. Heavy benchmark and seed-probe workflows are manual-only.

## E0008 — emission preservation with verified diverse noisy inputs
- Procedural emissive interior, 128x96, 24 spp, three distinguishable raw noisy seeds and two 1024-spp unfiltered references.
- Baseline emission mask: 66 pixels (0.54% of image). Standard emission-region RMSE mean 0.275820 vs emission-preserved 0.271765 (~1.47% reduction), improvement only 2/3 seeds.
- However, emission-region MAE mean worsens 0.185852 -> 0.206836 (~11.29%), and global RMSE mean worsens 0.091558 -> 0.091715. No default algorithm change justified.
- Results and source runs: docs/experiments/E0008.md and E0008_metrics.json.
- Fixed a glob bug where seed_aggregate.json was treated as a seed folder; numerical CI and Blender smoke tests passed after the correction. Heavy emission workflow is now manual-only.

## Implemented and checked
- Local runner: scripts/run_scene_benchmark.py. Loads an existing .blend without saving, supports chosen frame/resolution, noisy/reference spp and seeds, optional existing reference, and CPU/CUDA/OPTIX selection.
- Experiment provenance: source scene SHA256, scene name, selected view layer, Blender version, color management settings, frame, samples, seed and device recorded.
- Raw multilayer EXR exported from the same noisy render as Standard/High/Super; it contains Composite and ViewLayer parts. Region analysis selects the actual ViewLayer stored in metadata.
- Explicit spatial ROI and relative AOV radiance-contribution masks, HDR regional metrics, signed error maps (not material ID segmentation).
- Real headless Blender 5.0.1 external .blend integration test PASSED, including byte-identical .blend checksum, AOV parsing and ROI report. Evidence: https://github.com/mxlzz/ACD/actions/runs/43057833000
- Python/EXR test suite passed on this branch. Blender 5.3 node API smoke also passed, but Blender 5.3 composited rendering is unverified on cloud runners lacking EGL.
- Fixed synthetic OpenEXR test fixtures requiring contiguous NumPy channel buffers.

- E0005: first real official Classroom (CC0) rendered and analyzed. At 384x216 / 32 spp vs 256 spp reference: Standard RMSE 0.043961, High 0.044847, Super 0.052703, Raw 0.072410. AOV closure RMSE 3.55e-8. In the emission-dominated 1.4% subset, raw RMSE 0.035607 vs Standard 0.060156. See docs/experiments/E0005.md and CI run 43058679034.
- E0006: Classroom emission-preservation results were recorded, but the independence of the reference/input sampling was not validated; see docs/experiments/E0006.md and E0007.md.

## Remaining validation
- Actual professional-sized scenes at 1080p+, multiple input seeds, convergence-tested reference.
- RTX 4050 OPTIX run on Windows.
- Material-specific quality in reflections/transmission, HDR-FLIP or reviewed crops.
- Full pass closure and alpha behavior with complex Blender shaders.
- No universal superiority or verified commercial SID 5.3 equivalence.

## Next gates
1. Evaluate official Classroom (CC0), Barcelona Pavilion (CC-BY), or a licensed production .blend outside Git. Keep scene assets out of the repository.
2. Inspect reflected/transmitted ROIs and compare 3+ noisy seeds to two high-spp references when practical.
3. Test guided versus unguided denoising only where the region metrics justify it.
4. Leave expensive renders manual/local; preserve stable addon apart from experiments.

## Earlier project state

# Persistent project state — ACD

Updated: 2026-11-11
Base M0 merged to main by PR #1.
M1 development: PR #3, branch dev/acd-m1-exr-evaluation. Related issue #2.

## Verified
- GitHub Actions Python core+lab checks passed.
- Blender 5.0.1: addon nodes constructed; render test passed.
- Blender 5.3: addon node construction passed; composited rendering remains unverified in the cloud runner because of missing EGL dependencies.
- OpenEXR 3.3+ support: tests with synthetic EXR passes passed.
- Blender-generated raw multi-layer EXR ingested successfully (run 43048580433).
- For the 48×40, 8 spp factory scene: raw beauty vs AOV recomposition max absolute difference 8.26e-8.
- Same Cycles noisy render successfully processed via Raw, Standard, High, Super branches (run 43048979372).
- First reference run: 16 spp seed 539 against 256 spp seed 8819. Standard RMSE 0.002668, Raw 0.002796, High 0.006526, Super 0.018854. See docs/experiments/E0001.md.
- Removing the final OIDN from High/Super barely changes RMSE; the raw compositing graph reproduces raw with RMSE ~1e-8.
- Blender 5.0.1 guided AOV denoising ablation: High RMSE 0.005879 without guides vs 0.006526 with; Super 0.008978 vs 0.018854. Neither beats Standard 0.002668 (run 43050200840).

- E0002: 48x40 architectural interior, 16 spp vs two 4096 spp references: High RGB RMSE 0.150261, Standard 0.154318, Super 0.158825, Raw 0.302980. High ranks first against both, but MAE and log-luminance metrics favor other methods. The reference-to-reference RMSE is 0.041418: not converged. Full details: docs/experiments/E0002.md.
- Added automated log1p luminance RMSE, per-pixel p95 error and metric-specific rankings to avoid relying on global linear RMSE alone.
- Follow-up 96x80 at 32 spp and two 4096 spp references configured as an evaluation job.

- E0003 (run 43051674524): 96x80, 32 spp, same noisy input, two 4096 spp independent references. Super RGB RMSE 0.085272, Standard 0.089322, High 0.090164. Super also improves MAE, log-luminance RMSE and p95 pixel RMSE relative to Standard in this trial. Unguided Super RGB RMSE 0.081339, but guided Super leads on MAE and log-luminance. The two references differ (RMSE 0.03941). More seeds/scenes required; see docs/experiments/E0003.md.
- Note: comparison order changed from E0002 to E0003; image size and input spp changed together, so no single cause is established.

- E0004: 96x80 interior repeated with four noisy seeds (539, 911, 1337, 2026) and shared two 4096-spp references (run 43052249917). Mean RGB RMSE: Standard 0.078680, Super 0.080243, High 0.082621. However Super has lower mean MAE (0.030957 vs Standard 0.033328) and lower p95 pixel error (0.105689 vs 0.114824). Unguided High and Super have lower mean RMSE (0.076094 and 0.077236). No universal winner. See docs/experiments/E0004.md.
- The expensive architectural multi-seed battery is now manual workflow_dispatch, not a default PR check, to avoid wasteful repeated CPU render runs.

## Unverified, pending
- Blender 5.3 actual composited render on machine with working graphics runtime.
- Equivalence to released SID 5.3 and performance on practical interiors.
- Convergence-checked reference and multiple independent input seeds.
- Material-specific quality improvements, HDR perceptual metrics, and RTX performance.

## Immediate next gates
1. E0004 multi-seed experiment completed. Next: isolate resolution vs sample budget as single-variable changes, add scenes and reference convergence checks.
2. Inspect per-pass residual maps to isolate where distortion is introduced.
3. Benchmark three test scenes and several seeds/spp budgets.
4. Move beyond generic OIDN stacking only when a measurable benefit appears.

## Policy
No merge of experimental M1 as a production denoiser unless empirical and API tests substantiate it. Keep the source research and licensing record in GitHub.

## E0019 — Cozy Kitchen CC-BY-SA vendored and Blender validated

- Source: Blender official 3.5 splash by Nicole Morena, ~7.3 MiB; permission CC BY-SA.
- Validation: original SHA and metadata in benchmarks/scenes/cozy_kitchen.audit.json. Blender 5.0.1 Cycles CPU smoke 192x192 4 spp succeeded (not quality).
- Asset is public; keep license and attribution. Existing user scene remains unpublished.

## E0020 — Cozy Kitchen real benchmark and ROI post-analysis (2026-11-12)
- Run [43287450449](https://github.com/mxlzz/ACD/actions/runs/43287450449) success; 320×240, 24 spp ×3, reference 512 spp ×2. Details in [E0020](docs/experiments/E0020.md).
- Crops and ROI selection from references only: [benchmarks/results/cozy_e0020](benchmarks/results/cozy_e0020). Original EXRs remain Actions artifacts for 7 days; key numbers and previews permanently tracked.
- Interpretation restricted by finite-spp reference disagreement and no convergence proof; no denoiser improvement established.

## E0022 — Held-out nighttime architecture source incorporated (2026-11-12)
- Terraced Houses, Yunus Emre Karaman, MIT source pinned upstream commit 36c46d3; source 3,044,256 B and SHA256 in benchmarks/scenes/terraced_houses.audit.json. Renderer Blender5.0.1 Cycles 192px 4spp passed. Original source unmodified.
- Scene assigned held-out generalization benchmark: do not tune denoiser against it. No quality comparison performed by this smoke. The user's project remains unpublished.

## E0021 — Cozy Kitchen higher-reference quality archived (2026-11-12)
- Blender5.0.1 [run 43289852695](https://github.com/mxlzz/ACD/actions/runs/43289852695), 512x482, 24spp x3 and refs1024spp x2; refs spread/raw-error 13.53%, vs E0020 24.51%. OIDN compositor/Standard RMSE mean 0.0833928, High 0.0860779, Super 0.0971167; native best gradients. Two-ref + 3-seed detail table and crops [E0021](docs/experiments/E0021.md).
- Reused EXR original, no rerender; 3 reference-only ROIs and previews under benchmarks/results/cozy_e0021, derivatives of Nicole Morena Cozy Kitchen CC BY-SA. No perceputal superiority claim.

## E0023 — Exterior nocturno, discrepancia entre errores, diagnóstico archivado
- Run 43291659387 valida 320×240 24spp x3 y 512spp refs x2, nativo OIDN RMSE más alto que Raw pero MAE y gradiente menores. Informe E0023 y comparativas: docs/experiments/E0023.md, benchmarks/results/terraced_e0023. EXR fuente conservados temporalmente en Actions.
- Se midió concentración SSE peor 1% y errores por AOV emission/glossy sobre primera seed, contra mismas refs sin alterar algoritmos. Esta escena fue observada: requiere otra escena final ciega para evaluar un candidato entrenado.

## E0028 — Low-Poly Island third-scene source validated and versioned
- Official MIT source emrelab/blender-projects at immutable 36c46d3; SHA from benchmarks/scenes/low_poly_island.audit.json. Blender5 Cycles smoke 4spp passed, no assets missing. The previously examined Terraced scene shares its author; test is a new scene but NOT independent artist/style. Results quality still pending.

## E0030 — Low-Poly Island E0029 visual crops from saved EXRs
- Reference-selected diagnostic ROIs, same display curve and unmodified E0027 Emission50/100 parameters, derived MIT eight-panel crops in benchmarks/results/island_e0030/. No rerender, no claim of perceptual quality until inspected.

## E0034 result archive (2026-11-13)

- Recovered E0033 run 43416607737 exact JSON and existing EXR, generated no new Cycles renders. Fixed gitignore staging failure; numerical JSON and tracked report staged explicitly. Published 1:1 full image and disjoint reference-selected ROI PNG in benchmarks/results/hall_e0034/README.md; kept original .blend out. Frozen Emission50 worse global RMSE/border than OIDN in Modern Hall; no integration.

## E0035 completed — B0a contracts verified (2026-11-13)

## E0035 — Blender 5.2.4 LTS vs 5.3.0: API + mismo input (2026-11-13)

- [Successful workflow 43480823352](https://github.com/mxlzz/ACD/actions/runs/43480823352), initial EGL runtime failure in [43480476666](https://github.com/mxlzz/ACD/actions/runs/43480476666) corrected by installing libegl1. Both official Blender archives passed published SHA256.
- Procedural detail_target, 128x96, 16 spp noisy seed 539, 64 spp reference seed 8819. This is an API/smoke contract; reference NOT converged and no visual superiority claim.
- 5.2.4 (build cd5dc428cce1): Raw/AOV delta 0.0, Standard/OIDN delta 0.0.
- 5.3.0 (build 02f0899d78e3): Raw/AOV delta 0.0, Standard/OIDN delta 0.0.
- Cross-version **Raw beauty** RMSE 0.006166062714630608. Denoising Albedo RMSE 0.00032205058212830514, Denoising Normal RMSE 0.0004913281671895542. Changes across Blender versions combine renderer/guide/backend effects; must use fixed EXR to isolate denoiser.
- Cycles-internal denoising is configured/available in API, but **not measured**; 5.3.0 reports compositor API deprecation slated for Blender6.0; add compatibility planning, not algorithm tuning.
- [Exact JSON](E0035_RESULTS.json). Original EXRs/actions artifacts expire after 14 days. Addon stable untouched.

## E0036 — Cycles internal vs compositor OIDN actual (2026-11-13)

# E0036 — Denoising interno de Cycles vs nodo OIDN de compositor (mismo render)

- [Workflow E0036](https://github.com/mxlzz/ACD/actions/workflows/acd-e0036-cycles-internal.yml), Blender 5.2.4 LTS, scene procedural detail_target 128×96, 16spp, seed539, GPU none. Source: same RenderLayer Noisy Image, Image denoised and Denoising Albedo/Normal. Compositor OIDN Accurate/High/HDR. No reference converged or claim of quality winner.
- RMSE RGB entre salida interna y de compositor: 1.4466098094000755e-07; delta máximo 1.9073486328125e-06. Coincidencia exacta: False.
- Raw→OIDN integrado RMSE 0.2544771700358048; Raw→OIDN compositor 0.25447716631777373. Estos números miden diferencia entre salidas, NO si una es mejor.
- [JSON exacto](E0036_RESULTS.json). EXR/AOV en artifacts del run solo 14 días. Próxima puerta: misma entrada de forma verificable frente a OIDN standalone y controles de guías; luego referencias convergentes antes de ranking.
