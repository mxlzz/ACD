"""ACD Blender 5.x experimental adapter.

Independent, SID-inspired compositional pipeline. No upstream code copied.
Requires Blender 5.0+ and Cycles. This file has NOT been verified in Blender yet.
"""
bl_info = {
    "name": "ACD — Adaptive Compositional Denoiser (Experimental)",
    "author": "ACD contributors",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "Properties > Render > ACD",
    "description": "Standard, family-level and per-pass denoising prototypes for Cycles",
    "category": "Render",
}

import bpy
from bpy.props import BoolProperty, EnumProperty

PREFIX = "ACD | "
PREVIOUS_KEY = "_acd_previous_compositor"
PREVIOUS_PRESENT_KEY = "_acd_previous_saved"

FAMILIES = (
    ("Diffuse", "Diff"),
    ("Glossy", "Gloss"),
    ("Transmission", "Trans"),
)

ALIASES = {
    "Image": ("Image", "Combined"),
    "Denoising Albedo": ("Denoising Albedo",),
    "Denoising Normal": ("Denoising Normal",),
    "Alpha": ("Alpha",),
    "Emission": ("Emission", "Emit"),
    "Environment": ("Environment", "Env"),
    "Volume Direct": ("Volume Direct", "VolumeDir"),
    "Volume Indirect": ("Volume Indirect", "VolumeInd"),
}
for _family, _short in FAMILIES:
    for _kind, _suffix in (("Direct", "Dir"), ("Indirect", "Ind"), ("Color", "Col")):
        ALIASES[f"{_family} {_kind}"] = (
            f"{_family} {_kind}", f"{_short}{_suffix}"
        )


def active_socket(sockets, name, kind=None):
    matches = [socket for socket in sockets if socket.name == name]
    if kind is not None:
        matches = [socket for socket in matches if socket.type == kind]
    if not matches:
        raise RuntimeError(f"Missing node socket: {name}")
    return matches[0]


def combine(nodes, links, a, b, operation, label, position):
    node = nodes.new("ShaderNodeMix")
    node.data_type = "RGBA"
    node.blend_type = operation
    node.clamp_factor = True
    node.clamp_result = False
    node.label = label
    node.location = position
    active_socket(node.inputs, "Factor").default_value = 1.0
    links.new(a, active_socket(node.inputs, "A", "RGBA"))
    links.new(b, active_socket(node.inputs, "B", "RGBA"))
    return active_socket(node.outputs, "Result", "RGBA")


def denoise(nodes, links, image, normal, albedo, label, position):
    node = nodes.new("CompositorNodeDenoise")
    node.label = label
    node.location = position
    links.new(image, node.inputs["Image"])
    if albedo is not None:
        links.new(albedo, node.inputs["Albedo"])
    if normal is not None:
        links.new(normal, node.inputs["Normal"])
    node.inputs["HDR"].default_value = True
    # Blender 5 enum menu sockets use their display values.
    node.inputs["Prefilter"].default_value = "Accurate"
    node.inputs["Quality"].default_value = "High"
    return node.outputs["Image"]


def snapshot_view_layer(view_layer):
    """Capture the subset of render-pass settings this addon can modify."""
    targets = [
        (view_layer, "use_pass_combined"),
        (view_layer, "use_pass_diffuse_direct"),
        (view_layer, "use_pass_diffuse_indirect"),
        (view_layer, "use_pass_diffuse_color"),
        (view_layer, "use_pass_glossy_direct"),
        (view_layer, "use_pass_glossy_indirect"),
        (view_layer, "use_pass_glossy_color"),
        (view_layer, "use_pass_transmission_direct"),
        (view_layer, "use_pass_transmission_indirect"),
        (view_layer, "use_pass_transmission_color"),
        (view_layer, "use_pass_emit"),
        (view_layer, "use_pass_environment"),
        (view_layer.cycles, "denoising_store_passes"),
        (view_layer.cycles, "use_denoising"),
        (view_layer.cycles, "use_pass_volume_direct"),
        (view_layer.cycles, "use_pass_volume_indirect"),
    ]
    return [(target, name, getattr(target, name))
            for target, name in targets if hasattr(target, name)]


def enable_passes(view_layer, scene):
    for name in (
        "use_pass_combined",
        "use_pass_diffuse_direct", "use_pass_diffuse_indirect", "use_pass_diffuse_color",
        "use_pass_glossy_direct", "use_pass_glossy_indirect", "use_pass_glossy_color",
    ):
        setattr(view_layer, name, True)
    for suffix in ("direct", "indirect", "color"):
        setattr(view_layer, "use_pass_transmission_" + suffix, scene.acd_transmission)
    view_layer.use_pass_emit = scene.acd_emission
    view_layer.use_pass_environment = scene.acd_environment
    if hasattr(view_layer.cycles, "use_pass_volume_direct"):
        view_layer.cycles.use_pass_volume_direct = scene.acd_volumes
        view_layer.cycles.use_pass_volume_indirect = scene.acd_volumes
    view_layer.cycles.denoising_store_passes = True
    # We control denoising in the compositor; Image is then the raw beauty.
    view_layer.cycles.use_denoising = False
    view_layer.update_render_passes()


def render_socket(render_node, key, required=True):
    aliases = ALIASES.get(key, (key,))
    for candidate in aliases:
        socket = next(
            (output for output in render_node.outputs
             if output.name == candidate and output.enabled),
            None,
        )
        if socket is not None:
            return socket
    if required:
        available = ", ".join(s.name for s in render_node.outputs if s.enabled)
        raise RuntimeError(f"Render pass '{key}' unavailable. Enabled passes: {available}")
    return None


def family_output(tree, render_node, family, mode, normal, albedo, ypos):
    nodes, links = tree.nodes, tree.links
    direct = render_socket(render_node, family + " Direct")
    indirect = render_socket(render_node, family + " Indirect")
    material = render_socket(render_node, family + " Color")
    if mode == "SUPER":
        direct = denoise(nodes, links, direct, normal, albedo, family + " | direct", (-960, ypos))
        indirect = denoise(nodes, links, indirect, normal, albedo, family + " | indirect", (-960, ypos - 240))
        lighting = combine(nodes, links, direct, indirect, "ADD", family + " | sum", (-650, ypos))
        return combine(nodes, links, lighting, material, "MULTIPLY", family + " | material", (-370, ypos))
    lighting = combine(nodes, links, direct, indirect, "ADD", family + " | sum", (-950, ypos))
    colored = combine(nodes, links, lighting, material, "MULTIPLY", family + " | material", (-680, ypos))
    return denoise(nodes, links, colored, normal, albedo, family + " | high", (-380, ypos))


def make_tree(scene, view_layer):
    mode = scene.acd_mode
    tree = bpy.data.node_groups.new(PREFIX + view_layer.name + " | " + mode, "CompositorNodeTree")
    try:
        tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        nodes, links = tree.nodes, tree.links
        render_node = nodes.new("CompositorNodeRLayers")
        render_node.scene = scene
        render_node.layer = view_layer.name
        render_node.label = "Cycles: unfiltered render passes"
        render_node.location = (-1420, 180)
        view_layer.update_render_passes()

        beauty = render_socket(render_node, "Image")
        normal = render_socket(render_node, "Denoising Normal")
        albedo = render_socket(render_node, "Denoising Albedo")
        alpha = render_socket(render_node, "Alpha", required=False)

        if mode == "STANDARD":
            result = denoise(nodes, links, beauty, normal, albedo,
                             "Standard OIDN", (-640, 200))
        else:
            components = []
            for index, (family, _) in enumerate(FAMILIES):
                if family == "Transmission" and not scene.acd_transmission:
                    continue
                components.append(
                    family_output(tree, render_node, family, mode, normal, albedo, 600 - 760 * index)
                )
            if scene.acd_volumes:
                volume_direct = render_socket(render_node, "Volume Direct")
                volume_indirect = render_socket(render_node, "Volume Indirect")
                if mode == "SUPER":
                    volume_direct = denoise(nodes, links, volume_direct, None, None,
                                            "Volume direct", (-960, -1870))
                    volume_indirect = denoise(nodes, links, volume_indirect, None, None,
                                              "Volume indirect", (-960, -2110))
                    volume = combine(nodes, links, volume_direct, volume_indirect,
                                     "ADD", "Volume sum", (-660, -1870))
                else:
                    volume = combine(nodes, links, volume_direct, volume_indirect,
                                     "ADD", "Volume sum", (-960, -1870))
                    volume = denoise(nodes, links, volume, None, None,
                                     "Volume high", (-670, -1870))
                components.append(volume)
            if scene.acd_emission:
                emission = render_socket(render_node, "Emission")
                if scene.acd_filter_emission:
                    emission = denoise(nodes, links, emission, normal, albedo,
                                       "Emission OIDN", (-460, -2390))
                components.append(emission)
            if scene.acd_environment:
                components.append(render_socket(render_node, "Environment"))
            if not components:
                raise RuntimeError("No render contributions enabled")
            result = components[0]
            for index, component in enumerate(components[1:], 1):
                result = combine(nodes, links, result, component, "ADD",
                                 f"Add component {index}", (140 + 250 * index, -470))
            if scene.acd_final_filter:
                result = denoise(nodes, links, result, normal, albedo,
                                 "Post-composition OIDN", (1450, 120))

        if alpha is not None:
            if scene.acd_alpha_filter and mode != "STANDARD":
                alpha = denoise(nodes, links, alpha, normal, albedo,
                                "Alpha OIDN (experimental)", (1480, -600))
            set_alpha = nodes.new("CompositorNodeSetAlpha")
            set_alpha.label = "Restore / filter alpha"
            set_alpha.location = (1830, 140)
            set_alpha.inputs["Type"].default_value = "Replace Alpha"
            links.new(result, set_alpha.inputs["Image"])
            links.new(alpha, set_alpha.inputs["Alpha"])
            result = set_alpha.outputs["Image"]

        output = nodes.new("NodeGroupOutput")
        output.location = (2180, 140)
        links.new(result, output.inputs["Image"])
        tree["acd_mode"] = mode
        tree["acd_experimental"] = True
        return tree
    except Exception:
        bpy.data.node_groups.remove(tree)
        raise


class ACD_OT_build(bpy.types.Operator):
    bl_idname = "render.acd_build"
    bl_label = "Build ACD compositor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        if bpy.app.version < (5, 0, 0):
            self.report({"ERROR"}, "Blender 5.x is required")
            return {"CANCELLED"}
        if scene.render.engine != "CYCLES":
            self.report({"ERROR"}, "Select Cycles before building")
            return {"CANCELLED"}
        view_layer = context.view_layer
        old_compositor = scene.compositing_node_group
        state = snapshot_view_layer(view_layer)
        try:
            enable_passes(view_layer, scene)
            new_compositor = make_tree(scene, view_layer)
        except Exception as exc:
            for target, name, value in reversed(state):
                try:
                    setattr(target, name, value)
                except Exception:
                    pass
            view_layer.update_render_passes()
            self.report({"ERROR"}, f"ACD build failed, compositor preserved: {exc}")
            return {"CANCELLED"}
        if not scene.get(PREVIOUS_PRESENT_KEY, False):
            scene[PREVIOUS_PRESENT_KEY] = True
            scene[PREVIOUS_KEY] = old_compositor.name if old_compositor else ""
            if old_compositor:
                old_compositor.use_fake_user = True
        scene.compositing_node_group = new_compositor
        scene.render.use_compositing = True
        if old_compositor and old_compositor.name.startswith(PREFIX) and old_compositor.users == 0:
            bpy.data.node_groups.remove(old_compositor)
        self.report({"INFO"}, f"ACD {scene.acd_mode} compositor created; render with F12")
        return {"FINISHED"}


class ACD_OT_restore(bpy.types.Operator):
    bl_idname = "render.acd_restore"
    bl_label = "Restore previous compositor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        if not scene.get(PREVIOUS_PRESENT_KEY, False):
            self.report({"ERROR"}, "No previous compositor snapshot")
            return {"CANCELLED"}
        old_name = scene.get(PREVIOUS_KEY, "")
        if old_name and old_name not in bpy.data.node_groups:
            self.report({"ERROR"}, "Saved previous compositor no longer exists")
            return {"CANCELLED"}
        scene.compositing_node_group = bpy.data.node_groups.get(old_name) if old_name else None
        del scene[PREVIOUS_PRESENT_KEY]
        if PREVIOUS_KEY in scene:
            del scene[PREVIOUS_KEY]
        self.report({"INFO"}, "Previous compositor restored")
        return {"FINISHED"}


class ACD_PT_panel(bpy.types.Panel):
    bl_label = "ACD (experimental 0.1.0)"
    bl_idname = "ACD_PT_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        scene = context.scene
        column = self.layout.column(align=True)
        column.prop(scene, "acd_mode", text="Strategy")
        if scene.acd_mode != "STANDARD":
            column.prop(scene, "acd_final_filter", text="Post-composition OIDN")
            column.prop(scene, "acd_filter_emission", text="Filter emission")
        column.prop(scene, "acd_transmission", text="Transmission passes")
        column.prop(scene, "acd_volumes", text="Volume passes")
        column.prop(scene, "acd_emission", text="Emission pass")
        column.prop(scene, "acd_environment", text="Environment pass")
        column.prop(scene, "acd_alpha_filter", text="Filter alpha (experimental)")
        column.separator()
        column.operator("render.acd_build", icon="NODETREE")
        if scene.get(PREVIOUS_PRESENT_KEY, False):
            column.operator("render.acd_restore", icon="LOOP_BACK")
        column.label(text="Rebuild after changing settings.")
        column.label(text="Experimental: test before production use.")


CLASSES = (ACD_OT_build, ACD_OT_restore, ACD_PT_panel)


def register():
    for klass in CLASSES:
        bpy.utils.register_class(klass)
    bpy.types.Scene.acd_mode = EnumProperty(
        name="ACD strategy",
        items=[
            ("STANDARD", "Standard", "One OIDN on raw beauty"),
            ("HIGH", "High", "One OIDN per recombined lighting family"),
            ("SUPER", "Super", "OIDN on each direct and indirect contribution"),
        ],
        default="SUPER",
    )
    bpy.types.Scene.acd_final_filter = BoolProperty(default=True)
    bpy.types.Scene.acd_transmission = BoolProperty(default=True)
    bpy.types.Scene.acd_volumes = BoolProperty(default=False)
    bpy.types.Scene.acd_emission = BoolProperty(default=True)
    bpy.types.Scene.acd_environment = BoolProperty(default=True)
    bpy.types.Scene.acd_filter_emission = BoolProperty(default=True)
    bpy.types.Scene.acd_alpha_filter = BoolProperty(default=False)


def unregister():
    for name in (
        "acd_mode", "acd_final_filter", "acd_transmission", "acd_volumes",
        "acd_emission", "acd_environment", "acd_filter_emission", "acd_alpha_filter",
    ):
        delattr(bpy.types.Scene, name)
    for klass in reversed(CLASSES):
        bpy.utils.unregister_class(klass)


if __name__ == "__main__":
    register()
