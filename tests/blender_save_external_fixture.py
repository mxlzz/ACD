"""Create a tiny saved .blend as an external-file integration-test fixture."""
from __future__ import annotations

import os
from pathlib import Path

import bpy

target = Path(os.environ.get("ACD_FIXTURE_BLEND", "/tmp/acd_external_fixture.blend")).resolve()
target.parent.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_x = 32
scene.render.resolution_y = 32
scene.render.resolution_percentage = 100
bpy.ops.wm.save_as_mainfile(filepath=str(target), check_existing=False)
assert target.is_file() and target.stat().st_size > 1000
print("ACD TEST SCENE SAVED", target)
