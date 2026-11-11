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
