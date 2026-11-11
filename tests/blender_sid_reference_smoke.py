"""Blender 5-only smoke for a faithful behavioral SID reference adapter."""
import importlib.util
import os
from pathlib import Path

import bpy

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sid_reference", root / "addon" / "sid_reference.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)

def denoisers(tree):
    return [n for n in tree.nodes if n.bl_idname == "CompositorNodeDenoise"]

def incoming(tree, node, socket):
    return [l for l in tree.links if l.to_node == node and l.to_socket.name == socket]

def check_prefilter(tree, expected):
    for node in denoisers(tree):
        assert node.inputs["Prefilter"].default_value == expected, (node.label, node.inputs["Prefilter"].default_value)
        assert node.inputs["HDR"].default_value
        assert node.inputs["Quality"].default_value == "High"

def check_mix(tree):
    for node in tree.nodes:
        if node.bl_idname != "ShaderNodeMix":
            continue
        assert node.blend_type in {"ADD", "MULTIPLY"}, node.blend_type
        assert node.data_type == "RGBA"
        assert node.inputs["Factor"].default_value == 1.0
        assert not node.clamp_result

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 4
scene.render.resolution_x = 24
scene.render.resolution_y = 20
scene.render.resolution_percentage = 100
original = scene.compositing_node_group

try:
    for mode, expected_count in (("STANDARD", 1), ("HIGH", 6), ("SUPER", 9)):
        t = ref.build_reference_group(mode)
        assert len(denoisers(t)) == expected_count, (mode, len(denoisers(t)))
        assert t.get("sid_reference_equivalence_verified") is False
        assert t.get("sid_reference_upstream_commit") == ref.SOURCE_COMMIT
        assert any(n.bl_idname == "NodeGroupOutput" for n in t.nodes)
        check_prefilter(t, "Fast" if mode == "STANDARD" else "Accurate")
        check_mix(t)
        if mode != "STANDARD":
            emission = next(n for n in denoisers(t) if n.label == "Emission | unguided OIDN")
            alpha = next(n for n in denoisers(t) if n.label == "Alpha | independent guided OIDN")
            final = next(n for n in denoisers(t) if n.label == "Final | guided OIDN")
            assert incoming(t, emission, "Image")
            assert not incoming(t, emission, "Normal")
            assert not incoming(t, emission, "Albedo")
            for dn in (alpha, final):
                assert incoming(t, dn, "Image")
                assert incoming(t, dn, "Normal")
                assert incoming(t, dn, "Albedo")
            assert any(n.bl_idname == "CompositorNodeSetAlpha" for n in t.nodes)
        assert scene.compositing_node_group == original

    for mode, count in (("HIGH", 6), ("SUPER", 9)):
        # Volume adds 1 OIDN for High, 2 for Super; transmission disabled
        # removes 1 for High, 2 for Super.
        t = ref.build_reference_group(mode, volume=True, transmission=False,
                                     emission=False, environment=False)
        assert len(denoisers(t)) == count, (mode, len(denoisers(t)))
        volume_nodes = [n for n in denoisers(t) if n.label.startswith("Volume |")]
        assert volume_nodes
        for dn in volume_nodes:
            assert not incoming(t, dn, "Normal")
            assert not incoming(t, dn, "Albedo")
        check_mix(t)
    ref.prepare_reference_passes(bpy.context.view_layer)
    comp = ref.build_scene_reference(scene, bpy.context.view_layer, "SUPER")
    assert scene.compositing_node_group == original, "Reference constructor must not replace user's compositor"
    assert comp.get("sid_noisy_image_socket") in {"Noisy Image", "Image"}
    group = next(n for n in comp.nodes if n.bl_idname == "CompositorNodeGroup")
    assert group.node_tree.get("sid_reference_mode") == "SUPER"
    assert len([l for l in comp.links if l.to_node == group]) == len(group.inputs)
    if os.environ.get("ACD_SKIP_RENDER") != "1":
        scene.compositing_node_group = comp
        scene.render.use_compositing = True
        result = bpy.ops.render.render()
        assert "FINISHED" in result, result
    print("SID REFERENCE BLENDER SMOKE PASSED", bpy.app.version_string)
finally:
    scene.compositing_node_group = original
