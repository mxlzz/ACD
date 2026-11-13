"""E0043 — one Cycles render, exactly 3 built-in OIDN guidance modes.
No new denoising algorithm and no reference used at inference.
"""
from __future__ import annotations
import hashlib, json, os, sys, time
from pathlib import Path
import bpy

SRC_SHA="0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25"
source=Path(bpy.data.filepath)
if not source.is_file():
    raise RuntimeError("E0043 requires official .blend")
h=hashlib.sha256()
with source.open("rb") as f:
    for chunk in iter(lambda:f.read(8*1024*1024),b""):
        h.update(chunk)
if h.hexdigest()!=SRC_SHA: raise RuntimeError("Source changed")
if bpy.data.libraries:raise RuntimeError("External blend libraries prohibited")
missing=[im.name for im in bpy.data.images if im.source=="FILE" and im.filepath and not im.packed_file and not Path(bpy.path.abspath(im.filepath,library=im.library)).is_file()]
if missing: raise RuntimeError("Missing textures: "+str(missing))
root=Path(os.environ.get("ACD_E0043_ROOT","/tmp/acd-e0043")).resolve()
root.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
camera=bpy.data.objects.get("Cam Kitchen Table")
if camera is None or camera.type!="CAMERA":raise RuntimeError("Camera changed")
scene.camera=camera
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=32
scene.cycles.seed=539
scene.cycles.use_adaptive_sampling=False
scene.cycles.use_denoising=False
scene.render.resolution_x=640
scene.render.resolution_y=400
scene.render.resolution_percentage=100
view=bpy.context.view_layer
view.cycles.use_denoising=False
view.cycles.denoising_store_passes=True
view.update_render_passes()
tree=bpy.data.node_groups.new("E0043 isolated guidance ablation","CompositorNodeTree")
tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
layers=tree.nodes.new("CompositorNodeRLayers")
layers.scene=scene
layers.layer=view.name
def get(name):
    s=next((s for s in layers.outputs if s.name==name and s.enabled),None)
    if s is None:raise RuntimeError("Required socket "+name+" missing; present: "+str([x.name for x in layers.outputs if x.enabled]))
    return s
beauty=get("Image")
alb=get("Denoising Albedo")
nrm=get("Denoising Normal")
group=tree.nodes.new("NodeGroupOutput")
tree.links.new(beauty,group.inputs["Image"])
out=tree.nodes.new("CompositorNodeOutputFile")
out.directory=str(root)
out.file_name="e0043_"
out.format.media_type="IMAGE"
out.format.file_format="OPEN_EXR"
out.format.color_depth="32"
out.format.exr_codec="ZIP"
out.file_output_items.clear()
def emit(name,signal):
    out.file_output_items.new("RGBA",name)
    tree.links.new(signal,out.inputs[name])
emit("Raw",beauty)
for name,guide_alb,guide_normal in [("OIDN_RGB",False,False),("OIDN_Albedo",True,False),("OIDN_Both",True,True)]:
    node=tree.nodes.new("CompositorNodeDenoise")
    node.inputs["Prefilter"].default_value="Accurate"
    node.inputs["Quality"].default_value="High"
    node.inputs["HDR"].default_value=True
    tree.links.new(beauty,node.inputs["Image"])
    if guide_alb:tree.links.new(alb,node.inputs["Albedo"])
    if guide_normal:tree.links.new(nrm,node.inputs["Normal"])
    emit(name,node.outputs["Image"])
scene.compositing_node_group=tree
scene.render.use_compositing=True
scene.render.image_settings.media_type="IMAGE"
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_depth="32"
scene.render.filepath=str(root/"render.exr")
start=time.perf_counter()
res=bpy.ops.render.render(write_still=True)
duration=time.perf_counter()-start
if "FINISHED" not in res:raise RuntimeError("Cycles failed")
filehashes={}
for name in ("Raw","OIDN_RGB","OIDN_Albedo","OIDN_Both"):
    file=root/("e0043_"+name+".exr")
    if not file.is_file() or file.stat().st_size<100:raise RuntimeError("Missing output "+str(file))
    d=hashlib.sha256()
    with file.open("rb") as f:
        for block in iter(lambda:f.read(2*1024*1024),b""):d.update(block)
    filehashes[name]={"sha256":d.hexdigest(),"size":file.stat().st_size}
report={
    "experiment":"E0043","source_sha256":SRC_SHA,
    "artist":"Flavio Della Tommasa","blender":bpy.app.version_string,
    "camera":camera.name,"samples":32,"seed":539,"resolution":[640,400],
    "device":"CPU","adaptive":False,"cycles_internal_denoising":False,
    "methods":["Raw","OIDN_RGB","OIDN_Albedo","OIDN_Both"],
    "compositor_settings":{"quality":"High","prefilter":"Accurate","HDR":True},
    "single_render":True,"shared_raw_and_guide_sockets":True,
    "wall_seconds_total":duration,
    "files":filehashes,
    "convergence_proven":False,"source_not_saved":True
}
(root/"e0043_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
print("E0043_SHARED_RENDER",json.dumps(report,sort_keys=True),flush=True)
