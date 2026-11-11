"""Generate RAW, Standard, High and Super from a *single* Cycles render.

This is a very small functional comparison, NOT a representative image-quality
benchmark. Both filtered and unfiltered outputs share one RenderLayer evaluation.

Run: ACD_BENCH_DIR=/tmp/acd_bench blender -b --factory-startup -noaudio \
  --python-exit-code 1 --python tests/blender_compare_smoke.py
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import bpy

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("acd_blender", root / "addon" / "acd_blender.py")
addon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(addon)
addon.register()
try:
    destination = Path(os.environ.get("ACD_BENCH_DIR", "/tmp/acd_bench")).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.seed = 539
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 48
    scene.render.resolution_y = 40
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.filepath = str(destination / "composite.exr")
    view_layer = bpy.context.view_layer
    view_layer.cycles.use_denoising = False
    addon.enable_passes(view_layer, scene)

    tree = bpy.data.node_groups.new("ACD comparison (same noisy input)", "CompositorNodeTree")
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    layers = tree.nodes.new("CompositorNodeRLayers")
    layers.scene = scene
    layers.layer = view_layer.name
    layers.location = (-600, 0)
    group_output = tree.nodes.new("NodeGroupOutput")
    group_output.location = (1300, 400)
    tree.links.new(layers.outputs["Image"], group_output.inputs["Image"])

    fileout = tree.nodes.new("CompositorNodeOutputFile")
    fileout.directory = str(destination)
    fileout.file_name = "acd_compare_"
    fileout.format.media_type = "IMAGE"
    fileout.format.file_format = "OPEN_EXR"
    fileout.format.color_depth = "32"
    fileout.format.exr_codec = "ZIP"
    fileout.location = (1300, -200)

    # The source is the exact same RenderLayer evaluation for every branch.
    fileout.file_output_items.clear()
    fileout.file_output_items.new("RGBA", "Raw")
    tree.links.new(layers.outputs["Image"], fileout.inputs["Raw"])

    for i, mode in enumerate(("STANDARD", "HIGH", "SUPER")):
        scene.acd_mode = mode
        sub_tree = addon.make_tree(scene, view_layer)
        group = tree.nodes.new("CompositorNodeGroup")
        group.label = mode
        group.node_tree = sub_tree
        group.location = (150, 200 - 300 * i)
        fileout.file_output_items.new("RGBA", mode)
        tree.links.new(group.outputs["Image"], fileout.inputs[mode])

    scene.compositing_node_group = tree
    scene.render.use_compositing = True
    result = bpy.ops.render.render(write_still=True)
    assert "FINISHED" in result

    generated = sorted(destination.rglob("*.exr"))
    for p in generated:
        print("ACD CANDIDATE", p, p.stat().st_size)
    assert len(generated) >= 4, "Expected RAW and 3 filtered EXR outputs"
    (destination / "metadata.json").write_text(json.dumps({
        "blender": bpy.app.version_string,
        "scene": "factory startup",
        "samples": scene.cycles.samples,
        "seed": scene.cycles.seed,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "compositional_methods": ["Standard", "High", "Super"],
        "comparison": "one shared Cycles render, no independent reference yet",
        "files": [p.name for p in generated],
    }, indent=2) + "\n")
    print("ACD SAME-SAMPLE COMPARISON SMOKE PASSED", len(generated))
finally:
    addon.unregister()
