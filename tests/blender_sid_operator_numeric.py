"""M3.6 isolated compositor operator comparison, NO OIDN/denoising.

Blender 3.6: historical MixRGB + SepRGBA/CombRGBA.
Blender 5.0: ShaderNodeMix + SetAlpha, using the exact same frozen EXRs.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
from pathlib import Path

import bpy

SOURCE=Path(os.environ["ACD_OP_INPUT"]).resolve()
DEST=Path(os.environ["ACD_OP_OUTPUT"]).resolve()
FLAVOR=os.environ["ACD_OP_FLAVOR"]
assert FLAVOR in ("legacy","port")
assert bpy.app.version[:2] == ((3,6) if FLAVOR=="legacy" else (5,0))
DEST.mkdir(parents=True,exist_ok=True)

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
    scene.use_nodes=True
    tree=scene.node_tree
    tree.nodes.clear()
else:
    tree=bpy.data.node_groups.new("M3.6 isolated compositor operators","CompositorNodeTree")
    tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
    scene.compositing_node_group=tree
nodes,links=tree.nodes,tree.links
inputs={}
NAMES=("noisy","diffuse_direct","diffuse_indirect","diffuse_color","emission","alpha")
for name in NAMES:
    file=SOURCE/(name+".exr")
    assert file.is_file()
    image=nodes.new("CompositorNodeImage")
    image.image=bpy.data.images.load(str(file),check_existing=False)
    image.image.colorspace_settings.name="Non-Color"
    image.label=name
    inputs[name]=image.outputs["Image"]

def mix(op,left,right):
    if FLAVOR=="legacy":
        n=nodes.new("CompositorNodeMixRGB")
        n.blend_type=op
        n.inputs[0].default_value=1.0
        n.use_clamp=False
        links.new(left,n.inputs[1])
        links.new(right,n.inputs[2])
        return n.outputs[0]
    n=nodes.new("ShaderNodeMix")
    n.data_type="RGBA"
    n.blend_type=op
    n.clamp_result=False
    n.clamp_factor=True
    n.inputs["Factor"].default_value=1.0
    sock_a=next(s for s in n.inputs if s.name=="A" and s.type=="RGBA")
    sock_b=next(s for s in n.inputs if s.name=="B" and s.type=="RGBA")
    output=next(s for s in n.outputs if s.name=="Result" and s.type=="RGBA")
    links.new(left,sock_a)
    links.new(right,sock_b)
    return output

added=mix("ADD",inputs["diffuse_direct"],inputs["diffuse_indirect"])
multiplied=mix("MULTIPLY",added,inputs["diffuse_color"])
hdr=mix("ADD",inputs["noisy"],inputs["emission"])
if FLAVOR=="legacy":
    separate=nodes.new("CompositorNodeSepRGBA")
    combine=nodes.new("CompositorNodeCombRGBA")
    links.new(inputs["noisy"],separate.inputs[0])
    for c in "RGB":
        links.new(separate.outputs[c],combine.inputs[c])
    links.new(inputs["alpha"],combine.inputs["A"])
    recombined=combine.outputs[0]
    composite=nodes.new("CompositorNodeComposite")
    links.new(recombined,composite.inputs["Image"])
else:
    sa=nodes.new("CompositorNodeSetAlpha")
    sa.inputs["Type"].default_value="Replace Alpha"
    links.new(inputs["noisy"],sa.inputs["Image"])
    links.new(inputs["alpha"],sa.inputs["Alpha"])
    recombined=sa.outputs["Image"]
    out=nodes.new("NodeGroupOutput")
    links.new(recombined,out.inputs["Image"])

def export(name,socket):
    directory=DEST/name
    directory.mkdir(parents=True,exist_ok=True)
    node=nodes.new("CompositorNodeOutputFile")
    if FLAVOR=="port":
        node.format.media_type="IMAGE"
    node.format.file_format="OPEN_EXR"
    node.format.color_depth="32"
    node.format.color_mode="RGBA"
    node.format.exr_codec="ZIP"
    if FLAVOR=="legacy":
        node.base_path=str(directory)
        node.file_slots[0].path=name+"_"
        links.new(socket,node.inputs[0])
    else:
        node.directory=str(directory)
        node.file_name=name+"_"
        node.file_output_items.clear()
        node.file_output_items.new("RGBA","Image")
        links.new(socket,node.inputs["Image"])

for key in NAMES:
    export("raw_"+key,inputs[key])
for key,value in {"add_diffuse":added,"mul_diffuse":multiplied,
                  "add_emission_hdr":hdr,"recombine_alpha":recombined}.items():
    export(key,value)
assert "FINISHED" in bpy.ops.render.render()
outputs=["raw_"+n for n in NAMES]+["add_diffuse","mul_diffuse",
                                   "add_emission_hdr","recombine_alpha"]
for name in outputs:
    found=list((DEST/name).glob("*.exr"))
    assert len(found)==1,(name,found)
    shutil.copyfile(found[0],DEST/(name+".exr"))
manifest={
    "flavor":FLAVOR,"blender":bpy.app.version_string,
    "input_sha256":{n:hashlib.sha256((SOURCE/(n+".exr")).read_bytes()).hexdigest()
                    for n in NAMES},
    "outputs":{n:hashlib.sha256((DEST/(n+".exr")).read_bytes()).hexdigest()
               for n in outputs},
    "no_oidn":True,
    "factor":1.0,
    "mixer_api":"MixRGB" if FLAVOR=="legacy" else "ShaderNodeMix",
    "alpha_api":"SepRGBA/CombRGBA" if FLAVOR=="legacy" else "SetAlpha",
}
(DEST/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("M3.6 NO-DENOISER OPERATOR PROBE SUCCESS",FLAVOR,bpy.app.version_string)
