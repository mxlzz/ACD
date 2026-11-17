# F4 — Revisión comparativa de investigaciones implementables (2026-11-12)

**Lectura de repositorios y README, no implementación ni reproducción de sus papers.** Priorizar intervenciones que no exijan modificar Cycles antes de evaluar su coste real.

| Método / fuente | Arquitectura y datos que utiliza | Dependencia crítica para ACD | Estado / decisión |
|---|---|---|---|
| [Progressive Denoising (ProDen), Eurographics 2022](https://github.com/ArthurFirmino/progressive-denoising) | SURE como estimador de error de denoising, red auxiliar que predice mezcla por píxel y límites estadísticos para convergencia. Publica parche `oidn_patch/pd.patch` sobre OIDN histórico, pesos y dataset externos (3 GB train + 3 GB test), dependencias antiguas PyTorch/OpenImageIO. | SURE requiere perturbaciones/estadísticas y modelos preentrenados; no funciona como postproceso de dos RGB sin modificaciones. Hay que investigar qué variables se pueden estimar desde Cycles. | **Alta relevancia conceptual**, no port literal al OIDN 2.5.1. Primero prototipo de estimación de sesgo con controles y held-out. |
| [StatMC (SIGGRAPH Asia 2024)](https://github.com/cg-tuwien/StatMC) | Fork pbrt-v3, `StatPathIntegrator` registra estadísticas Monte Carlo y CUDA denoiser implementado sobre OpenCV; repo declara no apto para producción. CUDA 12.3, OpenCV 4.8.1, Clang/GCC particulares; comparadores OIDN/OptiX/ProDen. Publicación con Graphics Replicability Stamp (2025). | Instrumentar Cycles para acumular suficientes estadísticas por muestra, o montar un renderer de investigación separado. El EXR beauty/normal/albedo no contiene esas estadísticas en forma general. | **Buen baseline metodológico, integración directa en addon no viable con AOV convencionales**. Investigación de buffers/captura antes de adoptar. |
| [StatER (SIGGRAPH Asia 2025)](https://github.com/cg-tuwien/StatER) | Continúa StatMC; integrador pbrt-v3 modificado y soporte de varianza, transformaciones múltiples, reducción de error y muestreo adaptativo; denoiser CUDA/OpenCV separado. Graphics Replicability Stamp (2025). | Mismas dependencias por muestra y renderer, con mayor complejidad computacional; no comparar tiempos con Blender sin normalizar dispositivo/integración. | **Seguimiento investigación**, no prioridad de port a Blender antes de diagnóstico local. |

## Implicaciones para la siguiente hipótesis

1. No usar mezcla guiada por referencia en *inferencia*; valores de referencia se reservan solo para evaluación y calibración previa por escena de entrenamiento. Si se propone fusionar imagen cruda y denoised, estimar pesos desde datos accesibles al usuario en tiempo de uso y confrontar con mezcla constante/aleatoria y OIDN fijo.
2. La estimación de ruido/varianza por múltiples seeds de *la escena* es un experimento offline posible, pero no equivale a disponer de estadísticas por muestra durante el render ni prueba independencia. Para producto sería costoso y debe medirse.
3. Separar tres clases de datasets: sintéticos diseñados, escenas públicas con licencia e imágenes de trabajo autorizadas. Dividir train/val/test **por escena**. En ProDen/StatMC/StatER hay contenido de terceros/escenas externas; revisar licencia individual antes de redistribución.
4. Antes de crear fork de OIDN, priorizar prototipo postproceso independiente con métricas de referencia y controles. Si el método exige reentrenamiento o hooks internos, registrar dependencias y abrir rama/paquete específico; no modificar Blender en producción.

## Licencias

**No asumir** que los forks/papers comparten Apache-2.0 con OIDN. GitHub REST marca licencias de StatMC/StatER como `NOASSERTION` y no detecta licencia declarada de ProDen; inspeccionar `LICENSE.txt`, parches, submódulos, datasets y pesos antes de copiar código. Los enlaces fuente no autorizan por sí mismos relicenciar contenido.
