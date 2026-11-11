"""Run: blender -b --factory-startup --python-exit-code 1 --python tests/blender_smoke.py

Actual Blender 5+ and Cycles required. Validates integration, not image quality.
"""
import importlib.util
import pathlib

import bpy

root = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("acd_blender", root / "addon" / "acd_blender.py")
addon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(addon)
addon.register()
try:
    scene = bpy.context.scene
    assert bpy.app.version >= (5, 0, 0)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 4
    scene.render.resolution_x = 32
    scene.render.resolution_y = 32
    scene.render.resolution_percentage = 100
    initial_compositor = scene.compositing_node_group

    for mode in ("STANDARD", "HIGH", "SUPER"):
        scene.acd_mode = mode
        result = bpy.ops.render.acd_build()
        assert "FINISHED" in result, f"Build failed in {mode}: {result}"
        tree = scene.compositing_node_group
        assert tree and tree.get("acd_mode") == mode
        assert any(node.bl_idname == "NodeGroupOutput" for node in tree.nodes)
        assert any(node.bl_idname == "CompositorNodeDenoise" for node in tree.nodes)
        assert any(node.bl_idname == "CompositorNodeRLayers" for node in tree.nodes)
    render_result = bpy.ops.render.render()
    assert "FINISHED" in render_result, f"CPU render returned {render_result}"

    assert "FINISHED" in bpy.ops.render.acd_restore()
    assert scene.compositing_node_group == initial_compositor
    print("ACD BLENDER 5 SMOKE TEST PASSED", bpy.app.version_string)
finally:
    addon.unregister()
