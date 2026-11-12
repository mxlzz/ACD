# ACD V2 — Programa OIDN / calidad de detalle

Vigente desde 2026-11-12. [Issue #9](https://github.com/mxlzz/ACD/issues/9). Rama experimental `dev/acd-v2-oidn-detail-eval`, apilada sobre PR #4, **no es un reemplazo del addon publicado**.

## Pregunta principal
¿Podemos mejorar la fidelidad de detalle de OIDN moderno en renders arquitectónicos sin empeorar ruido residual, error HDR, artefactos o coste de manera injustificada? El objetivo es comprobación, no una promesa de superioridad. SID conserva valor como referencia comparativa, no como arquitectura obligatoria.

## Baselines inequívocos
- **Baseline operativo:** Blender 5.0.1, nodo OIDN del compositor Accurate/High/HDR con guías albedo y normal, exactamente la ruta medida en E0013. No confundirlo con denoise interno de Cycles ni con OptiX.
- **Baseline externo a implementar:** Open Image Denoise v2.5.1, mismo EXR/guías. No atribuir mejoras de 2.5.1 a calidad sin medir; su changelog incluye correcciones de seguridad y robustez.
- **Competidores:** Cycles OIDN interno y OptiX cuando la plataforma lo permita; SID público 4.x reconstruido se identifica `SID4_*`, distinto de SID comercial 5.x. No afirmar nada sobre SID 5.x sin binario/caso real.
- Toda comparación de *algoritmos* usa las mismas matrices de entrada; toda comparación de *Blender 4.x vs 5.x* separa primero cambios de Cycles en noisy beauty/AOV de cambios de denoiser.

## Fases, orden y puerta de salida

### F1 — Gobierno y preservación (actual)
Documentar giro con causa y evidencia; Issues/PR, mantener M0–M3/E0001–E0013 y sus resultados negativos, congelar addon estable. **Salida:** documentos y CI de trazabilidad aprobados.

### F2 — Auditoría y reproducibilidad OIDN (en curso)
Inspeccionar v2.5.1: runtime, preprocesamiento HDR, selección por guías, U-Net, pesos, entrenamiento, dispositivos y licencia. Primero CLI/binario oficial o biblioteca independiente sin fork; fork solo al necesitar cambios. **Salida:** protocolo fijo de igualdad de EXR, versión OIDN comprobada y tiempos; informe reproducible de 2.3.3 vs 2.5.1. Comparar pesos/configuración antes de inferir causalidad.

### F3 — Laboratorio de calidad de detalle (en curso)
Evaluar gradientes de color en espacio HDR comprimido usando máscara derivada **solo de la referencia**; reportar error de gradiente en bordes, razón de contraste en esos bordes y error residual en zonas planas. Son diagnósticos, no una prueba perceptual de 'detalle correcto'. Confrontar frente a error HDR global, MAE, regiones y recortes 1:1; anotar ambigüedad de referencia ruidosa.
**Salida:** pruebas numéricas sintéticas, métricas en el pipeline de batch y al menos dos escenas con semillas distintas y referencias razonables antes de cualquier ranking de calidad.

### F4 — Investigación y ablaciones
Revisión y portabilidad de ProDen (SURE, mezcla/adaptación y requerimientos de estadísticas), StatMC y StatER (estadísticas por muestra). Matriz de costes/accesibilidad de cada buffer en Cycles. **Salida:** seleccionar hipótesis verificable, con controles de mezcla constante/aleatoria y sin entrenamiento o fork prematuro.

### F5 — Candidatos fuera de muestra
Escenas divididas por escena, no por semillas/píxeles: desarrollo/validación/test. Un cambio gana solo si mejora métricas predeclaradas de detalle y globales en test, sin regresiones HDR relevantes. Guardar métricas/decisión por hipótesis y descartar negativas.

### F6 — Producto Blender
Paquete reproducible, licencias y recursos, CPU/GPU, tiempo y memoria, fallback OIDN nativo. Nunca fusionar con producción por éxito del smoke test.

## Riesgos y dependencias
1. E0007: Classroom Blender5 producía entradas casi idénticas con seeds diferentes; excluir de inferencia multi-seed hasta resolver. E0013: escenas 160×120, sin prueba de convergencia; no representan resultados profesionales.
2. Para resolución 1080p+, vidrio y texturas complejas: escena profesional licenciada y empaquetada o dataset abierto nuevo. No subir escenas propietarias a repos públicos.
3. SID comercial 5.x y OptiX requieren accesos/plataforma adicionales; la falta de éstos **no bloquea F1–F3**.
4. GitHub Actions artifacts expiran; conservar permanently scripts, configuraciones, hashes, resultados resumidos, interpretaciones y fallos. EXR extensos fuera de Git, identificados por hash.

## Trazabilidad
[STATUS.md](../STATUS.md) (ejecución real), [DECISION_LOG.md](DECISION_LOG.md) (decisiones por commit), [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) (reglas), [E0013](experiments/E0013.md) (últimos números SID vs OIDN) y [OIDN_SOURCE_AUDIT.md](OIDN_SOURCE_AUDIT.md) (inventario verificable). Este documento prevalece sobre hitos SID históricos en el roadmap anterior.


## Avance verificado 2026-11-12

F1 completado a nivel de gobierno (Issue #9, PR #10, trazabilidad y CI); F2 aisló versiones OIDN CLI 2.3.3/2.5.1 en E0015 (Glass idéntico, Interior pequeñas diferencias). F3 métricas de gradientes y pruebas sintéticas aprobadas, pero aún no validadas perceptualmente en texturas reales; primer fixture específico de lamas/juntas preparado, sin resultado al commit. F4 inspección de repositorios ProDen/StatMC/StatER documentada en [EXTERNAL_DENOISER_PRIOR_ART.md](EXTERNAL_DENOISER_PRIOR_ART.md); ninguno se ha ejecutado ni portado. F5/F6 bloqueadas hasta pruebas de escenas representativas. El roadmap no se reescribe sobre historia; consultar STATUS para verificaciones.


### E0016, 2026-11-12 — control de detalle y de backend

[E0016](experiments/E0016.md) valida que la métrica integrada funciona en escena controlada de lamas/juntas/vidrio, y detecta que ACD Super puede elevar contraste aparente mientras empeora RMSE y error de bordes. F3 **no concluido** por ausencia de escenas profesionales. El cambio de versión OIDN fue sensible a differences de inputs entre runs/posible ISA. Se habilita microensayo de CPU ISA con input sintético SHA fijo, antes de decidir algoritmo. Sin prueba de mejora ACD, no se abre F5.


### Puerta actual después de E0017 (2026-11-12)

Infraestructura, baseline OIDN, métricas de detalle y separación de versiones/hardware verificadas; docs E0014–E0017. Las únicas pruebas de detalle aún son 320×240 sintéticas. El paso próximo es aportar y analizar una escena **realista, sin filtrar contenidos privados** en repo público, y realizar varios seeds y referencias antes de una hipótesis F5. Los workflows pesados permanecen manuales; CI calidad automático. F5/F6 no realizados.
