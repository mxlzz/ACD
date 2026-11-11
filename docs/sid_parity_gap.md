# M3 — Brecha entre ACD y SID público (auditoría directa)

Revisión: 2026-11-11. **Prioridad corregida: primero portar y verificar la referencia SID; después mejorarla.**

## Referencia exacta

- Repositorio público: https://github.com/PidgeonTools/SuperImageDenoiser
- Commit de referencia `master`: `b4186389cac386eff9d777bb681c0051f8bd9bd2` (release histórico 4.0.0).
- Licencia upstream: **GNU GPL-3.0**. Su reutilización literal permite modificar y distribuir bajo las condiciones de GPL (fuentes, avisos de copyright, licencia y cambios identificados). El repositorio ACD actualmente no declara licencia; una integración derivada tiene consecuencias para la distribución de ACD. Decidir **antes** de copiar upstream.
- La versión comercial de SID v5.3.0, dentro de Pidgeon Tool Bag, **no es el mismo código fuente que está publicado aquí**. La ficha pública del producto indica compatibilidad hasta Blender 4.4, no Blender 5.x. No puede declararse equivalencia con la versión comercial solo por adaptar v4.0.

Código upstream auditado:
- `SID_QualityStandart.py`, `create_denoiser.py`
- `Cycles/SID_QualityHigh_Cycles.py`
- `Cycles/SID_QualitySuper_Cycles.py`
- `Cycles/SID_Create_Links_Cycles.py`
- `Cycles/SID_Create_Group_Cycles.py`
- `Cycles/SID_Create_Passes_Cycles.py`

Código ACD contrastado: [addon/acd_blender.py](../addon/acd_blender.py), rama `dev/acd-m2-real-scenes-regions`.

## Comparación funcional inicial

| Función | SID público | ACD actual | Consecuencia |
|---|---|---|---|
| Standard: prefilter | FAST | Accurate | Desajuste de parámetros, impide prueba de paridad |
| High | `(Direct+Indirect)*Color` y OIDN con Normal/Albedo | Igual estructura matemática | Necesita prueba por nodos y versión de OIDN |
| Super | OIDN en Direct/Indirect por separado, suma, aplica Color | Igual estructura matemática | Necesita prueba por nodos y versión de OIDN |
| Emisión | OIDN de emisión sin conectar Normal/Albedo (input del nodo solamente) | OIDN de emisión conectado a Normal/Albedo | Desajuste significativo de condicionamiento |
| Alfa | OIDN de Alpha con guías; recombina RGB final y Alpha filtrado | Reemplazo con alfa sin filtrar por defecto; filtrado opcional | Desajuste de salida alfa por defecto |
| Imagen de entrada | Usa `Noisy Image` cuando existe; de lo contrario `Image` | Toma `Image` desactivando denoising del view layer | Verificar equivalencia en Blender 5, no asumirla |
| Combinación de color | `CompositorNodeMixRGB` en cada ADD/MULTIPLY | `ShaderNodeMix` RGBA, factor 1, clamp result false | Cambia la API; medir semántica HDR y alfa |
| Volumen | Denoiser por grupo con Direct/Indirect, Color por defecto blanco | Rama propia de volumen sin guías | Revisar socket defaults, topología y outputs |
| Postfiltro final | OIDN final con guías; forma parte del grafo High/Super | Por defecto activado pero interruptor experimental | No equivale si está desactivado |
| Datos de salida | Calidad final más salidas por familia y emisión/entorno, EXR multilayer opcional | Salida final única de addon (laboratorio tiene EXR aparte) | Interfaz/facilidad de uso aún no replicada |
| OIDN y Blender | API histórica con `node.prefilter`, versión vieja de OIDN | Nodo Blender 5 con `Prefilter`, `Quality` y `HDR` | Igual topología puede producir píxeles distintos según versión |

La lista es inicial y necesita pruebas ejecutables por opción, especialmente albedo/normal, volumen y alfa. La equivalencia matemática parcial **no** justifica llamar a ACD una réplica del SID.

## Migración requerida en Blender 5

Documento oficial: https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/

- `scene.node_tree` y `scene.use_nodes` fueron sustituidos por un datablock `scene.compositing_node_group`; crear y asignar explícitamente el grupo.
- Los sockets de nodos agrupados usan `node_tree.interface.new_socket(...)`; salida mediante `NodeGroupOutput`.
- Los nodos MixRGB y Separate/Combine RGBA del código histórico requieren mapearse a nodos actuales con pruebas de equivalencia semántica, incluidos valores HDR y alfa.
- Auditar ajustes de render passes, nombre de `Noisy Image`, `Denoising Normal`, `Denoising Albedo`, flags de Cycles y evolución OIDN.
- Mantener intacto el compositor original, poder restaurarlo y no reemplazar silenciosamente conexiones ajenas.

## Vía de implementación

1. **Congelar upstream:** etiquetar commit exacto y extraer especificación de grafo *Standard / High / Super* (nodos, sockets, enlaces, defaults, grupos y ramas optativas). No dejar partes a interpretación.
2. **Elegir método legal:** (a) fork-port GPL de SID con atribución y código derivado; o (b) implementar comportamiento equivalente sin copiar código literal, para mantener el experimento ACD independiente. Una distribución combinada puede activar obligaciones copyleft; registrar la decisión.
3. **Modo SID4 Reference** en Blender 5, mantenido **separado de los modos experimentales ACD**; primero fidelidad funcional, después optimizaciones.
4. **Paridad automática:** comprobar cantidad/tipo de nodos, parámetros, links, comportamiento de emisión, alfa, volumen, colores, pass flags y output multilayer con un fixture determinista. Ejecutar test real en Blender 5.0.1 y 5.x posterior.
5. **Paridad experimental:** procesar los mismos canales EXR lineales en el SID original sobre una versión antigua compatible y en el port Blender 5. Reportar cambios por la versión subyacente de OIDN/Blender; la igualdad exacta pixel-a-pixel puede ser inalcanzable por backend distinto.
6. **Calidad visual:** test de interiores/vidrio y HDR con originales sin filtrar, ROIs y varias semillas realmente diferentes; reportar tiempo, RAM, sesgo y error, con la misma entrada.

**Puerta de cierre:** no declarar 'SID reproducido' hasta tener (i) topología funcional inspeccionada, (ii) parámetros/sockets comparados, (iii) pruebas reales en Blender, y (iv) diferencias residuales documentadas. Comparación con comercial SID v5.3.0 es otro objetivo y exige su código o un entorno/paquete de referencia legítimamente obtenido.

Issue de implementación: https://github.com/mxlzz/ACD/issues/7
