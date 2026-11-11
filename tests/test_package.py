import zipfile
from pathlib import Path

from scripts.package_addon import build


def test_install_zip_has_stable_module_name(tmp_path):
    file = build(tmp_path / "ACD_Blender5_experimental.zip")
    assert Path(file).exists()
    with zipfile.ZipFile(file) as archive:
        assert archive.namelist() == ["acd_blender.py"]
        assert b'"blender": (5, 0, 0)' in archive.read("acd_blender.py")
