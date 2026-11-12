"""Read-only functional audit of licensed Low-Poly Island .blend with Blender 5."""
from __future__ import annotations
import json
from pathlib import Path
import bpy

scene=bpy.context.scene
if not scene.camera:
    raise RuntimeError("Missing active camera")
if scene.render.engine != "CYCLES":
    raise RuntimeError(f"Expected Cycles saved in fixture; found {scene.render.engine}")
if not bpy.data.materials:
    raise RuntimeError("Scene has no materials")
libraries=[x.name for x in bpy.data.libraries]
missing=[
    image.name for image in bpy.data.images
    if image.source=="FILE" and image.filepath and image.packed_file is None
    and not Path(bpy.path.abspath(image.filepath,library=image.library)).is_file()
]
if libraries or missing:
    raise RuntimeError("Missing dependencies: libraries "+repr(libraries)+", textures "+repr(missing))
scene.cycles.device="CPU"
scene.cycles.samples=4
scene.cycles.use_denoising=False
for layer in scene.view_layers:
    layer.cycles.use_denoising=False
scene.render.resolution_x=192
scene.render.resolution_y=192
scene.render.resolution_percentage=100
scene.render.use_compositing=False
scene.render.image_settings.file_format="PNG"
scene.render.filepath="/tmp/acd_island_smoke.png"
if "FINISHED" not in bpy.ops.render.render(write_still=True):
    raise RuntimeError("Cycles smoke render not finished")
if not Path(scene.render.filepath).is_file():
    raise RuntimeError("Cycles output not generated")
report={
    "blender":bpy.app.version_string,
    "source":"emrelab/blender-projects @36c46d3b49ea872f6039e07a5e4769b5f9443654",
    "creator":"Yunus Emre Karaman",
    "license":"MIT",
    "original_blend_untouched":True,
    "scene":scene.name,"camera":scene.camera.name,
    "objects":len(bpy.data.objects),
    "meshes":sum(ob.type=="MESH" for ob in bpy.data.objects),
    "lights":sum(ob.type=="LIGHT" for ob in bpy.data.objects),
    "materials":len(bpy.data.materials),
    "images":len(bpy.data.images),
    "missing_textures":len(missing),
    "external_blend_libraries":len(libraries),
    "cycles_smoke":"192x192 4 spp CPU, no denoise",
    "smoke_success":True,
    "not_quality_validation":True
}
Path("/tmp/acd_island_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print("ACD_ISLAND_AUDIT",json.dumps(report,sort_keys=True))
