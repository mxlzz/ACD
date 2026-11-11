# Auditoría de características de denoising de Cycles

2026-11-11. Alcance: código fuente de **Blender v5.0.1**. Corrige la suposición simplificada de que Normal y Albedo siempre representan el primer hit.

Fuentes originales:
- [v5.0.1: intern/cycles/kernel/film/denoising_passes.h](https://github.com/blender/blender/blob/v5.0.1/intern/cycles/kernel/film/denoising_passes.h)
- [Implementación del nodo Denoise en Blender](https://projects.blender.org/blender/blender/src/branch/main/source/blender/nodes/composite/nodes/node_composite_denoise.cc)
- [OIDN RT: características y hits posteriores](https://www.openimagedenoise.org/documentation.html)
- [Cambio posterior para specular albedo y DLSS](https://projects.blender.org/blender/blender/commit/cbd6e92bee)

## Hechos de código: v5.0.1, función film_write_denoising_features_surface

1. Recorre las clausuras BSDF/BSSRDF y calcula normales y componentes de albedo mediante pesos muestrales.
2. Considera especulares muy suaves los cierres cuya rugosidad especular cuadrática no supera 0,075² (con excepciones de tipo de clausura).
3. Cuando la parte no especular supera el 25 % del peso total, escribe el promedio de normales en espacio de cámara y el albedo ponderado por el throughput.
4. **Si predominan cierres especulares, espera al rebote siguiente** y acumula su albedo en el throughput de las características en vez de registrar inmediatamente el hit.
5. Son características agregadas para el camino: no son automáticamente un juego diferente de guías para cada subpase Diffuse/Glossy/Transmission y Direct/Indirect.

## Hecho del compositor OIDN

La implementación actual del nodo denoiser de Blender ignora Normal cuando Albedo falta. E0012 produjo variantes «Normal-only» idénticas a «sin guías», de acuerdo con la implementación. La opción inválida se eliminó del generador, conservando lectura de reportes históricos.

## Interpretación corregida

- **Refutada:** «las guías de Cycles siempre corresponden al primer hit». v5.0.1 ya sigue rebotes de predominio especular.
- **No demostrada:** «estas guías son las equivocadas para cada AOV y causan toda la pérdida de calidad High/Super». E0012 mostró efectos causales al desconectar guías, pero no probó el mecanismo físico responsable.
- **Por investigar:** instrumentar o identificar buffers adecuados por señal de radiancia solo si la auditoría de los rebotes y una comparación controlada demuestra que faltan. Cambios nuevos en la versión principal de Cycles (por ejemplo specular albedo para DLSS) no implican que el nodo OIDN de 5.0.1 los admita.

## Puerta antes de modificar Cycles

Auditar procedencia del throughput/flag a través de distintos rebotes; verificar materiales delta, vidrio rugoso, metal rugoso y reflejos secundarios; demostrar qué características recibe cada subpase; comparar con la información que ya exporta Cycles. Si no hay mejora fuera de escena, no crear un motor paralelo.
