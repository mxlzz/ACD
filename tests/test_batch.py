import numpy as np
import pytest

OpenEXR = pytest.importorskip("OpenEXR")
from acd_lab.batch import evaluate_batch


def save(path, value):
    values = np.full((3, 4), value, dtype=np.float32)
    with OpenEXR.File({}, {channel: values for channel in "RGB"}) as file:
        file.write(str(path))


def test_compare_batch(tmp_path):
    save(tmp_path / "reference.exr", 0.5)
    save(tmp_path / "acd_compare_Raw.exr", 0.8)
    save(tmp_path / "acd_compare_STANDARD.exr", 0.6)
    save(tmp_path / "acd_compare_HIGH.exr", 0.7)
    save(tmp_path / "acd_compare_SUPER.exr", 0.55)
    report = evaluate_batch(tmp_path)
    assert report["rank_by_rmse"][0] == "SUPER"
    assert report["rank_by_rmse"][-1] == "Raw"
    assert report["rmse_reduction_vs_raw"]["SUPER"] > 0
