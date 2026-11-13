"""E0036 Blender real: Cycles-internal OIDN vs OIDN compositor from ONE render.

No new neural model, no reference, no algorithm ranking. The compositor node
filters the Noisy Image pass of the same render that provides internally
denoised Image. Asset-free procedural architectural detail fixture.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from scene_detail_target import make_detail_target


def out_socket(node, name):
    return next((s for s in node.outputs if s.name == name and s.enabled), None)


def require(node, name):
    socket = out_socket(node, name)
    if socket is None:
        raise RuntimeError(
            "E0036 requires RLayers output '" + name +
            "'; available enabled: " + ", ".join(s.name for s in node.outputs if s.enabled)
        )
    return socket


scene = bpy.context.scene
make_detail_target(scene)
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.seed = 539
scene.cycles.samples = 16
scene.cycles.use_adaptive_sampling = False
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.render.resolution_x = 128
scene.render.resolution_y = 96
scene.render.resolution_percentage = 100
view_layer = bpy.context.view_layer
view_layer.cycles.use_denoising = True
view_layer.cycles.denoising_store_passes = True
view_layer.update_render_passes()

destination = Path(os.environ.get("ACD_E0036_DIR", "/tmp/acd-e0036")).resolve()
destination.mkdir(parents=True, exist_ok=True)

tree = bpy.data.node_groups.new("E0036: shared noisy input; internal vs composer", "CompositorNodeTree")
tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
layers = tree.nodes.new("CompositorNodeRLayers")
layers.scene = scene
layers.layer = view_layer.name

raw = require(layers, "Noisy Image")
cycles_internal = require(layers, "Image")
albedo = require(layers, "Denoising Albedo")
normal = require(layers, "Denoising Normal")

dn = tree.nodes.new("CompositorNodeDenoise")
dn.inputs["Prefilter"].default_value = "Accurate"
dn.inputs["Quality"].default_value = "High"
dn.inputs["HDR"].default_value = True
tree.links.new(raw, dn.inputs["Image"])
tree.links.new(albedo, dn.inputs["Albedo"])
tree.links.new(normal, dn.inputs["Normal"])

group_output = tree.nodes.new("NodeGroupOutput")
tree.links.new(cycles_internal, group_output.inputs["Image"])

fileout = tree.nodes.new("CompositorNodeOutputFile")
fileout.directory = str(destination)
fileout.file_name = "acd_e0036_"
fileout.format.media_type = "IMAGE"
fileout.format.file_format = "OPEN_EXR"
fileout.format.color_depth = "32"
fileout.format.exr_codec = "ZIP"
fileout.file_output_items.clear()
for name, source in (("Raw", raw), ("CyclesInternal", cycles_internal), ("CompositorOIDN", dn.outputs["Image"])):
    fileout.file_output_items.new("RGBA", name)
    tree.links.new(source, fileout.inputs[name])

scene.compositing_node_group = tree
scene.render.use_compositing = True
scene.render.image_settings.media_type = "IMAGE"
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_depth = "32"
scene.render.filepath = str(destination / "render.exr")
result = bpy.ops.render.render(write_still=True)
if "FINISHED" not in result:
    raise RuntimeError("Cycles render failed")

files = {}
for name in ("Raw", "CyclesInternal", "CompositorOIDN"):
    path = destination / ("acd_e0036_" + name + ".exr")
    if not path.is_file() or path.stat().st_size < 100:
        raise RuntimeError("Missing Cycles/compositor output: " + str(path))
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    files[name] = {"path": str(path), "sha256": h, "bytes": path.stat().st_size}

report = {
    "experiment": "E0036",
    "classification": "single-render input identity diagnostic, NOT reference quality",
    "blender": bpy.app.version_string,
    "blender_build": bpy.app.build_hash.decode(errors="replace") if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),
    "samples": 16, "seed": 539, "resolution": [128, 96],
    "scene": "procedural detail_target",
    "cycles_scene_denoiser": scene.cycles.denoiser,
    "cycles_scene_use_denoising": scene.cycles.use_denoising,
    "cycles_view_layer_use_denoising": view_layer.cycles.use_denoising,
    "compositor": {"prefilter": "Accurate", "quality": "High", "hdr": True},
    "raw_from_same_layers": True,
    "methods": ["Raw", "CyclesInternal", "CompositorOIDN"],
    "files": files,
    "reference_convergence_proven": False,
    "caveat": "Both algorithms consume the same Cycles RLayers noisy pass on one render. Internal OIDN and compositor OIDN may use distinct guide handling; output difference is not a quality ranking.",
}
(destination / "e0036_metadata.json").write_text(json.dumps(report, indent=2) + "\n")
print("ACD_E0036_SAME_RENDER", json.dumps({"blender": report["blender"], "files": files, "internal": True}, sort_keys=True))
