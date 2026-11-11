# M2 — External .blend scene benchmark and regional analysis

**Project plan:** [docs/ROADMAP.md](docs/ROADMAP.md). **Scientific foundations and hypotheses:** [docs/research_foundations.md](docs/research_foundations.md). These are reference documents; the status below records actual implementation and evidence.

Updated: 2026-11-11. Branch dev/acd-m2-real-scenes-regions, draft PR #4 stacked on M1 PR #3.

## M3.6 — Operadores sin OIDN: prueba real aprobada (2026-11-11)

- [Run 43106813982](https://github.com/mxlzz/ACD/actions/runs/43106813982) **success**, [artifact 13893069815](https://github.com/mxlzz/ACD/actions/runs/43106813982/artifacts/13893069815). Entradas iguales (`source_inputs_equal=true`).
- **Resultados aislados 3.6 vs 5:** ADD, MULTIPLY, ADD con emisión HDR idénticos píxel a píxel en RGB y alfa (RMSE=0). SepRGBA/CombRGBA frente a SetAlpha devuelve RGB idéntico, alfa RMSE=3.84746e-08 y máximo absoluto 5.96046e-08.
- **Inferencia:** estas operaciones y el mapeo de alfa probado no explican las diferencias mucho mayores en High/Super (RGB RMSE 0.065–0.068 y alfa ~0.00387). Esto acota causas hacia OIDN/parametrización/otras ramas, pero no las identifica de manera exhaustiva.
- **Siguiente:** aislar nodos OIDN individuales bajo exactamente las mismas entradas (Fast, Accurate guiado, emisión Accurate sin guías, alfa Accurate guiado).

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
