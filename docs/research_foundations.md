# ACD — Investigación técnica y trazabilidad de decisiones

**Revisión de fuentes:** 2026-11-11. **Alcance:** síntesis inicial orientada a las decisiones de ACD, NO revisión sistemática exhaustiva de toda la literatura. Se registran propuestas, límites, implementaciones públicas y evidencia producida por el propio proyecto.

Ver [ROADMAP.md](ROADMAP.md) para el orden de desarrollo; [STATUS.md](../STATUS.md) para estado real; [experiments/](experiments/) para resultados y runs de CI. Esta investigación **no implica que se haya probado un algoritmo dentro de ACD**.

## Convenciones de evidencia

- **F — Fuente verificada:** capacidades y restricciones documentadas en papers, manuales y código abierto; la fuente no valida nuestra implementación.
- **E — Evidencia experimental ACD:** resultado medido en un commit/escena concreta, con limitaciones explícitas.
- **H — Hipótesis propia ACD:** idea aún no corroborada; requiere baseline, ablation y evaluación fuera de muestra.
- **B — Brecha/integración:** falta instrumentación o datos de Cycles/Blender para aplicar el método tal cual.

## Fuentes y utilidad práctica

### R01. Super Image Denoiser (SID) público — decomposición composicional

**F:** [Pidgeon Tools, código público GPL-3.0](https://github.com/PidgeonTools/SuperImageDenoiser), archivos `Cycles/SID_QualityHigh_Cycles.py`, `Cycles/SID_QualitySuper_Cycles.py`, `Cycles/SID_Create_Links_Cycles.py`. Nuestra [auditoría específica](sid_source_audit.md).

- High recompone luz directa + indirecta por familia, modula por color de material y filtra la contribución.
- Super filtra directo e indirecto separadamente, suma, aplica color; la implementación pública recompone, procesa emisión/volumen/entorno cuando corresponde, y ejecuta filtrado final; alfa tiene tratamiento distinto.
- **Límite:** código histórico ≠ evidencia de que nuestro grafo sea idéntico a SID comercial 5.3. No se copió código sujeto a GPL.
- **Uso ACD:** referencia verificable de M3; diferencias con OIDN nativo medidas en E0001–E0008, sin deducir superioridad universal.

### R02. Intel Open Image Denoise (OIDN) — baseline e imágenes auxiliares

**F:** [Documentación del filtro RT](https://www.openimagedenoise.org/documentation.html), [proyecto](https://github.com/RenderKit/oidn).

- El filtro de ray tracing admite belleza HDR y opcionalmente albedo y normal; hay prefiltrado de guías; está entrenado para ruido Monte Carlo.
- Las guías ayudan en muchas escenas, pero el resultado puede depender de si corresponden a la señal filtrada.
- **Restricción explícita:** el filtro `RT` no se ofrece como denoiser de fotografías normales.
- **Restricción verificada de Blender:** [código compositor Denoise](https://projects.blender.org/blender/blender/src/branch/main/source/blender/nodes/composite/nodes/node_composite_denoise.cc) y [commit Blender sobre prioridad Albedo/Normal](https://projects.blender.org/blender/blender/commit/e873f6cb154a06018c545549a9993e26ba595e6e) documentan que **Normal no puede utilizarse de forma significativa sin Albedo** en este nodo. E0012 verificó que los resultados «Normal-only» fueron numéricamente idénticos a «sin guías»; esas configuraciones no son dos tratamientos científicos diferentes.
- **Código fuente verificado de Cycles 5.0.1:** el renderer ya sigue determinados rebotes de predominio especular antes de emitir Denoising Normal y Albedo. No suponer que siempre usa el primer hit. La [auditoría de origen de guías](cycles_guide_source_audit.md) recoge las condiciones exactas, el umbral de rugosidad, fuentes y limitaciones.
- **Guías de hits posteriores:** la [documentación OIDN RT](https://www.openimagedenoise.org/documentation.html) explica que para reflejos/transmisión los hits posteriores pueden mejorar el resultado. Cycles implementa parcialmente ese recorrido pero los buffers actuales no están separados por cada subpase. No sabemos todavía si ese desajuste explica las pérdidas de High/Super.
- **Uso ACD:** baseline Standard, comparación de calidad configurada y prueba con/sin guías por componente (M3/H-01); la propuesta de guías de hits posteriores es todavía una hipótesis de integración.

### R03. NVIDIA OptiX denoiser SDK — comparador e implementación alternativa

**F:** [Ejemplo oficial OptiX SDK](https://github.com/NVIDIA/optix-sdk/blob/main/SDK/optixDenoiser/OptiXDenoiser.h), [OptiX Programming Guide](https://raytracing-docs.nvidia.com/optix8/guide/optix_guide.241022.LTR.pdf).

- La biblioteca del SDK tiene guías de normal/albedo, modos AOV, temporal y `upscale2x`; algunos casos de reflejo funcionan mejor con guías de hits posteriores.
- **B:** estas capacidades del SDK no implican que el nodo actual de Blender exponga los mismos modos; GPU NVIDIA, contexto CUDA y buffers compatibles son requisitos de integración.
- **Uso ACD:** comparador bajo mismo input y presupuesto, primera versión mediante función nativa disponible; integración de SDK solo si justificada (M3/M6).

### R04. KPCN — predicción de núcleos para el filtrado Monte Carlo

**F:** [Bako et al., Kernel-Predicting Convolutional Networks for Denoising Monte Carlo Renderings, SIGGRAPH 2017](https://doi.org/10.1145/3072959.3073708).

- La red predice núcleos locales de filtrado informados por entradas auxiliares, en lugar de devolver simplemente RGB final.
- **Uso ACD:** fundamento de la selección de pesos espaciales (H-03) y pruebas de preservación de detalle. **No** se implementó KPCN ni se descargaron pesos.

### R05. Deep Compositional Denoising — Disney Research

**F:** [Zhang et al., EGSR 2021](https://studios.disneyresearch.com/2021/07/30/deep-compositional-denoising-for-high-quality-monte-carlo-rendering/).

- Propone aprender a descomponer un render ruidoso en componentes y guías que luego son procesados con filtros específicos por componente.
- **Distinción crítica:** la descomposición es **aprendida** y parte de estadísticas agregadas por el renderer. No equivale a sumar más nodos OIDN; tampoco está implementada en ACD.
- **Uso ACD:** justificación científica de explorar condicionamiento y selección por componente (H-01/H-03). **B:** necesitaría un dataset apropiado y señales adicionales.

### R06. SVGF — varianza y reconstrucción multiescala/temporal

**F:** [Schied et al., Spatiotemporal Variance-Guided Filtering, HPG 2017](https://research.nvidia.com/labs/rtr/publication/schied2017spatiotemporal/).

- Utiliza estimaciones de varianza de luminancia, acumulación temporal y filtro jerárquico en espacio de imagen para separar ruido y estructura.
- **Uso ACD:** fundamento para comparar filtrado multiescala / mapas de confianza (H-03/H-04).
- **B:** la parte temporal requiere vectores de movimiento, reproyección, historia y control de disoclusiones. No se puede aplicar el mismo procedimiento a una única imagen sin dichos datos.

### R07. StatMC y StatER — correcciones estadísticas Monte Carlo

**F:** [Sakai et al. 2024, StatMC](https://users.cg.tuwien.ac.at/~hiroyuki/StatMC/), [código StatMC](https://github.com/cg-tuwien/StatMC), [Sakai et al. 2025, StatER](https://users.cg.tuwien.ac.at/~hiroyuki/StatER/), [código StatER](https://github.com/cg-tuwien/StatER).

- Estiman estadísticas de muestras de radiancia; StatER incorpora transformaciones Box–Cox, reducción/corrección de varianza y mecanismos de muestreo adaptativo.
- **B:** la implementación pública extiende **pbrt-v3** con un integrador propio y buffers de estadísticas. No es un addon que pueda conectarse directamente al compositor de Blender. Reproducir resultados requeriría una captura estadística válida o modificación del renderer.
- **Uso ACD:** referencia a largo plazo para mapas de incertidumbre y decisiones de muestreo (H-04 / M5); no afirmar que ACD ejecuta StatER.

### R08. NVIDIA NRD — señales distintas y denoising espaciotemporal

**F:** [NRD, repositorio oficial](https://github.com/NVIDIA-RTX/NRD).

- RELAX/REBLUR tratan por separado irradiancia/radiancia especular y difusa y usan G-buffers como normal, rugosidad, profundidad y movimiento; SIGMA se centra en sombras.
- **B:** requiere integración de motor/gráficos, buffers y, para su ventaja temporal, secuencias de fotogramas. No es reemplazo drop-in del nodo Blender.
- **Uso ACD:** bibliografía para tratar reflejos, rugosidad y estabilidad temporal; fase posterior a M4.

### R09. HDR-FLIP — evaluación perceptual de renders HDR

**F:** [NVlabs/flip](https://github.com/NVlabs/flip), [HDR-FLIP paper](https://research.nvidia.com/publication/2021-05_HDR-FLIP).

- Implementa una métrica perceptual de diferencias HDR con exposición controlada, complementaria a MAE/RMSE.
- **Uso ACD:** incorporar evaluación perceptual (M2.1/M3) sin confundirla con la métrica log1p de luminancia actualmente experimental. Declarar parámetros de evaluación y revisar mapas de error.

### R10. Noise2Noise — entrenamiento sin objetivos completamente limpios

**F:** [Lehtinen et al., ICML 2018](https://proceedings.mlr.press/v80/lehtinen18a.html).

- Bajo supuestos estadísticos apropiados, pares ruidosos independientes permiten entrenar restauración sin targets perfectos.
- **Condición fundamental:** independencia/propiedades del ruido, emparejamiento y sesgo deben examinarse. **E0007 detectó que cambiar la semilla no basta para producir pares diferentes en Classroom**.
- **Uso ACD:** posible entrenamiento de selector o modelo pequeño (M4/M5) solo tras demostrar diversidad y analizar sesgos de referencias; no hay entrenamiento hoy.

### R11. Superresolución y restauración fotográfica

**F:** [Real-ESRGAN, Wang et al.](https://github.com/xinntao/Real-ESRGAN), [Restormer, Zamir et al., CVPR 2022](https://github.com/swz30/Restormer), [Handheld Multi-Frame Super-Resolution, Google 2019](https://research.google/pubs/handheld-multi-frame-super-resolution/).

- Real-ESRGAN es una aproximación a SR con degradaciones sintéticas y una prioridad perceptual que puede **inferir detalles** no presentes en el render.
- Restormer es un modelo de restauración fotográfica que aborda ruido y desenfoque; su dominio no es automáticamente el de Cycles.
- La superresolución multifotograma de Google combina observaciones RAW realmente capturadas con pequeños desplazamientos; requiere datos adicionales y un pipeline de cámara, no una única imagen comprimida.
- **Uso ACD:** separar dos objetivos: *fidelidad* a escena/radiancia y *reconstrucción perceptual*; comparar baselines simples antes de modelos aprendidos. M6 (render 2×) y M7 (fotografía RAW) serán módulos específicos.

## Trazabilidad: qué propuesta nace de qué evidencia

| Hipótesis | Origen documentado | Estado de ACD | Validación que la haría aceptable | Roadmap |
| --- | --- | --- | --- | --- |
| **H-01**: guías específicas de componente mejoran reconstrucción | R01, R02, R03, R05 | E0001/E0002 muestran efectos **contradictorios** por escena | Múltiples materiales, ablación de guías, escenas/semillas retenidas | M3/M4 |
| **H-02**: preservar emisión evita borrar detalles luminosos | R01, R08, E0005 | E0006/E0008: mejoras de RMSE regional **mixtas**; MAE puede empeorar | Varias escenas, ROIs fijas, convergencia, sin empeorar métricas globales | M2/M3 |
| **H-03**: selección/fusión espacial supera mejor método global | R04, R05, R06, R08 | **No implementada**; hipótesis conceptual | Pesos sin mirar referencia de test; evaluación out-of-scene, ablations | M4 |
| **H-04**: usar varianza/estadísticas por muestra mejora filtro y sampling | R06, R07, R10 | **No implementada**; faltan buffers confiables | Estadísticas compatibles con Cycles, mejora bajo presupuesto fijo | M5 |
| **H-05**: denoising y upscale 2× guiado por AOV pueden superar el upscale posterior | R03, R11 | **No implementada** | Referencia realmente renderizada a resolución destino, fidelidad de bordes y texturas | M6 |
| **H-06**: una infraestructura común sirve para fotos con motor distinto | R02, R10, R11 | Diseño, **no módulo fotográfico** | Datasets RAW, ruido de cámara, color/ISP, referencias sin alucinaciones | M7 |

## Evidencia ACD propia: lo que realmente sabemos hasta ahora

- **E0001:** recomposición de AOV en escena mínima prácticamente idéntica al beauty. Standard fue mejor que High/Super por RMSE en ese entorno.
- **E0002–E0004:** el modo con menor error varía con resolución, métrica y semillas; un modo global no gana siempre. Referencias finitas; resultados restringidos a interiores pequeños.
- **E0005–E0006:** Classroom real identifica un problema de luces/emisión; conservación de emisión parecía mejorar una ROI, **pero** independencia de semillas no validada.
- **E0007:** en Classroom, cambiar `seed` o `sample_offset` casi no modificaba la imagen; el interior procedural sí produjo entradas distintas. Los promedios derivados de entradas casi idénticas no sustentan afirmaciones multisemilla.
- **E0008:** variante que conserva emisión mejora ligeramente RMSE promedio de la ROI (~1.47%) pero empeora MAE de esa misma ROI (~11.29%) y RMSE global; no debe activarse por defecto.
- Las cifras, origen de escena, comandos y limitaciones están en [experiments/](experiments/); no deben reescribirse como conclusiones generales.

## Criterios de selección de fuentes y actualización

1. Priorizar artículos originales, documentación del autor y código fuente; anotar si es paper, implementacion pública, SDK o producto sin código.
2. Nunca confundir disponibilidad del repositorio con licencia de sus **pesos**, datasets, dependencias o integrabilidad con Blender.
3. Registrar versión de librerías y condiciones de render; una implementación reciente puede diferir del paper original.
4. Mantener hallazgos negativos. Si una hipótesis no supera el baseline en datos no vistos, documentar y descartar o posponer.
5. Este catálogo no sustituye un barrido bibliográfico sistemático de 50–100 proyectos. Ese barrido sería una investigación independiente con criterios explícitos de inclusión, extracción y fecha.
