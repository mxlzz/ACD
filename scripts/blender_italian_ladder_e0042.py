"""E0042: Italian Flat 640x400 independent reference ladder without denoising."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import resource
import time
import bpy

ROOT=Path(os.environ.get("ACD_E0042_ROOT","/tmp/acd-e0042")).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
PIN="0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25"
source=Path(bpy.data.filepath)
if not source.is_file():
    raise RuntimeError("Source .blend must be loaded")
h=hashlib.sha256()
with source.open("rb") as f:
    for block in iter(lambda:f.read(8*1024*1024),b""):
        h.update(block)
if h.hexdigest()!=PIN:
    raise RuntimeError("Italian Flat binary hash mismatch")
missing=[i.name for i in bpy.data.images if i.source=="FILE" and i.filepath and not i.packed_file
         and not Path(bpy.path.abspath(i.filepath,library=i.library)).is_file()]
if missing or bpy.data.libraries:
    raise RuntimeError("External assets missing / linked libraries: "+repr(missing))
scene=bpy.context.scene
cam=bpy.data.objects.get("Cam Kitchen Table")
if not cam or cam.type!="CAMERA":
    raise RuntimeError("E0040 camera not found")
scene.camera=cam
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.use_adaptive_sampling=False
scene.cycles.use_denoising=False
for layer in scene.view_layers:
    layer.cycles.use_denoising=False
scene.render.use_compositing=False
scene.render.resolution_x=640
scene.render.resolution_y=400
scene.render.resolution_percentage=100
scene.render.image_settings.media_type="IMAGE"
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_depth="32"
scene.render.image_settings.color_mode="RGBA"
scene.render.image_settings.exr_codec="ZIP"
grid=[(spp,seed) for spp in (32,64,128) for seed in (8819,8922)]
report=[]
for spp,seed in grid:
    scene.cycles.samples=spp
    scene.cycles.seed=seed
    dest=ROOT/f"ref_640x400_{spp}spp_seed{seed}.exr"
    scene.render.filepath=str(dest)
    tic=time.perf_counter()
    result=bpy.ops.render.render(write_still=True)
    elapsed=time.perf_counter()-tic
    if "FINISHED" not in result or not dest.is_file() or dest.stat().st_size<=100:
        raise RuntimeError("Output not written: "+dest.name)
    hx=hashlib.sha256()
    with dest.open("rb") as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):
            hx.update(block)
    row={"file":dest.name,"resolution":[640,400],"spp":spp,"seed":seed,
         "wall_seconds":float(elapsed),"file_sha256":hx.hexdigest(),
         "bytes":dest.stat().st_size,
         "process_peak_rss_kb":int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)}
    report.append(row)
    print("ACD_E0042_RENDER",json.dumps(row,sort_keys=True),flush=True)
payload={
    "experiment":"E0042","source_sha256":PIN,"source_author":"Flavio Della Tommasa",
    "source_license":"Official Blender Cycles Demo, CC-BY (catalog version unspecified)",
    "camera":cam.name,"blender":bpy.app.version_string,
    "device":"CPU","resolution":[640,400],"adaptive_sampling":False,
    "denoising":False,"original_blend_untouched":True,
    "samples_grid":[32,64,128],"seeds":[8819,8922],
    "entries":report,
    "independent_seed_streams_proven":False,
    "reference_convergence_proven":False,
    "intent":"Finite-reference disagreement only, no denoiser rankings"
}
(ROOT/"e0042_manifest.json").write_text(json.dumps(payload,indent=2)+"\n")
print("ACD_E0042_FINISHED",len(report),flush=True)
