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
