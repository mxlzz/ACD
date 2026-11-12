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
missing = [
    img.name
    for img in bpy.data.images
    if img.source == "FILE" and img.filepath and img.packed_file is None
    and not Path(bpy.path.abspath(img.filepath, library=img.library)).is_file()
]
libraries = [lib.name for lib in bpy.data.libraries]
if not scene.camera:
    raise RuntimeError("No active camera; cannot publish an unverified benchmark scene")
if missing:
    raise RuntimeError("Missing unbundled texture resources: " + repr(missing[:20]))
if libraries:
    raise RuntimeError("Linked external .blend libraries not packaged: " + repr(libraries))
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
    "unbundled_missing_images": len(missing),
    "external_blend_libraries": len(libraries),
    "smoke_render": "192x192; 4 spp; Cycles CPU; no denoising; only functional validation",
    "smoke_render_success": True,
    "not_a_quality_benchmark": True
}
Path(os.environ.get("ACD_AUDIT_OUTPUT", "/tmp/acd_public_scene_audit.json")).write_text(json.dumps(report, indent=2) + "\n")
print("ACD_PUBLIC_SCENE_AUDIT", json.dumps(report, sort_keys=True))
