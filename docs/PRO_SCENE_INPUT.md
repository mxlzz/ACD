# Protocolo de ingreso — escena profesional para evaluar ACD

**Propósito:** medir si una variante mejora el denoising nativo sin depender exclusivamente de fixtures procedimentales pequeños. No se necesita reemplazar la configuración del proyecto por la de los ejemplos anteriores.

## Escena solicitada

Un archivo Blender `.blend` **representativo de un render arquitectónico**, con cámara activa, motores/materiales compatibles con Cycles y texturas/recursos presentes. Idealmente, vidrio o reflejos, materiales texturados, luces artificiales o emisión y detalles pequeños. Una sola escena es suficiente para iniciar, aunque no prueba generalización.

- En Blender: `File → External Data → Pack Resources` para incluir imágenes/recursos que lo permitan. Revisar referencias externas no empaquetables (bibliotecas enlazadas, caches, assets con restricciones).
- Elegir encuadre, escena y frame que deban evaluarse. No es necesario renderizarlo antes; el benchmark genera varias entradas y referencias.
- Si el proyecto es privado o contiene datos de terceros, compartir una copia anonimizada/autorizada en lugar de publicarlo en el repositorio abierto.
- Blender objetivo: 5.0.1 inicialmente (para coincidir con los experimentos); si el proyecto necesita otra versión, documentarla antes de ejecutar.

## Ejecución local existente

El repositorio ya dispone de `scripts/run_scene_benchmark.py`. No modifica el `.blend` original ni escribe sobre la carpeta existente de resultados. Ejemplo de consola, ajustando rutas:

```bash
python scripts/run_scene_benchmark.py \
  --blender /ruta/a/blender \
  --blend /ruta/escena.blend \
  --output /ruta/resultados_nuevos \
  --samples 32 \
  --reference-samples 2048 \
  --extra-seeds 911,1337 \
  --second-reference \
  --methods STANDARD,HIGH,SUPER,SID4_STANDARD,SID4_HIGH,SID4_SUPER,NATIVE_COMP_OIDN
```

Instalar el laboratorio Python con `python -m pip install -e ".[exr]"`. Para GPU usar `--device OPTIX` o `CUDA` cuando Blender esté configurado y soporte la tarjeta. Sin GPU se puede usar `CPU`, con mayor coste de render. Conviene probar primero un `--dry-run` y un tamaño razonable.

## Evidencia mínima

Conservar archivo de entrada o su SHA256, `metadata.json`, EXR ruidosos por seed, al menos dos referencias y sus muestras, `metrics.json`, `seed_aggregate.json`, salida RGBA de cada candidato. Rechazar inferencias si las semillas o referencias no varían de forma útil, o si el error entre referencias es significativo.

**Criterio de avance:** un algoritmo experimental debe superar al baseline OIDN en un criterio predefinido y sostenerlo en escenas fuera de desarrollo, sin empeorar arbitrariamente HDR, bordes o materiales. Ninguna tabla de RMSE aislada certifica calidad visual.
