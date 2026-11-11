"""M3.8: actual OIDN parameter ablations in Blender 3.6 and Blender 5.0.1.

ONE frozen image/albedo/normal fixture per run, no SID graph or mixers.
Blender 3.6: historical Prefilter and use_hdr (True/False).
Blender 5: same prefilter / HDR with Quality High, Balanced, Fast.
The matching error to historical OIDN is NOT a ranking of image fidelity.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
from pathlib import Path
import bpy

INPUT=Path(os.environ["ACD_M38_INPUT"]).resolve()
OUT=Path(os.environ["ACD_M38_OUTPUT"]).resolve()
FLAVOR=os.environ["ACD_M38_FLAVOR"].lower()
assert FLAVOR in ("legacy","port")
assert bpy.app.version[:2]==((3,6) if FLAVOR=="legacy" else (5,0))
OUT.mkdir(parents=True,exist_ok=True)
CASES={
    "guided_fast":("noisy","Fast",True),
    "guided_accurate":("noisy","Accurate",True),
    "emission_accurate":("emission","Accurate",False),
    "alpha_accurate":("alpha","Accurate",True),
}
RAW=("noisy","normal","albedo","alpha","emission")
QUALITIES=("High","Balanced","Fast")
HDRS=(True,False)

scene=bpy.context.scene
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=1
scene.render.resolution_x=96
scene.render.resolution_y=64
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="OPEN_EXR"
scene.render.image_settings.color_depth="32"
scene.render.filepath=str(OUT/"unused_render.exr")
scene.render.use_compositing=True
scene.view_settings.view_transform="Standard"
if FLAVOR=="legacy":
    scene.use_nodes=True
    tree=scene.node_tree
    tree.nodes.clear()
else:
    tree=bpy.data.node_groups.new("M3.8 OIDN fixed EXR parameter matrix","CompositorNodeTree")
    tree.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
    scene.compositing_node_group=tree
nodes,links=tree.nodes,tree.links
sources={}
for name in RAW:
    filepath=INPUT/(name+".exr")
    assert filepath.is_file(),filepath
    image=nodes.new("CompositorNodeImage")
    image.image=bpy.data.images.load(str(filepath),check_existing=False)
    image.image.colorspace_settings.name="Non-Color"
    image.label="Frozen EXR: "+name
    sources[name]=image.outputs["Image"]

def make_filter(base,source,prefilter,guided,quality,hdr):
    n=nodes.new("CompositorNodeDenoise")
    n.label=base+" | quality="+quality+" hdr="+str(hdr)
    if FLAVOR=="legacy":
        n.prefilter=prefilter.upper()
        n.use_hdr=hdr
        links.new(sources[source],n.inputs[0])
        if guided:
            links.new(sources["normal"],n.inputs[1])
            links.new(sources["albedo"],n.inputs[2])
    else:
        n.inputs["Prefilter"].default_value=prefilter
        n.inputs["Quality"].default_value=quality
        n.inputs["HDR"].default_value=hdr
        links.new(sources[source],n.inputs["Image"])
        if guided:
            links.new(sources["normal"],n.inputs["Normal"])
            links.new(sources["albedo"],n.inputs["Albedo"])
    return n.outputs["Image"]

def save(name,socket):
    folder=OUT/name
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
    save("raw_"+name,sources[name])
generated={}
for base,(source,prefilter,guided) in CASES.items():
    for hdr in HDRS:
        settings=(("Legacy",) if FLAVOR=="legacy" else QUALITIES)
        for quality in settings:
            key=base+"__"+quality.lower()+"__h"+str(int(hdr))
            image=make_filter(base,source,prefilter,guided,quality,hdr)
            save(key,image)
            generated[key]={
                "source":source,"prefilter":prefilter,"guided":guided,
                "quality":None if FLAVOR=="legacy" else quality,"hdr":hdr,
            }

# Composite output only ensures a valid scene compositor; FileOutput nodes
# are the sole metric sources, no view transform or PNG in measurements.
first=next(k for k in generated if k.endswith("__h1"))
if FLAVOR=="legacy":
    composite=nodes.new("CompositorNodeComposite")
    # An image filter's output; connection not used for numerical measurement.
    filt=next(n for n in nodes if n.bl_idname=="CompositorNodeDenoise")
    links.new(filt.outputs["Image"],composite.inputs["Image"])
else:
    output=nodes.new("NodeGroupOutput")
    filt=next(n for n in nodes if n.bl_idname=="CompositorNodeDenoise")
    links.new(filt.outputs["Image"],output.inputs["Image"])

assert "FINISHED" in bpy.ops.render.render()
output_keys=["raw_"+name for name in RAW]+list(generated)
for name in output_keys:
    found=list((OUT/name).glob("*.exr"))
    assert len(found)==1,(name,found)
    shutil.copyfile(found[0],OUT/(name+".exr"))
build_options=bpy.app.build_options
metadata={
    "flavor":FLAVOR,"blender":bpy.app.version_string,
    "build_hash":str(bpy.app.build_hash),
    "build_options_openimagedenoise":getattr(build_options,"openimagedenoise",None),
    "oidn_semantic_version":"unknown; inspect bundled libs in workflow",
    "input_sha256":{name:hashlib.sha256((INPUT/(name+".exr")).read_bytes()).hexdigest()
                    for name in RAW},
    "filters":generated,
    "source_color_space":"Non-Color EXR, 32-bit float RGBA",
    "comparison_scope":"cross-Blender output closeness, not quality against converged reference",
}
(OUT/"manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
print("M3.8 OIDN MATRIX COMPLETE",FLAVOR,bpy.app.version_string,len(generated))
