# M3.1 — SID público: especificación funcional congelada

**Estado:** especificación extraída del SID público; no es todavía un port validado.
**Upstream:** https://github.com/PidgeonTools/SuperImageDenoiser commit \`b4186389cac386eff9d777bb681c0051f8bd9bd2\` (GPL-3.0); no equivale al SID comercial 5.3.

## Política de propiedad intelectual

Se implementará un **adaptador original** que siga el comportamiento observado y la especificación de entradas/salidas, sin copiar líneas, nombres internos ni estructura de fuente del plugin GPL. Esto deja separados ACD y una potencial distribución derivada. Una comprobación legal formal de compatibilidad solo será necesaria si se redistribuye código upstream o se crea un fork de éste.

## Grafo requerido

Conexiones comunes: \`Noisy Image\` (cuando exista habilitado; en caso contrario \`Image\` sin denoising del view layer), \`Denoising Normal\`, \`Denoising Albedo\`, \`Alpha\`, familias Diffuse/Glossy/Transmission Direct+Indirect+Color; opcionales Volume Direct/Indirect, Emission y Environment.

### Standard
- Un solo nodo OIDN: Image ← Noisy Image, Normal ← Denoising Normal, Albedo ← Denoising Albedo.
- **Prefilter = Fast**, no Accurate. Solo una salida final. Esta rama pública **no crea un denoiser independiente de alfa**.

### High
- Para cada familia presente: suma Direct + Indirect, multiplica por Color, aplica un solo OIDN con Normal+Albedo (prefilter Accurate).
- Para Volume: misma familia con Color=1 y sin conexión de Normal/Albedo.
- Suma salidas de familias; añade Emission **filtrada sin Normal/Albedo**; añade Environment **sin filtrar**.
- Aplica OIDN final (Normal+Albedo); filtra Alpha por OIDN **separado** (Normal+Albedo) y combina RGB final con Alpha procesada.

### Super
- Para cada familia: OIDN independiente sobre Direct e Indirect (ambos con Normal+Albedo), suma sus salidas y luego multiplica por Color.
- Para Volume: igual lógica Super pero **sin guías** y Color=1.
- Emission, Environment, OIDN final y Alpha: misma política que High.

### Mezcla: detalle de compatibilidad
- Los scripts originales crean \`CompositorNodeMixRGB\` de tipo ADD o MULTIPLY **sin conectar Fac**. La implementación del compositor antiguo tenía Fac=1 para esas operaciones ([cambio oficial que explica regresión de 4.5](https://projects.blender.org/blender/blender/pulls/155885)). El port debe declarar **Factor=1.0**, \`clamp_result=False\`, color linear HDR y operación ADD/MULTIPLY.
- El addon ACD original usaba \`ShaderNodeMix\` también con Fac=1, así que **esa no es una discrepancia probada**; su equivalencia numérica/HDR todavía requiere una prueba real.
- En Blender 5.0, \`scene.compositing_node_group\` reemplaza a \`scene.node_tree\`; la salida de un grupo compositor requiere un \`NodeGroupOutput\` con socket Color.

### Prefilter, Quality, HDR
- El SID público fijaba solo \`prefilter=FAST\` en Standard, \`ACCURATE\` en High/Super. En Blender 5 se expresa en socket \`Prefilter\`, no en atributo de nodo.
- **Quality** y **HDR** son opciones explícitas de Blender 5, no equivalentes configurables documentadas en el SID público. Portarlas con valores definidos y reportar esa diferencia, sin atribuirla al SID original. OIDN backend y resultados numéricos pueden diferir entre versiones de Blender.

## Criterios de aceptación para M3.2

1. Función de construcción de grupos por modo, separada del código \`addon/acd_blender.py\`. No modificar automáticamente \`scene.compositing_node_group\`.
2. Tests headless de Blender 5.0.1 y 5.3: topología, número de denoisers, albedo/normal, factor de mezclas, modo Fast/Accurate, alfa y emisión, ramas opcionales.
3. Integración con entrada de RenderLayers, sin perder o sobrescribir el compositor que tenía el usuario.
4. Test mínimo de render CPU al menos en Blender 5.0.1. Registrar las limitaciones de OIDN, alpha, API y equivalencia cross-version en la ficha de paridad.
5. No declarar equivalencia visual o pixel-a-pixel con SID 4.0 hasta contrastar contra el plugin histórico ejecutado en Blender compatible.

## Referencias fuente

- https://github.com/PidgeonTools/SuperImageDenoiser/blob/master/SID_QualityStandart.py
- https://github.com/PidgeonTools/SuperImageDenoiser/blob/master/Cycles/SID_QualityHigh_Cycles.py
- https://github.com/PidgeonTools/SuperImageDenoiser/blob/master/Cycles/SID_QualitySuper_Cycles.py
- https://github.com/PidgeonTools/SuperImageDenoiser/blob/master/Cycles/SID_Create_Links_Cycles.py
- https://github.com/PidgeonTools/SuperImageDenoiser/blob/master/Cycles/SID_Create_Passes_Cycles.py
- https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/
