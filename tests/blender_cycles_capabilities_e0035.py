"""E0035: inventory actual compositor/Cycles API from the running Blender build."""
import json
import os
from pathlib import Path
import bpy

scene = bpy.context.scene
scene.render.engine = "CYCLES"
view_layer = bpy.context.view_layer
tree = bpy.data.node_groups.new("E0035 denoise API probe", "CompositorNodeTree")
node = tree.nodes.new("CompositorNodeDenoise")

def get_attr(obj, name):
    try:
        return str(getattr(obj, name))
    except (AttributeError, RuntimeError, TypeError):
        return None

def as_str(value):
    return value.decode(errors="replace") if isinstance(value, bytes) else str(value)

info = {
    "blender": bpy.app.version_string,
    "build_hash": as_str(getattr(bpy.app, "build_hash", "")),
    "build_branch": as_str(getattr(bpy.app, "build_branch", "")),
    "cycles_scene_use_denoising": get_attr(scene.cycles, "use_denoising"),
    "cycles_view_layer_use_denoising": get_attr(view_layer.cycles, "use_denoising"),
    "cycles_scene_denoiser": get_attr(scene.cycles, "denoiser"),
    "cycles_view_layer_denoiser": get_attr(view_layer.cycles, "denoiser"),
    "compositor_node_group_supported": hasattr(scene, "compositing_node_group"),
    "node_type": node.bl_idname,
    "denoise_inputs": [s.name for s in node.inputs],
    "denoise_outputs": [s.name for s in node.outputs],
    "cycles_internal_output_compared": False,
}
target = Path(os.environ["ACD_E0035_CAPABILITIES"])
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(info, indent=2) + "\n")
print("ACD_E0035_API", json.dumps(info, sort_keys=True))
