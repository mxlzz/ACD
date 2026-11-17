"""Blender E0064: read-only Cycles framing preview of Lone Monk.

Reuses source-pinned original camera and aspect ratio; no denoising,
no compositor, no geometric/material edits, no saving of source .blend.
"""
import importlib.util
import json
import os
import time
from pathlib import Path

import bpy

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("e0064_contract",root/"scripts/lone_monk_contract_e0064.py")
contract=importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)

source=Path(bpy.data.filepath)
contract.inspect_source(source)
scene=bpy.context.scene
if scene.name!=contract.SCENE or scene.camera is None or scene.camera.name!=contract.CAMERA:
    raise RuntimeError("Unexpected scene/camera: refusing non-pinned rendering")
if bpy.app.version[:3]!=(5,2,4):
    raise RuntimeError("Unsupported Blender version for experiment")
missing_images=[
    image.name for image in bpy.data.images
    if image.source=="FILE" and image.filepath and image.packed_file is None
    and not Path(bpy.path.abspath(image.filepath,library=image.library)).is_file()
]
if missing_images:
    raise RuntimeError(f"Unexpected missing textures: {missing_images[:10]}")
if bpy.data.libraries:
    raise RuntimeError("Unexpected linked .blend libraries in source")

old_width,old_height=scene.render.resolution_x,scene.render.resolution_y
width,height=contract.frame_size(old_width,old_height)
saved_pixel_aspect=[float(scene.render.pixel_aspect_x),float(scene.render.pixel_aspect_y)]
output=Path(os.environ.get("ACD_E0064_DIRECTORY","/tmp/e0064"))
output.mkdir(parents=True,exist_ok=True)

scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=contract.SAMPLES
scene.cycles.seed=contract.SEED
scene.cycles.use_adaptive_sampling=False
scene.cycles.use_denoising=False
for layer in scene.view_layers:
    layer.cycles.use_denoising=False
scene.render.use_border=False
scene.render.use_crop_to_border=False
scene.render.resolution_x=width
scene.render.resolution_y=height
scene.render.resolution_percentage=100
scene.render.use_compositing=False
scene.render.image_settings.media_type="IMAGE"
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.image_settings.color_depth="8"
scene.render.filepath=str(output/"framing.png")
scene.render.film_transparent=False

begin=time.monotonic()
done=bpy.ops.render.render(write_still=True)
seconds=time.monotonic()-begin
if "FINISHED" not in done:
    raise RuntimeError("Blender render operator returned failure")
if not (output/"framing.png").is_file() or (output/"framing.png").stat().st_size<4096:
    raise RuntimeError("No valid nontrivial framing preview generated")

record={
    "experiment":"E0064",
    "source_sha256":contract.SOURCE_SHA,
    "source_url":contract.SOURCE_URL,
    "blender_version":bpy.app.version_string,
    "original_active_scene":scene.name,
    "original_camera":scene.camera.name,
    "original_frame":scene.frame_current,
    "camera_lens_mm":float(scene.camera.data.lens),
    "camera_type":str(scene.camera.data.type),
    "original_source_resolution":[old_width,old_height],
    "original_source_pixel_aspect":saved_pixel_aspect,
    "render_resolution":[width,height],
    "render_samples":contract.SAMPLES,
    "render_seed":contract.SEED,
    "color_management":{
        "view_transform":scene.view_settings.view_transform,
        "look":scene.view_settings.look,
        "exposure":float(scene.view_settings.exposure),
        "gamma":float(scene.view_settings.gamma),
    },
    "cycles_cpu_wall_seconds":round(seconds,2),
    "preview_bytes":(output/"framing.png").stat().st_size,
    "image_missing_count":0,
    "linked_library_count":0,
    "render_compositor_disabled":True,
    "denoiser_disabled":True,
    "new_algorithm":False,
    "quality_result":False,
    "purpose":"Framing/semantic ROI selection before high-spp or denoiser comparison",
}
(output/"framing_metadata.json").write_text(json.dumps(record,indent=2)+"\n")
print("E0064_FRAMING_FINISHED",json.dumps(record,sort_keys=True),flush=True)
