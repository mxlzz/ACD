> E0036 real same-render Cycles internal vs compositor OIDN 5.2.4 LTS workflow triggered; no quality ranking, one noise realization; results pending.

> E0036 B0b new same-render design: Raw Noisy Image, Cycles internal OIDN and compositor OIDN from identical Render Layers with known guide sockets; Python analysis contract and synthetic tests written; next run Blender 5.2.4; no claims until real jobs pass.

> E0035 archive first run 43481397097 failed EXR path due nested artifact directory (not algorithm). Fix via unique recursive file selection, rerun no Blender.

> E0035 run 43480823352 verified both Blender 5.2.4 LTS and 5.3.0 tiny Cycles/compositor contract: Raw/AOV exact within build and Standard==compositor OIDN. Added archive-only workflow to preserve metrics and compare cross-version raw/guides; pending. No Cycles-internal quality comparison yet.

> E0035 run 43480476666: SHA256, Blender5.2/5.3 API and unit tests OK, both render jobs abort(134) because ubuntu runner lacks libEGL.so.1. Install OS EGL/OpenGL dependencies, retry identical protocol; not compatibility verdict yet.

> E0035 workflow official Blender 5.2.4/5.3.0 tiny CPU API/compositor smoke committed and triggered by path. Await real jobs, do not declare denoiser quality.

> E0035 code implemented: API scan, tiny same-seed beauty/AOV contracts and un-converged 64spp reference diagnostic. Workflow not yet run, no claims of 5.2/5.3 compatibility. Await official-build matrix.

> **REORIENTACIÓN 2026-11-13:** plan B0–B4 vigente en docs/ACD_V2_REORIENTATION_2026-11-13.md. Iniciar B0a pruebas actuales 5.2.4 LTS y 5.3.0; no nuevos candidatos hasta corpus y referencias. Mantener OIDN como baseline, freeze Emission50/High/Super.

> E0034 #43451534590 success: E0033 exact JSON and 5 PNG variants preserved. Central viewer index benchmarks/results/README.md links saved previews from all major scenes, distinguishes Git PNG from expiring EXR Actions artifacts. No algorithm or addon changes.

> E0034 generated image comparisons successfully from archived E0033 EXR in run 43451223536; only git add failed due docs/experiments ignore. Correcting root .gitignore exception and explicitly staging both E0033 MD/JSON. Re-run publication only (no new Blender render).

> E0033 43416607737 render+metrics OK; Git publish failed due recursive .gitignore experiments/. OIDN RMSE 0.022238 / 0.022156 vs Emission50 0.022302 / 0.022215 (regression global), refs differ 0.021531. E0034 recovers original EXR and publishes viewable gallery without rerender, pending run.

> E0032 run 43415697217 éxito: Modern Hall Blender5 Cycles 4spp, sin faltantes; SHA b35b6694, 22 materiales, 32 mallas, no republicar .blend hasta aclarar licencia conversión. E0033 prueba 512px 3 seeds24spp dos refs1024spp, Emission50 fijo y controles, workflow independiente preparado; resultados pendientes.

> E0031 descartado: smoke 43414866242 falló por lapajne.jpg y lapajne.jpg.001 faltantes; SHA MIT válido, archivo NO incorporado. E0032 previsto: Modern Hall (NewSee2l035, Bitterli/cuteday), fuente .blend externa 5.79 MB, smoke Blender5 sin publicar binario ni benchmark; revisar licencia de conversión antes de redistribuir. Ver docs/experiments/E0032.md.

> E0031: candidato MIT Living Room de Jure Sorn (autor distinto), prueba de ingreso con hash, licencia y Blender5 4spp solo funcional. Pendiente; ver docs/experiments/E0031.md. E0030 inspeccionado: brillo ROI 0.17294 OIDN vs 0.15049 Emission50 (ref1), pero 2 ROI solapadas 52.4%; no hay 4 evidencias independientes ni superioridad visual general.

> E0030 postprocess of E0029 original Island EXRs prepared, 4 reference-only ROIs, 8 image panels per ROI, same fixed diagnostic display and per-region first/second-ref RMSE; publish MIT derived crops only on success. Pending workflow, no rerender.

> E0029 [Actions #43309302172](https://github.com/mxlzz/ACD/actions/runs/43309302172) COMPLETADO, nueva Low-Poly Island MIT 320x272, 3 seeds24 spp, refs512 x2: Emission50 congelado reduce OIDN RMSE 0.06554→0.05335 (-18.6%), pero gradiente bordes 0.03935→0.03962 (+0.7%); segunda ref confirma. [E0029](experiments/E0029.md). Falta evaluación visual y escena de otro autor; no integrar addon ni entrenar OIDN. Workflow solo manual.

> E0028 imported and validated MIT Low-Poly Island via Actions #43308643155. E0029 prespecified third-scene emission experiment (320px, 24spp x3, twin 512spp refs, fixed E0027 weights), pending run. Preserve holdout caveat shared author with Terraced; no addon merge.

> **E0028 en preparación (2026-11-12):** Low-Poly Island de Yunus Emre Karaman, .blend 2.62 MB MIT source commit 36c46d3, geometría/iluminación inéditas para ACD aunque autor compartido con Terraced. Workflow comprobará blob/hash, licencia y Blender5 Cycles 4spp antes de subirlo, luego comparación con E0027 parámetros fijos sin tuning. [E0028](experiments/E0028.md). Importación y benchmark no verificados al commit.

> **E0027 verificado:** Emission AOV ayuda a discriminar entre Cozy (0.04% emisión; RMSE 0.083393→0.083196) y Terraced nocturno (4.49% emisión; RMSE 0.167785→0.122200 con maxmix50). Pero error de gradientes nocturnos sube 0.06795→0.07210 (maxmix100 lo empeora más). [Informe](experiments/E0027.md), [Actions #43307378645](https://github.com/mxlzz/ACD/actions/runs/43307378645). **No integrar** sin nueva escena no observada y verificar calidad de bordes. Workflow manual tras éxito.

> **E0027 planteado 2026-11-12:** fusión OIDN/Raw guiada por Emission AOV del mismo Cycles render, escala fija .25, mezcla máxima .5/1.0, control uniforme con mismo peso medio, sin usar referencias en inferencia; resultados cross-scene Cozy/Terraced por dos refs/tres seeds. [Protocolo E0027](experiments/E0027.md). No hay ejecución ni validación, no tocar addon estable.

> **E0026 concluido / variante rechazada:** [run #43306559564](https://github.com/mxlzz/ACD/actions/runs/43306559564), 16 tests, Cozy OIDN 0.08339 HDR RMSE vs RAW_BRIGHT100 0.13909; Terraced OIDN 0.16778 vs RAW_BRIGHT100 0.10936. Gating solo por luminosidad Raw no generaliza y empeora detalle interior. [E0026](experiments/E0026.md). No integrar ni ajustar percentiles en datos observados. Siguiente hipótesis usar AOV emisión Cycles para discriminar highlights emisivos, con controles y validación nueva; F5 no liberada.

> **E0026 prototipo independiente de Blender (2026-11-12):** input-only Raw luminance gate 97–99.5% con max mix .5/1.0 frente OIDN; controles 10/50% mezcla global, prueba sin rerender en Cozy E0021 y Terraced E0023 (dos refs, tres seeds), mismos parámetros. [E0026](experiments/E0026.md). No hay resultado ni validación held-out; F5 aún experimental y addon estable congelado.

> **E0025 completado:** [run #43305700278](https://github.com/mxlzz/ACD/actions/runs/43305700278), sesgo lum HDR top1% de referencia OIDN ~-0.85% en total, pero 56% píxeles sobre ref y error absoluto ~0.799 vs Raw 0.338; High/Super cambian signo de sesgo, sin fidelidad perfecta. [E0025](experiments/E0025.md). Siguiente hipótesis experimental: fusionar Raw/OIDN guiado **solo por input**, controlar vs mezcla constante, sin entrenar ni tocar addon. E0025 workflow manual tras éxito.

> **E0025 preparado 2026-11-12:** E0024 identifica top1% HDR ref como fuente de exceso RMSE nocturno; nuevo diagnóstico del signo de diferencia en luminancia sobre máscara *reference-only*, 3 semillas/2 referencias usando EXRs ya existentes. Tests sintéticos y workflow de bajo coste; ejecución pendiente y F5 todavía no habilitado. [E0025](experiments/E0025.md).

> **E0024 verificado 2026-11-12:** [run 43305087148](https://github.com/mxlzz/ACD/actions/runs/43305087148), top1% brillo referencia concentra ~71.7% SSE OIDN vs 35.5% Raw. RMSE OIDN dentro=1.4207 vs Raw=0.7151; fuera=0.08967 vs Raw=0.09701. Segunda ref reproduce. [Informe](experiments/E0024.md). Es error espacial HDR, no causalidad de emisión; siguiente E0025 sesgo de luminancia con signo sobre mismos EXR. Workflow E0024 manual para ahorrar Actions.

> E0024 workflow trigger actualizado para cambios específicos de test/parser HDR tail, tras corrección de mensaje NaN. Reejecución pendiente, no crear nuevos renders. 

> E0024 primera ejecución [43304804793](https://github.com/mxlzz/ACD/actions/runs/43304804793): 6/7 tests pasan, único fallo de regex `Nonfinite` frente a error real `raw: found NaN or infinite values`, sin cálculos EXR. Ajuste de aserción solamente, nueva ejecución pendiente.

> **E0024 (2026-11-12) en preparación:** auditoría de top 1 % HDR ref-luminance y raw error, máscaras comunes para Raw/OIDN/High/Super, errores dentro/fuera y concentración SSE; E0023 EXR existentes, **sin rerender**. Workflow E0024 pendiente. Detectada redundancia: E0021 ya probó Cozy 512×482 1024spp refs, por lo que el nuevo workflow E0020 320px se dejó solo manual y su ejecución redundante no debe definir nuevas decisiones. [E0024](experiments/E0024.md).

> **E0020 piloto preparado:** Cozy Kitchen fuente oficial vendorizada (E0019); render 320px, 24 spp x3 seeds, refs 512 spp x2, OIDN compositor nativo vs ACD Standard/High/Super, metrics HDR/gradiente y raw AOV. Ejecutar/verificar Actions antes de conclusión, ampliar resolución y referencias tras controlar divergencia. [Protocolo](experiments/E0020.md). Sin intervención del addon estable.

> E0023 script y workflow preparados: reportar concentración del error HDR peor1% + ROI de emisión/glossy desde el EXR 24spp existente, comparando Raw vs OIDN en tres seeds/dos refs; y guardar 3 recortes de referencias/diagnóstico en GitHub MIT sin volver a renderizar. Ejecución aún no validada; no atribuir el aumento RMSE a causa específica.

> E0023 diagnóstico HDR 2026-11-12: Raw gana RMSE 0.120 frente OIDN 0.168, pero OIDN gana MAE y error de gradientes. Nueva métrica de concentración SSE peor 1 % con tests creada; analizar aún en EXR existentes sin rerender. Escena nocturna E0023 ya observada, así que no es test ciego para cambios posteriores. E0021 ROI/crops archivados y quality validada.

> E0021 run #43289852695 Blender5.0.1 Cozy Kitchen **success**: 512×482, 24spp ×3 refs1024spp ×2; discrepancia de refs 0.03551 RMSE (13.53% raw, vs 24.51% E0020). OIDN nativo/Standard menor RMSE y gradiente que High/Super; se prepara postprocesamiento ROI con 2 refs y 3 seeds, no rerender; workflow, pruebas y publicación E0021 aún pendientes.

> 2026-11-12 mantenimiento CI: el workflow `acd-blender-runtime-bundle.yml` descargaba y archivaba 374MB en cada sync del PR #10; ahora es manual únicamente, dejando quality CI automático y benchmarks por disparo controlado. Objetivo: evitar consumo de minutos y artefactos sin evidencia nueva.

> **E0022 verificado y E0023 lanzable, 2026-11-12:** exterior nocturno MIT ya versionado (SHA y licencia), Blender5 smoke passed [#43291261400](https://github.com/mxlzz/ACD/actions/runs/43291261400). Workflow E0023 usa 24 spp ×3, refs 512 ×2 a ancho320 para **test retenido**. Preparado, ejecución pendiente. E0021 de Cozy Kitchen 1024spp referencias continúa separadamente.

> **E0022 candidatura hold-out:** Terraced Houses exterior nocturno, MIT, 3.04MB y git blob SHA fijo; [E0022](experiments/E0022.md). Se preparó workflow de importación con verificación Blender5/autor/licencia, todavía pendiente de ejecución, asignación como **test de generalización** y no datos de optimización. Complementa Cozy Kitchen; no reemplaza escena profesional.

> F3 comparabilidad de referencias: agregado analizador reutilizable para dos referencias y 3 seeds por método, con ROI solo desde refs y recortes 3x, ahora para E0021. La corrida E0021 de mayor resolución sigue pendiente de verificación; el análisis toma sus artifacts, sin rerender. Conservar F5 suspendido hasta evidencias de detalle.

> **E0021 preparado (2026-11-12):** E0020 informe +3 ROI/crops permanentes ya disponibles. Para reducir discrepancia de referencias y preservar encuadre, E0021 usa ancho máximo 512 derivando alto desde resolución original, 24 spp ×3 seeds, refs 1024 spp ×2, estándar/High/Super/OIDN nativo. Nuevo runner guarda fuente/aspect metadata y desactiva autoexec. Workflow y CI aún pendientes; artefactos de referencia versionados tras revisión, no confiar en métricas aisladas.

> E0020 postprocesamiento [run 43288965340](https://github.com/mxlzz/ACD/actions/runs/43288965340) generó ROI/3 crops y métricas sin rerender, pero el `git add` falló por regla ignore sobre nuevos docs experimentales. Fix allowlist `git add -f` solo para E0020.md y preview/JSON. Publicación pendiente nueva ejecución. Métricas globales E0020 ya verificadas.

> E0020 [run 43287450449](https://github.com/mxlzz/ACD/actions/runs/43287450449) **success**: Native/Standard mejor RMSE global y edge gradient que High/Super con 320×240 24 spp ×3 y ref 512 spp ×2; discrepancia referencias 0.06105 y orden contra referencia 2 no idéntico. Postprocesamiento de EXR existente para regiones/crops ref-only y reporte E0020 documentado, **ejecución pendiente** en nuevo workflow. No gastar otro render hasta revisar datos.

> F3 corrección región 2026-11-12: `region_cli` ahora incluye `NATIVE_COMP_OIDN` y SID4 (si existen) para comparar AOV/ROI con ACD. E0020 ya iniciado en commit anterior, por lo que se considerará reprocesamiento desde los mismos EXR, sin relanzar renders. Nuevo test EXR y CI pendientes.

> **E0020 preparado, 2026-11-12:** Cozy Kitchen versionada y SHA fijo; workflow único para Blender5 CPU 320×240 (24 spp ×3 seeds; 512 spp ×2 refs), Standard/High/Super/native, AOV y regiones. Runner externa con autoexec desactivado. Generador de resumen reproducible y tests. **Sin datos reales E0020 hasta ejecución.** La fase 512p/FHD exige validar primera convergencia y coste.

> **E0019 ✅ completado (2026-11-12):** Cozy Kitchen (Nicole Morena, CC BY-SA) `benchmarks/scenes/cozy_kitchen.blend` 7.33 MiB, SHA256 `5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395`, GitHub Actions [#43285518302](https://github.com/mxlzz/ACD/actions/runs/43285518302) success y archivo verificado en tree; Blender5.0.1 Cycles 192² ×4 spp render OK, sin assets faltantes. [E0019](experiments/E0019.md). Próxima etapa de calidad: multi-seed + dos refs a 512² y detalle/crops. Se reemplazó import automático con workflow de revalidación read-only manual; test SHA en CI. Escena profesional del usuario no publicada.

> E0019 [Run 43285264648](https://github.com/mxlzz/ACD/actions/runs/43285264648): Blender5.0.1 abrió Cozy Kitchen y renderizó Cycles 192×192 a 4 spp, sin dependencias faltantes; 1077 objetos, 175 materiales, 2 cámaras. El bloqueo de publicación era `.gitignore` para .blend; fix limitado a `git add -f benchmarks/scenes/cozy_kitchen.blend` (sin modificar regla general), reintento pendiente.

> E0019 primer import [43285007004](https://github.com/mxlzz/ACD/actions/runs/43285007004) falló antes de Blender debido a un chequeo de cabecera `BLENDER` que no contempla .blend comprimidos. Se conserva tamaño esperado, se registra tipo/bytes, se delega validación al parser Blender5 real. Nueva ejecución pendiente. No se publicó binario.

> **E0019 iniciado 2026-11-12:** escena oficial Blender 3.5 Cozy Kitchen de Nicole Morena, 7.3 MiB, CC BY-SA, workflow que *solo publica el binario si Blender5.0.1 lo abre y renderiza sin dependencias faltantes*. [E0019](experiments/E0019.md). El render funcional y commit binario están pendientes de prueba al escribir este documento. Escena del usuario no se sube.

> **E0018, 2026-11-12:** escena arquitectónica real entregada. Inventario Cycles FHD con 137 objetos, 86 materiales y 121 imágenes packed; detalles [E0018](experiments/E0018.md). No subir original por rutas internas y activos BlenderKit/Blendkit de terceros. Prioridad: abrir con Blender5, probar dependencias, render mínimo, multi-seed y referencias. Workflow portátil por verificar, F5 suspendido.
> **E0017 2026-11-12 validado:** fixed-PFM ISA run #43237525190, inputs idénticos SHA en AMD AVX2 vs AVX-512, diferencias numéricas ~7.41e-7 por hardware; OIDN v2.3.3/v2.5.1 outputs iguales **dentro** de cada CPU para esta escena. [E0017](experiments/E0017.md). **F3 pendiente representatividad:** datos .blend arquitectónicos reales 1080p+ o dataset público equivalente, con detalle auténtico para confrontar RMSE/MAE/gradiente y crops; no hay mejora ACD verificada. **CI:** workflows de render M3.9/ V2 y diagnóstico ISA pasan a manual, quality gate automático; evita rerun caro cada commit. Guardar estado y resultados verificados, docs de experimentos y PR #10 draft. Quality pendiente en este commit.

> **F3 E0016 2026-11-12 completado:** fixture `detail_target` 320×240 y métricas de gradiente vs RMSE contrastan aparente nitidez de Super con fidelidad; OIDN nativo superior en RMSE y error de bordes en los ejemplos. [E0016](experiments/E0016.md), [run 43235485653](https://github.com/mxlzz/ACD/actions/runs/43235485653), quality 90 tests. **F2 incertidumbre nueva:** outputs 2.3.3/2.5.1 CLI varían entre jobs aunque mismos SHA de binarios, pero entradas difieren ligeramente; posible backend AMX-FP16, **ISA probe** con PFM determinista pendiente. F5/F6 requieren escenas reales de detalle fuera del conjunto de desarrollo, no seguir optimizando 320×240 sintético.

> **F2 E0015 ejecutado 2026-11-12:** aislada versión CLI OIDN 2.3.3/2.5.1 con mismos PFM/flags [run 43234478588](https://github.com/mxlzz/ACD/actions/runs/43234478588). Glass salidas idénticas; interior pequeñas diferencias, 2.3.3 mejor RMSE de 3/3 semillas, sin generalización. [E0015](experiments/E0015.md). **F3 siguiente:** nuevo `detail_target` 320×240, metrología borde/flat por referencia, workflow a verificar. **F4:** estado y requerimientos de ProDen/StatMC/StatER en [EXTERNAL_DENOISER_PRIOR_ART.md](EXTERNAL_DENOISER_PRIOR_ART.md). Eliminar duplicación de workflow M3.9 como optimización de CI, dejar addon estable intacto.

> **F2 / E0014 ejecutado, 2026-11-12:** OIDN 2.5.1 CLI validado en [run #43233365334](https://github.com/mxlzz/ACD/actions/runs/43233365334); no mejora frente a OIDN compositor en medias de RMSE/gradiente de dos fixtures. No hay equivalencia de prefilter. Nuevo comparador aislado CLI 2.3.3 vs CLI 2.5.1 diseñado; workflow y CI de esta revisión pendientes. Seguir F3 con textura fina/profesional después de interpretar aislado. Referencia [E0014](experiments/E0014.md).

> **F2 verificación en curso 2026-11-12:** CI Python aprobada #43233365339 (89 pruebas). El workflow OIDN nuevo no disparó automáticamente; los pasos standalone OIDN 2.5.1 se anexaron al workflow M3.9 ya operativo como puente temporal, sin cambiar algoritmos. Esperar evidencia real, depurar errores y fijar resultados E0014. Producto estable sin cambios.

> **F2 candidato 2026-11-12:** CLI standalone OIDN 2.5.1, conversión PFM y pruebas; workflow de mismos AOVs por seed preparado, **CI aún pendiente**. No asumir equivalencia entre prefilter de Blender y comportamiento por defecto de OIDN standalone; revisar run, documentar E0014 y priorizar escena con detalle fino. F1/F3 CI previa aprobada #43231850644; addon estable intacto.

> **F3 código candidato — 2026-11-12:** métrica de error de gradientes RGB en referencia y por región implementada con pruebas sintéticas; CI aún pendiente, ningún ranking de escena real obtenido. Revalidación: F1 documentación creada, F2 auditoría inicial realizada, F3 falta ejecución/validación en renders representativos. Guías operativas en [ACD_V2_PLAN.md](ACD_V2_PLAN.md) y [test_protocol.md](test_protocol.md).

> **NUEVA PRIORIDAD 2026-11-12:** [ACD V2 — OIDN y evaluación de detalle](ACD_V2_PLAN.md), [Issue #9](https://github.com/mxlzz/ACD/issues/9). El programa histórico M3/SID a continuación se conserva por trazabilidad y **ya no es la puerta obligatoria hacia mejoras**. Se revalidó la pertinencia de la infraestructura M1–M3 y E0013. F1 en proceso (documentación/CI pendiente), F2 auditoría estática iniciada, F3 métricas de detalle pendientes. No se modificó producción.

# ACD — Roadmap de investigación y desarrollo

**Documento rector del plan.** Revisión inicial: 2026-11-11. Vigente para la rama `dev/acd-m2-real-scenes-regions`.

Este plan es una **referencia revisable**, no un calendario ni una promesa de superioridad. Cada hito requiere evidencia para avanzar. Las prioridades y el esfuerzo relativo pueden cambiar cuando los experimentos contradigan una hipótesis.

## Objetivo y límites

Desarrollar un sistema de reconstrucción para Blender/Cycles capaz de comparar y, cuando sea demostrable, mejorar la calidad obtenida a igual presupuesto de muestras frente al denoising nativo. El primer producto será un denoiser de **fidelidad radiométrica** para renders estáticos. La superresolución y el tratamiento de fotografía serán módulos posteriores que compartirán infraestructura de evaluación, **no necesariamente el mismo modelo de ruido**.

- La referencia pública estudiada de Super Image Denoiser es el código histórico disponible en GitHub. **No se ha demostrado equivalencia con SID comercial 5.3.**
- Un mejor RMSE en una escena **no** prueba superioridad general ni superioridad perceptual.
- La capacidad de ejecutar un nodo en Blender **no** prueba que la imagen resultante sea correcta.
- Las referencias finitas de 1024/4096 spp no son automáticamente ground truth convergido.
- Para la investigación fuente, evidencias e hipótesis véase [research_foundations.md](research_foundations.md).

## Control de rumbo en cada cambio

**Protocolo exigible:** [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md). **Registro de decisiones por commit:** [DECISION_LOG.md](DECISION_LOG.md). La CI comprueba que cada nuevo commit actualice conjuntamente roadmap, estado y bitácora. Esta verificación **no reemplaza** el juicio técnico ni las pruebas de Blender.

**Hito activo:** M3 / [Issue #7](https://github.com/mxlzz/ACD/issues/7). La especificación [M3_SID_REFERENCE_SPEC.md](M3_SID_REFERENCE_SPEC.md) y el constructor independiente `addon/sid_reference.py` están implementados en la rama experimental; no reemplazan al addon estable.

**Puertas comprobadas en Actions (2026-11-11):** [quality gate #43098851163](https://github.com/mxlzz/ACD/actions/runs/43098851163), [Blender 5.0.1/5.3 smoke #43098851162](https://github.com/mxlzz/ACD/actions/runs/43098851162), y [SID 3.6 original vs port 5.0 graph contract #43098851161](https://github.com/mxlzz/ACD/actions/runs/43098851161) terminaron correctamente. Este último reportó `passed=true`, `errors=[]`, solo para invariantes estructurales limitados. 5.3 omite benchmarks pesados por configuración.

**Puertas verificadas después de la corrección:** [contratos SID 3.6/5.0 #43101708644](https://github.com/mxlzz/ACD/actions/runs/43101708644) `success` con artifact de **tres JSON** ([descarga](https://github.com/mxlzz/ACD/actions/runs/43101708644/artifacts/13890459701)); [quality gate #43101708666](https://github.com/mxlzz/ACD/actions/runs/43101708666) `success`; [Blender smoke #43101708862](https://github.com/mxlzz/ACD/actions/runs/43101708862) `success` en 5.0.1/5.3. Los runs antiguos en cola no explican por sí solos el origen del problema (Issue #8), que ya no bloquea las pruebas nuevas.

**M3.5 Standard observado:** run [43104673773](https://github.com/mxlzz/ACD/actions/runs/43104673773) \`success\` con 3 entradas EXR exactamente idénticas en passthrough. Diferencia RGB Standard RMSE 0.03285426 (HDR RMSE 0.04103480); alfa RMSE 0, sin demostración de paridad píxel ni superioridad. Artifact conservado en el run.

**M3.6 operadores sin OIDN validados:** [run 43106813982](https://github.com/mxlzz/ACD/actions/runs/43106813982) `success`. ADD/MULTIPLY/HDR idénticos en RGB/alfa, y recombinación alfa diferencia máxima ~5.96e-08. Se descarta una gran brecha de estas operaciones en el fixture de prueba, no en todas las combinaciones posibles.

**M3.7 OIDN aislado aprobado (evidencia real):** [run #43107260820](https://github.com/mxlzz/ACD/actions/runs/43107260820) y [artifact #13895310157](https://github.com/mxlzz/ACD/actions/runs/43107260820/artifacts/13895310157), control de entrada válido. Diferencias RGB RMSE interversiones: Fast guiado 0.03285428 (coincide con Standard integral 0.03285426), Accurate guiado 0.03060210, emisión Accurate sin guías 0.06191731, alfa RGB guiada 0.00618145, Diffuse Direct 0.00425341. Emisión ROI HDR 0.21570960 (High/Super globales en esa región 0.22306/0.23224). M3.6 ya había verificado identidad práctica de operaciones de mezcla.

**M3.8 error de sintaxis del workflow observado:** [run #43111531413](https://github.com/mxlzz/ACD/actions/runs/43111531413) terminó antes de crear jobs; un nombre de paso con `Archive matrix: EXRs` tenía un `:` sin entrecomillar. Corrección localizada al YAML; el experimento aún no se ejecutó. No se modifica metodología por un error de orquestación.

**M3.8 resultados CI comprobados:** [run 43111684409](https://github.com/mxlzz/ACD/actions/runs/43111684409) y [artifact 13896511879](https://github.com/mxlzz/ACD/actions/runs/43111684409/artifacts/13896511879) con 8 legacy + 24 port. Blender5 OIDN 2.3.3 localizado. HDR=false acerca algunas salidas históricas, pero produce grandes cambios en emisiones dentro de Blender5 (RMSE 0.9046); no falsear radiancia con esa configuración.

**M3.9 primera corrida completada, evidencia no concluyente:** [run 43112553045](https://github.com/mxlzz/ACD/actions/runs/43112553045). Glass Lobby: ACD Standard/OIDN compositor RMSE idéntico 0.14789 vs Raw 0.32117, referencias 384 spp discrepancia relativa 0.31496 (alerta). Classroom: noisy seeds y refs prácticamente idénticas, control de diversidad falla; no establecer ranking multisemilla. Mejorar protocolo antes de tomar decisiones algorítmicas.

**M3.9 segunda corrida ejecutada — no se demostró ventaja sobre OIDN nativo:** [CI #43113414513](https://github.com/mxlzz/ACD/actions/runs/43113414513), tres seeds y dos refs de 1024 spp en Glass Lobby e interior emisivo. Ambos pasan cribado de diversidad (no prueba de independencia/convergencia). RMSE medio Glass: Standard/OIDN 0.14833401, High 0.17022242, Super 0.17611973; emisivo: Standard/OIDN 0.08236044, preservación emisión 0.08267392, High 0.08670461, Super 0.09241571. Variantes SID4 tampoco superaron nativo. Datos detallados y limitaciones en [E0013](experiments/E0013.md). El incidente Classroom ya estaba en E0007: evitar reiteración de pruebas inválidas.

**Siguiente requisito de calidad:** recibir un `.blend` real de arquitectura autorizado y representativo, con recursos empaquetados, para probar ACD fuera de los fixtures de desarrollo. [Protocolo de ingreso](PRO_SCENE_INPUT.md) y runner local existente `scripts/run_scene_benchmark.py`. Ningún cambio algorítmico en producción hasta definir una hipótesis con validación fuera de escena. **No fusionar PR #4**.

**M3.9 segunda corrida candidata:** sustituir Classroom inválido por `interior_emissive`, referencias 1024 spp ×2 con semillas distintas y 3 low-spp noisy seeds, activar ablación preexistente preservación de emisión. Registrar la diferencia directa ACD vs nativo y SID4 para descubrir candidatos redundantes. Incluir flags de validez que impidan conclusiones cuando semilla/reference fallan. **CI pendiente**.

**M3.9 preparado, pendiente CI:** dos escenas Cycles (glass_lobby procedural y Classroom CC0), 160×120, low spp 24×2 semillas; dos referencias independientes de 384 spp; medir SID4 Standard/High/Super, ACD Standard/High/Super y nodo nativo OIDN compositor sobre los mismos pixels. Revisar coincidencia de rankings entre referencias y dispersión entre seeds; esto sigue siendo piloto de baja resolución, no superioridad certificada.

**M3.8 ensayo configuracional implementado, resultado pendiente:** Nuevo workflow `sid-oidn-parameter-matrix.yml`: 4 filtros × HDR on/off × Quality High/Balanced/Fast Blender5 (24 outputs) contrastados contra 8 salidas correspondientes de Blender3.6. Las fuentes oficiales distinguen `Prefilter`, HDR y Quality; la última opción no es configurable del mismo modo en Blender3.6. Registrar deltas *entre implementaciones* y efectos de cambios *dentro de Blender5*, sin llamar “mejor” al candidato que más se parezca al histórico. Guardar inputs, hashes, EXR, mapas. CI pendiente.

**Siguiente gate M3.8:** auditar diferencias OIDN de versión/configuración y ensayar ablaciones de `Prefilter`, `Quality`, `HDR` con exactamente el mismo EXR, sin forzar convergencia visual por afinado arbitrario; luego validar contra escenas Cycles complejas y referencias suficientemente convergidas. **No promover M3 ni fusionar PR #4 por coincidencia estructural o un solo fixture sintético.**

**M3.7 próximo control:** OIDN directo aislado, con prefilters Fast/Accurate, guías, emisión y alfa, inputs EXR congelados. Nuevo workflow `sid-oidn-numeric-parity.yml` candidato; CI pendiente al commit. Este experimento deberá determinar si las divergencias se manifiestan antes de ensamblar High/Super, pero no certifica causa exacta ni versión OIDN equivalente.

**M3.5 High/Super medidos:** [CI #43106273482](https://github.com/mxlzz/ACD/actions/runs/43106273482) completada, artefacto EXR/NPZ [13894002202](https://github.com/mxlzz/ACD/actions/runs/43106273482/artifacts/13894002202). Passthrough de 15 AOV válido. High RGB RMSE 0.06531013, Super 0.06788146; región emisiva High 0.22305557 y Super 0.23223786; alfa global ambos ~0.0038727. **No es comparación contra ground truth** ni identifica causas de diferencias.

**M3.6 objetivo inmediato:** descartar/medir diferencias de operaciones del compositor (MixRGB → ShaderNodeMix ADD/MULTIPLY/HDR; SepRGBA/CombRGBA → SetAlpha), sin OIDN, usando entradas EXR congeladas y salidas comparables. Implementación del workflow `sid-operator-numeric-parity.yml` como candidato, CI pendiente. Solo después aislar cambios de backend OIDN y realizar test con escenas reales.

**M3.5 fallo de orquestación observado:** en [run 43106081661](https://github.com/mxlzz/ACD/actions/runs/43106081661), pytest del fixture aprobó pero la invocación directa de script impidió importar el namespace `scripts`. Ajustar comando a `python -m scripts.sid_highsuper_numeric_fixture` y equivalente de comparador; no cambiar datos, grafo ni tolerancias. Nueva CI pendiente.

**M3.5 High/Super siguiente prueba:** workflow \`sid-highsuper-numeric-parity.yml\` preparado con 15 AOV, datos congelados, controles de lectura por Blender y diferencias RGBA/ROI. **CI pendiente**. Si pasa el control de entradas y genera métricas, registrar el alcance; no cerrar M3 sin analizar el backend y escenas reales.

**M3.5 observación real de CI:** [#43104453238](https://github.com/mxlzz/ACD/actions/runs/43104453238) ejecutó exitosamente upstream Standard en Blender 3.6, pero no el port Blender 5 porque OutputFile estaba por defecto en media MULTI_LAYER_IMAGE; `OPEN_EXR` solo se permite tras fijar `media_type="IMAGE"`. Corrección mínima en driver para Blender 5. **Reejecución pendiente; no interpretar todavía deltas del denoiser.**

**Refuerzo de método M3.5 (antes de resultados):** el control de passthrough se aplica por separado a imagen ruidosa, albedo y normal, con comparación entre versiones; las diferencias de ambos compositores respecto del EXR de origen se reportan, pero no se confunden con un efecto OIDN. Corrige además el conteo de píxeles sin máscara. El criterio de salida mantiene una tolerancia de entrada cross-version de 0.001 y salidas finitas. Este refinamiento no equivale a ejecución aprobada.

**M3.5 implementado como experimento candidato (verificar CI):** `.github/workflows/sid-numeric-parity.yml` genera imagen/albedo/normal en EXR lineal con SHA-256, ejecuta SID Standard upstream (Blender 3.6.23) y port Standard (5.0.1), guarda passthrough y outputs, reporta diferencias RGB HDR/alfa y mapas firmados. Su entrada sintética 96×64 no sustituye escenas Cycles. El control de passthrough (máx absoluto ≤0.001) evita atribuir al filtro diferencias en lectura/escritura. **CI aún pendiente al momento de este commit**. Una ejecución fallida no invalida el método sin inspeccionar sus logs. High/Super continuarán una vez confirmado Standard.

**Siguiente etapa M3.5 (criterio de aceptación):** ejecutar SID histórico en Blender 3.6 y SID Reference en 5.0 sobre **exactamente el mismo EXR/guías/AOV**. Guardar hashes de entrada, versiones, todos los outputs (RGB/alpha), mapas de error HDR, configuraciones OIDN y distinción explícita entre desviaciones de backend y desajustes de cableado. Empezar con Standard y luego High/Super; no probar optimización adaptativa ni declarar identidad pixel a pixel antes de medir. PR #4 permanece draft.

## Prioridad rectificada: replicar SID antes de optimizar ACD

La implementación actual `addon/acd_blender.py` está **inspirada en** SID, pero no es un port fiel. La [auditoría de diferencias](sid_parity_gap.md) detectó desajustes concretos (prefiltrado Standard, guías de emisión, alfa, lectura de Noisy Image y semántica de nodos). **La prioridad inmediata pasa a ser M3 (Issue #7)**: construir un modo de referencia SID 4.0 históricamente fiel en Blender 5.x y verificarlo, **antes** de declarar alguna mejora de ACD sobre SID. Los benchmarks M2 siguen disponibles como infraestructura y datos; los ensayos de optimización M4 quedan pospuestos hasta tener baseline de SID validado. El código actual no debe denominarse réplica fiel.

## Escala de esfuerzo relativo

**S** = cambios localizados y pruebas automáticas; **M** = varias piezas de código y nuevos datos de prueba; **L** = experimentación significativa, dependencia de escenas/referencias, posible trabajo GPU; **XL** = investigación abierta o entrenamiento/integración con otros motores. Estas etiquetas NO indican fechas ni duración asegurada.

## Etapas, dependencias y condiciones de salida

| Hito | Estado | Prioridad | Esfuerzo | Condición de salida verificable |
| --- | --- | --- | --- | --- |
| **M0 — Base de ACD Core + Lab** | **Completado**, PR #1 fusionado | Cerrado | M | Addon experimental, laboratorio numérico, smoke de Blender y CI |
| **M1 — EXR y comparación controlada** | Implementado experimentalmente, PR #3 abierto | Alta | M | EXR/AOV con reconstrucción verificada, resultados por método y metadatos, tests verdes; después fusionar si pasa revisión |
| **M2 — Escenas reales y análisis regional** | En curso, PR #4 abierto | Media (infraestructura de M3) | L | Dos o más escenas complejas reproducibles, ROIs, diferentes muestras **verificadas**, evaluación de referencias y casos fallidos |
| **M2.1 — Validez estadística del laboratorio** | En curso / requisito de M2 | Alta (soporte de M3) | M–L | Control explícito de independencia/diversidad de ruido y de referencias, muestreo multi-escena y congelación de datasets |
| **M3 — Réplica funcional de SID público 4.0 para Blender 5.x** | Prioridad rectificada, Issue #7 | **Máxima (ahora)** | L | Auditar fidelidad al SID público por etapas, HDR/alpha/reflejos/transmisión, con comparaciones justas a OIDN/OptiX |
| **M4 — Fusión adaptativa, H-01/H-03** | Hipótesis | Alta, tras M2/M3 | L–XL | Pesos locales/pasada por componente probados en escenas y semillas no usadas para calibrar; evidencias y ablaciones |
| **M5 — Estadística y muestreo, H-04** | Investigación | Media, tras M4 | XL | Buffers de incertidumbre confiables; prueba contra multimuestreo de igual presupuesto y contra filtros existentes |
| **M6 — Upscale HDR de renders, H-05** | Diseño futuro | Media, tras M3/M4 | L–XL | Comparación 2× contra bicúbico/Lanczos y método aprendido con referencia renderizada realmente a resolución alta |
| **M7 — Fotografía/RAW, H-06** | Diseño futuro | Baja por ahora | XL | Pipeline distinto para ruido fotográfico, datasets con referencia, control de color y resultados por objetivo de fidelidad/percepción |
| **M8 — Producto y distribución** | Futuro | Depende de resultados | L | API/instalador estable, rendimiento, perfil de calidad reproducible, licencias y compatibilidad Blender |

### M2 / M2.1: soporte del benchmark; subordinado a la validación SID/M3

**Seguimiento operativo:** [Issue #5 — Validez de muestreo, referencias y métricas](https://github.com/mxlzz/ACD/issues/5). El issue incluye los criterios de aceptación y evidencia que deben cerrarse antes de atribuir mejoras de calidad al algoritmo.

**Avance M2.1 (2026-11-11):** control de máscaras con SHA-256 por pertenencia real de píxeles, diagnóstico de incertidumbre de referencias finitas y comprobación de diversidad de inputs sin declarar independencia estadística. Pruebas automatizadas añadidas y E0008 repetido íntegramente con resultados reproducidos ([E0010](experiments/E0010.md)). La segunda escena procedural de vidrio y metal ([E0011](experiments/E0011.md)) favoreció a Standard; aún faltan escenas profesionales externas y convergencia de referencia.

1. **Cerrar las anomalías de muestreo de Classroom (E0007):** ninguna estadística multi-seed es válida por el solo hecho de cambiar un número. El laboratorio ya bloquea rankings cuando imágenes supuestamente distintas son casi idénticas. Investigar causa; no dar por demostrado el efecto con el chequeo heurístico de diversidad solamente.
2. **Revalidar el agregador regional (E0008):** repetir el flujo completo después de corregir el bug `seed_aggregate.json` interpretado como carpeta; documentar la máscara fija y las diferencias de MAE/RMSE. Mantener sin activar por defecto la preservación de emisión.
3. **Obtener una segunda escena arquitectónica exigente** (vidrio/especular/indirecta) con licencia y procedencia registradas, sin subir assets ajenos a Git. Repetir AOV closure, muestras verificadas y 2 referencias con distinta secuencia de muestreo.
4. **Subir progresivamente a resoluciones representativas** y ajustar las muestras según convergencia, sin gastar CPU en referencias que no permitan comparar métodos con precisión.
5. **Análisis por región:** vidrio, metal, superficies difusas, iluminación indirecta y emisores. Usar ROI fijadas antes de ver resultados y AOV como diagnóstico de contribución, no como IDs de materiales.
6. **Añadir métrica perceptual HDR** con condiciones de exposición declaradas, además de RMSE/MAE/p95, y revisar recortes a tamaño nativo.
7. **Cerrar o descartar hipótesis fallidas:** las conclusiones negativas también quedan documentadas y no se incorporan al motor.

**E0012:** [Ablación de guías Albedo/Normal](experiments/E0012.md): High mejora sin guías intermedias, Super no. Normal sin Albedo no es válido en OIDN de Blender. La [auditoría del código de Cycles v5.0.1](cycles_guide_source_audit.md) demuestra que el renderer ya sigue ciertos rebotes especulares; H-01 ahora investiga la correspondencia de guías por subpase en lugar de duplicar esa lógica. Seguimiento operativo: [Issue #6](https://github.com/mxlzz/ACD/issues/6).

### M3: replicar SID público y normalizar su evaluación

**Issue principal:** [#7 — Réplica SID 4.0 para Blender 5.x](https://github.com/mxlzz/ACD/issues/7). Diferencias auditadas en [sid_parity_gap.md](sid_parity_gap.md). La prioridad es funcional (grafo, parámetros, passes y outputs), **antes** de comparar calidad o desarrollar filtros nuevos.

- Configurar exactamente la semántica de las contribuciones directas/indirectas y la segunda pasada tal como aparece en el SID público; comparar también emisión y alfa. La documentación del algoritmo **no** garantiza reproducir el código comercial.
- Registrar versiones OIDN, Blender, prefiltrado, guías, render backend, memoria y tiempo. Evitar comparar configuraciones o sample counts diferentes.
- Incluir OIDN nativo, OptiX nativo cuando la GPU esté disponible, Standard/High/Super y ablaciones con/sin guías por contribución.
- Criterio de salida: evidencia reproducible sobre varias escenas y semillas, mostrando también pérdidas en regiones donde cada modo falla.

### M4: hipótesis adaptativas (investigar, no prometer)

- **H-01:** condicionamiento de guías por tipo de señal (un normal/albedo del primer hit puede no representar el detalle dentro de reflejos o de cada pase).
- **H-03:** una fusión por región/píxel, con pesos calculados sin mirar la referencia de test, puede mejorar la curva error-tiempo en imágenes no vistas.
- Baselines obligatorios: mejor modo global fijo, interpolaciones fijas, mapas aleatorios/constantes, ablation sin guía.
- Bloquear sobreajuste: separar conjuntos de calibración, validación y prueba por **escena**, no solo por píxel.
- Si no mejora en datos no vistos, no se integra; volver a M3 o rediseñar la hipótesis.

### M5 a M7: exploraciones sin compromiso de adopción

- **M5:** StatER/StatMC proponen estadísticas por muestra que Cycles no entrega directamente en el EXR usual. Comenzar por muestreos pareados y mapas de varianza estimada; la integración dentro del renderer es una opción avanzada, no una dependencia inicial.
- **M6:** distinguir nitidez inferida de detalle realmente recuperado. Probar modelos específicos de upscale y/o OptiX SDK (la disponibilidad del SDK no implica una opción idéntica en el nodo de Blender).
- **M7:** OIDN `RT` está documentado para imágenes de ray tracing, no para ruido de cámara. Reusar la infraestructura, con algoritmos de fotografía/RAW específicos y benchmark aparte.

## Reglas de promoción de una modificación al producto

1. **Corrección funcional:** sintaxis, pruebas y Blender real pasan; no alterar archivos de producción sin backup.
2. **Validez científica:** inputs comparables, seed-diversity y referencia controladas, métricas y recortes auditables.
3. **Calidad consistente:** mejora frente a un baseline definido sin una regresión importante en una clase relevante de materiales o región; registrar también tiempo y memoria.
4. **Reproducibilidad:** commit, scene hash, Blender version, AOV, muestras, semillas/patrón, imagen lineal y JSON de resultados quedan identificados.
5. **Revisión de licencia:** código de terceros, pesos, datasets y archivos `.blend` pueden tener licencias distintas.

## Registro persistente y actualizaciones

- **Este archivo:** qué se pretende hacer y por qué prioridad.
- [research_foundations.md](research_foundations.md): evidencia externa y matriz de trazabilidad entre fuentes e hipótesis.
- [STATUS.md](../STATUS.md): último estado observado; jamás sustituirlo por planes futuros.
- [experiments/](experiments/): pruebas E0001+, incluyendo hallazgos negativos y limitaciones.
- Issues / PR: implementación y validación antes de fusionar.

Al cerrar una etapa o cambiar de dirección, actualizar **STATUS**, este roadmap y las entradas de investigación asociadas. No inferir que una tarea está terminada por la existencia de código o de una ejecución de Actions.

> **E0019 validated fixture:** Official Cozy Kitchen by Nicole Morena CC BY-SA at benchmarks/scenes/cozy_kitchen.blend; Blender 5.0.1 smoke checked, SHA in .audit.json. Quality benchmark pending.

> **E0020 numeric benchmark completed:** Cozy Kitchen 320×240 24 spp ×3, 512 spp ×2, reports and 3 reference-only region crops versioned at [E0020](experiments/E0020.md). OIDN native still baseline. No F5 algorithm until reference convergence/detailed material validation.

> **E0022 held-out scene validated and imported:** MIT Terraced Houses of Yunus Emre Karaman, 3MB, authored .blend+license SHA pinned; Blender5 Cycles smoke passed; next evaluate native baseline vs ACD without optimizing on held-out data.

> **E0021 complete:** 512x482 preserves source ratio, 24spp×3 and refs1024spp×2; ref disagreement/raw ratio 13.5%, consistent rankings. Three ROI crops+2-reference averages stored at [E0021](experiments/E0021.md); native OIDN still benchmark leader. Not a F5 algorithm improvement.

> E0023 reporte permanente: exterior nocturno Terraced Houses MIT, discrepancia Raw/OIDN en RMSE vs MAE; concentración de error HDR y AOV más 3 recortes desde referencias en [E0023](experiments/E0023.md). Ninguna mejora de denoiser probada.

> E0028 import: Low-Poly Island MIT by Yunus Emre Karaman, 2.62MB, source pinned and smoke Cycles validated (see benchmarks/scenes/low_poly_island.audit.json); unexamined as ACD denoiser benchmark at this commit. Quality test to follow.

> E0030 reference-controlled Island MIT eight-panel emission diagnostics stored in benchmarks/results/island_e0030; numerical regional checks and ROI in analysis.json; no OCIO or perceptual claim.

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
