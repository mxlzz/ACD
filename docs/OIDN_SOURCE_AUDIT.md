# OIDN v2.5.1 — auditoría inicial de fuente y plan de reproducción

Fecha 2026-11-12. **Auditoría estática, no benchmark ni ejecución del código en ACD**. Fuente fijada al tag [v2.5.1](https://github.com/RenderKit/oidn/tree/v2.5.1), publicado 2026-08-18. Licencia raíz [Apache-2.0](https://github.com/RenderKit/oidn/blob/v2.5.1/LICENSE.txt). Pesos alojados en [oidn-weights](https://github.com/RenderKit/oidn-weights), repositorio separado bajo Apache-2.0; comprobar además `third-party-programs.txt` y licencias de submódulos para cualquier distribución.

## Mapa de componentes localizado en código (tag fijo)

| Ruta | Función verificada mediante inspección | Pregunta del experimento |
|---|---|---|
| [core/rt_filter.cpp](https://github.com/RenderKit/oidn/blob/v2.5.1/core/rt_filter.cpp) | Asigna modelos HDR/LDR por presencia de albedo/normal; parámetros `hdr`, `srgb`, `cleanAux`; función de transferencia | ¿Qué pesos usa cada configuración y cómo escala la señal? |
| [core/unet_filter.cpp](https://github.com/RenderKit/oidn/blob/v2.5.1/core/unet_filter.cpp) | Núcleo de inferencia de red y filtros | ¿Cómo se realiza la evaluación y el tiling? |
| [core/input_process.cpp](https://github.com/RenderKit/oidn/blob/v2.5.1/core/input_process.cpp) | Tratamiento de entradas | ¿Qué modifica HDR, exposición y guías? |
| [training/model.py](https://github.com/RenderKit/oidn/blob/v2.5.1/training/model.py) | Modelos U-Net PyTorch con convoluciones 3×3, pooling y conexiones de salto | ¿Qué podría aprenderse con otro dataset? |
| [training/train.py](https://github.com/RenderKit/oidn/blob/v2.5.1/training/train.py) | Entrenamiento | ¿Qué buffers y targets necesita? |
| [weights](https://github.com/RenderKit/oidn-weights) | Submódulo de pesos preentrenados, archivos .tza en Git LFS | ¿Son idénticos los pesos entre 2.3.3 y 2.5.1? |
| [apps/oidnDenoise.cpp](https://github.com/RenderKit/oidn/blob/v2.5.1/apps/oidnDenoise.cpp) | CLI de inferencia | ¿Podemos ejecutar mismo EXR sin Blender y conservar AOV? |
| [devices/](https://github.com/RenderKit/oidn/tree/v2.5.1/devices) | CPU, CUDA, HIP, Metal, SYCL | Variación entre plataformas y tiempos |

La fuente recomienda `git lfs install; git clone --recursive https://github.com/RenderKit/oidn.git`. Para reproducibilidad fijar tag v2.5.1 y commits de submódulos; preferir [binarios oficiales](https://www.openimagedenoise.org/downloads.html) en primer ensayo. **No se ha clonado, compilado, ejecutado ni creado fork todavía**. GitHub Actions del proyecto comprobó que Blender 5.0.1 incluye biblioteca `libOpenImageDenoise.so.2.3.3`. Debemos distinguir biblioteca distribuida del dispositivo/filtro efectivamente utilizado.

## Fuentes comparativas a verificar en ACD
- [ProDen / Progressive Denoising (Eurographics 2022)](https://github.com/ArthurFirmino/progressive-denoising): SURE y fusión por píxel usando error estimado; su repo contiene parches a **OIDN histórico**, no se debe suponer compatibilidad con 2.5.1.
- [StatMC (SIGGRAPH Asia 2024)](https://github.com/cg-tuwien/StatMC): método estadístico implementado sobre pbrt-v3; necesita estadísticas derivadas de muestras, no disponibles en beauty EXR convencional de Cycles.
- [StatER (SIGGRAPH Asia 2025)](https://github.com/cg-tuwien/StatER): mejora estadística posterior; estudiar implementación y costes de extracción de buffers antes de afirmar que puede instalarse como addon independiente.

## Prueba F2 todavía pendiente
Obtener EXR de input idéntico para OIDN de Blender5.0.1 y standalone2.5.1, registrar SHA256, tipo HDR/guías, precisión, OIDN build string, CPU/GPU, tiempo, versiones y outputs. **No confundir salida numéricamente distinta con superioridad**. Usar E0013 de partida, pero aumentar resolución y diversidad de escenas para conclusión. No reemplazar dependencias de Blender en producción.


## F2 ejecutado, actualización 2026-11-12

El trabajo ya no se limita a auditoría estática: se descargaron y ejecutaron los **binarios oficiales** 2.3.3/2.5.1 en GitHub Actions CPU, con PFM/guías y metadatos de procedencia. [E0014](experiments/E0014.md) compara standalone2.5.1 con nodo compositor Blender; [E0015](experiments/E0015.md) aísla versiones con mismos inputs por run; [E0016](experiments/E0016.md) encuentra cambios entre runners con entradas no idénticas y sin captura ISA; [E0017](experiments/E0017.md) confirma diferencias numéricas muy pequeñas entre AVX2 y AVX-512 para un PFM sintético idéntico, sin atribuir E0015 a AMX todavía. No se ha compilado fork, entrenado pesos, probado OptiX ni validado calidad en escena profesional.
