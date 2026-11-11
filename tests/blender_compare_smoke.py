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
    scene_variant = os.environ.get("ACD_SCENE", "factory")
    if scene_variant == "interior":
        interior_spec = importlib.util.spec_from_file_location("acd_scene", root / "tests" / "scene_factory.py")
        interior = importlib.util.module_from_spec(interior_spec)
        interior_spec.loader.exec_module(interior)
        interior.make_interior(scene)
    elif scene_variant != "factory":
        raise ValueError("Unknown ACD_SCENE: " + scene_variant)
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

    # Check the compositor's mathematical pass sum without any denoisers.
    # If this disagrees with RAW, the processing graph itself is not trustworthy.
    family_terms = []
    for family in ("Diffuse", "Glossy", "Transmission"):
        direct = addon.render_socket(layers, family + " Direct")
        indirect = addon.render_socket(layers, family + " Indirect")
        color = addon.render_socket(layers, family + " Color")
        lighting = addon.combine(tree.nodes, tree.links, direct, indirect, "ADD", family + " raw sum", (-350, -1100))
        family_terms.append(addon.combine(tree.nodes, tree.links, lighting, color, "MULTIPLY", family + " raw color", (-150, -1100)))
    family_terms.append(addon.render_socket(layers, "Emission"))
    family_terms.append(addon.render_socket(layers, "Environment"))
    recomposed = family_terms[0]
    for index, term in enumerate(family_terms[1:], 1):
        recomposed = addon.combine(tree.nodes, tree.links, recomposed, term, "ADD", "Raw components " + str(index), (100 + 230 * index, -1400))
    fileout.file_output_items.new("RGBA", "RawRecomposed")
    tree.links.new(recomposed, fileout.inputs["RawRecomposed"])

    methods = (
        ("STANDARD", True, "STANDARD", False),
        ("HIGH", True, "HIGH", False),
        ("SUPER", True, "SUPER", False),
        ("HIGH", False, "HIGH_no_final", False),
        ("SUPER", False, "SUPER_no_final", False),
        ("HIGH", True, "HIGH_no_guides", True),
        ("SUPER", True, "SUPER_no_guides", True),
    )
    for i, (mode, final_filter, output_name, strip_guides) in enumerate(methods):
        scene.acd_mode = mode
        scene.acd_final_filter = final_filter
        sub_tree = addon.make_tree(scene, view_layer)
        if strip_guides:
            # This is an ablation, NOT a recommended permanent addon setting.
            for dn in sub_tree.nodes:
                if dn.bl_idname == "CompositorNodeDenoise":
                    for edge in tuple(sub_tree.links):
                        if edge.to_node == dn and edge.to_socket.name in ("Albedo", "Normal"):
                            sub_tree.links.remove(edge)
        group = tree.nodes.new("CompositorNodeGroup")
        group.label = output_name
        group.node_tree = sub_tree
        group.location = (150, 200 - 300 * i)
        fileout.file_output_items.new("RGBA", output_name)
        tree.links.new(group.outputs["Image"], fileout.inputs[output_name])

    scene.compositing_node_group = tree
    scene.render.use_compositing = True
    result = bpy.ops.render.render(write_still=True)
    assert "FINISHED" in result

    generated = sorted(destination.rglob("*.exr"))
    for p in generated:
        print("ACD CANDIDATE", p, p.stat().st_size)
    assert len(generated) >= 4, "Expected RAW and 3 filtered EXR outputs"
    # A separate, higher-sample unfiltered reference uses a different seed.
    # This is still a low-resolution smoke reference, not a converged benchmark.
    reference_spp = int(os.environ.get("ACD_REFERENCE_SPP", "256"))
    reference_seed = 8819
    scene.compositing_node_group = None
    scene.render.use_compositing = False
    scene.cycles.samples = reference_spp
    scene.cycles.seed = reference_seed
    scene.render.filepath = str(destination / "reference.exr")
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    ref_result = bpy.ops.render.render(write_still=True)
    assert "FINISHED" in ref_result
    assert (destination / "reference.exr").is_file()
    print("ACD REFERENCE", destination / "reference.exr", "spp", reference_spp)

    (destination / "metadata.json").write_text(json.dumps({
        "blender": bpy.app.version_string,
        "scene": scene_variant,
        "samples": 16,
        "seed": 539,
        "reference_samples": reference_spp,
        "reference_seed": reference_seed,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "compositional_methods": [name for _, _, name, _ in methods],
        "other_output": "RawRecomposed: mathematical node-graph pass sum without denoising",
        "comparison": "one shared Cycles render + independent high-sample reference (not convergence-verified)",
        "files": [p.name for p in generated],
    }, indent=2) + "\n")
    print("ACD SAME-SAMPLE COMPARISON SMOKE PASSED", len(generated))
finally:
    addon.unregister()
