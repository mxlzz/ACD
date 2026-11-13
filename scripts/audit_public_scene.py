"""Read-only Blender 5 Cycles smoke check of a third-party public fixture.

Invoked in a disposable Actions checkout, with --disable-autoexec. Never saves
the original .blend. Report is intentionally limited to non-sensitive counts.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import bpy

scene = bpy.context.scene
camera_count = sum(ob.type == "CAMERA" for ob in bpy.data.objects)
# Optional archive-only path correction for files actually included in a verified ZIP.
# Never save the source .blend, and never fabricate replacement images.
asset_path_remaps = []
if os.environ.get("ACD_AUDIT_RELINK_ROOT"):
    unpacked = Path(os.environ["ACD_AUDIT_RELINK_ROOT"]).resolve()
    if not unpacked.is_dir():
        raise RuntimeError("Archive root missing for in-memory relink")
    for image in bpy.data.images:
        if image.source != "FILE" or not image.filepath or image.packed_file:
            continue
        actual = Path(bpy.path.abspath(image.filepath, library=image.library))
        if actual.is_file():
            continue
        basename = image.filepath.replace("\\", "/").rsplit("/", 1)[-1]
        choices = [p.resolve() for p in unpacked.rglob(basename) if p.is_file()]
        if len(choices) == 1 and choices[0].is_relative_to(unpacked):
            image.filepath = str(choices[0])
            asset_path_remaps.append({
                "image": image.name, "archive_relative_path": str(choices[0].relative_to(unpacked)),
                "in_memory_only": True
            })
        else:
            print("ACD_AUDIT_UNRESOLVED_TEXTURE", image.name, basename, "candidate_count", len(choices))

missing = [
    img.name
    for img in bpy.data.images
    if img.source == "FILE" and img.filepath and img.packed_file is None
    and not Path(bpy.path.abspath(img.filepath, library=img.library)).is_file()
]
libraries = [lib.name for lib in bpy.data.libraries]

# IES photometric profiles affect lighting but do not appear in bpy.data.images.
# A valid render fixture must not silently omit them.
missing_ies = []
shader_trees = [x.node_tree for collection in (bpy.data.materials,bpy.data.worlds,bpy.data.lights)
                for x in collection if x.use_nodes and x.node_tree]
shader_trees += [x for x in bpy.data.node_groups if x.bl_idname == "ShaderNodeTree"]
seen = set()
for tree in shader_trees:
    if tree.as_pointer() in seen:
        continue
    seen.add(tree.as_pointer())
    for node in tree.nodes:
        if node.bl_idname == "ShaderNodeTexIES" and node.mode == "EXTERNAL":
            path = Path(bpy.path.abspath(node.filepath)) if node.filepath else None
            if path is None or not path.is_file():
                missing_ies.append({"node_tree":tree.name, "node":node.name,
                                    "filepath":node.filepath})
if not scene.camera:
    raise RuntimeError("No active camera; cannot publish an unverified benchmark scene")
if missing:
    raise RuntimeError("Missing unbundled texture resources: " + repr(missing[:20]))
if libraries:
    raise RuntimeError("Linked external .blend libraries not packaged: " + repr(libraries))
if missing_ies:
    raise RuntimeError("Missing external photometric IES profiles: " + repr(missing_ies[:15]))
if not bpy.data.materials:
    raise RuntimeError("No materials found")

# Smoke test only. NEVER persist these settings to .blend.
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 4
scene.cycles.use_denoising = False
for layer in scene.view_layers:
    layer.cycles.use_denoising = False
scene.render.resolution_x = 192
scene.render.resolution_y = 192
scene.render.resolution_percentage = 100
scene.render.use_compositing = False
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.environ.get("ACD_AUDIT_RENDER", "/tmp/acd_public_scene_smoke.png")
result = bpy.ops.render.render(write_still=True)
assert "FINISHED" in result
assert Path(scene.render.filepath).is_file()

report = {
    "source": os.environ.get("ACD_AUDIT_SOURCE", "Blender Foundation official Blender 3.5 splash / Cozy Kitchen / Nicole Morena"),
    "blender_used": bpy.app.version_string,
    "scene": scene.name,
    "saved_file_untouched": True,
    "active_camera": scene.camera.name,
    "cameras": camera_count,
    "objects": len(bpy.data.objects),
    "meshes": sum(o.type == "MESH" for o in bpy.data.objects),
    "materials": len(bpy.data.materials),
    "images": len(bpy.data.images),
    "packed_images": sum(bool(img.packed_file) for img in bpy.data.images),
    "asset_path_remaps": asset_path_remaps,
    "unbundled_missing_images": len(missing),
    "external_blend_libraries": len(libraries),
    "missing_ies_profiles": missing_ies,
    "smoke_render": "192x192; 4 spp; Cycles CPU; no denoising; only functional validation",
    "smoke_render_success": True,
    "not_a_quality_benchmark": True
}
Path(os.environ.get("ACD_AUDIT_OUTPUT", "/tmp/acd_public_scene_audit.json")).write_text(json.dumps(report, indent=2) + "\n")
print("ACD_PUBLIC_SCENE_AUDIT", json.dumps(report, sort_keys=True))
