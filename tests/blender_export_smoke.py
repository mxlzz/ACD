"""Generate a real, unfiltered Cycles multi-layer EXR in headless Blender 5.0.

Run via:
ACD_TEST_EXR=/tmp/acd_raw_smoke.exr blender -b --factory-startup -noaudio \
  --python-exit-code 1 --python tests/blender_export_smoke.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import bpy

target = Path(os.environ.get("ACD_TEST_EXR", "/tmp/acd_raw_smoke.exr")).resolve()
target.parent.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.cycles.seed = 173
scene.render.use_compositing = False
scene.render.resolution_x = 48
scene.render.resolution_y = 40
scene.render.resolution_percentage = 100
# Blender 5 groups formats by media type: select multilayer first.
scene.render.image_settings.media_type = "MULTI_LAYER_IMAGE"
scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
scene.render.image_settings.color_depth = "32"
scene.render.image_settings.exr_codec = "ZIP"
scene.render.filepath = str(target)
scene.render.film_transparent = False

layer = bpy.context.view_layer
layer.cycles.use_denoising = False
layer.cycles.denoising_store_passes = True
for key in (
    "use_pass_diffuse_direct", "use_pass_diffuse_indirect",
    "use_pass_diffuse_color", "use_pass_glossy_direct",
    "use_pass_glossy_indirect", "use_pass_glossy_color",
    "use_pass_transmission_direct", "use_pass_transmission_indirect",
    "use_pass_transmission_color", "use_pass_emit", "use_pass_environment",
):
    setattr(layer, key, True)
if hasattr(layer.cycles, "use_pass_volume_direct"):
    layer.cycles.use_pass_volume_direct = True
    layer.cycles.use_pass_volume_indirect = True
layer.update_render_passes()

assert scene.camera is not None, "Factory scene must include a camera"
state = bpy.ops.render.render(write_still=True)
assert "FINISHED" in state, f"Render failed: {state}"
assert target.is_file() and target.stat().st_size > 1024, (
    f"Expected multilayer EXR not found at {target}"
)

meta = {
    "renderer": scene.render.engine,
    "blender": bpy.app.version_string,
    "sample_count": scene.cycles.samples,
    "seed": scene.cycles.seed,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    "view_layer": layer.name,
    "render_use_compositing": scene.render.use_compositing,
    "denoising": layer.cycles.use_denoising,
    "file_format": scene.render.image_settings.file_format,
    "exr_channels": "inspect-exr determines actual stored channels",
}
target.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
print("ACD RAW EXR WRITTEN", target, "bytes", target.stat().st_size)
