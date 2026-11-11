"""Probe the UNMODIFIED public GPL SID 4.x inside supported Blender 3.6.

The upstream code is cloned into the Actions runner only, not vendored in ACD.
A synthetic Python package shell avoids importing unrelated updater/UI modules.
This examines graph topology/parameters, not pixel-equivalence.
"""
import importlib
import json
import os
import sys
import types
from pathlib import Path

import bpy

root = Path(os.environ["SID_UPSTREAM_ROOT"]).resolve()
assert (root / "Cycles" / "SID_Create_Links_Cycles.py").exists()
assert bpy.app.version[:2] == (3, 6), bpy.app.version_string

pkg = types.ModuleType("sid_public")
pkg.__path__ = [str(root)]
pkg.SID_Settings = object
sys.modules["sid_public"] = pkg
cycles = types.ModuleType("sid_public.Cycles")
cycles.__path__ = [str(root / "Cycles")]
sys.modules["sid_public.Cycles"] = cycles

standard = importlib.import_module("sid_public.SID_QualityStandart")
high = importlib.import_module("sid_public.Cycles.SID_QualityHigh_Cycles")
sup = importlib.import_module("sid_public.Cycles.SID_QualitySuper_Cycles")
links = importlib.import_module("sid_public.Cycles.SID_Create_Links_Cycles")

class Settings:
    quality = "HIGH"
    denoiser_type = "SID"
    use_transmission = True
    use_volumetric = False
    use_emission = True
    use_environment = True

def report(tree):
    mixes = [n for n in tree.nodes if n.bl_idname == "CompositorNodeMixRGB"]
    dns = [n for n in tree.nodes if n.bl_idname == "CompositorNodeDenoise"]
    incoming = {}
    for dn in dns:
        incoming[dn.label or dn.name] = sorted(
            link.to_socket.name
            for link in tree.links if link.to_node == dn
        )
    return {
        "mix_factors": [float(n.inputs[0].default_value) for n in mixes],
        "mix_operations": [n.blend_type for n in mixes],
        "denoisers": len(dns),
        "prefilters": [n.prefilter for n in dns],
        "guide_links": incoming,
    }

s = standard.create_sid_denoiser_standard()
h_sub = high.create_sid_denoiser_high_cy()
u_sub = sup.create_sid_denoiser_super_cy()
h_top = links.create_links_cy(h_sub, Settings())
settings2 = Settings()
settings2.quality = "SUPER"
u_top = links.create_links_cy(u_sub, settings2)

result = {
    "source": "PidgeonTools/SuperImageDenoiser",
    "source_commit": "b4186389cac386eff9d777bb681c0051f8bd9bd2",
    "blender": bpy.app.version_string,
    "standard": report(s),
    "high_subgroup": report(h_sub),
    "super_subgroup": report(u_sub),
    "high_top": report(h_top),
    "super_top": report(u_top),
}
out = Path(os.environ["ACD_LEGACY_MANIFEST"])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n")
print("SID PUBLIC LEGACY GRAPH CONTRACT", json.dumps(result))
