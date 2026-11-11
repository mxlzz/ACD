"""M3.7 isolated compositor OIDN, same input EXRs, across Blender 3.6 and 5.0.

No SID graph and no mixer; isolates Fast, Accurate, emission, and alpha OIDN.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
from pathlib import Path
import bpy

SRC=Path(os.environ["ACD_OIDN_INPUT"]).resolve()
DEST=Path(os.environ["ACD_OIDN_OUTPUT"]).resolve()
FLAVOR=os.environ["ACD_OIDN_FLAVOR"]
assert FLAVOR in ("legacy","port")
assert bpy.app.version[:2]==((3,6) if FLAVOR=="legacy" else (5,0))
DEST.mkdir(parents=True,exist_ok=True)
CASES={
    "guided_fast":("noisy","Fast",True),
    "guided_accurate":("noisy","Accurate",True),
    "emission_accurate_unguided":("emission","Accurate",False),
    "alpha_accurate_guided":("alpha","Accurate",True),
    "diffuse_direct_accurate_guided":("diffuse_direct","Accurate",True),
}
RAW=("noisy","albedo","normal","alpha","emission","diffuse_direct")
scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=1
scene.render.resolution_x=96
scene.render.resolution_y=64
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_depth="32"
scene.render.filepath=str(DEST/"unused_render.exr")
scene.render.use_compositing=True
scene.view_settings.view_transform="Standard"
if FLAVOR=="legacy":
    scene.use_nodes=True
    tree=scene.node_tree
    tree.nodes.clear()
else:
    tree=bpy.data.node_groups.new("M3.7 isolated OIDN experiment","CompositorNodeTree")
    tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
    scene.compositing_node_group=tree
nodes,links=tree.nodes,tree.links
source={}
for name in RAW:
    image=nodes.new("CompositorNodeImage")
    image.image=bpy.data.images.load(str(SRC/(name+".exr")),check_existing=False)
    image.image.colorspace_settings.name="Non-Color"
    source[name]=image.outputs["Image"]

def denoise(name,source_name,prefilter,guided):
    dn=nodes.new("CompositorNodeDenoise")
    dn.label=name
    if FLAVOR=="legacy":
        dn.prefilter=prefilter.upper()
        links.new(source[source_name],dn.inputs[0])
        if guided:
            links.new(source["normal"],dn.inputs[1])
            links.new(source["albedo"],dn.inputs[2])
    else:
        dn.inputs["Prefilter"].default_value=prefilter
        dn.inputs["Quality"].default_value="High"
        dn.inputs["HDR"].default_value=True
        links.new(source[source_name],dn.inputs["Image"])
        if guided:
            links.new(source["normal"],dn.inputs["Normal"])
            links.new(source["albedo"],dn.inputs["Albedo"])
    return dn.outputs["Image"]

outcomes={name:denoise(name,*settings) for name,settings in CASES.items()}
if FLAVOR=="legacy":
    composite=nodes.new("CompositorNodeComposite")
    links.new(outcomes["guided_fast"],composite.inputs["Image"])
else:
    output=nodes.new("NodeGroupOutput")
    links.new(outcomes["guided_fast"],output.inputs["Image"])

def export(name,socket):
    folder=DEST/name
    folder.mkdir(parents=True,exist_ok=True)
    node=nodes.new("CompositorNodeOutputFile")
    if FLAVOR=="port":
        node.format.media_type="IMAGE"
    node.format.file_format="OPEN_EXR"
    node.format.color_depth="32"
    node.format.color_mode="RGBA"
    node.format.exr_codec="ZIP"
    if FLAVOR=="legacy":
        node.base_path=str(folder)
        node.file_slots[0].path=name+"_"
        links.new(socket,node.inputs[0])
    else:
        node.directory=str(folder)
        node.file_name=name+"_"
        node.file_output_items.clear()
        node.file_output_items.new("RGBA","Image")
        links.new(socket,node.inputs["Image"])

for name in RAW:
    export("raw_"+name,source[name])
for name,socket in outcomes.items():
    export(name,socket)
result=bpy.ops.render.render()
assert "FINISHED" in result
output_names=["raw_"+name for name in RAW]+list(outcomes)
for name in output_names:
    matches=list((DEST/name).glob("*.exr"))
    assert len(matches)==1,(name,matches)
    shutil.copyfile(matches[0],DEST/(name+".exr"))
manifest={
    "flavor":FLAVOR,"blender":bpy.app.version_string,
    "input_sha256":{name:hashlib.sha256((SRC/(name+".exr")).read_bytes()).hexdigest()
                    for name in RAW},
    "cases":{name:{"image":source_name,"prefilter":prefilter,"guided":guided}
             for name,(source_name,prefilter,guided) in CASES.items()},
    "blender5_oidn_settings":None if FLAVOR=="legacy" else {"Quality":"High","HDR":True},
    "old_oidn_settings":"Historical SID set only Prefilter in Blender 3.6" if FLAVOR=="legacy" else None,
    "oidn_backend_version":"not exposed by this test",
}
(DEST/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("M3.7 ISOLATED OIDN COMPLETE",FLAVOR,bpy.app.version_string,list(outcomes))
