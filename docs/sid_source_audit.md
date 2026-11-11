# Public SID source audit

Source: https://github.com/PidgeonTools/SuperImageDenoiser
Files studied (master, 2026-11-11):
- Cycles/SID_QualityHigh_Cycles.py
- Cycles/SID_QualitySuper_Cycles.py
- Cycles/SID_Create_Links_Cycles.py
- Cycles/SID_Create_Passes_Cycles.py
- LICENSE (GNU General Public License v3)

High: sum Direct/Indirect, multiply the Color AOV, denoise each family.
Super: denoise Direct and Indirect separately, add, multiply the Color AOV.
The outer graph composes families and optional volume, emission and environment contributions, denoises the recomposed result, and separately filters the alpha channel.
"Noisy Image" is used only if available; otherwise the original "Image" pass is used.

Blender 5 introduces scene.compositing_node_group, an explicit compositor node-group interface and a Group Output node in place of the old Composite node.

No upstream source code was copied. Source GPLv3 matters if later importing actual code; that would change redistribution obligations.

## Rectificación / brechas (2026-11-11)

El registro histórico anterior listaba correctamente la estructura algebraica pero omitía diferencias de implementación que impiden afirmar paridad. Auditoría directa y matriz detallada: [sid_parity_gap.md](sid_parity_gap.md).

- SID Standard utiliza `prefilter=FAST`; ACD prefiltrado Accurate para todos.
- SID filtra emisión **sin** conectar Denoising Normal y Albedo al nodo de emisión; ACD sí conecta ambas.
- SID filtra alfa por separado y luego recombina RGBA; ACD preserva alfa sin filtrar por defecto.
- SID selecciona Noisy Image cuando está habilitado; ACD utiliza Image con denoising del view layer apagado.
- Deben compararse detalladamente MixRGB vs ShaderNodeMix, volúmenes, salida EXR y diferencias de OIDN por versión.
- Pidgeon Tool Bag SID v5.3.0 es una referencia comercial posterior y diferente: no asumir equivalencia con la fuente GPL histórica.

Implementación y pruebas priorizadas en [Issue #7](https://github.com/mxlzz/ACD/issues/7).
