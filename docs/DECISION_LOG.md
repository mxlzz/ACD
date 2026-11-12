# Bitácora de decisiones y control de rumbo

Regla: una entrada por cambio/commit posterior a la instauración del protocolo. No reescribir entradas anteriores; añadir una nueva con decisión y resultado.

## 2026-11-11 — Institución de control de rumbo (M3 / Issue #7)

- **Objetivo original revisado:** reproducir SID público fielmente en Blender 5.x, y usarlo como baseline antes de intentar mejoras.
- **Motivo:** la auditoría `docs/sid_parity_gap.md` mostró diferencias concretas entre el SID histórico y el prototipo (prefiltrado, emisión, alfa, entradas), mientras que M1/M2 habían avanzado con un algoritmo inspirado en SID sin equivalencia verificada.
- **Decisión:** M3 tiene prioridad absoluta. M2 y el laboratorio permanecen como herramientas; M4/adaptativo en espera. Cada cambio tendrá trazabilidad en ROADMAP, STATUS y esta bitácora.
- **Cambio implementado:** protocolo explícito, comprobador de coherencia documental de commits y tests del comprobador; integración a CI Python.
- **Validación:** pruebas del verificador incorporadas. El resultado real de GitHub Actions debe leerse en el run correspondiente; no se declara aprobado anticipadamente.
- **Limitación:** la CI detecta omisiones documentales, no evalúa por sí sola la calidad del razonamiento o la fidelidad al código SID.
- **Desvío de ruta:** ninguno; la modificación hace exigible la prioridad M3 establecida.
- **Próximo paso:** especificación ejecutable de grafos/sockets de SID público (Standard/High/Super y opciones) para iniciar el modo SID Reference.


## 2026-11-11 — M3.1, especificación de paridad SID antes de escribir código

- **Hito revisado:** M3 / Issue #7. Conforme al protocolo, no se inició optimización de ACD.
- **Decisión:** congelar comportamiento de SID público v4.0 en `docs/M3_SID_REFERENCE_SPEC.md`.
- **Hechos auditados:** Standard usa prefilter FAST; High/Super ACCURATE; emisión sin guías, Alfa con denoiser independiente; Volume sin guías. MixRGB no cambia a factor 0.5: el default histórico de mezcla ADD/MULTIPLY era 1.0 (fuente oficial Blender).
- **Método de implementación:** adaptador original de comportamiento equivalente, independiente de un fork/copia literal GPL. Se mantendrán referencias y atribución de inspiración.
- **Verificación:** lectura directa de código upstream y documentación Blender, sin ejecutar aún la referencia. CI para este commit pendiente.
- **Desviación:** ninguna.
- **Siguiente acción:** desarrollar grupo Blender 5 y pruebas para propiedades de nodos, alfa, emisión y renders.


## 2026-11-11 — M3.2, primer constructor independiente SID Reference

- **Ruta comprobada:** M3 / Issue #7, implementación de baseline SID público; no contiene fusión adaptativa ni modificación del addon estable.
- **Decisión:** crear un módulo Blender 5 aislado que genere Standard/High/Super con las políticas documentadas de guía, emisión, volumen, entorno y alfa.
- **Compatibilidad:** factor MixRGB=1 explícito; Standard FAST; High/Super ACCURATE; filtro final y alfa separados; emisión sin guías. Quality/HDR en Blender 5 quedan como decisiones del adaptador y no se presentan como idénticas al backend histórico.
- **Validación incorporada:** tests de topología Blender 5, parámetros y render 5.0.1; 5.3 construcción únicamente si EGL no está disponible.
- **Evidencia real:** resultados GitHub Actions pendientes. No se declara equivalencia con SID real.
- **Desvío:** ninguno. Continúa la separación entre los prototipos y la referencia.
- **Siguiente paso:** evaluar CI, corregir casos fallidos, comenzar paridad entre versiones con mismo EXR.


## 2026-11-11 — M3.2, corrección previa de contrato opcional

- **Ruta revisada:** M3, prueba de nodos para variantes optativas del SID público.
- **Hallazgo:** al desactivar transmisión/emisión y activar volumen, la cuenta esperada de denoisers es 5 High y 8 Super, no 6/9 como la variante predeterminada.
- **Acción:** corregir aserciones; fuente del recuento: número de filtros del grafo congelado, no una suposición del runner.
- **Estado:** tests de Blender pendientes de CI; no declarar aprobados hasta observar el workflow.
- **Próximo:** validar constructor real y reparar incompatibilidades documentadas.


## 2026-11-11 — M3.3, comparar SID Reference y ACD sin sesgos de ruido

- **Objetivo:** compatibilidad funcional del port SID y estudio de diferencias respecto de ACD experimental bajo la misma entrada.
- **Cambio:** se agregan variantes SID4_* opcionales a tests/blender_compare_smoke.py, al lector de batches y a CI Blender 5.0.1. No hay cambios en el addon ACD de uso real.
- **Control:** RenderLayer compartido entre todas las ramas de un mismo render; sin aumentar muestras ni usar referencias para seleccionar parámetros.
- **Resultado actual:** código y tests añadidos; CI física de Blender aún pendiente. La referencia 64 spp de este smoke es para comprobar ejecución, no validar calidad.
- **Ruta:** M3 / Issue #7 respetado, sin avanzar a filtros adaptativos.
- **Siguiente:** revisar fallas de CI, corregir y medir contra la implementación upstream en Blender 3.6.


## 2026-11-11 — M3.4, comparar grafos directamente con el SID histórico ejecutado

- **Ruta verificada:** M3 / Issue #7; la comparación frente al origen sigue siendo el requisito prioritario.
- **Método:** clonar temporalmente SID GPL 4.0 a un runner, en el commit fijado; cargar únicamente funciones de grafos en Blender 3.6.23, sin importar herramientas UI ni copiar fuente al repositorio.
- **Invariantes:** OIDN por familia y postfiltro, MixRGB Fac, prefilter Fast/Accurate, emisión sin guías y alfa filtrada con guías. Una diferencia detiene la CI.
- **Validación añadida:** tests sintéticos Python del comparador y workflow con manifests JSON de ambos Blenders. **CI real en cola**, no verificada.
- **Límite:** igualdad estructural no prueba mismo motor OIDN ni igualdad de píxeles. La rama estable permanece intacta.
- **Siguiente:** estudiar comparación real del SID original y SID Reference sobre EXR comunes y corregir cualquier desigualdad medida.


## 2026-11-11 — M3.4, corrección de serialización de documentos/workflow

- **Alineación:** M3 / Issue #7; cambio de infraestructura de pruebas de fuente histórica.
- **Hallazgo:** el generador del archivo de GitHub Actions dejó barras inversas antes de expresiones `${{ runner.temp }}`, por lo que los paths dinámicos no se resolverían correctamente. La especificación también tenía backticks escapados.
- **Acción:** retirar los escapes literales, sin cambiar el test ni el algoritmo.
- **Validación:** inspección de contenido final por API de GitHub; resultado real del workflow aún pendiente.
- **Siguiente:** ejecutar Blender 3.6/5.0 y cotejar grafos.


## 2026-11-11 — M3.4, corregir contexto de variables a nivel job

- **Ruta:** M3 / Issue #7, prueba de grafos del SID histórico. No cambia el denoiser.
- **Evidencia observada:** runs 43098302573 y 43098385953 terminaron con fallo y **cero jobs**, antes de ejecutar Blender.
- **Causa de infraestructura:** el workflow situaba `runner.temp` en valores `jobs.<job>.env`; esa referencia no es válida al evaluar ese bloque.
- **Acción:** emplear rutas constantes `/tmp/acd_sid_upstream`, `/tmp/acd_sid_legacy_contract.json` y `/tmp/acd_sid_port_contract.json` en job.env.
- **Validación:** configuración corregida; nuevos jobs / resultados pendientes.
- **Desviación:** ninguna. Continuar M3 sin extraer conclusiones de paridad hasta la verificación real.


## 2026-11-11 — M3, bloqueo externo de validación en GitHub Actions

- **Objetivo reconfirmado:** M3 / Issue #7, reproducir SID público antes de optimizar; roadmap y port permanecen orientados a esa prioridad.
- **Verificado:** desde las 20:27 UTC, al menos 19 runs recientes en estado `queued`, sin ningún job creado (API `jobs.total_count=0`), incluyendo quality gate y Blender smoke ya existentes. Los dos intentos previos del nuevo workflow con sintaxis inválida fueron reparados; esto no explica que los workflows existentes tampoco inicien.
- **Acción:** abrir Issue #8 con runs y pasos de inspección para usuario; no fusionar ni atribuir paridad. Se corrigió un bug en la condición de conteo Standard de `scripts/compare_sid_contracts.py` y se agregó test de regresión.
- **Incertidumbre:** causa real de la cola desconocida. No inferir cuota, billing ni runner incapaz sin mensaje explícito de GitHub.
- **Decisión de prioridad:** no avanzar a optimizaciones, UI de distribución ni renders de calidad cuando la verificación básica del port aún está bloqueada.
- **Próximo paso:** inspeccionar Actions/Settings/avisos, destrabar CI, ejecutar los tests y analizar los manifests. Ese es el primer punto que requiere intervención del propietario del repo.


## 2026-11-11 — M3.4, reparar artifacts y registrar CI física recuperada

- **Alineación:** M3 / Issue #7. La reproducibilidad del cotejo upstream y del port es prerrequisito de paridad, sin introducir un denoiser nuevo.
- **Evidencia anterior:** runs 43098851163 (quality gate) y 43098851162 (Blender 5 smoke) `success`; run 43098851161 ejecutó realmente el SID original en Blender 3.6.23 y el port en 5.0.1 y devolvió `passed=true` para un contrato estructural limitado.
- **Defecto observado:** el step de artifact en el run 43098851161 informó `No files were found`: los probes escriben en `/tmp/acd_sid_{legacy,port}_contract.json`, el comparador escribe `/tmp/sid_contract_comparison.json`, pero el upload usaba `runner.temp`. Un run verde sin evidencia descargable incumple trazabilidad.
- **Decisión/cambio:** corregir exactamente los tres paths de `upload-artifact` y cambiar `if-no-files-found` a `error`. No alterar el grafo ni afirmar paridad de imágenes.
- **Criterio de aceptación:** una nueva ejecución de paridad debe terminar en verde **y** publicar un artifact legible con los tres JSON. **Resultado posterior al commit todavía no verificado.**
- **Limitaciones:** queda sin demostrar equivalencia OIDN, tratamiento alfa y salida HDR entre Blender 3.6 y 5.0. Los runs previos sin jobs no identifican por sí mismos la causa de la cola.
- **Siguiente:** validar artifacts, después diseñar prueba comparativa numérica del SID público y el port con la misma entrada EXR.


## 2026-11-11 — M3.4, comprobación posterior del artifact y cierre del bloqueo operativo

- **Hito revisado:** M3 / Issue #7. Mantener paridad SID pública antes de cualquier mejora experimental.
- **Evidencia posterior, mismo código de comparación:** run 43101708644 `success`, informe `passed=true` y `errors=[]`. El upload registró tres archivos y publicó artifact 13890459701; run 43101708666 comprobó tests Python y trazabilidad; run 43101708862 finalizó `success` en Blender 5.0.1 y 5.3.
- **Resultado:** la corrección de rutas en e529c6b está verificada físicamente. Se preservan contratos y artifacts, con retención temporal; la evidencia de CI en logs permanece referenciada por identificador.
- **Limitaciones:** las discrepancias numéricas Blender 3.6/5.0 siguen sin analizar; la causa de las colas sin jobs antiguos es desconocida. Éxito del workflow no implica SID idéntico ni superior.
- **Decisión:** cerrar el bloqueo operativo de Issue #8, mantener abierto M3 / Issue #7 y PR #4 como draft. No fusionar.
- **Próximo experimento M3.5:** input EXR idéntico + hashes y ambos motores, probar Standard primero y High/Super después; comparar HDR, alfa y error por región con versiones del backend consignadas.


## 2026-11-11 — M3.5, primer experimento de paridad numérica real (Standard)

- **Hito verificado:** M3 / Issue #7. Se mantiene separada la versión comercial no pública; comparar upstream GPL histórico con adaptador sin copiar fuentes.
- **Decisión:** congelar una única batería sintética EXR con hashes, ejecutar Standard en Blender 3.6 y 5.0 con misma entrada y registrar passthrough RGB/A. Este control es requisito para atribuir diferencias a la cadena de denoising.
- **Implementación:** fixture Python/OpenEXR reproducible, driver compositor cross-version, comparación numérica con ROI HDR/transparencia y artefactos EXR/NPZ/JSON. Workflow aislado bajo PR trigger y despacho manual, sin nuevos filtros de ACD.
- **Aceptación:** los dos Blenders cargan SHA idénticos; el passthrough cumple tolerancia 0.001; outputs RGBA finitos, mapas firmados y manifiestos exportados. El informe cuantifica diferencias, no exige igualdad píxel ni inventa backend OIDN.
- **Estado al commit:** código candidato creado; **Actions aún no ejecutada/verificada**. Los resultados serán anexados en un nuevo registro; error de ejecución no será reinterpretado como disparidad numérica.
- **Limitación:** fixture sintético 96×64 y Standard. No evalúa High/Super ni escena real, calidad perceptual ni rendimiento.
- **Siguiente:** ejecutar CI y analizar resultados del upstream real; ampliar gradualmente a High/Super cuando el control de entrada pase.


## 2026-11-11 — M3.5, controles separados para todas las entradas

- **Hallazgo en auditoría previa a CI:** verificar solo la imagen ruidosa no verifica el albedo/normal; y exigir identidad entre EXR almacenado y passthrough interno puede señalar como fallo una transformación de premultiplicación legítima (idéntica entre ambas versiones).
- **Decisión:** archivar tres pares de outputs passthrough (noisy, albedo, normal); validar igualdad entre versiones (máx absoluto 0.001), reportar también diferencia frente a archivo original sin imponerles el mismo umbral.
- **Defecto técnico asociado:** el campo `pixels` en métricas globales usaba altura y no ancho×altura. Corregido y cubierto por test.
- **Estado:** cambio anterior a la ejecución observada del piloto; resultado numérico aún pendiente y no se declara por anticipado. Se mantiene el mismo fixture congelado y ninguna modificación del port de producción.
- **Siguiente:** ejecutar pipeline real, revisar tres controles y recién entonces interpretar diferencias HDR, RGB y alfa de SID.


## 2026-11-11 — M3.5, corregir media type del compositor Blender 5

- **Evidencia real:** run https://github.com/mxlzz/ACD/actions/runs/43104453238: generación de 3 EXR y tests Python OK; upstream Blender 3.6 produjo outputs. Blender 5 falló en `CompositorNodeOutputFile` con `TypeError: enum "OPEN_EXR" not found in ('OPEN_EXR_MULTILAYER')`.
- **Causa localizada:** se intentó configurar file_format OPEN_EXR manteniendo media_type MULTI_LAYER_IMAGE por defecto. El pipeline existente del proyecto configura media_type IMAGE primero.
- **Cambio:** fijar `node.format.media_type="IMAGE"` únicamente en el branch Blender 5 antes del formato EXR; no tocar el grafo SID ni la tolerancia de comparación.
- **Aceptación:** rerun produce RGBA EXR de raw, albedo, normal y SID del port y reporte comparativo. **Resultado pendiente posterior al commit.**
- **Siguiente:** revisar el próximo paso fallido, si lo hubiera, y nunca dar por validada paridad numérica hasta completar datos y controles.

## 2026-11-11 — M3.5 Standard medido; High/Super integrado como candidato

- **Prueba real:** run 43104673773 y artifact 13893222574. Noisy, normal y albedo pasaron con identidad exacta entre Blender 3.6/5.0 y EXR original.
- **Resultados numéricos:** Standard RGB RMSE 0.03285426, MAE 0.01902902, máximo 0.46119857; ROI HDR RMSE 0.04103480; alfa idéntica (RMSE 0). Son diferencias de salidas entre dos versiones/OIDN, no error respecto de convergencia.
- **Decisión:** extender M3.5 a los grafos High y Super reales, con 15 AOV/guías congelados y verificación de passthrough por cada buffer; medir emisiones y alfa.
- **Cambio:** scripts de fixture, driver y comparador, unit tests, workflow aislado que clona GPL original solo en runner. No modificar el addon estable ni afirmar superioridad.
- **Estado del nuevo pipeline:** código candidato; pruebas reales High/Super pendientes. Siguiente etapa: verificar CI, corregir las incompatibilidades del harness sobre evidencia concreta y analizar diferencias por canal y región.


## 2026-11-11 — M3.5 High/Super, corregir ejecución de módulos Python

- **Resultado real:** https://github.com/mxlzz/ACD/actions/runs/43106081661: unit test del generador `1 passed`, pero `python scripts/sid_highsuper_numeric_fixture.py` falló en `from scripts.sid_standard_numeric_fixture import make_arrays` (ModuleNotFoundError), porque la ejecución por ruta fija `sys.path[0]` en `scripts`.
- **Decisión/cambio:** invocar generador y comparador como módulos Python mediante `python -m scripts.sid_highsuper_numeric_fixture` y `python -m scripts.compare_sid_highsuper_numeric`. No modificar algoritmos, datos, importadores Blender ni alterar resultados inexistentes.
- **Estado:** nueva CI no ejecutada al momento de este commit. Seguir validando hasta que se creen los pares High/Super y queden registrados los errores RGBA/HDR.


## 2026-11-11 — M3.5 High/Super medidos y priorizar experimento M3.6

- **Evidencia real:** https://github.com/mxlzz/ACD/actions/runs/43106273482 `success`; artifact https://github.com/mxlzz/ACD/actions/runs/43106273482/artifacts/13894002202. Quince AOV con SHA y controles de passthrough válidos en ambos Blenders.
- **Diferencias observadas:** High RGB RMSE=0.06531013, max=2.04866791; Super RGB RMSE=0.06788146, max=1.89871454; región emisiva High RMSE=0.22305557, Super=0.23223786. Alfa RMSE ~0.0038727 para ambos.
- **Conclusión acotada:** no es identidad de imágenes. Los controles descartan drift aparente de entrada, pero no diferencian cambios OIDN de semántica de operadores RGB/alfa. No alterar aún SID Reference ni anunciar un bug concreto en él.
- **Experimento siguiente M3.6:** construir graph mínimo sin denoiser en Blender3.6 (MixRGB Add/Multiply, Sep/Comb RGBA) y Blender5.0 (ShaderNodeMix Add/Multiply, SetAlpha), misma entrada EXR/Alpha; exportar salidas y reportar diferencias por canal.
- **Estado de M3.6:** candidato agregado, CI aún pendiente de inspección; no se afirma resultado anticipado.
- **Protección:** no tocar addon estable, no incorporar código GPL ni adelantar M4.


## 2026-11-11 — M3.6, descartar operaciones de mezcla como explicación principal y preparar M3.7

- **Evidencia:** https://github.com/mxlzz/ACD/actions/runs/43106813982 `success`; artifact https://github.com/mxlzz/ACD/actions/runs/43106813982/artifacts/13893069815.
- **Medido sin OIDN:** MixRGB ADD/MULTIPLY/HDR vs ShaderNodeMix producen exactamente mismos píxeles. Sep/CombRGBA vs SetAlpha entrega RGB igual y alfa con RMSE 3.84746e-08 / máximo 5.96046e-08. Los inputs passthrough también coinciden.
- **Interpretación limitada:** estos nodos aislados no explican las diferencias de High/Super (alfa RMSE ~0.0038727, RGB/HDR más altos). No demuestra que todas las variantes de grafo sean iguales; OIDN/parametrización sigue sin aislarse.
- **Decisión:** nuevo experimento M3.7 sobre OIDN individual, manteniendo entradas y guías congeladas y comparando Fast/Accurate, emisión sin guía, alfa guiada y difusión guiada. No aplicar correcciones a OIDN basadas solo en una métrica interversión.
- **Estado:** scripts/workflow candidatos para Blender3.6 y 5.0; CI aún no ejecutada al commit. Revisión posterior exigida antes de nuevas hipótesis.


## 2026-11-11 — M3.7, medición aislada de OIDN y próximo gate de versiones

- **Resultado ejecutado:** [run 43107260820](https://github.com/mxlzz/ACD/actions/runs/43107260820) `success` con [artifact 13895310157](https://github.com/mxlzz/ACD/actions/runs/43107260820/artifacts/13895310157). Passthrough de entradas válido; ambos Blenders procesaron los mismos EXR, sin nodos de mezcla SID.
- **Valores medidos de RGB RMSE entre versiones:** Fast guiado 0.0328542782, Accurate guiado 0.0306021047, emisión Accurate sin guías 0.0619173071 (ROI emisiva 0.2157095979), imagen alfa Accurate guiada 0.0061814454, Diffuse Direct Accurate guiado 0.0042534052.
- **Correspondencia:** Fast aislado coincide dentro del redondeo con el Standard integral RMSE 0.0328542603. La emisión aislada produce un error de magnitud similar al observado en el ROI emisivo de High/Super; por tanto tiene prioridad como mecanismo a investigar. La contribución cuantitativa de cada filtro al resultado final aún no está calculada.
- **Criterio de interpretación:** los canales A de los EXR OIDN aislados tienen RMSE=0, mientras el RGB de alfa como imagen filtrada sí cambia. La salida High/Super combina dicho RGB como alfa final. No inferir equivalencia de alfa solo por la igualdad del canal A en este experimento.
- **Decisión de desarrollo:** no tocar `addon/sid_reference.py` ni introducir optimizaciones. M3.8 debe cotejar versiones OIDN y diferencias de `Quality/HDR/Prefilter` con ablaciones congeladas antes de corregir el port; las escenas arquitectónicas verdaderas y referencias convergidas siguen siendo el siguiente nivel de evidencia.
- **Estado:** se registran datos de M3.7 comprobados en CI, sin paridad de píxeles, sin comparación con SID comercial y sin superioridad demostrada.


## 2026-11-11 — M3.8, aislar parámetros OIDN antes de modificar el addon

- **Motivación empírica:** M3.6 descartó diferencias relevantes de ADD/MULTIPLY/SetAlpha aisladas; M3.7 detectó diferencias numéricas ya en filtros OIDN individuales.
- **Decisión:** ejecutar la misma entrada EXR en Blender 3.6 con HDR true/false (y prefilter de SID), y en Blender 5 con Quality High/Balanced/Fast × HDR true/false, manteniendo prefilter/guías. Examinar versiones de build y bibliotecas OIDN distribuidas, sin inventar una versión efectiva del backend.
- **Implementación candidata:** drivers `tests/blender_sid_oidn_matrix.py`, comparador `scripts/compare_sid_oidn_matrix.py`, contrato de regresión `tests/test_sid_oidn_matrix.py`, workflow `.github/workflows/sid-oidn-parameter-matrix.yml`.
- **Criterio:** validar hashes y raw passthrough, 8 legacy + 24 port outputs, métricas y mapas firmados con distinciones inter/intraversión. No minimizar RMSE respecto al histórico como si fuera un ground truth convergido.
- **Estado:** CI aún sin ejecutar al commit. No alterar `addon/sid_reference.py` ni el addon estable hasta establecer causa y mejorar resultados sobre escenas reales.


## 2026-11-11 — M3.8, corregir sintaxis YAML previa a creación de jobs

- **Observado:** run 43111531413 `failure`, `jobs=[]`, workflow identificado por ruta. Inspección de fuente encontró un paso con `- name: Archive matrix: EXRs, ...` (dos puntos no citados dentro del scalar).
- **Corrección:** entrecomillar completamente el nombre del paso, dejando toda la lógica experimental intacta.
- **Estado:** la próxima ejecución definirá si queda corregida la validación YAML y si corren las pruebas; no se presume validación de OIDN.


## 2026-11-11 — M3.8 medido y M3.9 preparado con escena Cycles de referencia

- **Hecho verificado:** run 43111684409 `success`, 8 legacy+24 port. OIDN Blender5.0.1 2.3.3 instalado; origen legacy no resuelto. HDR off cambia mucho el resultado y no es una alternativa justificable por reducción de diferencia histórica.
- **Cambio en banco:** añadir `NATIVE_COMP_OIDN` (CompositorNodeDenoise Accurate/High/HDR) como baseline individual, identificado expresamente como *nodo compositor* y no denoiser interno de Cycles; incluirlo en comparador y prueba.
- **M3.9 candidato:** workflow en matriz glass_lobby (procedimental) y Classroom CC0 (escena externa real), low24 spp (2 seeds) y dos ref384 spp, 160×120. Reportar RMSE/MAE/luminancia log, incertidumbre de referencia y estabilidad entre semillas, sin concluir convergencia.
- **Estado:** CI posterior al commit pendiente; `addon/sid_reference.py` y addon estable no se modifican; no fusionar PR #4 hasta ver resultados.


## 2026-11-11 — M3.9, primera corrida real; bloquear comparaciones estadísticas inválidas

- **Evidencia:** run 43112553045 `success` para glass_lobby y Classroom CC0. Artifacts 13897341205 y 13896727821.
- **Glass Lobby:** Raw RMSE 0.32117, ACD Standard y OIDN compositor RMSE 0.14789017, ACD/SID4 High ~0.17137 y Super ~0.18369. Aunque rank por dos referencias coincide, `reference_disagreement_over_raw_error=0.31496` activa alerta de spread. No certificar ranking.
- **Classroom:** noisy seeds 539/911 casi idénticas (RMSE ~8.43e-7) y referencias separadas RMSE ~1.65e-6. `input_diversity_heuristic_passed=false` y `almost_identical_reference_images=true`. **Rechazar inferencias multisemilla** y conservar el run como evidencia de problema de muestreo no diagnosticado.
- **Cambio de evaluación:** incluir flags explícitos de validez y métricas directas entre candidatos; evita confundir igualdad de errores respecto de referencia con identidad de píxeles.
- **Diseño segunda corrida:** glass_lobby + interior_emissive, 1024 spp ×2 refs, 24 spp ×3 noisy seeds, comparar también `STANDARD_emission_preserved`. No modificar denoiser ni promover ninguna variante con los datos actuales.
- **Estado:** nuevo workflow por verificar y debilidad de Classroom sin causa comprobada.


## 2026-11-11 — M3.9 segunda corrida verificada: baseline nativo no superado, exigir nuevo escenario

- **Prueba real:** [run 43113414513](https://github.com/mxlzz/ACD/actions/runs/43113414513) `success`, artifacts 13896374534 Glass y 13897536701 interior emisivo. Tres noisy seeds con diversidad verificada y dos referencias 1024 spp no idénticas; convergencia todavía no demostrada.
- **Resultado directo:** promedios RMSE Glass Raw 0.31338931, Standard/Compositor OIDN 0.14833401, High 0.17022242 y Super 0.17611973. Emisivo Raw 0.24915133, Standard/OIDN 0.08236044, High 0.08670461 y Super 0.09241571. SID4 Reference High/Super quedan peor que native en ambos. Preservación de emisión emisiva 0.08267392 (peor promedio +~0.38 % aunque gana 1/3 semillas). No hay evidencia de mejora universal.
- **Hallazgo del proceso:** E0007 ya contenía evidencia de la anomalía de semillas de Classroom; fue improcedente repetir Classroom como supuesto benchmark multisemilla en primer M3.9. Se documenta la redundancia en E0013 para prevenir nuevos experimentos sin revisar precedentes.
- **Identificación fuente:** en código oficial Blender tag v3.6.23, build_environment/cmake/versions.cmake declara OIDN 1.4.3; binario Blender5.0.1 del runner contiene OIDN 2.3.3. Distinguir dependencia fuente de biblioteca runtime y no afirmar causalidad exclusiva de versiones.
- **Decisión:** no cambiar addon SID4 Reference ni estable, ni promover Quality/HDR menos fieles a radiancia por proximidad histórica. Archivar números fuera de artifacts temporales (E0013) y preparar un benchmark profesional con `.blend` aportado/autorizado; el runner `scripts/run_scene_benchmark.py` ya está implementado. PR #4 permanece draft.
- **Criterio próximo:** distintas escenas reales, múltiples seeds verificadas, 2 o más referencias razonables y validación de detalle, glass, glossy, emisión HDR; hipótesis y comparación contra nativo predefinidas.


## 2026-11-12 — F1 ACD V2, reorientación hacia OIDN y fidelidad de detalle

- **Motivo, no hipótesis:** E0013 compara SID4 port, ACD y nodo nativo OIDN en dos escenas pequeñas y encuentra equivalencia Standard/OIDN en RMSE, sin ventaja High/Super; no resuelve la conservación visual de textura ni representa SID5 comercial. No procede mantener la paridad SID como prioridad absoluta.
- **Decisión:** OIDN compositor nativo Blender5.0.1 es baseline inmediato; OIDN 2.5.1 se estudia independientemente; SID4 es histórico, SID5 un comparador no reproducido, no se asume calidad superior.
- **Cambio de rumbo registrado:** F1–F6 en ACD_V2_PLAN.md e Issue #9; protocolo anterior M3 reemplazado formalmente con condiciones de validez y trazabilidad conservadas. Auditoría de OIDN v2.5.1 es **lectura de código**, no ejecución, clon o benchmarking.
- **Validación:** repo/branch/issue y commits de documentación; CI de esta revisión pendiente. ACD addon original y SID Reference sin cambios.
- **Próximo:** implementar y probar métricas de gradiente bajo máscara definida solo desde referencia; luego benchmark OIDN standalone con mismos EXR y guías.


## 2026-11-12 — F3, diagnósticos por gradientes de referencia (commit de implementación)

- **Hipótesis:** un RMSE global no distingue bien blur de detalles arquitectónicos. Añadir error de gradiente en bordes relevantes de la *referencia* y diferencia en zonas planas, sin seleccionar máscaras a partir de salidas candidatas.
- **Diseño:** `asinh` por canal conserva signo de valores HDR; máscaras sobre magnitud de diferencias RGB, incluidas texturas isoluminantes; ROI con pares verdaderamente adyacentes. No reemplaza RMSE lineal ni métricas perceptuales ni modelos de error de referencia.
- **Controles:** pruebas sintéticas de blur y oversharpen deben dar error de gradiente positivo; un sharpening puede elevar contraste sin mejorar fidelidad; ruido plano detectado; referencia lisa no genera ranking de bordes. Tests de integración regional añadidos.
- **Estado:** commit de código y pruebas; CI real pendiente. Sin modificaciones de producción ni denoiser.
- **Siguiente:** ejecutar CI, corregir fallos, ampliar a EXR reales y evaluar rankings sobre varios seeds y escenas.


## 2026-11-12 — F2, comparador OIDN oficial con igualdad de EXR/AOV por seed

- **Método:** PFM de 32 bits con transformaciones únicamente de formato endian/orden de filas, binario OIDN 2.5.1 descargado con SHA256 de asset oficial, `--hdr --alb --nrm -q high -d cpu` y verificación numérica de beauty exportado en raw multlayer vs candidato Raw.
- **Corrección de procedencia:** antes solo se guardaba multilayer de seed inicial; ahora cada seed exporta sus propias guías; mezclar guías de seed anterior sería científicamente inválido.
- **Incertidumbre:** el compositor Blender5.0.1 usa prefilter Accurate; CLI `cleanAux` por defecto false, sin garantía de identidad de políticas ni modelos. La comparación 2.3.3/2.5.1 exploratoria no aísla todas las causas.
- **Estado:** código, tests y CI del experimento añadidos, validación real pendiente, sin cambios al addon estable. Siguiente: revisar CI y publicar E0014 con números verificados.


## 2026-11-12 — F2, activar comparador OIDN sobre workflow ya existente

- **Control observado:** quality gate del commit adf4132 pasó: 89 tests, PFM y detail incluidas. No había nuevo run del workflow OIDN creado (aun sin prueba de ejecución).
- **Decisión de orquestación:** añadir descarga SHA fijado y comparador standalone al workflow `sid-architectural-pilot.yml`, que se dispara por modificación del propio workflow y ya ejecuta Blender real. No se alteran algoritmos ni escenas; se obtiene un nuevo método/versión sobre inputs existentes.
- **Resultado:** cambio de workflow registrado; nuevo run pendiente. Si falla descarga o guías incompatibles, documentar causa y corregir sin reinterpretar como defecto de OIDN.
- **Siguiente:** observar run, capturar errores de gradiente/HDR y diferencias raw/PFM, preservar evidencia E0014.


## 2026-11-12 — E0014 verificado, diseñar aislamiento de versión OIDN en CLI

- **Hecho observado:** run 43233365334 dos jobs success, verificado SHA oficial OIDN 2.5.1 y coincidencia raw beauty/AOV/colores PFM bajo 1e-5. Blender5 compositor supera media CLI 2.5.1 en RMSE y error de gradiente sobre Glass/interior emisivo a 192×144, 24 spp, tres seeds; E0014 fija resultados con números por seed y referencias.
- **Limitación causal:** mezcla de diferencias OIDN 2.3.3 vs 2.5.1, parametrización y prefilter Accurate del compositor; no etiquetar 2.5.1 como inferior en general.
- **Siguiente intervención falsable:** mismos PFM, mismas guías y mismos flags en CLI 2.3.3 y 2.5.1; medir contra dos referencias; comprobar repetibilidad 2.5.1. El tag 2.3.3 no publica digest de asset en GitHub REST, así que registrar SHA obtenida sin afirmar pinning externo hasta verificarla.
- **Estado:** código de aislamiento, tests de flags y workflow preparados; aún no observada nueva ejecución ni resultados.


## 2026-11-12 — E0015 aislado + detalle arquitectónico controlado y prior art

- **Verificado:** run 43234478588 completó CLI OIDN v2.3.3/v2.5.1 con mismos inputs y parámetros CPU HDR High. Glass output idéntico bit a bit en PFM para 3 seeds; interior output RMSE mutuo 0.00221–0.00225 y 2.3.3 ligeramente menor RMSE global 3/3. E0015 consigna tabla, controles y límites; no inferir mejor calidad general.
- **F3 hipótesis comprobable preparada:** escena de 52 slats, juntas de alta frecuencia, metal, vidrio y microbump a 320×240 debe permitir verificar si diagnósticos de gradiente capturan pérdidas de detalle frente a referencia, sin premiar más nitidez aparente. No hay resultados todavía ni prueba de referencia convergida.
- **F4 revisión de código upstream:** ProDen 2022 usa SURE+modelo de mezcla y parches OIDN históricos, StatMC/StatER usan fork pbrt-v3, requieren estadísticas por muestra y CUDA/OpenCV; no son filtros postproceso listos para Blender EXR. Documento de prior art y licencias advierte dependencias.
- **Corrección de orquestación:** retirar puente temporal OIDN CLI del workflow M3.9 luego de confirmar que V2 sí dispara; evitar pruebas caras duplicadas. Conservamos workflows históricos independientes.
- **Estado:** cambios nuevos de escena/workflow/documentación por validar en CI y Blender real. Próximo: observar run, depurar y registrar E0016; solo luego diseñar hipótesis algorítmica.


## 2026-11-12 — E0016, detalles visuales y probable variación entre CPU ISA (sin causalidad establecida)

- **Resultados:** job 43235485653, 3 escenas success, detalle-target 320×240. OIDN compositor/ACD Standard RMSE=0.0608849, edge=0.0721193; High RMSE=0.0613499, edge=0.0721533; Super 0.0632406, 0.0726432. Super aumenta ratio contraste 0.723 vs 0.670 y baja MAE pero empeora otros errores. No declarar ganador perceptual sin crops 1:1 y referencia mejor.
- **Limitación de E0015 descubierta:** OIDN 2.3.3 y 2.5.1 binarios mismos SHA entre runs, pero color PFM diferente RMSE 4.96e-5 entre corridas; la superioridad v2.3.3 en una corrida no se repitió como diferencia de versión en corrida posterior. Diferencias de rendimiento sugieren CPUs ISA distintos; v2.4 añadió AMX-FP16 y v2.5 lo optimizó, pero aún falta confirmar CPU efectiva en jobs.
- **Próxima prueba controlada:** PFM matemático de hash fijo en Ubuntu22/24 runners, log CPU/ISA desde `oidnDenoise -v 2`, versión/digest/output, comparación directa sin Blender. El código prueba reproducibilidad de fixture. No usar datos de distinto CPU como comparación absoluta de rendimiento.
- **Aprobación de etapa:** F3 instrumentación y ejecución parcial logradas; F5/F6 en espera por necesidad de casos representativos. 


## 2026-11-12 — E0017 confirma ISA/hardware; workflows pesados manuales; siguiente puerta profesional

- **Evidencia:** run 43237525190, Ubuntu24 AMD EPYC 7763 (AVX2) y Ubuntu22 AMD EPYC 9V45 (AVX-512), PFM de tres passes SHA idénticos entre hosts. Salida 2.3.3==2.5.1 por host, salida entre hosts RMSE 7.4117e-7. ISA afecta valores en pequeño grado. No suficiente para explicar E0015 ~0.0022; falta observar backend AMX y/o causas de variabilidad en inputs entre workers.
- **Conclusión metodológica:** detener comparaciones de rendimiento absoluto entre diferentes VMs; registrar CPU/ISA y entradas SHA en resultados. No afirmar una ganancia por upgrade OIDN. E0017 permanente.
- **Orquestación:** deshabilitar disparo de workflows pesados por sincronizaciones de PR (mantenidos con `workflow_dispatch`); quality automático sigue asegurando contrato y trazabilidad. Evita nueva ejecución del mismo benchmark por cambio documental sin nueva hipótesis.
- **Bloqueo para F5:** aún no hay evidencia profesional de un detalle que OIDN pierda y ACD recupere fielmente; necesitamos escena arquitectónica autorizada o dataset público de calidad. No entrenar, no fork, no mezclar algoritmos sin objetivo verificable. PR experimental permanece draft, addon estable intacto.
- **Estado del commit:** instrucciones y resultados documentados, nueva validación quality pendiente.

## 2026-11-12 — E0018, primera escena arquitectónica real autorizada

- **Hecho:** archivo original 166–167 MB recibido, Zstandard Blender 5.0, hash y DNA del archivo verificados. Escena Cycles FHD, una cámara activa, 5 cámaras, 137 objetos, 86 materiales, 121/122 imágenes empaquetadas; 2 referencias a librerías enlazadas.
- **Decisión:** usar la escena para pruebas privadas, no poner el archivo editable en GitHub público. Posee rutas internas y componentes BlenderKit con licencias no comprobadas individualmente; el usuario consintió uso, no transfirió licencias de terceros. GitHub tiene además límite normal de 100 MB por blob.
- **Validación:** inspección binaria, no Blender real ni render. Se crea workflow para obtener Blender oficial 5.0.1 y continuar inspección local en condiciones reproducibles; CI pendiente.
- **Siguiente:** Blender --factory-startup --disable-autoexec para diagnóstico, smoke Cycles y luego métricas EXR. El addon estable permanece intacto.


## 2026-11-12 — E0019, elegir fixture público compacto de Blender

- **Necesidad:** prueba arquviz representativa y compartible en repo GitHub sin publicar materiales/procedencia dudosa de escena del usuario. La escena de usuario E0018 pesa ~159 MiB y conserva assets de terceros.
- **Selección:** Cozy Kitchen Blender 3.5 por Nicole Morena, 7,685,702 B y CC BY-SA publicado por Blender; no inferir versión particular ni modificar licencia de código de ACD. Mejor comparador arquitectónico que fixtures sin textura.
- **Control antes de publicar:** workflow de importación con URL oficial, tamaño/header, apertura en Blender5 sin autoexec, cámara/materiales/recursos y render funcional. Solo el éxito habilita commit binario con SHA y metadatos, manteniendo trazabilidad ROADMAP/STATUS/DECISION_LOG incluso para commit automático.
- **Estado:** scripts/workflow/docs comprometidos; aún no hay binario ni ejecución que demuestre compatibilidad. No se cambia addon.


## 2026-11-12 — E0019 corrección del validador de archivos .blend

- Hecho: primer run 43285007004 falló en inspección superficial inicial sin llegar a Blender (HTTP 200, payload 7.3 MiB). Un archivo .blend puede estar comprimido y no comenzar en texto plano por la cabecera BLENDER; no asumir formato de byte literal.
- Corrección: mantener control exacto del tamaño oficial y diagnóstico con `file`/primeros bytes, posponer validez estructural al parser oficial Blender5 y smoke. Binario todavía no publicado, nuevo run pendiente.


## 2026-11-12 — E0019 verificación real de Cozy Kitchen y excepción de ignore

- **Observado:** GH Actions 43285264648, Blender5.0.1 Cycles abrió y renderizó (192×192 4 spp) sin recursos de imagen faltantes: 1077 objetos, 1058 mesh, 175 materiales, 2 cámaras, 0 bibliotecas externas. Descarga 7,685,702 bytes. No es benchmark de calidad.
- **Problema de publicación:** la regla general `*.blend` en .gitignore bloqueó `git add`, impidiendo el commit pese a superar el render. No se cambió el archivo ni se publicó.
- **Corrección:** añadir `-f` solo al archivo pequeño específico; no tocar .gitignore ni promover otros artefactos. Reintento verificable, CI posterior al commit.

## 2026-11-12 — E0019 official scene binary incorporated after Blender smoke check

- Decision: adopt a redistributable compact public architectural scene as reproducible benchmark fixture. Source official Blender 3.5 splash by Nicole Morena (CC BY-SA). Binary verified before commit with exact byte size, active camera, packed resources and Cycles CPU 4-spp render. No quality conclusions.
- Control: sha256 and audit recorded, source unchanged; benchmark must preserve artist attribution and ShareAlike terms. User-provided scene stays private.


## 2026-11-12 — E0019 final: scene asset oficial publicado tras validar y seguro ante cambios

- **Validado:** Run 43285518302 completó descarga de fuente oficial y abrió/renderizó en Blender 5.0.1 con --disable-autoexec; sin assets faltantes; se confirmó commit `b63204749a95109eb5e913d6f4a1c4607cb7ddac` y blob `benchmarks/scenes/cozy_kitchen.blend` de 7,685,702 bytes. SHA256 `5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395` coincide con manifest. Licencia obra CC BY-SA y crédito Nicole Morena. No se modificó contenido.
- **Problemas previos cerrados:** validador raw magic incompatible con formatos comprimidos; `.gitignore` correctamente ignora .blend generalmente, excepción de `git add -f` para único fixture. Ambos fallos quedaron trazados. El usuario original E0018 no fue publicado.
- **Seguridad:** reemplazar workflow de importación `contents:write` y push automático por comprobación manual `contents:read` tras su cometido. Agregar test Python de sha/tamaño/licencia/manifest para detectar reemplazo accidental.
- **Calidad:** smoke 4 spp no representa resultado denoised ni contiene referencias; siguiente checkpoint es un benchmark a 512² con dos refs y tres seeds. No se puede afirmar ventaja sobre OIDN por haber conseguido datos de prueba.


## 2026-11-12 — E0020, experimento real Cozy Kitchen sobre EXR idéntico

- **Motivo:** E0019 aporta escena realista pública bajo CC BY-SA de 7.33 MiB, verificada funcionalmente con Blender5.0.1. Necesidad F3: evidenciar si métodos ACD preservan detalle verdadero frente a baseline OIDN, en escena materialmente más compleja.
- **Método predefinido:** 320×240, 24 spp ×3 seeds, 512 spp ×2 refs, misma rama RenderLayer y AOV, métodos Standard/High/Super/NATIVE_COMP_OIDN, HDR RGB RMSE/MAE, gradientes en bordes de referencia y en plano, ROI por AOV; comprobar diversidad y discrepancia de referencia antes de ranking. Calidad no inferida del smoke.
- **Seguridad:** Blender abre escena pública con `--disable-autoexec`; no guardar .blend modificado. Workflow automático solo por su propio fichero, no reiterar al modificar docs. Informe E0020 se genera desde JSON con caveats sin ganador declarado.
- **Estado al commit:** código/workflow/test nuevo; CI y corrida todavía pendientes. Primer número solo cuando el run muestre outputs reales.


## 2026-11-12 — F3, regresión de omisión OIDN nativo en regiones

- **Defecto observado:** `region_cli.compare_regions_from_files` tenía un listado fijo sin `NATIVE_COMP_OIDN`, aunque el benchmark por imagen y por seed sí tenía baseline. Esto impedía diagnosticar el fallo central (detalle OIDN) por AOV/región.
- **Corrección acotada:** incluir `NATIVE_COMP_OIDN` y versiones SID4 cuando sus EXR estén presentes, sin modificar selección/máscaras ni métricas. Test EXR incluye aserción explícita del nativo en ROI. Antes de interpretaciones E0020 se reparará la comparación regional desde los EXR originales, no se ejecutará otro render idéntico.
- **Evidencia:** código y test en este commit; CI pendiente. Sin cambio al addon ni al método de denoising.


## 2026-11-12 — E0020 primera corrida Cozy Kitchen y post-análisis

- **Observación:** GitHub Actions 43287450449 success, 320×240, 24 spp ×3 seeds, 512 spp ×2 refs; raw RMSE 0.25433; Native/Standard 0.1058435; High 0.1072723; Super 0.1286238, todos en promedio y ref1. Referencias RMSE mutuo 0.06105, 24.5% del error del raw; ranking contra refs no exactamente coincidente. No se demuestra convergencia.
- **Decisión:** no comenzar mejora algorítmica. Reutilizar EXR para controlar regiones de detalle seleccionadas solo por referencias, añadir nativo a ROI, medir segunda referencia con mismos candidatos y generar recortes comparables 3x sin interpolación. No rerender, commit posterior de reporte con authoria/licencia CC BY-SA si pasa.
- **Datos permanentes en este commit:** números resumidos/URL, scripts/workflow/tests. Informe y crops finales pendientes hasta ejecución, nunca afirmar que existen antes de confirmarlos.


## 2026-11-12 — E0020 postprocesamiento con EXR reales y corrección de gitignore

- **Evidencia:** el run 43288965340 restauró artifacts E0020, ejecutó análisis con OIDN nativo en regiones, seleccionó tres zonas de gradiente desde refs exclusivamente y generó tres comparativas, reporte JSON y Markdown. Archivo de salida disponible como artifact 13975528472.
- **Desviación:** publicación git bloqueada por regla general de ignore de `docs/experiments` para archivos nuevos, no por fallo de análisis. Esta situación es análoga a la importación .blend.
- **Corrección:** `git add -f` solo para rutas analíticas E0020 concretas, sin tocar reglas ignore globales. Mantener la documentación de cambios de flujo en STATUS/ROADMAP/DECISION_LOG del mismo commit. Reintento pendiente y verificar SHA de branch tras push.

## 2026-11-12 — E0020 ROI analysis (no rerender)
- Reused exact EXRs from Actions 43287450449 via gh run download. Computed both-reference rankings and corrected region metrics including NATIVE_COMP_OIDN. Crops chosen only from two refs, display transform explicitly non-OCIO.
- Persisted E0020.md plus coordinates, 3 derived CC BY-SA images under benchmarks/results/cozy_e0020 (credit Nicole Morena), and JSON. Numerical conclusions remain provisional for 320×240 finite refs. No ACD algorithm change.


## 2026-11-12 — E0021, aumentar resolución y spp con aspecto preservado

- **E0020 confirmado:** informe E0020 y recortes tras postproceso fueron versionados con fuente/atribución CC BY-SA y ROIs determinadas por refs. Baseline nativo incluido en diagnóstico de regiones.
- **Justificación E0021:** referencia par E0020 discrepaba 0.0610 RMSE, ~24.5% del error raw (casi alerta 25%); a 320×240 los detalles reales son demasiado pequeños para evaluar pérdida de textura. Aumentar muestreo de referencias a 1024 cada una y tamaño sin modificar la proporción original de la imagen.
- **Método:** `--max-width 512` conserva resolución original con alto proporcional, 24 spp×3 seeds, 1024 spp×2 refs, mismo objeto RenderLayer y AOV. Comparar referencias 1/2 y rankings. Controlar coste y no repetir sin razón. Corrida pendiente, tests nuevos.
- **Riesgo:** diferencias de entorno/ruido/reference y métodos per-pass; ni mejor resolución ni más spp prueban convergencia ni calidad visual. F5 aún suspendido.


## 2026-11-12 — F3, ampliar interpretación E0021 a ambos refs y todas las semillas

- **Motivación:** el analizador inicial de E0020 generaba recortes desde dos referencias, pero la tabla de error del reporte por ROI correspondía solo a seed inicial, mientras los rankings globales resumían tres. Fijar método explícito evita confundir unidades.
- **Implementación:** `scripts/analyze_cozy_exr.py` calcula medias de RMSE/gradientes de **3 seeds contra cada referencia** y rankings por referencia, más ROI elegidas desde promedio de refs, con los mismos candidatos y curva diagnóstica visual por método. Regiones incluyen OIDN nativo.
- **Estado:** código y tests nuevos; evaluación real sobre E0021 pendiente. No modifica algoritmo OIDN ni geometría original; no demuestra mejora por sí mismo.


## 2026-11-12 — F3, fuente retenida de distinto dominio (E0022)

- **Problema:** medir solo Cozy Kitchen después de inspeccionarla puede sobreajustar la elección de una solución a ese fixture, no representar otras escenas. Introducir un exterior nocturno con emisiones y materiales sencillos para pruebas fuera de desarrollo.
- **Fuente:** Terraced Houses (Yunus Emre Karaman), repo MIT `emrelab/blender-projects`, commit SHA fijado `36c46d3`, 3,044,256 bytes, blob SHA1 fijo. README afirma MIT sobre .blend, pero autor nota tutoriales antiguos de procedencia no especificada.
- **Protocolo:** descargar solo desde commit inmutable, verificar git blob, licencia y tamaño, abrir sin autoexec en Blender5 y render Cycles 4spp antes de publicar. En este commit es candidato, no validado. No tocar el archivo de usuario ni el addon estable.

## 2026-11-12 — E0022, held-out MIT night scene verified and copied from immutable source
- Upstream repo emrelab/blender-projects commit 36c46d3, MIT explicitly covers .blend scene according to its README and LICENSE. Filename, size, Git blob SHA1 and postdownload SHA256 recorded; source unmodified.
- 192px Cycles 4spp smoke passed under --disable-autoexec before commit. Add original license and attribution. Source author notes tutorial-based modelling with unknown tutorial credits: retain this provenance; no implication of endorsement.
- Assign as a held-out scene, distinct from Cozy Kitchen development; no denoiser training or parameter tuning against it.


## 2026-11-12 — E0022 verificado y E0023 evaluación retenida

- **Verificación E0022:** run 43291261400 success, Blender5 Cycles 4 spp, fuente MIT `Terraced Houses` con SHA256 y Git blob fijados, licencia original preservada, no faltan activos. Fixture ahora versionado y se incluye test de integridad en CI.
- **E0023 diseño:** tras fijar explícitamente el baseline, probar sobre exterior nocturno no usado durante diagnóstico de Cozy Kitchen: 320 de ancho preservando relación fuente, 24 spp ×3 seeds, dos refs 512 spp, OIDN compositor frente ACD Standard/High/Super, mismo EXR y guías. Informe compacto generalizado. Resultado real por validar.
- **Regla:** no ajustar hiperparámetros, modelo o código de ACD usando esta escena *si pretendemos utilizarla como held-out final*. Datos de prueba sirven para informar generalización, no para elegir los cambios. F5 aún no iniciado.


## 2026-11-12 — Auditoría de costo GitHub Actions: runtime Blender no debe dispararse por PR

- **Evidencia:** runs `ACD Blender 5.0.1 offline runtime bundle` aparecieron repetidamente al sincronizar el PR #10, descargando archivando ~374MB en cada commit documental. No aportan a los benchmarks ya existentes que descargan Blender por cache.
- **Decisión:** cambiar solo el workflow del runtime efímero a `workflow_dispatch`, preservándolo cuando se necesite; quality CI permanece automático, E0021/E0023 workflows de benchmark siguen corriendo.
- **Costo evitado:** no generar descargas/artefactos de runtime en commits posteriores sin motivo. Cambio de ejecución, no de algoritmo.


## 2026-11-12 — E0021 ejecutado, preservar detalle en ROI con 2 referencias y 3 seeds

- **Verificado:** GH Actions 43289852695 success, escena Cozy Kitchen original, proporción preservada 512×482, 24spp×3, refs1024spp×2. Discrepancia refs/raw bajó de E0020 ~24.5% a 13.5% pero no prueba convergencia. OIDN compositor/Standard RMSE media 0.0833928 y borde 0.0896975, High 0.0860779/0.0902929, Super 0.0971167/0.0962214. Ranking total entre refs coherente.
- **Siguiente comprobación:** recuperar EXR real, medir todas semillas con ambas refs y visualizar ROI de alto gradiente elegidas sin salida candidata; persistir reporte y previews bajo licencia original CC BY-SA. Workflow nuevo no vuelve a renderizar.
- **Estado al commit:** datos y workflow; ejecución del postprocesador aún pendiente. Ninguna mejora algorítmica demostrada.

## 2026-11-12 — E0021 two-reference detail analysis preserved
- Reused exact EXR artifacts from run 43289852695, computed RMSE and reference-selected edge gradients on all three noisy seeds against both reference renders. Crops selected without candidate signals, tonemapping non-OCIO diagnostic. Attribution Nicole Morena CC BY-SA.
- Result: Native compositor OIDN/Standard lower RMSE and edge-gradient error vs ACD High/Super on this development scene at 512x482. Reference discrepancy decreased relative to E0020 but convergence/independence still unproven. No algorithm trained or altered.


## 2026-11-12 — E0023 discrepancia RMSE vs MAE: medir outliers HDR antes de atribuir causas

- **Hecho:** 24spp×3 seeds, refs512spp×2, noche Terraced Houses: raw RMSE 0.12014 < OIDN0.16778, pero raw MAE0.02815 > OIDN0.02107 y error gradiente0.12109 > OIDN0.06795. No demuestra superioridad visual de raw ni causa específica.
- **Nueva metrología:** reportar fracción SSE en el peor 1% de píxeles, valor extremo y p99 sobre datos lineales HDR. Tests sintéticos de un outlier vs error uniforme. No se ha corrido en la escena real a este commit.
- **Higiene experimental:** al usar E0023 para identificar una anomalía, deja de ser un held-out ciego en el sentido estricto. Cualquier candidato F5 exige validación sobre otra escena no observada. Sin alterar denoiser.


## 2026-11-12 — E0023 análisis AOV/errores extremos independiente de Cycles

- **Diseño:** interpretar contradicción Raw mejor RMSE vs OIDN mejor MAE y gradientes: calcular error concentrado peor1%, comparar errores de máscaras AOV emisión/glossy/transmission/environment, recortes de ROI elegidas solo desde refs; tres seeds frente a ambas refs en misma escena.
- **Fuente:** EXR de Actions 43291659387 que ya incluyen RAW, AOV y OIDN, sin rerender ni cambios de algoritmo. Proveniencia y licencia de Yunus Emre Karaman MIT.
- **Estado:** script y workflow de lectura/persistencia por ejecutar. Hasta completar no afirmar causa de aumento RMSE. E0023 ya se ha visto, por lo que no puede considerarse test de generalización ciego de futuros cambios.

## 2026-11-12 — E0023 auditoría de outliers y AOV a partir de mismo EXR
- Reprocesados los datos exactos de Actions 43291659387 sin volver a renderizar. Error cuadrático concentrado peor 1%, AOV emisión/glossy, tres ROIs de referencias, tres seeds vs dos referencias. Fuente original MIT Yunus Emre Karaman y copyright intacto.
- No asignar causalidad a emisión solo por máscara de energía AOV ni elegir parámetros a partir de esta escena ya examinada. Una nueva escena no observada será necesaria para test final.


## 2026-11-12 — E0020 primer benchmark multiseed en escenario público real

- **Objetivo y evidencia:** E0019 provee escena oficialmente publicada de Blender 3.5, CC BY-SA, 7.33 MiB y render smoke Blender5 OK. Ejecutar calidad inicial sin necesitar usuario ni publicar el archivo privado E0018.
- **Plan fijo:** 320px de ancho con relación de aspecto original, 24 spp, tres seeds 539/911/1337 y dos refs 512 spp 8819/8922. Métodos igualan RenderLayer/guías, comparar Standard/High/Super vs compositor OIDN y raw; métricas RMSE HDR, MAE, gradiente en borde, plano y ratio contraste (no usar solo nitidez).
- **Validez:** si las referencias divergen en exceso o seed variation falla, no inferir ranking. 320px es exploratorio (aliasing), no FHD profesional. Siguiente 512/1024px o dataset independiente tras resultados.
- **Estado:** workflow y protocolo comprometidos, sin resultados al commit. Renders solo por workflow de esta revisión y dispatch manual posterior; no ejecutar en cada commit.
