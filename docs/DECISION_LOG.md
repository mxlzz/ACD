# Bitácora de decisiones y control de rumbo

Regla: una entrada por cambio/commit posterior a la instauración del protocolo. No reescribir entradas anteriores; añadir una nueva con decisión y resultado.

## 2026-11-11 — Institución de control de rumbo (M3 / Issue #7)

- **Objetivo original revisado:** reproducir SID público fielmente en Blender 5.x, y usarlo como baseline antes de intentar mejoras.
- **Motivo:** la auditoría \`docs/sid_parity_gap.md\` mostró diferencias concretas entre el SID histórico y el prototipo (prefiltrado, emisión, alfa, entradas), mientras que M1/M2 habían avanzado con un algoritmo inspirado en SID sin equivalencia verificada.
- **Decisión:** M3 tiene prioridad absoluta. M2 y el laboratorio permanecen como herramientas; M4/adaptativo en espera. Cada cambio tendrá trazabilidad en ROADMAP, STATUS y esta bitácora.
- **Cambio implementado:** protocolo explícito, comprobador de coherencia documental de commits y tests del comprobador; integración a CI Python.
- **Validación:** pruebas del verificador incorporadas. El resultado real de GitHub Actions debe leerse en el run correspondiente; no se declara aprobado anticipadamente.
- **Limitación:** la CI detecta omisiones documentales, no evalúa por sí sola la calidad del razonamiento o la fidelidad al código SID.
- **Desvío de ruta:** ninguno; la modificación hace exigible la prioridad M3 establecida.
- **Próximo paso:** especificación ejecutable de grafos/sockets de SID público (Standard/High/Super y opciones) para iniciar el modo SID Reference.


## 2026-11-11 — M3.1, especificación de paridad SID antes de escribir código

- **Hito revisado:** M3 / Issue #7. Conforme al protocolo, no se inició optimización de ACD.
- **Decisión:** congelar comportamiento de SID público v4.0 en \`docs/M3_SID_REFERENCE_SPEC.md\`.
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
