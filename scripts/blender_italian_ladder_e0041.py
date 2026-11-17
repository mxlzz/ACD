"""E0041: Italian Flat independent-seed, finite-spp noise and CPU cost pilot.

This is reference-disagreement scouting, not denoiser comparison or proof
of convergence. The source file stays unmodified and outside the repository.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import resource
import time

import bpy

ROOT=Path(os.environ.get("ACD_E0041_ROOT","/tmp/acd-e0041")).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
SOURCE_HASH="0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25"
if not bpy.data.filepath:
    raise RuntimeError("E0041 must open Italian Flat source")
source=Path(bpy.data.filepath)
hashobj=hashlib.sha256()
with source.open("rb") as f:
    for chunk in iter(lambda:f.read(8*1024*1024),b""):
        hashobj.update(chunk)
if hashobj.hexdigest()!=SOURCE_HASH:
    raise RuntimeError("Italian Flat source SHA256 mismatch")
missing=[
    im.name for im in bpy.data.images if im.source=="FILE"
    and im.filepath and im.packed_file is None
    and not Path(bpy.path.abspath(im.filepath,library=im.library)).is_file()
]
if missing or bpy.data.libraries:
    raise RuntimeError("E0041 source has missing/linked assets "+str(missing))
scene=bpy.context.scene
camera=bpy.data.objects.get("Cam Kitchen Table")
if camera is None or camera.type!="CAMERA":
    raise RuntimeError("Preselected E0040 camera not present")
scene.camera=camera
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.use_adaptive_sampling=False
scene.cycles.use_denoising=False
for layer in scene.view_layers:
    layer.cycles.use_denoising=False
scene.render.use_compositing=False
scene.render.resolution_percentage=100
scene.render.image_settings.media_type="IMAGE"
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_mode="RGBA"
scene.render.image_settings.color_depth="32"
scene.render.image_settings.exr_codec="ZIP"
protocol=[(320,200,spp,seed) for spp in (8,16,32) for seed in (8819,8922)]
protocol.append((640,400,8,8819))
results=[]
for width,height,spp,seed in protocol:
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.cycles.samples=spp
    scene.cycles.seed=seed
    path=ROOT/f"ref_{width}x{height}_{spp}spp_seed{seed}.exr"
    scene.render.filepath=str(path)
    tic=time.perf_counter()
    status=bpy.ops.render.render(write_still=True)
    seconds=time.perf_counter()-tic
    if "FINISHED" not in status or not path.is_file() or path.stat().st_size<100:
        raise RuntimeError("Expected EXR not written: "+str(path))
    filehash=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b""):
            filehash.update(chunk)
    entry={
        "file":path.name,"resolution":[width,height],"samples":spp,"seed":seed,
        "render_and_write_wall_seconds":float(seconds),
        "bytes":path.stat().st_size,
        "sha256":filehash.hexdigest(),
        "cpu_peak_rss_kb":int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
    }
    results.append(entry)
    print("ACD_E0041_RENDERED",json.dumps(entry,sort_keys=True),flush=True)
report={
    "experiment":"E0041","blender":bpy.app.version_string,
    "source":"Italian Flat, Flavio Della Tommasa, CC-BY Blender official demo",
    "source_sha256":SOURCE_HASH,
    "camera_name":camera.name,
    "original_blend_untouched":True,
    "render_engine":"CYCLES","render_device":"CPU",
    "adaptive_sampling":False,"denoising":False,
    "fixed_source_reference":False,
    "protocol":"320x200 spp 8/16/32 x seeds 8819/8922; 640x400 spp8 seed8819 only for cost",
    "results":results,
    "limits":"Small resolution and finite noisy references, no convergence, no denoiser ranking, no 1080p extrapolation without qualification",
}
(ROOT/"e0041_render_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
print("ACD_E0041_FINISHED",len(results),flush=True)
