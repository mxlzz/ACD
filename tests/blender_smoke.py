"""Manually run with: blender -b --factory-startup --python tests/blender_smoke.py

Requires actual Blender >= 5 and Cycles; this is not part of ordinary GitHub CI.
No claims about image quality: verifies node construction, registration, basic rendering.
"""
import importlib.util
import pathlib

import bpy

root = pathlib.Path(__file__).resolve().parents[1]
module_path = root / "addon" / "acd_blender.py"
spec = importlib.util.spec_from_file_location("acd_blender", module_path)
addon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(addon)
addon.register()

try:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 4
    scene.render.resolution_x = 32
    scene.render.resolution_y = 32
    scene.render.resolution_percentage = 100

    for mode in ("STANDARD", "HIGH", "SUPER"):
        scene.acd_mode = mode
        result = bpy.ops.render.acd_build()
        assert "FINISHED" in result, f"Build failed in {mode}: {result}"
        tree = scene.compositing_node_group
        assert tree and tree.get("acd_mode") == mode
        assert any(node.bl_idname == "NodeGroupOutput" for node in tree.nodes)

    bpy.ops.render.render()
    assert scene.compositing_node_group is not None
    print("ACD BLENDER 5 SMOKE TEST PASSED")
finally:
    addon.unregister()
