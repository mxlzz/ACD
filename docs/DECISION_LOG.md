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


## 2026-11-12 — E0024 priorizar diagnóstico HDR y no duplicar E0020

- **Contexto recuperado:** E0021 completó ya Cozy Kitchen 512×482 a 24spp x3, refs 1024spp x2. E0023 completó exterior nocturno: Raw mejor RMSE pero peor MAE/gradientes que OIDN, error cuadrático concentrado en peor 1 % de píxeles. Nuevo workflow de 320px E0020 es redundante, cambiar a manual y no inferir resultados nuevos. Rendimiento de Actions es recurso limitado.
- **Método E0024:** máscaras top1% de luminancia de la referencia y top1% de error Raw, idénticas por método, dos refs y tres seeds, SSE/RMSE/MAE dentro y fuera. La máscara raw-error seleccionada tiene sesgo en favor del raw: explícitamente **no** usar como evaluación de superioridad ni en inferencia.
- **Protocolo:** test sintético de máscara invariante frente a candidato, empates, conservación SSE, HDR y validación input. Workflow lee EXR existentes run 43291659387; no recrea referencias ni altera el denoiser. Estado real del diagnóstico pendiente al commit.
- **Puerta F5:** no activada. Cualquier hipótesis basada en región nocturna examinada debe validarse en otra escena no vista y evitar leakage de referencia a tiempo de uso.


## 2026-11-12 — E0024 verificación de precondición NaN en test

- Primera CI E0024 #43304804793 falló antes de leer EXR, específicamente por texto del error del validador `rgb`; no se observó corrupción de método ni resultados de escena.
- Se corrigió `pytest.raises` para esperar el mensaje real de `rgb`, manteniendo que NaN sea rechazado y sin modificar algoritmo. Próximo: reejecución controlada con EXR existentes.


## 2026-11-12 — E0024 disparo mínimo de pipeline corregido

- El cambio de test corrigió error de regex, pero GitHub solo ejecutaba el workflow cuando cambiaba YAML. Se añadieron rutas de test y diagnóstico al trigger para revalidar sin ejecución de Blender y sin re-render de escena. Evitar reruns por cambios documentales.


## 2026-11-12 — E0024 confirma concentración por highlights con máscara reference-only

- **Run exitoso:** #43305087148, 7 tests y análisis EXR original E0023 (sin rerender). Datos 320×240, tres seeds y dos refs 512 spp. El top1% de brillo de referencia concentra ~71.69% SSE OIDN frente 35.46% Raw; RMSE local OIDN 1.42073, Raw 0.71512. Fuera del top1%, OIDN 0.08967 mejora Raw 0.09701. Dos refs patrón robusto; no implica convergencia.
- **Limitación:** RMSE no distingue error por subestimación o sobreestimación de luminancia, desplazamiento espacial, AOV emission o glossy; clasificación no causal. Máscara por error raw tiene sesgo y no debe considerarse ranking de filtros.
- **Decisión:** no incorporar corrección HDR ni retocar pesos todavía. Preparar E0025 análisis de signo/energía con los EXR existentes; E0024 workflow vuelve a manual. Conservar método y resultados en documento permanente.


## 2026-11-12 — E0025 medir sesgo firmado en iluminación HDR antes de corregir OIDN

- A partir de E0024 el top1% brillo según referencia conserva 71.69% SSE de OIDN en escena nocturna, pero RMSE no señala dirección. Hipótesis falsable: filtro atenúa o amplifica iluminación media en ese subconjunto.
- Diseño: máscara seleccionada únicamente por luminancia RGB de referencia, única para todos los candidatos; reportar delta de luminancia con signo, ratio de energía, porcentaje de pixels sobre y bajo referencia, para ambas referencias/tres seeds. Registro sin rerender desde EXR E0023, con pruebas direccionales y caso de referencia cero.
- Estado: código/test/workflow preparados, ejecución pendiente. No mezclar selección de máscara con estimación en inferencia, no inferir causa por emisión o red sin pruebas.


## 2026-11-12 — E0025 sesgo firmado de highlights verificado

- E0025 GH run 43305700278 completó 10 tests y cuantificación con 3 seeds, 2 refs del E0023. En top1% luminosidad referencia OIDN ratio 0.99147 (ref1), delta -0.19294, abs error 0.79937 vs Raw 0.33771; 56.16% píxeles sobre referencia, por lo tanto sesgo global promedio no implica subestimación uniforme. Ref2 confirma ratio 0.99088 y delta -0.20627. High/Super corrigen signo medio pero mantienen error local elevado.
- **Decisión:** no corregir exposición ni reasignar emisión basándose en media. Probar, solo offline, fusión Raw/OIDN con control *input-only* sobre dos escenas observadas, además de fusión constante como ablation; exigir tercer conjunto no observado antes de conclusión. E0025 workflow queda manual.


## 2026-11-12 — E0026 ablation de mezcla HDR seleccionada por Raw en inferencia

- E0024/E0025 señalan error OIDN en 1% más luminoso de referencias, Raw con menor error local y mayor error fuera. Hipótesis de combinación local solo con raw at runtime, sin acceso a referencia ni parámetros por escena, no requiere fork neuronal.
- Cuatro condiciones predeclaradas: FIXED10, FIXED50 globales, RAW_BRIGHT50 y RAW_BRIGHT100 con percentiles Raw 97/99.5 y smoothstep. OIDN/Raw/ACD High/Super se conservan de referencias. Mismas variantes en Cozy E0021 y Terraced E0023 contra ambas referencias y 3 seeds, RGB RMSE, MAE, edge, top1% ref y outside.
- **Limitaciones:** los dos escenarios ya fueron observados y motivaron la hipótesis, por tanto evaluación exploratoria; no holdout. El threshold por Raw puede elegir fireflies, reintroducir ruido/artefactos y no ser seguro a FHD. No cambiar parámetros post hoc para maximizar RMSE observado, descartar si empeora.
- **Estado:** scripts y workflow sin rerender comprometidos, tests/ejecución por verificar, addon/producto estable intactos.


## 2026-11-12 — E0026 negativo fuera de escena: gating Raw por brillo rechazado

- **Evidencia de GH run #43306559564:** 16 tests, dos escenas previamente examinadas, tres seeds/dos refs. RAW_BRIGHT100 mejora Terraced RMSE 0.16778->0.10936 y MAE 0.02107->0.01609, pero empeora fuertemente Cozy RMSE 0.08339->0.13909, edge 0.08970->0.13272. Segunda referencia conserva orden. Fusión local 50% también empeora Cozy 0.08339->0.09781.
- **Decisión negativa:** no promover algoritmo, no reajustar umbrales Raw/mezclas ad hoc por escena, pues sería sobreajuste a datos ya observados. Esta es una hipótesis descartada como estrategia universal simple.
- **Siguiente candidato:** guía física `Emission` AOV disponible en Cycles podría separar luces de superficies reflectantes, sin que se use la referencia para seleccionar píxeles en inferencia. Investigar su presencia en ambas escenas y compararla con mezcla global y Raw input. No anticipar mejora ni integrar sin validación ciega.


## 2026-11-12 — E0027 AOV Emission como posible guía física de preservación HDR

- E0026 falló en Cozy y mejoró Terraced usando brillo Raw. Atribución hipotética: indicador por brillo incluye texturas/glossy y fireflies no emisivos. E0027 usa Cycles `emission` AOV **del mismo seed** sin referencia en inferencia; peso `w=maxMix*emitL/(emitL+0.25)`, maxMix 0.5/1.0, benchmarkado frente a control constante peso medio.
- Dos escenas ya observadas E0021/E0023, cada una 3 semillas y dos refs; registrar disponibilidad y fracción no cero del pase, RMSE/MAE, bordes y RMSE dentro/fuera top1% ref. Ningún parámetro se ajustará retrospectivamente a escena. Mejora en ambas requerida para proseguir y nueva tercera escena para generalizar.
- Tests de no emisión => OIDN exacto, emisión localizada, no dependencia de denoised en peso, negativo, NaN y shapes. Código/workflow pendiente de GH Actions, sin cambio en addon.


## 2026-11-12 — E0027 AOV Emission mejora RMSE sin superar completamente OIDN

- **Evidencia:** run #43307378645, 11 tests, sin rerender. Cozy Kitchen AOV_EMISSION50 RMSE 0.083196 vs OIDN 0.083393 (escena con 0.04% emisión); noche Terraced RMSE 0.12220 vs OIDN0.167785 y MAE0.01765 vs0.02107, pero edge se degrada 0.067948->0.072103. Variante AOV_EMISSION100 RMSE noche0.11304 pero edge0.08098. Control constante de peso medio no consigue misma mejora.
- **Decisión:** conservar AOV_EMISSION50/100 como candidatos experimentales, sin integrar addon. No ajustar factor de escala .25 tras mirar resultados. Seleccionar nueva escena bajo licencia verificada antes de observar sus imágenes y medir sin modificar parámetros; considerar calidad de borde como restricción. La segunda referencia de las dos escenas confirma resultados, pero no es validación independiente de contenido.


## 2026-11-12 — E0028 test posterior sin retocar parámetros: elegir Low-Poly Island MIT

- Selección previa de nuevo contenido: emrelab/blender-projects, autor Yunus Emre Karaman, low-poly-island/v4.5 Cycles con cabin, vidrio, lámparas; MIT según README+LICENSE, blob e540ffe... (2,621,405 B), commit upstream 36c46d3. No ha sido usado en experimentos ACD. Mismo autor que Terraced implica relación estilística, no independencia total.
- No modificar AOV emission scale .25 ni pesos max .5/1 de E0027 tras observar este archivo. Preparar descarga oficial inmutable, verificación SHA git blob/tamaño, render smoke Blender5, solo después commit de .blend original, licencia y audit. Estado pendiente.
- Próximo: benchmark del nuevo contenido y reporte con dos refs/varios seeds, luego criterios para ampliar a escena profesional, sin prometer ganancia.

## 2026-11-12 — E0028 external island fixture imported before measuring ACD
- Pinned MIT source repo commit 36c46d3, original Git blob e540ffe, smoke Blender5 Cycles functional, no missing images/linked libraries. Scene is different from Cozy/Terraced, but shares Terraced author and stylized lighting; not sufficient alone for generalization across professional architectural renders.
- Original bin unchanged, source license copied, metadata SHA/credits stored; no candidate parameters changed. Next quality test will compare E0027 emitted-guide configurations prespecified earlier.


## 2026-11-12 — E0029 fixed parameter validation on new island scene

- E0028 MIT Low-Poly Island binary audited and published with source hash, Blender5 smoke OK. Workflow importer disabled to avoid duplicate push.
- E0029 prespecified E0027 emission scale .25 and max raw weights .5/1, three noisy seeds and two high-spp references, same-seed AOV and native OIDN comparators. Results pending; no tuning permitted on this scene. Original addon unchanged.


## 2026-11-12 — E0029 validación en nueva escena: evidencia favorable, no promoción

- Run #43309302172 success, 21 tests, 3 semillas y 2 referencias 512 spp para Low-Poly Island MIT de Yunus Emre Karaman. E0027 Emission50 con escala .25 inalterada logra RMSE 0.05335 vs OIDN nativo 0.06554, pero error de bordes 0.03962 vs 0.03935. ACD High/Super tienen errores HDR severos 0.143. Ref2 repite mejora.
- E0029 confirma hipótesis de preservación localizada de emisión en una tercera geometría sin tuning, pero la comparte autor con Terraced, no hay convergencia de referencias garantizada y el error de bordes sube. No afirmar superioridad perceptual ni general, no instalar variante en addon. Congelar E0029 workflow como manual, conservar EXR en artifacts y números en docs.
- Próximo: diagnóstico de recortes y una escena de autor independiente, más revisión de luminancia para eliminar halos/saltos antes de integración.


## 2026-11-12 — E0030 frozen visual diagnostics before selecting new model

- E0029 Emission50 reduces RMSE on new Island scene with small edge regression. Need visually inspect localized artifacts rather than promote algorithm on scalar score. E0030 selects ROI from *both references alone* and produces fixed-transfer Raw/OIDN/Emission50/100 and High/Super panels, local RMSE, no new render or parameter tuning. All derivative images MIT with attribution; pending workflow.

## 2026-11-12 — E0030 reference-only diagnostic crops for Island
- Reused EXR E0029 run 43309302172, selected a high-HDR ROI and gradient ROIs exclusively from two finite references, rendered same transfer to Raw/OIDN/Emission50/100/High/Super. Derived MIT images and local metrics permanently stored. No readjustment of candidate parameters or rerender.


## 2026-11-13 — E0030 revisión visual y E0031 nueva fuente independiente

- E0030: se inspeccionaron los 4 paneles archivados y sus métricas de dos referencias; la fusión Emission50 conserva una ganancia local HDR en luces intensas, pero no demuestra superioridad perceptual. **Limitación confirmada:** la ROI brightest solapa la detail_1 3354/6400 píxeles (52.4%), aunque las tres ROI de detalle son disjuntas entre sí. Se conserva E0030 sin reetiquetar cuatro vistas como cuatro regiones independientes. Ver informe E0030 revisado.
- E0031: se seleccionó Living Room ©2014 Jure Sorn MIT, autor distinto, archivo .blend original 7,328,212 B en gto76/living-room, commit a36bac4 y blob 51374a6. Añadido workflow para verificar integridad/licencia, faltantes y render Cycles Blender5 de 192px 4spp antes de copiar binario a repo; **smoke pendiente al commit**. Si falla compatibilidad/dependencias, no incorporar el fichero. No se ejecutó aún prueba de calidad ni se tocó addon.
- Puerta: 512px+ y 2 referencias sobre fuente nueva ya validada, con parámetros E0027 congelados y ROI disjuntas para un benchmark manual. No entrenar/forkear ni promover Emission50 mientras persistan regresiones de bordes y falta de diversidad profesional.


## 2026-11-13 — E0031 fuente rechazada, E0032 smoke independiente preparado

- E0031 [GH Actions 43414866242](https://github.com/mxlzz/ACD/actions/runs/43414866242): hash, tamaño y licencia MIT pasaron; abrió Blender5.0.1 pero falló el control funcional por `lapajne.jpg` y `lapajne.jpg.001` ausentes (y advertencia de archivo pre-2.50). **Sin render ni .blend versionado**, sin mediciones ACD. Rechazado sin sustituir recursos.
- E0032: nueva fuente arquitectónica de autor NewSee2l035, conversión Mitsuba→Blender de Modern Hall/Bitterli, GitHub `cuteday/scenes_blender` commit 4271a72, blob 6c60f72, 5,793,896 B. Origen CC BY 3.0, licencia de conversión a revisar antes de redistribuir. Workflow lee fuente externa sin incluirla en repo y exige hash, Blender5 cámara/materiales/texturas, render 192px 4spp; quality benchmark no iniciado. No cambia addon ni coeficientes Emission50.
- La comprobación Python/trazabilidad del commit precedente [run 43414877028](https://github.com/mxlzz/ACD/actions/runs/43414877028) pasó. CI verde no mide calidad de denoise.


## 2026-11-13 — E0032 compatibilidad superada; E0033 benchmark congelado

- [Run E0032 #43415697217](https://github.com/mxlzz/ACD/actions/runs/43415697217) **success**: Modern Hall cuteday source SHA256 b35b6694eb231d0d4d5d9ee9bbe63122218183fd519a05c7d5db0e62cbdaeca1, 5,793,896 B, 22 materiales, 32 mallas, 1 cámara, 3 imágenes empaquetadas / 4 imágenes, ningún archivo externo faltante, Cycles Blender5.0.1 192²×4spp completado; fuente externa efímera NO subida a ACD. Conversión y derechos de redistribución independientes aún sin resolver.
- E0033 diseñado con mismos coeficientes E0027 y control de mezcla constante, 512px, 24spp×3 y refs1024×2, números y pruebas de borde/HDR guardables permanentemente. **No reportar números antes de ejecución.** Workflow autoiniciado por incorporación y CI Python.
- E0031 continúa rechazado por texturas faltantes; ACD stable addon no modificado.



## E0033 run completed — numerical result, Git archiving issue (2026-11-13)

- Run: https://github.com/mxlzz/ACD/actions/runs/43416607737 . Blender 5.0.1 rendered all three 24-spp seeds, two 1024-spp references and the lab produced scores. The final git-add failed because the ignore rule experiments/ covers docs/experiments/, but 149 MB of EXRs/JSON were uploaded as artifact 14034252923, expiring 2026-11-27. This is a publication error, NOT a rendering/denoiser failure.
- First/second ref global HDR RMSE OIDN 0.02223804 / 0.02215599; frozen Emission50 0.02230239 / 0.02221500, worse in both. ACD High 0.02371872 / 0.02366157; ACD Super 0.03184713 / 0.03176431. First-ref edge RMSE OIDN 0.03445690 vs Emission50 0.03455458 (regression); top 1% reference brightness RMSE OIDN 0.01197959 vs Emission50 0.00643289 (localized improvement).
- Reference-to-reference RMSE 0.02153122 (similar scale to denoised error). No reference convergence proven, and no universal ranking should be inferred. Emission50 FAILED to improve global quality on an independent artist/scene and must not be promoted or tuned against this now-observed scene.
- E0034 is a postprocess-only recovery workflow: exact JSON + EXRs from the existing run, source-only ROI selection and nonoverlapping crops, fixed display transfer, archive PNG in Git. Its run is not yet verified at this commit. Addon stable unchanged.


## 2026-11-13 — E0034 publication staging correction
- E0034 run 43451223536 generated the postprocessed PNG and verified original E0033 EXRs, but the git-add phase was blocked again by the broad nested-ignore rule for docs/experiments. No new render or scientific results. Fix the root ignore mismatch with an explicit documentation exception and force-stage both numeric JSON and tracked report, while retaining broad exclusions for .blend/.exr assets. This is a packaging fix, not algorithm adjustment.

## E0034 result archive (2026-11-13)

- Recovered E0033 run 43416607737 exact JSON and existing EXR, generated no new Cycles renders. Fixed gitignore staging failure; numerical JSON and tracked report staged explicitly. Published 1:1 full image and disjoint reference-selected ROI PNG in benchmarks/results/hall_e0034/README.md; kept original .blend out. Frozen Emission50 worse global RMSE/border than OIDN in Modern Hall; no integration.



## 2026-11-13 — Índice permanente de imágenes del laboratorio
- E0034 [run 43451534590](https://github.com/mxlzz/ACD/actions/runs/43451534590) success; commit de archivo f20d2a854f61e0681ffd6a659f0565b15269c124; resultados E0033 exactos y PNG E0034 versionados. Nuevo índice benchmarks/results/README.md integra Modern Hall, Island, Cozy Kitchen E0020/E0021 y Terraced; enlaza licencias, full/crops y diferencia entre PNG permanentes y artifacts EXR temporales. README principal enlaza el índice. No hubo nuevo render ni cambio al addon.


## 2026-11-13 — Corrección de rumbo de ACD V2, antes de E0035

- **Hechos:** OIDN compositor es baseline reproducible; Standard equivale a él en ensayos locales. High/Super no tienen mejora consistente; Emission50 reduce el error de pocas luces pero retrocede en bordes y no supera globalmente a OIDN en Modern Hall; referencias E0033 no probadas convergentes. Los tests unitarios de ACD no miden nitidez a escala de producción.
- **Decisión:** priorizar [B0–B4](ACD_V2_REORIENTATION_2026-11-13.md). B0 versiones Blender 5.2.4 LTS/5.3.0 y distinción OIDN compositor/Cycles interno/OIDN CLI; 5.0.1 queda para historia. B1 corpus de escenas realistas y holdout por escena. B2 referencias convergentes, HDR-FLIP y OCIO, tiempo vs más spp. B3 hipótesis de guías por un error reproducible. B4 promoción solo con evidencia fuera de muestra.
- **Restricciones:** Emission50/High/Super congelados, no entrenamiento/fork ni merge addon; experimentos GPU o 1080p solo manuales. Documentar hashes, costes, fallos, licencias. Primera etapa B0a se preinscribe E0035, smoke pequeño, no ranking entre versiones con renders diferentes.


## 2026-11-13 — B0a/E0035: contrato reproducible implementado (ejecución pendiente)

- Código nuevo: tests/blender_cycles_capabilities_e0035.py registra sockets/propiedades de denoise de la versión real, scripts/summarize_blender_compat_e0035.py comprueba fuente RAW igual al beauty AOV de la misma seed y compara Standard con OIDN compositor, tests/test_blender_compat_e0035.py rechaza mezclar informes de diferentes versiones. 
- Clasificación: **tests de contrato**, no calidad visual. Resolución 128×96, noisy16spp, referencia64spp (no convergida). Cycles-internal todavía sin ejecutar. Próximo workflow E0035 matrices 5.2.4 LTS/5.3.0 y checksums oficiales.


## 2026-11-13 — E0035 control de versiones iniciado

- Workflow E0035 incorporado con matriz Blender 5.2.4 LTS y 5.3.0 de archivos oficiales + hash, API compositor/Cycles y render ligero con misma beauty y AOV dentro de cada job.
- Push de workflow dispara primera corrida; siguientes solo manual o cambio explícito a este workflow. Resultado **pendiente de GitHub Actions**, no benchmark de calidad ni comprobación Cycles-internal. Addon estable intacto.


## 2026-11-13 — E0035 primer smoke abortado por biblioteca faltante en runner

- [Actions run 43480476666](https://github.com/mxlzz/ACD/actions/runs/43480476666): **ambos jobs fallaron** tras pasar tests, SHA256 oficial, Blender --version y enumeración API. En el paso de render se produjo abort 134 con mensaje **libEGL.so.1: cannot open shared object file**; Blender 5.3 además advirtió que el backend Vulkan no se inicializaba. Esto indica una dependencia runtime del runner, no prueba de defecto del denoiser ni de incompatibilidad del addon.
- Corrección limitada a CI: instalar libegl1/libgl1-mesa-dri/libopengl0/libxkbcommon0 y verificar ldconfig antes de render; repetir igual fixture/configuración. No modificar el método, reference spp o addon. Resultado del segundo intento pendiente.


## 2026-11-13 — E0035 real success; archival validation triggered

- [Run 43480823352](https://github.com/mxlzz/ACD/actions/runs/43480823352) dos jobs **success**. Blender oficiales 5.2.4 LTS (build cd5dc428cce1) y 5.3.0 (02f0899d78e3), verificación SHA256/tiny Cycles 128×96, 16 spp, misma beauty raw/AOV delta=0, Standard vs OIDN compositor delta=0 en cada versión. Ninguna de estas cifras indica calidad real.
- Se agregó pipeline E0035 archive que recupera EXR/reportes **ya generados** y mide diferencias pixel/guías entre versiones, publica JSON pequeño en docs/experiments. **Su ejecución pendiente**. El denoiser integrado de Cycles todavía no fue evaluado; pasar a B0b después de registrar deltas.



## 2026-11-13 — E0035 archive corrected: nested artifact layout

- Run [43481397097](https://github.com/mxlzz/ACD/actions/runs/43481397097) retrieved both E0035 artifacts and validated report versions, then failed reading EXR because Actions upload preserved `acd-e0035-render/` subfolder rather than placing raw EXR at archive root. Not a rendering/algorithm error. Fix by locating exactly one file recursively per name and rejecting ambiguous artifacts. Re-run without Blender/denoiser.

## E0035 completed — B0a contracts verified (2026-11-13)

## E0035 — Blender 5.2.4 LTS vs 5.3.0: API + mismo input (2026-11-13)

- [Successful workflow 43480823352](https://github.com/mxlzz/ACD/actions/runs/43480823352), initial EGL runtime failure in [43480476666](https://github.com/mxlzz/ACD/actions/runs/43480476666) corrected by installing libegl1. Both official Blender archives passed published SHA256.
- Procedural detail_target, 128x96, 16 spp noisy seed 539, 64 spp reference seed 8819. This is an API/smoke contract; reference NOT converged and no visual superiority claim.
- 5.2.4 (build cd5dc428cce1): Raw/AOV delta 0.0, Standard/OIDN delta 0.0.
- 5.3.0 (build 02f0899d78e3): Raw/AOV delta 0.0, Standard/OIDN delta 0.0.
- Cross-version **Raw beauty** RMSE 0.006166062714630608. Denoising Albedo RMSE 0.00032205058212830514, Denoising Normal RMSE 0.0004913281671895542. Changes across Blender versions combine renderer/guide/backend effects; must use fixed EXR to isolate denoiser.
- Cycles-internal denoising is configured/available in API, but **not measured**; 5.3.0 reports compositor API deprecation slated for Blender6.0; add compatibility planning, not algorithm tuning.
- [Exact JSON](E0035_RESULTS.json). Original EXRs/actions artifacts expire after 14 days. Addon stable untouched.


## 2026-11-13 — B0b/E0036: estudio con idéntico RenderLayer diseñado

- Implementados tests/blender_cycles_internal_e0036.py y scripts/analyze_cycles_internal_e0036.py. En una sola ejecución Cycles, se activa denoising integrado OIDN y se obtienen tres EXR del mismo nodo Render Layers: Raw/Noisy Image, CyclesInternal/Image y CompositorOIDN con Accurate/High/HDR + albedo/normal. Por tanto se eliminan diferencias entre seeds/renders al comparar ambas rutas. Fixtures procedurales 128×96, 16spp, sin ground truth; solo se informará **diferencia entre outputs**, no ranking de calidad.
- Tests sintéticos comprueban identidad, detección de diferencias y rechazo de dimensión. Workflow por crear/ejecutar tras este commit. No modificar ni forzar expectativas de igualdad: diferentes preprocesamientos pueden dar imágenes distintas.


## 2026-11-13 — B0b E0036 real smoke initiated (pending results)

- Workflow [.github/workflows/acd-e0036-cycles-internal.yml](.github/workflows/acd-e0036-cycles-internal.yml) agregado y disparado: Blender oficial 5.2.4 LTS verificado, Cycles 16 spp, una sola ejecución, RLayers Noisy Image/Imagen denoised interna/CompositorOIDN, mismo albedo y normal. Métricas RMSE entre outputs, sin ground truth ni ranking. No requiere escena o intervención privada.
- Si falla, conservar mensaje real y reparar causa; no interpretar como diferencia de calidad. Resultados pendientes en Actions.

## E0036 — Cycles internal vs compositor OIDN actual (2026-11-13)

# E0036 — Denoising interno de Cycles vs nodo OIDN de compositor (mismo render)

- [Workflow E0036](https://github.com/mxlzz/ACD/actions/workflows/acd-e0036-cycles-internal.yml), Blender 5.2.4 LTS, scene procedural detail_target 128×96, 16spp, seed539, GPU none. Source: same RenderLayer Noisy Image, Image denoised and Denoising Albedo/Normal. Compositor OIDN Accurate/High/HDR. No reference converged or claim of quality winner.
- RMSE RGB entre salida interna y de compositor: 1.4466098094000755e-07; delta máximo 1.9073486328125e-06. Coincidencia exacta: False.
- Raw→OIDN integrado RMSE 0.2544771700358048; Raw→OIDN compositor 0.25447716631777373. Estos números miden diferencia entre salidas, NO si una es mejor.
- [JSON exacto](E0036_RESULTS.json). EXR/AOV en artifacts del run solo 14 días. Próxima puerta: misma entrada de forma verificable frente a OIDN standalone y controles de guías; luego referencias convergentes antes de ranking.


## Checkpoint verificado 2026-11-13 — B0a terminado, B0b parcialmente resuelto

- **E0035:** [run 43480823352](https://github.com/mxlzz/ACD/actions/runs/43480823352), ambas versiones oficiales Blender 5.2.4 LTS y 5.3.0 verificadas por hash y con smoke real. En ambas, Raw/beauty de AOV delta máximo 0 y ACD Standard = OIDN compositor (RMSE=0, tiny fixture). [Resultado permanente](docs/experiments/E0035_RESULTS.json). Entre versiones, beauty Raw difiere RMSE **0.00616606**, albedo **0.00032205** y normal **0.00049133**: NO comparables como mismo input para atribuir cambios a filtro. [Archivo de contraste](https://github.com/mxlzz/ACD/actions/runs/43481617537) también completado.
- **E0036:** [run 43482278177](https://github.com/mxlzz/ACD/actions/runs/43482278177) **success**: Blender 5.2.4, mismo RenderLayer seed539 16spp 128×96, Cycles-internal OIDN vs OIDN compositor con albedo/normal. Diferencia RMSE **1.44660981e-7**, máximo **1.90734863e-6**, no igualdad bit a bit; muy cercanos en este fixture. Sin referencia convergida y sin conclusión perceptual. [Informe](docs/experiments/E0036.md) y [JSON](docs/experiments/E0036_RESULTS.json).
- **Siguiente dependencia B0b:** verificar OIDN CLI 2.5.1 sobre **idéntico Raw EXR y guías de E0036/E0035**, registrando prefilter, HDR, pesos/backend, CPU/ISA y tiempos normalizados; si las rutas difieren, aislar configuración antes de juzgar calidad. No volver a ejecutar automáticamente High/Super/Emission50 ni modificar addon.


## 2026-11-13 — E0037 preinscripción y método

- Objetivo: comparar OIDN standalone 2.5.1 sobre los datos reales ya congelados de E0035 (16 spp, 128×96, dos versiones) sin re-renderizar ni atribuir calidad. Se exige SHA256 exacto de Raw, compositor y multilayer, verificación de PFM float32 e identidad de AOV.
- Dos modos: raw_aux (OIDN RT high/HDR guías originales, cleanAux=false) vs accurate_like (OIDN RT high prefilter solo albedo, luego normal, luego beauty con cleanAux=true). La guía de OIDN indica este prefiltrado; no se asume paridad exacta con el compositor Blender y no se mide verdad de referencia.
- A registrar: RMSE directo respecto a compositor por misma versión, mayor diferencia, SHA256, flags de CPU y walltime por subprocess con overhead. Resultado todavía no obtenido; workflow separado en próximo commit. No tocar addon.


## 2026-11-13 — E0037 workflow ingresado

- Archivo .github/workflows/acd-e0037-oidn-cli-guides.yml dispara un único run que recupera E0035 artifacts, verifica SHA256 fuente y release OIDN 2.5.1, evalúa variantes raw_aux / accurate_like y archiva métricas permanentes. No se hace render ni comparación perceptual. El reporte de calidad aún no existe al momento del commit.

## E0037: OIDN 2.5.1 standalone on frozen E0035 source (2026-11-13)

[Protocolo preinscrito](E0037_PLAN.md). [E0035 fuente](E0035_RESULTS.json).
Raw/AOV originales y hashes de las dos versiones verificados. Solo CPU, 4 threads; sin nuevos renders ni verdad de referencia convergente.

| Blender fuente | Sin filtrar guías RMSE | Prefiltrado RT + cleanAux RMSE |
|---|---:|---:|
| 5.2.4 | 0.046473111 | 0.040350220 |
| 5.3.0 | 0.046456395 | 0.040380501 |

La comparación mide distancia de salida respecto al nodo compositor, no calidad. La variante de guías prefiltradas se aproxima al prefiltrado Accurate, pero no asegura idéntica versión/ponderación/preprocesamiento de Blender.
Los tiempos incorporan tres procesos y overhead de archivo, no comparables directamente con el denoising integrado.

[JSON exacto con flags, hashes y tiempos](E0037_RESULTS.json).


## 2026-11-13 — E0038 control versión OIDN 2.5.0 vs 2.5.1

- Fuente Blender v5.2.4/v5.3.0 build_files/build_environment/cmake/versions.cmake establece OIDN_VERSION 2.5.0. E0037 usó standalone 2.5.1 y no igualó al compositor, incluso con guías prefiltradas. El release OIDN 2.5.0 x86_64 linux tiene digest SHA256 254a8355856f8cd433edb7dd832b5fb02e7157d073f7d22e331ce06533fb491f según GitHub release asset.
- E0038 compara ambos binarios oficiales sobre PFM idénticos y misma configuración; verifica hashes de E0035/E0037, y separa distancia versión vs distancia Blender. **No mide calidad**. El workflow se inicia con este commit.

## E0038 — comparación OIDN 2.5.0/2.5.1 sobre los mismos PFM

Blender 5.2.4/5.3.0 CMake version pins OIDN 2.5.0. Ambos binarios standalone oficiales usados con mismos PFM, flags, CPU 4 threads. Entradas verificadas frente a E0035/E0037. Sin nuevos renders.

| Blender fuente | Variante | OIDN 2.5.0 vs 2.5.1 | OIDN 2.5.0 vs compositor Blender |
|---|---|---:|---:|
| 5.2.4 | raw_aux | 0.000001955 | 0.046473076 |
| 5.2.4 | accurate_like | 0.000002026 | 0.040350198 |
| 5.3.0 | raw_aux | 0.000001967 | 0.046456354 |
| 5.3.0 | accurate_like | 0.000002056 | 0.040380591 |

La cercanía entre outputs no demuestra calidad superior. Si persisten diferencias con Blender con OIDN 2.5.0, revisar la identidad del socket de guía y la ruta de prefiltrado antes de atribuirlas al motor.
Resultados numéricos, hashes y flags: [E0038_RESULTS.json](E0038_RESULTS.json).


## 2026-11-13 — E0039: identidad de guías comprobable

- E0038 confirmó que la versión 2.5.0 vs 2.5.1 aporta RMSE ~2e-6, mientras CLI vs Blender sigue ~0.04035 en guías prefiltradas: divergencia sin explicar.
- El código de Blender 5.2.4 node_composite_denoise.cc usa OIDN RT y filtros auxiliares separados; para comprobar si son idénticas las señales, E0039 exportará en el mismo render los sockets Noisy Image, Denoising Albedo y Denoising Normal y comparará contra EXR multilayer, sin usar referencias para ranking. También invalida un supuesto si esas guías no coinciden.
- Cambio de blender_compare_smoke.py limitado a bandera opt-in ACD_E0039_CAPTURE_SOCKETS; flujo estándar intacto. Workflow E0039 dispara y publica reportes si pasa.



## 2026-11-13 — E0039 primera corrida: falta socket Noisy Image con Cycles denoising desactivado

- [Run 43491904780](https://github.com/mxlzz/ACD/actions/runs/43491904780) abortó antes de renderizar al exigir RLayers Noisy Image; Blender5.2.4 expuso Image y los AOV Denoising Albedo/Normal, pero no Noisy Image al tener denoising de Cycles desactivado. El baseline usa Image en ese caso, no se debe inventar socket.
- Corrección estrictamente de contrato E0039: capturar RLayers Image como ResolvedRaw (misma imagen de partida que usa compositor), Albedo y Normal sin modificar; comparar con multilayer EXR del mismo render. El pipeline estándar no cambia. Reintento activado por cambio de workflow.

## E0039 socket/AOV contract result (2026-11-13)

Blender 5.2.4 LTS, 128×96, 16 spp, una ejecución Cycles. Exports de sockets del compositor y AOV de mismo render. No ranking de calidad.

| Señal | RMSE socket vs AOV | Max absoluto |
|---|---:|---:|
| ResolvedRaw | 0.000000000 | 0.000000000 |
| Albedo | 0.000000000 | 0.000000000 |
| Normal | 0.000000000 | 0.000000000 |

Si las guías no coinciden, el EXR archivado no reproduce exactamente los inputs del nodo. Si coinciden, revisar otros estados de filtro/buffer/versiones. Sin ground truth convergente.
[JSON completo](E0039_RESULTS.json).
