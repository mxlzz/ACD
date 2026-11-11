"""Generate RAW, Standard, High and Super from a *single* Cycles render.

This is a very small functional comparison, NOT a representative image-quality
benchmark. Both filtered and unfiltered outputs share one RenderLayer evaluation.

Run: ACD_BENCH_DIR=/tmp/acd_bench blender -b --factory-startup -noaudio \
  --python-exit-code 1 --python tests/blender_compare_smoke.py
"""
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import shutil
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
    if scene_variant in ("interior", "interior_emissive", "glass_lobby"):
        interior_spec = importlib.util.spec_from_file_location("acd_scene", root / "tests" / "scene_factory.py")
        interior = importlib.util.module_from_spec(interior_spec)
        interior_spec.loader.exec_module(interior)
        if scene_variant == "interior_emissive":
            interior.make_interior_emissive(scene)
        elif scene_variant == "glass_lobby":
            lobby_spec = importlib.util.spec_from_file_location(
                "acd_lobby", root / "tests" / "scene_glass_lobby.py"
            )
            lobby = importlib.util.module_from_spec(lobby_spec)
            import sys
            sys.path.insert(0, str(root / "tests"))
            try:
                lobby_spec.loader.exec_module(lobby)
            finally:
                sys.path.pop(0)
            lobby.make_glass_lobby(scene)
        else:
            interior.make_interior(scene)
    elif scene_variant == "external":
        if not bpy.data.filepath:
            raise RuntimeError("ACD_SCENE=external requires Blender launched with a saved .blend")
        if scene.camera is None:
            raise RuntimeError("Selected Blender scene has no active camera")
        missing = []
        for img in bpy.data.images:
            if img.source == "FILE" and img.packed_file is None and img.filepath:
                filename = bpy.path.abspath(img.filepath, library=img.library)
                if "<UDIM>" not in filename and not Path(filename).is_file():
                    missing.append(filename)
        if missing:
            raise RuntimeError("Missing external image assets; pack files or fix paths: " + str(missing[:12]))
        if os.environ.get("ACD_FRAME"):
            scene.frame_set(int(os.environ["ACD_FRAME"]))
        print("ACD EXTERNAL BLEND LOADED", bpy.data.filepath, "scene", scene.name)
    elif scene_variant != "factory":
        raise ValueError("Unknown ACD_SCENE: " + scene_variant)
    scene.render.engine = "CYCLES"
    device = os.environ.get("ACD_DEVICE", "CPU").upper()
    if device not in {"CPU", "CUDA", "OPTIX"}:
        raise ValueError("ACD_DEVICE must be CPU, CUDA or OPTIX")
    if device != "CPU":
        addon_preferences = bpy.context.preferences.addons.get("cycles")
        if addon_preferences is None:
            raise RuntimeError("Cycles addon preferences unavailable; cannot select GPU")
        prefs = addon_preferences.preferences
        prefs.compute_device_type = device
        prefs.get_devices()
        devices = [d for d in prefs.devices if d.type == device]
        if not devices:
            raise RuntimeError("No available " + device + " device detected")
        for d in prefs.devices:
            d.use = (d.type == device)
    scene.cycles.device = "CPU" if device == "CPU" else "GPU"
    input_spp = int(os.environ.get("ACD_INPUT_SPP", "16"))
    input_seed = int(os.environ.get("ACD_INPUT_SEED", "539"))
    width = int(os.environ.get("ACD_WIDTH", str(scene.render.resolution_x if scene_variant == "external" else 48)))
    height = int(os.environ.get("ACD_HEIGHT", str(scene.render.resolution_y if scene_variant == "external" else 40)))
    assert input_spp > 0 and 8 <= width <= 4096 and 8 <= height <= 4096
    scene.cycles.samples = input_spp
    scene.cycles.seed = input_seed
    scene.cycles.use_denoising = False
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    capture_aov = os.environ.get("ACD_CAPTURE_AOV", "0") == "1"
    if capture_aov:
        scene.render.image_settings.media_type = "MULTI_LAYER_IMAGE"
        scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    else:
        scene.render.image_settings.media_type = "IMAGE"
        scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.filepath = str(destination / "raw_multilayer.exr" if capture_aov else destination / "composite.exr")
    view_layer = bpy.context.view_layer
    view_layer.cycles.use_denoising = False
    scene.acd_volumes = True if scene_variant == "external" else scene.acd_volumes
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

    all_methods = (
        ("STANDARD", True, "STANDARD", "full"),
        ("HIGH", True, "HIGH", "full"),
        ("SUPER", True, "SUPER", "full"),
        ("HIGH", False, "HIGH_no_final", "full"),
        ("SUPER", False, "SUPER_no_final", "full"),
        # Legacy ablations remove guides from both intermediate and final OIDN.
        ("HIGH", True, "HIGH_no_guides", "remove_all"),
        ("SUPER", True, "SUPER_no_guides", "remove_all"),
        # New controlled subpass ablations retain the final OIDN guidance.
        ("STANDARD", True, "STANDARD_no_guides", "component_none"),
        ("HIGH", True, "HIGH_component_no_guides", "component_none"),
        ("SUPER", True, "SUPER_component_no_guides", "component_none"),
        ("HIGH", True, "HIGH_component_albedo", "component_albedo"),
        ("SUPER", True, "SUPER_component_albedo", "component_albedo"),
        # Normal-only is invalid in Blender's OIDN compositor: Normal cannot
        # meaningfully be used unless Albedo is linked. E0012 observed outputs
        # pixel-identical to the no-guide variants. Preserve historical EXR
        # readers but do not generate these misleading duplicate variants.
    )
    configured_names = [name.strip() for name in os.environ.get(
        "ACD_METHODS", "STANDARD,HIGH,SUPER,HIGH_no_final,SUPER_no_final,HIGH_no_guides,SUPER_no_guides"
    ).split(",") if name.strip()]
    if len(configured_names) != len(set(configured_names)):
        raise ValueError("Duplicate method names in ACD_METHODS")
    invalid = {"HIGH_component_normal", "SUPER_component_normal"} & set(configured_names)
    if invalid:
        raise ValueError(
            "Normal-only OIDN is not a valid Blender denoising ablation. "
            "The compositor ignores Normal if Albedo is unconnected. "
            "See E0012 and Blender source."
        )
    unknown = set(configured_names) - {entry[2] for entry in all_methods}
    if unknown or not configured_names:
        raise ValueError("Unsupported method selection: " + str(sorted(unknown)))
    methods = tuple(entry for entry in all_methods if entry[2] in configured_names)
    for i, (mode, final_filter, output_name, guide_policy) in enumerate(methods):
        scene.acd_mode = mode
        scene.acd_final_filter = final_filter
        sub_tree = addon.make_tree(scene, view_layer)
        if guide_policy != "full":
            # Ablations change only guide *connections*, never the raw render.
            # For component_* policies, retain guided post-composition OIDN so
            # differences isolate intermediate pass filtering. Legacy remove_all
            # deliberately strips both stages for comparison with E0001/E0002.
            for dn in sub_tree.nodes:
                if dn.bl_idname != "CompositorNodeDenoise":
                    continue
                if (guide_policy.startswith("component_")
                        and dn.label == "Post-composition OIDN"):
                    continue
                for edge in tuple(sub_tree.links):
                    if edge.to_node != dn:
                        continue
                    guide = edge.to_socket.name
                    drop = (
                        guide_policy in ("remove_all", "component_none")
                        or (guide_policy == "component_albedo" and guide == "Normal")
                    )
                    if guide in ("Albedo", "Normal") and drop:
                        sub_tree.links.remove(edge)
        group = tree.nodes.new("CompositorNodeGroup")
        group.label = output_name
        group.node_tree = sub_tree
        group.location = (150, 200 - 300 * i)
        fileout.file_output_items.new("RGBA", output_name)
        tree.links.new(group.outputs["Image"], fileout.inputs[output_name])

    # Research ablation E0006: preserve raw emission instead of filtering it.
    # Directly visible emissive regions can be nearly deterministic even at
    # low spp. Compare numerically; do not assume this is always superior.
    emission_ablation = os.environ.get("ACD_PRESERVE_EMISSION", "0") == "1"
    if emission_ablation:
        raw_emission = addon.render_socket(layers, "Emission")
        raw_beauty = addon.render_socket(layers, "Image")
        normal = addon.render_socket(layers, "Denoising Normal")
        albedo = addon.render_socket(layers, "Denoising Albedo")
        indirect_beauty = addon.combine(
            tree.nodes, tree.links, raw_beauty, raw_emission, "SUBTRACT",
            "Beauty minus raw emission", (-800, -2100)
        )
        filtered_nonemissive = addon.denoise(
            tree.nodes, tree.links, indirect_beauty, normal, albedo,
            "OIDN excluding emission AOV", (-400, -2100)
        )
        emission_protected = addon.combine(
            tree.nodes, tree.links, filtered_nonemissive, raw_emission,
            "ADD", "Restore original emission", (100, -2100)
        )
        fileout.file_output_items.new("RGBA", "STANDARD_emission_preserved")
        tree.links.new(emission_protected, fileout.inputs["STANDARD_emission_preserved"])

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
    reference_seed = int(os.environ.get("ACD_REFERENCE_SEED", "8819"))
    external_reference = os.environ.get("ACD_REFERENCE_FILE", "")
    scene.compositing_node_group = None
    scene.render.use_compositing = False
    scene.render.filepath = str(destination / "reference.exr")
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    if external_reference:
        ref_source = Path(external_reference).resolve()
        if not ref_source.is_file() or ref_source.suffix.lower() != ".exr":
            raise RuntimeError("ACD_REFERENCE_FILE must point to an existing .exr")
        if ref_source != (destination / "reference.exr").resolve():
            shutil.copy2(ref_source, destination / "reference.exr")
        print("ACD EXISTING REFERENCE", ref_source)
    else:
        scene.cycles.samples = reference_spp
        scene.cycles.seed = reference_seed
        ref_result = bpy.ops.render.render(write_still=True)
        assert "FINISHED" in ref_result
        assert (destination / "reference.exr").is_file()
        print("ACD REFERENCE", destination / "reference.exr", "spp", reference_spp)
    second_reference = os.environ.get("ACD_DOUBLE_REFERENCE") == "1" and not external_reference
    if second_reference:
        scene.cycles.seed = reference_seed + 103
        scene.render.filepath = str(destination / "reference_check.exr")
        check_result = bpy.ops.render.render(write_still=True)
        assert "FINISHED" in check_result
        assert (destination / "reference_check.exr").is_file()
        print("ACD SECOND INDEPENDENT REFERENCE", destination / "reference_check.exr")

    # Repeat the same compositor with different *noisy* render seeds.
    # The independent, higher-spp references above are reused unchanged.
    extra_seeds = [
        int(token) for token in os.environ.get("ACD_EXTRA_SEEDS", "").split(",")
        if token.strip()
    ]
    if input_seed in extra_seeds or len(extra_seeds) != len(set(extra_seeds)):
        raise ValueError("Extra seeds must be unique and distinct from the original")
    for extra_seed in extra_seeds:
        extra_dir = destination / ("seed_" + str(extra_seed))
        extra_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination / "reference.exr", extra_dir / "reference.exr")
        if second_reference:
            shutil.copy2(destination / "reference_check.exr", extra_dir / "reference_check.exr")
        scene.compositing_node_group = tree
        scene.render.use_compositing = True
        scene.cycles.samples = input_spp
        scene.cycles.seed = extra_seed
        scene.render.filepath = str(extra_dir / "composite.exr")
        fileout.directory = str(extra_dir)
        repeated_result = bpy.ops.render.render(write_still=True)
        assert "FINISHED" in repeated_result
        assert (extra_dir / "acd_compare_Raw.exr").exists()
        print("ACD EXTRA INPUT SEED COMPLETE", extra_seed)

    blend_hash = None
    if scene_variant == "external":
        hasher = hashlib.sha256()
        with open(bpy.data.filepath, "rb") as stream:
            while True:
                chunk = stream.read(4 * 1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        blend_hash = hasher.hexdigest()
    (destination / "metadata.json").write_text(json.dumps({
        "blender": bpy.app.version_string,
        "scene": scene_variant,
        "source_blend": str(bpy.data.filepath) if scene_variant == "external" else None,
        "source_blend_sha256": blend_hash,
        "scene_name": scene.name,
        "view_layer": view_layer.name,
        "frame": scene.frame_current,
        "render_device": device,
        "capture_aov": capture_aov,
        "color_management": {
            "view_transform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposure": scene.view_settings.exposure,
            "gamma": scene.view_settings.gamma,
            "display_device": scene.display_settings.display_device,
        },
        "cycles": {
            "max_bounces": scene.cycles.max_bounces,
            "use_adaptive_sampling": scene.cycles.use_adaptive_sampling,
            "use_denoising": scene.cycles.use_denoising,
        },
        "samples": input_spp,
        "seed": input_seed,
        "reference_samples": reference_spp,
        "reference_seed": reference_seed,
        "second_reference": second_reference,
        "second_reference_seed": reference_seed + 103 if second_reference else None,
        "extra_input_seeds": extra_seeds,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "compositional_methods": [name for _, _, name, _ in methods],
        "other_output": "RawRecomposed: mathematical node-graph pass sum without denoising",
        "emission_ablation": emission_ablation,
        "comparison": "one shared Cycles render + independent high-sample reference (not convergence-verified)",
        "files": [p.name for p in generated],
    }, indent=2) + "\n")
    print("ACD SAME-SAMPLE COMPARISON SMOKE PASSED", len(generated))
finally:
    addon.unregister()
