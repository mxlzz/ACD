import json

import numpy as np
import pytest

OpenEXR = pytest.importorskip("OpenEXR")

from acd_lab.region_cli import compare_regions_from_files
from acd_lab.cli import main


def save_exr(path, values):
    channels = {channel: np.ascontiguousarray(values[..., index], dtype=np.float32)
                for index, channel in enumerate("RGB")}
    with OpenEXR.File({}, channels) as image:
        image.write(str(path))


def test_regions_from_saved_exrs_and_roi_file(tmp_path, capsys):
    target = np.zeros((4, 6, 3), np.float32)
    altered = target.copy()
    altered[:, :2] = 1
    save_exr(tmp_path / "reference.exr", target)
    save_exr(tmp_path / "acd_compare_STANDARD.exr", altered)
    save_exr(tmp_path / "acd_compare_SUPER.exr", target)
    regions_path = tmp_path / "rois.json"
    regions_path.write_text(json.dumps({
        "regions": [{"name": "left", "rect_norm": [0, 0, 1 / 3, 1]},
                    {"name": "right", "rect_norm": [2 / 3, 0, 1, 1]}]
    }), encoding="utf-8")
    result = compare_regions_from_files(
        tmp_path, regions_file=regions_path, error_maps=tmp_path / "maps.npz"
    )
    left = result["regions"]["left"]["metrics"]
    right = result["regions"]["right"]["metrics"]
    assert left["STANDARD"]["rmse_linear"] == pytest.approx(1)
    assert right["STANDARD"]["rmse_linear"] == pytest.approx(0)
    assert left["SUPER"]["rmse_linear"] == pytest.approx(0)
    assert (tmp_path / "maps.npz").is_file()
    assert main(["compare-regions", "--directory", str(tmp_path),
                 "--regions", str(regions_path)]) == 0
    assert "whole_image" in capsys.readouterr().out


def test_duplicate_region_rejected(tmp_path):
    target = np.zeros((2, 3, 3), np.float32)
    save_exr(tmp_path / "reference.exr", target)
    save_exr(tmp_path / "acd_compare_STANDARD.exr", target)
    rois = tmp_path / "rois.json"
    rois.write_text('{"regions":[{"name":"whole_image","rect_norm":[0,0,1,1]}]}')
    with pytest.raises(ValueError, match="Duplicate"):
        compare_regions_from_files(tmp_path, regions_file=rois)
