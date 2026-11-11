"""M3.5 Standard cross-version test, processing identical on-disk EXR buffers.

Blender 3.6 loads the actual upstream GPL code from a temporary clone.
Blender 5 uses our independently implemented SID Reference. No code vendoring.
Outputs include raw passthrough controls, so compositor/color IO drift can be
separated from differences in OIDN and the reference implementation.
"""
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

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path(os.environ["ACD_NUMERIC_INPUT"]).resolve()
DEST = Path(os.environ["ACD_NUMERIC_OUTPUT"]).resolve()
FLAVOR = os.environ["ACD_NUMERIC_FLAVOR"].lower()
EXPECTED_COMMIT = "b4186389cac386eff9d777bb681c0051f8bd9bd2"
assert FLAVOR in ("legacy", "port")
assert (bpy.app.version[:2] == (3, 6)) if FLAVOR == "legacy" else (bpy.app.version[:2] == (5, 0))
assert INPUT.is_dir()
DEST.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 1
scene.render.resolution_x = 96
scene.render.resolution_y = 64
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_depth = "32"
scene.render.image_settings.exr_codec = "ZIP"
scene.render.filepath = str(DEST / "render_not_a_reference.exr")
scene.render.use_compositing = True
scene.view_settings.view_transform = "Standard"

if FLAVOR == "legacy":
    upstream = Path(os.environ["SID_UPSTREAM_ROOT"]).resolve()
    assert (upstream / "SID_QualityStandart.py").is_file()
    pkg = types.ModuleType("sid_numeric_public")
    pkg.__path__ = [str(upstream)]
    pkg.SID_Settings = object
    sys.modules["sid_numeric_public"] = pkg
    standard = importlib.import_module("sid_numeric_public.SID_QualityStandart")
    sid_group = standard.create_sid_denoiser_standard()
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
else:
    spec = importlib.util.spec_from_file_location("sid_reference", ROOT / "addon" / "sid_reference.py")
    sid = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sid)
    assert sid.SOURCE_COMMIT == EXPECTED_COMMIT
    sid_group = sid.build_reference_group("STANDARD")
    tree = bpy.data.node_groups.new("M3.5 numeric Standard port", "CompositorNodeTree")
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.compositing_node_group = tree

nodes = tree.nodes
links = tree.links
inputs = {}
for label in ("noisy", "albedo", "normal"):
    path = INPUT / (label + ".exr")
    assert path.is_file(), path
    node = nodes.new("CompositorNodeImage")
    node.label = "Frozen EXR: " + label
    node.image = bpy.data.images.load(str(path), check_existing=False)
    node.image.colorspace_settings.name = "Non-Color"
    inputs[label] = node

group = nodes.new("CompositorNodeGroup")
group.node_tree = sid_group
links.new(inputs["noisy"].outputs["Image"], group.inputs["Noisy Image"])
links.new(inputs["normal"].outputs["Image"], group.inputs["Denoising Normal"])
links.new(inputs["albedo"].outputs["Image"], group.inputs["Denoising Albedo"])

if FLAVOR == "legacy":
    composite = nodes.new("CompositorNodeComposite")
    links.new(group.outputs["Denoised Image"], composite.inputs["Image"])
else:
    graph_out = nodes.new("NodeGroupOutput")
    links.new(group.outputs["Denoised Image"], graph_out.inputs["Image"])

def file_output(name, source):
    folder = DEST / name
    folder.mkdir(parents=True, exist_ok=True)
    node = nodes.new("CompositorNodeOutputFile")
    node.format.file_format = "OPEN_EXR"
    node.format.color_depth = "32"
    node.format.exr_codec = "ZIP"
    node.format.color_mode = "RGBA"
    if FLAVOR == "legacy":
        node.base_path = str(folder)
        node.file_slots[0].path = name + "_"
        links.new(source, node.inputs[0])
    else:
        node.directory = str(folder)
        node.file_name = name + "_"
        node.file_output_items.clear()
        node.file_output_items.new("RGBA", "Image")
        links.new(source, node.inputs["Image"])

file_output("raw", inputs["noisy"].outputs["Image"])
file_output("raw_albedo", inputs["albedo"].outputs["Image"])
file_output("raw_normal", inputs["normal"].outputs["Image"])
file_output("sid", group.outputs["Denoised Image"])

result = bpy.ops.render.render()
assert "FINISHED" in result, result
for name in ("raw", "raw_albedo", "raw_normal", "sid"):
    images = sorted((DEST / name).rglob("*.exr"))
    assert len(images) == 1, (name, [str(x) for x in images])
    shutil.copyfile(images[0], DEST / (name + ".exr"))

input_hashes = {name: hashlib.sha256((INPUT / (name + ".exr")).read_bytes()).hexdigest()
                for name in ("noisy", "normal", "albedo")}
meta = {
    "flavor": FLAVOR,
    "version": bpy.app.version_string,
    "upstream_commit": EXPECTED_COMMIT,
    "mode": "STANDARD",
    "input_sha256": input_hashes,
    "color_space": "Non-Color for all imported EXRs",
    "view_transform": scene.view_settings.view_transform,
    "oidn_version": "not directly exposed by this test",
    "prefilter": "FAST" if FLAVOR == "legacy" else "Fast",
    "blender5_adapter_settings": None if FLAVOR == "legacy" else {"Quality": "High", "HDR": True},
    "output_sha256": {name: hashlib.sha256((DEST / (name + ".exr")).read_bytes()).hexdigest()
                      for name in ("raw", "raw_albedo", "raw_normal", "sid")},
    "scope": "Synthetic 96x64 compositor comparison; not a natural-scene quality benchmark",
}
(DEST / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
print("SID M3.5 STANDARD RENDER SUCCESS", json.dumps(meta))
