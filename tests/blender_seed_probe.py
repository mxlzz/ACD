"""Probe actual Cycles seed effect in a separate Blender process.

The benchmark initially changed scene.cycles.seed within one session; some
Classroom outputs were nearly identical. This probe renders uncomposted raw
RGB from separate sessions to isolate whether render-session caching or
scene-specific settings cause the anomaly.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import bpy

scene = bpy.context.scene
seed = int(os.environ["ACD_PROBE_SEED"])
offset = int(os.environ.get("ACD_PROBE_OFFSET", "0"))
label = os.environ.get("ACD_PROBE_LABEL", str(seed))
if not label.replace("_", "").isalnum():
    raise ValueError("ACD_PROBE_LABEL must be alphanumeric/underscore")
directory = Path(os.environ["ACD_PROBE_DIR"])
directory.mkdir(parents=True, exist_ok=True)

scene.render.engine = "CYCLES"
scene.render.use_compositing = False
scene.compositing_node_group = None
scene.render.resolution_x = 96
scene.render.resolution_y = 54
scene.render.resolution_percentage = 100
scene.cycles.device = "CPU"
scene.cycles.use_denoising = False
scene.cycles.use_adaptive_sampling = False
scene.cycles.samples = 16
scene.cycles.seed = seed
pattern = os.environ.get("ACD_PROBE_PATTERN")
if pattern:
    allowed = {item.identifier for item in scene.cycles.bl_rna.properties["sampling_pattern"].enum_items}
    if pattern not in allowed:
        raise ValueError(f"Sampling pattern {pattern} not in {sorted(allowed)}")
    scene.cycles.sampling_pattern = pattern
if not hasattr(scene.cycles, "sample_offset"):
    raise RuntimeError("Cycles sample_offset not supported by this Blender build")
scene.cycles.sample_offset = offset
scene.render.image_settings.media_type = "IMAGE"
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_depth = "32"
scene.render.filepath = str(directory / (label + ".exr"))
settings = []
for s in bpy.data.scenes:
    settings.append({
        "name": s.name,
        "seed": s.cycles.seed,
        "samples": s.cycles.samples,
        "pattern": s.cycles.sampling_pattern,
        "animated_seed": s.cycles.use_animated_seed,
        "background_scene": s.background_set.name if s.background_set else None,
        "layers": [
            {"name": layer.name, "samples": layer.samples}
            for layer in s.view_layers
        ],
    })
metadata = {
    "active_scene": scene.name,
    "active_view_layer": bpy.context.view_layer.name,
    "requested_seed": seed,
    "sample_offset": offset,
    "sampling_pattern": scene.cycles.sampling_pattern,
    "output_label": label,
    "settings_all_scenes": settings,
}
print("ACD_SEED_PROBE_SETTINGS", json.dumps(metadata, sort_keys=True))
result = bpy.ops.render.render(write_still=True)
assert "FINISHED" in result
assert Path(scene.render.filepath).is_file()
(directory / (label + ".json")).write_text(json.dumps(metadata, indent=2) + "\n")
print("ACD_SEED_PROBE_COMPLETE", seed, scene.render.filepath)
