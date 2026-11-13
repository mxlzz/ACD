import json
from pathlib import Path

import pytest
from scripts.summarize_blender_compat_e0035 import analyze, sha256


def test_sha256(tmp_path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"hello")
    assert sha256(p) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_mixed_blender_versions_rejected_before_exr_io(tmp_path):
    root = tmp_path / "render"
    root.mkdir()
    (root / "metadata.json").write_text(json.dumps({"blender": "5.2.4"}))
    caps = tmp_path / "api.json"
    caps.write_text(json.dumps({"blender": "5.3.0"}))
    with pytest.raises(ValueError, match="same Blender version"):
        analyze(root, caps)
