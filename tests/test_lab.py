import json

import numpy as np
import pytest

from acd_lab.core import check_recomposition, compare_images, recompose
from acd_lab.cli import main


def img(value, shape=(4, 6, 3)):
    return np.full(shape, value, dtype=np.float32)


def test_pass_sum():
    passes = {
        "diffuse_direct": img(0.5),
        "diffuse_indirect": img(0.25),
        "diffuse_color": img(0.5),
        "glossy_direct": img(0.125),
        "glossy_indirect": img(0.125),
        "glossy_color": img(1.0),
        "emission": img(0.25),
    }
    expected = 0.375 + 0.25 + 0.25
    np.testing.assert_allclose(recompose(passes), expected)
    assert check_recomposition(recompose(passes), passes)["metrics"]["exact_match"]


def test_incomplete_pass_family():
    with pytest.raises(ValueError, match="incomplete"):
        recompose({"diffuse_direct": img(1)})


def test_inconsistent_resolution():
    with pytest.raises(ValueError, match="mismatching"):
        recompose({
            "diffuse_direct": img(1),
            "diffuse_indirect": img(2, (2, 6, 3)),
            "diffuse_color": img(1),
        })


def test_hdr_values_preserved():
    raw = img(0.0)
    raw[0, 0] = [12.0, 0.5, -0.5]
    np.testing.assert_array_equal(recompose({"emission": raw}), raw)


def test_alpha_excluded():
    x = np.ones((2, 2, 4), dtype=np.float32)
    y = x.copy()
    y[..., 3] = 0
    assert compare_images(x, y)["exact_match"]


def test_psnr_needs_declared_range():
    reference, candidate = img(1.0), img(1.5)
    assert compare_images(reference, candidate)["psnr_db"] is None
    result = compare_images(reference, candidate, data_range=2.0)
    assert result["rmse_linear"] == pytest.approx(0.5)
    assert result["psnr_db"] == pytest.approx(20 * np.log10(4))


def test_nonfinite_rejected():
    bad = img(1.0)
    bad[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        compare_images(bad, img(1), data_range=1)


def test_no_recognized_passes():
    with pytest.raises(ValueError, match="No recognized"):
        recompose({"invalid": img(1)})


def test_cli_roundtrip(tmp_path, capsys):
    reference, candidate = img(1), img(1.25)
    np.savez(tmp_path / "ref.npz", image=reference)
    np.savez(tmp_path / "cand.npz", image=candidate)
    report = tmp_path / "report.json"
    assert main([
        "compare", "--reference", str(tmp_path / "ref.npz"),
        "--candidate", str(tmp_path / "cand.npz"),
        "--data-range", "1", "--output", str(report),
    ]) == 0
    assert json.loads(report.read_text())["mae_linear"] == 0.25
    assert "mae_linear" in capsys.readouterr().out
