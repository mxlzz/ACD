"""E0040: render every author-supplied camera cheaply, in an isolated copy.

Input .blend not saved. Camera audit only, not denoiser evaluation.
"""
import bpy
import hashlib
import json
import os
from pathlib import Path
import time

root=Path(os.environ.get("ACD_E0040_DIR","/tmp/acd-e0040"))
root.mkdir(parents=True,exist_ok=True)
if not bpy.data.filepath:
    raise RuntimeError("Must open official Italian Flat .blend")
source=Path(bpy.data.filepath)
actual=hashlib.sha256(source.read_bytes()).hexdigest()
expected="0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25"
if actual!=expected:
    raise RuntimeError("Source SHA256 mismatch")

missing=[
    img.name for img in bpy.data.images
    if img.source=="FILE" and img.filepath and img.packed_file is None
    and not Path(bpy.path.abspath(img.filepath,library=img.library)).is_file()
]
if missing or bpy.data.libraries:
    raise RuntimeError("Unresolved image or linked library in protected source: "+str(missing))

scene=bpy.context.scene
cameras=sorted((x for x in bpy.data.objects if x.type=="CAMERA"),key=lambda x:x.name)
if not (2<=len(cameras)<=15):
    raise RuntimeError("Unexpected camera count: "+str(len(cameras)))
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=4
scene.cycles.use_adaptive_sampling=False
scene.cycles.use_denoising=False
for view_layer in scene.view_layers:
    view_layer.cycles.use_denoising=False
scene.render.use_compositing=False
scene.render.resolution_x=320
scene.render.resolution_y=200
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"

rows=[]
for index,camera in enumerate(cameras,1):
    scene.camera=camera
    scene.render.filepath=str(root/f"camera_{index:02d}.png")
    start=time.perf_counter()
    result=bpy.ops.render.render(write_still=True)
    elapsed=time.perf_counter()-start
    path=Path(scene.render.filepath)
    if "FINISHED" not in result or not path.is_file() or path.stat().st_size<100:
        raise RuntimeError("Camera preview render failed: "+camera.name)
    translation=camera.matrix_world.translation
    rows.append({
        "index":index,"camera_name":camera.name,"png":path.name,
        "camera_location":[float(x) for x in translation],
        "lens_mm":float(camera.data.lens),
        "render_wall_seconds":float(elapsed),
        "png_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "original_scene_camera_changed_in_memory_only":True,
    })
report={
    "experiment":"E0040","blender":bpy.app.version_string,
    "source":"Italian Flat by Flavio Della Tommasa, official Blender Cycles CC-BY",
    "source_sha256":actual,"cameras":rows,
    "resolution":[320,200],"samples":4,
    "render_device":"CPU","denoising":False,
    "original_blend_saved":False,"image_quality_ranking":False,
    "method":"Seven artist cameras; 4spp each; source-native display transform; these are preview thumbnails, not reference images"
}
(root/"e0040_camera_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print("ACD_E0040_CAMERA_AUDIT",json.dumps({
    "total":len(rows),"camera_names":[x["camera_name"] for x in rows],
    "times":[round(x["render_wall_seconds"],2) for x in rows]},sort_keys=True))
