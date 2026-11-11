"""Behavioral SID 4.x reference for Blender 5 compositing.

An independently authored adapter built from a documented public node-graph
SPECIFICATION, not copied GPL plugin code. No UI registration and NO implicit
replacement of the user's compositor.

Reference: public SuperImageDenoiser master b4186389cac386eff9d777bb681c0051f8bd9bd2
Caveat: Blender 5 OIDN/compositor may not generate pixel-identical results
to the historical Blender release; cross-version validation is pending.
"""
from __future__ import annotations

import bpy

SOURCE_COMMIT = "b4186389cac386eff9d777bb681c0051f8bd9bd2"
MODES = ("STANDARD", "HIGH", "SUPER")
FAMILIES = (("Diffuse", "Diff"), ("Glossy", "Gloss"), ("Transmission", "Trans"))

ALIASES = {
    "Noisy Image": ("Noisy Image", "Image", "Combined"),
    "Denoising Albedo": ("Denoising Albedo",),
    "Denoising Normal": ("Denoising Normal",),
    "Alpha": ("Alpha",),
    "Emission": ("Emission", "Emit"),
    "Environment": ("Environment", "Env"),
    "Volume Direct": ("Volume Direct", "VolumeDir"),
    "Volume Indirect": ("Volume Indirect", "VolumeInd"),
}
for _name, _short in FAMILIES:
    for _kind, _suffix in (("Direct", "Dir"), ("Indirect", "Ind"), ("Color", "Col")):
        ALIASES[f"{_name} {_kind}"] = (f"{_name} {_kind}", f"{_short}{_suffix}")


def _interface(tree, name, direction, socket_type="NodeSocketColor"):
    return tree.interface.new_socket(name=name, in_out=direction, socket_type=socket_type)


def _lookup(outputs, key, *, required=True):
    for alias in ALIASES.get(key, (key,)):
        for socket in outputs:
            if socket.name == alias and socket.enabled:
                return socket
    if required:
        available = ", ".join(s.name for s in outputs if s.enabled)
        raise RuntimeError(f"Missing Cycles pass {key!r}. Available: {available}")
    return None


def _mix(tree, left, right, operation, name):
    """Emulate historical compositor MixRGB for ADD/MULTIPLY with Fac=1."""
    node = tree.nodes.new("ShaderNodeMix")
    node.data_type = "RGBA"
    node.blend_type = operation
    node.clamp_result = False
    node.clamp_factor = True
    node.label = name
    node.inputs["Factor"].default_value = 1.0
    a = next(x for x in node.inputs if x.name == "A" and x.type == "RGBA")
    b = next(x for x in node.inputs if x.name == "B" and x.type == "RGBA")
    out = next(x for x in node.outputs if x.name == "Result" and x.type == "RGBA")
    tree.links.new(left, a)
    tree.links.new(right, b)
    return out


def _oidn(tree, image, normal, albedo, *, label, prefilter):
    node = tree.nodes.new("CompositorNodeDenoise")
    node.label = label
    tree.links.new(image, node.inputs["Image"])
    if albedo is not None:
        tree.links.new(albedo, node.inputs["Albedo"])
    if normal is not None:
        tree.links.new(normal, node.inputs["Normal"])
    # Blender 5 exposes these controls as sockets; earlier SID only set
    # prefilter. Quality and HDR are explicit adapter defaults, not an
    # assertion of backend equivalence to old SID.
    node.inputs["Prefilter"].default_value = prefilter
    node.inputs["Quality"].default_value = "High"
    node.inputs["HDR"].default_value = True
    return node.outputs["Image"]


def _family(tree, inp, family, mode, normal, albedo, *, guided=True):
    direct, indirect = inp.outputs[family + " Direct"], inp.outputs[family + " Indirect"]
    material = inp.outputs[family + " Color"] if family != "Volume" else None
    n = normal if guided else None
    a = albedo if guided else None
    if mode == "HIGH":
        light = _mix(tree, direct, indirect, "ADD", family + " | combine raw light")
        colored = _mix(tree, light, material, "MULTIPLY", family + " | modulate material") if material else light
        return _oidn(tree, colored, n, a, label=family + " | guided family", prefilter="Accurate")
    direct_filtered = _oidn(tree, direct, n, a, label=family + " | direct filtered", prefilter="Accurate")
    indirect_filtered = _oidn(tree, indirect, n, a, label=family + " | indirect filtered", prefilter="Accurate")
    light = _mix(tree, direct_filtered, indirect_filtered, "ADD", family + " | combine filtered light")
    return _mix(tree, light, material, "MULTIPLY", family + " | modulate material") if material else light


def build_reference_group(
    mode, *,
    transmission=True, volume=False, emission=True, environment=True,
):
    """Return an isolated, reusable compositor subgroup; no scene mutation."""
    if bpy.app.version < (5, 0, 0):
        raise RuntimeError("SID reference adapter requires Blender 5.0 or newer")
    if mode not in MODES:
        raise ValueError(f"Unknown SID mode: {mode}")
    tree = bpy.data.node_groups.new("SID Reference | " + mode, "CompositorNodeTree")
    try:
        for name in ("Noisy Image", "Denoising Normal", "Denoising Albedo"):
            _interface(tree, name, "INPUT", "NodeSocketVector" if name == "Denoising Normal" else "NodeSocketColor")
        if mode != "STANDARD":
            _interface(tree, "Alpha", "INPUT")
            for family, _ in FAMILIES:
                if family == "Transmission" and not transmission:
                    continue
                for suffix in ("Direct", "Indirect", "Color"):
                    _interface(tree, family + " " + suffix, "INPUT")
            if volume:
                _interface(tree, "Volume Direct", "INPUT")
                _interface(tree, "Volume Indirect", "INPUT")
            if emission:
                _interface(tree, "Emission", "INPUT")
            if environment:
                _interface(tree, "Environment", "INPUT")

        _interface(tree, "Denoised Image", "OUTPUT")
        if mode != "STANDARD":
            for family, _ in FAMILIES:
                if family != "Transmission" or transmission:
                    _interface(tree, "Denoised " + family, "OUTPUT")
            if volume:
                _interface(tree, "Denoised Volume", "OUTPUT")
            if emission:
                _interface(tree, "Denoised Emission", "OUTPUT")
            if environment:
                _interface(tree, "Environment", "OUTPUT")

        inp = tree.nodes.new("NodeGroupInput")
        out = tree.nodes.new("NodeGroupOutput")
        normal, albedo = inp.outputs["Denoising Normal"], inp.outputs["Denoising Albedo"]
        if mode == "STANDARD":
            image = _oidn(tree, inp.outputs["Noisy Image"], normal, albedo,
                          label="Standard | single OIDN", prefilter="Fast")
            tree.links.new(image, out.inputs["Denoised Image"])
        else:
            contributions = []
            for family, _ in FAMILIES:
                if family == "Transmission" and not transmission:
                    continue
                filtered = _family(tree, inp, family, mode, normal, albedo)
                contributions.append((family, filtered))
                tree.links.new(filtered, out.inputs["Denoised " + family])
            if volume:
                filtered = _family(tree, inp, "Volume", mode, normal, albedo, guided=False)
                contributions.append(("Volume", filtered))
                tree.links.new(filtered, out.inputs["Denoised Volume"])
            if emission:
                filtered = _oidn(tree, inp.outputs["Emission"], None, None,
                                  label="Emission | unguided OIDN", prefilter="Accurate")
                contributions.append(("Emission", filtered))
                tree.links.new(filtered, out.inputs["Denoised Emission"])
            if environment:
                contributions.append(("Environment", inp.outputs["Environment"]))
                tree.links.new(inp.outputs["Environment"], out.inputs["Environment"])

            # SID sums the family outputs and only THEN runs the final denoiser.
            result = contributions[0][1]
            for name, contribution in contributions[1:]:
                result = _mix(tree, result, contribution, "ADD", "Add " + name)
            image = _oidn(tree, result, normal, albedo,
                          label="Final | guided OIDN", prefilter="Accurate")
            alpha = _oidn(tree, inp.outputs["Alpha"], normal, albedo,
                          label="Alpha | independent guided OIDN", prefilter="Accurate")
            # Blender 5 replacement for old Separate RGBA + Combine RGBA.
            # Channel equivalence with old SID requires an EXR alpha test.
            set_alpha = tree.nodes.new("CompositorNodeSetAlpha")
            set_alpha.label = "Final | combine denoised RGB and Alpha"
            set_alpha.inputs["Type"].default_value = "Replace Alpha"
            tree.links.new(image, set_alpha.inputs["Image"])
            tree.links.new(alpha, set_alpha.inputs["Alpha"])
            tree.links.new(set_alpha.outputs["Image"], out.inputs["Denoised Image"])

        tree["sid_reference_upstream_commit"] = SOURCE_COMMIT
        tree["sid_reference_mode"] = mode
        tree["sid_reference_blender5_adapter"] = True
        tree["sid_reference_equivalence_verified"] = False
        return tree
    except Exception:
        bpy.data.node_groups.remove(tree)
        raise


def prepare_reference_passes(view_layer, *, transmission=True, volume=False, emission=True, environment=True):
    """Explicit, mutating preflight. Caller should snapshot/restore settings."""
    for family, _ in FAMILIES:
        enabled = (family != "Transmission" or transmission)
        for suffix in ("direct", "indirect", "color"):
            setattr(view_layer, f"use_pass_{family.lower()}_{suffix}", enabled)
    view_layer.use_pass_emit = emission
    view_layer.use_pass_environment = environment
    if hasattr(view_layer.cycles, "use_pass_volume_direct"):
        view_layer.cycles.use_pass_volume_direct = volume
        view_layer.cycles.use_pass_volume_indirect = volume
    view_layer.cycles.denoising_store_passes = True
    view_layer.cycles.use_denoising = False
    view_layer.update_render_passes()


def build_scene_reference(scene, view_layer, mode="SUPER", **options):
    """Build a stand-alone test compositor. Does NOT assign it to the scene."""
    sub = build_reference_group(mode, **options)
    tree = bpy.data.node_groups.new("SID Reference Scene | " + mode, "CompositorNodeTree")
    try:
        _interface(tree, "Image", "OUTPUT")
        layers = tree.nodes.new("CompositorNodeRLayers")
        layers.scene = scene
        layers.layer = view_layer.name
        view_layer.update_render_passes()
        node = tree.nodes.new("CompositorNodeGroup")
        node.node_tree = sub
        node.label = "SID Reference " + mode
        tree["sid_reference_upstream_commit"] = SOURCE_COMMIT
        tree["sid_noisy_image_socket"] = "Noisy Image" if (
            _lookup(layers.outputs, "Noisy Image", required=False) is not None
            and any(x.name == "Noisy Image" and x.enabled for x in layers.outputs)
        ) else "Image"
        for socket in node.inputs:
            actual = _lookup(layers.outputs, socket.name)
            tree.links.new(actual, socket)
        out = tree.nodes.new("NodeGroupOutput")
        tree.links.new(node.outputs["Denoised Image"], out.inputs["Image"])
        # Important: not replacing scene.compositing_node_group.
        return tree
    except Exception:
        bpy.data.node_groups.remove(tree)
        if sub.users == 0:
            bpy.data.node_groups.remove(sub)
        raise
