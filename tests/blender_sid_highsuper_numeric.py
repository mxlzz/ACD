"""Run real pinned GPL SID High/Super or independent Blender 5 port, same EXRs."""
from __future__ import annotations
import hashlib
import importlib
import importlib.util
import json
import os
import shutil
import sys
import types
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[1]
INPUT=Path(os.environ["ACD_NUMERIC_INPUT"]).resolve()
DEST=Path(os.environ["ACD_NUMERIC_OUTPUT"]).resolve()
FLAVOR=os.environ["ACD_NUMERIC_FLAVOR"]
MODE=os.environ["ACD_NUMERIC_MODE"]
COMMIT="b4186389cac386eff9d777bb681c0051f8bd9bd2"
assert FLAVOR in ("legacy","port") and MODE in ("HIGH","SUPER")
assert bpy.app.version[:2] == ((3,6) if FLAVOR=="legacy" else (5,0))
DEST.mkdir(parents=True,exist_ok=True)

BINDINGS=[
    ("noisy","Noisy Image","Noisy Image"),
    ("normal","Denoising Normal","Denoising Normal"),
    ("albedo","Denoising Albedo","Denoising Albedo"),
    ("alpha","Alpha","Alpha"),
    ("diffuse_direct","DiffDir","Diffuse Direct"),
    ("diffuse_indirect","DiffInd","Diffuse Indirect"),
    ("diffuse_color","DiffCol","Diffuse Color"),
    ("glossy_direct","GlossDir","Glossy Direct"),
    ("glossy_indirect","GlossInd","Glossy Indirect"),
    ("glossy_color","GlossCol","Glossy Color"),
    ("transmission_direct","TransDir","Transmission Direct"),
    ("transmission_indirect","TransInd","Transmission Indirect"),
    ("transmission_color","TransCol","Transmission Color"),
    ("emission","Emit","Emission"),
    ("environment","Env","Environment"),
]
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=1
scene.render.resolution_x=96
scene.render.resolution_y=64
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_depth="32"
scene.render.filepath=str(DEST/"render_unused.exr")
scene.render.use_compositing=True
scene.view_settings.view_transform="Standard"

if FLAVOR=="legacy":
    upstream=Path(os.environ["SID_UPSTREAM_ROOT"]).resolve()
    assert (upstream/"Cycles"/"SID_Create_Links_Cycles.py").is_file()
    pkg=types.ModuleType("sid_numeric_hs")
    pkg.__path__=[str(upstream)]
    pkg.SID_Settings=object
    sys.modules["sid_numeric_hs"]=pkg
    cyc=types.ModuleType("sid_numeric_hs.Cycles")
    cyc.__path__=[str(upstream/"Cycles")]
    sys.modules["sid_numeric_hs.Cycles"]=cyc
    hi=importlib.import_module("sid_numeric_hs.Cycles.SID_QualityHigh_Cycles")
    su=importlib.import_module("sid_numeric_hs.Cycles.SID_QualitySuper_Cycles")
    links=importlib.import_module("sid_numeric_hs.Cycles.SID_Create_Links_Cycles")
    class Settings:
        quality=MODE
        denoiser_type="SID"
        use_transmission=True
        use_volumetric=False
        use_emission=True
        use_environment=True
    subtree=(hi.create_sid_denoiser_high_cy() if MODE=="HIGH"
             else su.create_sid_denoiser_super_cy())
    sid_tree=links.create_links_cy(subtree,Settings())
    scene.use_nodes=True
    tree=scene.node_tree
    tree.nodes.clear()
else:
    spec=importlib.util.spec_from_file_location("sid_reference",ROOT/"addon"/"sid_reference.py")
    ref=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    assert ref.SOURCE_COMMIT==COMMIT
    sid_tree=ref.build_reference_group(MODE,transmission=True,volume=False,
                                       emission=True,environment=True)
    tree=bpy.data.node_groups.new("M3.5 "+MODE+" SID comparison","CompositorNodeTree")
    tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
    scene.compositing_node_group=tree

nodes,edges=tree.nodes,tree.links
group=nodes.new("CompositorNodeGroup")
group.node_tree=sid_tree
inputs={}
for key,old,new in BINDINGS:
    img=nodes.new("CompositorNodeImage")
    img.image=bpy.data.images.load(str(INPUT/(key+".exr")),check_existing=False)
    img.image.colorspace_settings.name="Non-Color"
    inputs[key]=img
    edges.new(img.outputs["Image"],group.inputs[old if FLAVOR=="legacy" else new])
if FLAVOR=="legacy":
    co=nodes.new("CompositorNodeComposite")
    edges.new(group.outputs["Denoised Image"],co.inputs["Image"])
else:
    out=nodes.new("NodeGroupOutput")
    edges.new(group.outputs["Denoised Image"],out.inputs["Image"])

def export(name,socket):
    folder=DEST/name
    folder.mkdir(parents=True,exist_ok=True)
    node=nodes.new("CompositorNodeOutputFile")
    if FLAVOR=="port":node.format.media_type="IMAGE"
    node.format.file_format="OPEN_EXR"
    node.format.color_depth="32"
    node.format.color_mode="RGBA"
    node.format.exr_codec="ZIP"
    if FLAVOR=="legacy":
        node.base_path=str(folder)
        node.file_slots[0].path=name+"_"
        edges.new(socket,node.inputs[0])
    else:
        node.directory=str(folder)
        node.file_name=name+"_"
        node.file_output_items.clear()
        node.file_output_items.new("RGBA","Image")
        edges.new(socket,node.inputs["Image"])

for key,_,_ in BINDINGS:
    export("raw_"+key,inputs[key].outputs["Image"])
export("sid",group.outputs["Denoised Image"])
assert "FINISHED" in bpy.ops.render.render()
names=["raw_"+key for key,_,_ in BINDINGS]+["sid"]
for name in names:
    matches=list((DEST/name).glob("*.exr"))
    assert len(matches)==1,(name,matches)
    shutil.copyfile(matches[0],DEST/(name+".exr"))
report={
    "mode":MODE,"flavor":FLAVOR,"blender":bpy.app.version_string,
    "upstream_commit":COMMIT,
    "input_sha256":{key:hashlib.sha256((INPUT/(key+".exr")).read_bytes()).hexdigest()
                    for key,_,_ in BINDINGS},
    "output_sha256":{key:hashlib.sha256((DEST/(key+".exr")).read_bytes()).hexdigest()
                     for key in names},
    "options":{"transmission":True,"volume":False,"emission":True,"environment":True},
    "oidn_version":"not exposed",
    "blender5_adapter_settings":None if FLAVOR=="legacy" else {"Quality":"High","HDR":True},
}
(DEST/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
print("SID HIGH/SUPER ORIGINAL/PORT COMPLETE",MODE,FLAVOR,bpy.app.version_string)
