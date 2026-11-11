"""Inspect the independent Blender 5 SID reference graph, without rendering."""
import importlib.util
import json
import os
from pathlib import Path

import bpy

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sid_reference", root / "addon" / "sid_reference.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)
results = {}
for mode in ref.MODES:
    tree = ref.build_reference_group(mode)
    denoisers = [n for n in tree.nodes if n.bl_idname == "CompositorNodeDenoise"]
    mixes = [n for n in tree.nodes if n.bl_idname == "ShaderNodeMix"]
    incoming = {
        n.label: sorted(link.to_socket.name for link in tree.links if link.to_node == n)
        for n in denoisers
    }
    results[mode.lower()] = {
        "mix_factors": [float(n.inputs["Factor"].default_value) for n in mixes],
        "mix_operations": [n.blend_type for n in mixes],
        "denoisers": len(denoisers),
        "prefilters": [n.inputs["Prefilter"].default_value for n in denoisers],
        "guide_links": incoming,
    }
result = {
    "source_commit": ref.SOURCE_COMMIT,
    "blender": bpy.app.version_string,
    "modes": results,
}
out = Path(os.environ["ACD_PORT_MANIFEST"])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n")
print("SID REFERENCE BLENDER 5 GRAPH CONTRACT", json.dumps(result))
