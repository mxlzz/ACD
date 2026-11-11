"""Real OpenEXR v3 roundtrips. Written synthetic channels are NOT render benchmarks."""
import numpy as np
import pytest

OpenEXR = pytest.importorskip("OpenEXR")

from acd_lab.exr import read_exr, describe_exr
from acd_lab.core import check_recomposition


def ch(base, rgb, destination):
    for i, name in enumerate("RGB"):
        destination[f"ViewLayer.{base}.{name}"] = np.ascontiguousarray(rgb[..., i], dtype=np.float32)


def make_fixture(tmp_path):
    data = {}
    dims = (3, 4, 3)
    color = np.full(dims, .7, dtype=np.float32)
    direct = np.full(dims, .2, dtype=np.float32)
    indirect = np.full(dims, .1, dtype=np.float32)
    reconstructed = (direct + indirect) * color
    ch("Combined", reconstructed, data)
    ch("DiffDir", direct, data)
    ch("DiffInd", indirect, data)
    ch("DiffCol", color, data)
    data["ViewLayer.Combined.A"] = np.ones(dims[:2], dtype=np.float32)
    path = tmp_path / "synthetic.exr"
    with OpenEXR.File({}, data) as file:
        file.write(str(path))
    return path, reconstructed


def test_openexr_cycles_channels(tmp_path):
    file, expected = make_fixture(tmp_path)
    result = read_exr(file)
    assert set(result) == {
        "image", "alpha", "diffuse_direct", "diffuse_indirect", "diffuse_color"
    }
    np.testing.assert_allclose(result["image"], expected, rtol=1e-6)
    assert result["alpha"].shape == (3, 4, 1)
    assert check_recomposition(result["image"], result)["metrics"]["rmse_linear"] < 1e-6


def test_inspection_exposes_exact_channels(tmp_path):
    file, _ = make_fixture(tmp_path)
    report = describe_exr(file)
    names = report["parts"][0]["channels"]
    assert "ViewLayer.DiffDir.R" in names
    assert report["parts"][0]["height"] == 3


def test_requires_layer_disambiguation(tmp_path):
    channels = {}
    for layer in ("Main", "Secondary"):
        for c in "RGB":
            channels[f"{layer}.Combined.{c}"] = np.ones((2, 2), dtype=np.float32)
    file = tmp_path / "two.exr"
    with OpenEXR.File({}, channels) as f:
        f.write(str(file))
    with pytest.raises(ValueError, match="multiple layers"):
        read_exr(file)
    assert read_exr(file, layer="Secondary")["image"].shape == (2, 2, 3)


def test_reject_missing_channel(tmp_path):
    data = {f"Main.Combined.{c}": np.ones((2, 2), dtype=np.float32) for c in "RGB"}
    data["Main.DiffDir.R"] = np.ones((2, 2), dtype=np.float32)
    file = tmp_path / "partial.exr"
    with OpenEXR.File({}, data) as f:
        f.write(str(file))
    with pytest.raises(ValueError, match="incomplete"):
        read_exr(file)
