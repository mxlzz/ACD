"""E0050: compositing-only replay of original Raw with original/swapped AOV guides."""
from __future__ import annotations
import json,os
from pathlib import Path
import bpy

original=Path(os.environ["ACD_E0050_ORIGINAL"]).resolve()
alt=Path(os.environ["ACD_E0050_ALT"]).resolve()
target=Path(os.environ["ACD_E0050_OUTPUT"]).resolve()
target.mkdir(parents=True,exist_ok=True)
for root in (original,alt):
    for name in ("raw_multilayer.exr","metadata.json"):
        if not (root/name).is_file():raise RuntimeError("Absent "+str(root/name))
scene=bpy.context.scene
scene.render.resolution_x=512
scene.render.resolution_y=512
scene.render.resolution_percentage=100
scene.render.image_settings.media_type="IMAGE"
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_depth="32"
scene.render.image_settings.exr_codec="ZIP"
scene.render.use_compositing=True
scene.render.filepath=str(target/"dummy.exr")
base_meta=json.loads((original/"metadata.json").read_text())
alt_meta=json.loads((alt/"metadata.json").read_text())
layer=base_meta["view_layer"]
if layer!=alt_meta["view_layer"]:raise RuntimeError("View layer mismatch")

tree=bpy.data.node_groups.new("E0050 same noisy RGB / two native AOV sources","CompositorNodeTree")
tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")

def image_node(path,layer_name=None):
    image=bpy.data.images.load(str(path),check_existing=False)
    image.colorspace_settings.name="Linear Rec.709" if "Linear Rec.709" in bpy.types.ColorManagedInputColorspaceSettings.bl_rna.properties["name"].enum_items else image.colorspace_settings.name
    node=tree.nodes.new("CompositorNodeImage")
    node.image=image
    if layer_name is not None:
        node.layer=layer_name
    print("E0050_IMAGE_SOCKET_LIST",path.name,
          [(s.name,s.enabled) for s in node.outputs],flush=True)
    return node

raw=image_node(original/"acd_compare_Raw.exr")
first=image_node(original/"raw_multilayer.exr",layer)
second=image_node(alt/"raw_multilayer.exr",layer)
def out(node,n):
    matches=[s for s in node.outputs if s.name==n and s.enabled]
    if len(matches)!=1:
        raise RuntimeError("Missing exact compositor EXR socket "+n+
                           "; actual="+str([s.name for s in node.outputs]))
    return matches[0]

raw_socket=out(raw,"Image")
fileout=tree.nodes.new("CompositorNodeOutputFile")
fileout.directory=str(target)
fileout.file_name="e0050_"
fileout.format.media_type="IMAGE"
fileout.format.file_format="OPEN_EXR"
fileout.format.color_depth="32"
fileout.format.exr_codec="ZIP"
fileout.file_output_items.clear()
def emit(name,socket):
    fileout.file_output_items.new("RGBA",name)
    tree.links.new(socket,fileout.inputs[name])
emit("RawReplayed",raw_socket)
def denoiser(source,label):
    node=tree.nodes.new("CompositorNodeDenoise")
    node.inputs["Prefilter"].default_value="Accurate"
    node.inputs["Quality"].default_value="High"
    node.inputs["HDR"].default_value=True
    tree.links.new(raw_socket,node.inputs["Image"])
    tree.links.new(out(source,"Denoising Albedo"),node.inputs["Albedo"])
    tree.links.new(out(source,"Denoising Normal"),node.inputs["Normal"])
    emit(label,node.outputs["Image"])
denoiser(first,"NativeGuidesReplay")
denoiser(second,"AlternativeGuides")
group=tree.nodes.new("NodeGroupOutput")
tree.links.new(raw_socket,group.inputs["Image"])
scene.compositing_node_group=tree
result=bpy.ops.render.render(write_still=True)
if "FINISHED" not in result:raise RuntimeError("Compositor replay failed")
for name in ("RawReplayed","NativeGuidesReplay","AlternativeGuides"):
    p=target/("e0050_"+name+".exr")
    if not p.is_file() or p.stat().st_size<100:raise RuntimeError("Missing replay output: "+str(p))
print("E0050_BOTH_GUIDES_REPLAY_RENDERED",flush=True)
