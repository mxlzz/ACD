# E0062 — Escena arquitectónica independiente: Lone Monk (preinscrita 2026-11-16)

**Criterio rector:** mejorar de manera comprobable la fidelidad de detalle de OIDN para arquitectura en Blender, sin compensar ruido por falsa nitidez ni costos injustificados. E0054/E0059 no demostraron un error residual específico; el siguiente insumo es otra escena arquitectónica Cycles completa, no otro filtro.

## Fuente fijada y autoría
Lone Monk, Carlo Bergonzini / Monorender, escena interior de edificio románico. Demo oficial de Blender Cycles, licencia **CC BY** (obliga atribución). URL primaria https://download.blender.org/demo/cycles/lone-monk_cycles_and_exposure-node_demo.blend ; espejo oficial https://mirror.blender.org/demo/cycles/lone-monk_cycles_and_exposure-node_demo.blend ; tamaño de index **33.452.252 bytes** para archivo actualizado en octubre de 2026. **La huella SHA256 se fija al terminar la adquisición comprobada** y queda en `benchmarks/scenes/lone_monk.source.json`; el tamaño por sí solo no prueba identidad. La escena original no se commitea ni altera.

## Puertas de aceptación (solo fuente funcional)
1. Descargar de uno de dos hosts oficiales, tamaño exacto y cabecera `BLENDER`; registrar URL, versión Blender y SHA256.
2. Abrir sin autoejecución (`--disable-autoexec`) en Blender 5.2.4. Verificar cámara activa, materiales y todas las dependencias externas: imágenes, IES y linked libraries. Rechazar recursos ausentes o no embebidos.
3. Solo después, render Cycles CPU a 192×192 4 spp con denoising desactivado. Un fallo queda registrado, no se inventan texturas/luminarias ni se modifica la iluminación para hacerlo pasar. No guardar el archivo original.
4. Persistir diagnóstico, hash y decisión PASS/FAIL en `docs/experiments/E0062.md`, `E0062_RESULTS.json` y manifest. No publicar el .blend, EXR ni preview.

## Rol científico
Si pasa, es **escena nueva de desarrollo** con autor independiente de Cozy Kitchen y complejidad arquitectónica. Aún NO es holdout de calidad, no se midieron seeds, convergencia ni resoluciones de entrega. Próximo control relevante: verificar que distintas semillas Cycles producen Raw distinto en esa cámara y version; luego fijar regiones materiales/geométricas a densidad de 1080–1920 antes de realizar un benchmark controlado con OIDN y dos referencias de error estimado. Si falla, descartar sin insistir en un ajuste específico de esta fuente.

No fusionar ni modificar addon; PR #10 draft; evitar reabrir High/Super, sharpen u otras variantes ya examinadas. La salida solo establece si esta escena sirve como fixture experimental reproducible.

## Corrección de identidad de fuente anterior al smoke

El primer run 43947290538 descargó el archivo desde Blender, pero se detuvo en la comparación del tamaño tomado del índice: no hubo smoke ni aceptación. El tamaño del listado web no se tratará como hash de identidad. El siguiente run comprobará cabecera binaria BLENDER, bytes en un intervalo razonable, origen oficial (solo dos URLs permitidas), registrará SHA256 real y auditará cámara, recursos, IES y render. **El SHA256 adquirido quedará inmutable para ejecuciones futuras**; un cambio posterior de bytes exigirá volver a auditar. Este ajuste no relaja la aceptación de materiales ausentes ni reemplaza el .blend.
