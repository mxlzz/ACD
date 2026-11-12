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
