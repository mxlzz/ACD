"""Regional consistency checks use synthetic files with known values."""
import json
import numpy as np
import pytest

OpenEXR = pytest.importorskip("OpenEXR")
from acd_lab.region_aggregate import aggregate_region_reports


def save_exr(path, data):
    with OpenEXR.File({}, {
        c: np.ascontiguousarray(data[..., i], dtype=np.float32)
        for i, c in enumerate("RGB")
    }) as file:
        file.write(str(path))


def region(baseline, candidate, *, count=20):
    return {
        "regions": {
            "aov_emission": {
                "pixels": count,
                "coverage": count / 25,
                "metrics": {
                    "STANDARD": {"rmse_linear": baseline, "mae_linear": baseline/2},
                    "STANDARD_emission_preserved": {"rmse_linear": candidate, "mae_linear": candidate/2}
                },
            }
        },
        "region_definitions": {
            "aov_emission": {
                "type": "relative_aov_magnitude",
                "fraction_threshold": .35,
                "minimum_signal": .01,
            }
        }
    }


def test_fixed_mask_region_aggregate_with_verified_distinct_inputs(tmp_path):
    raw = np.zeros((5,5,3), dtype=np.float32)
    raw[0,0] = 1
    different = np.zeros_like(raw)
    different[3,4] = 2
    save_exr(tmp_path / "reference.exr", np.zeros_like(raw))
    save_exr(tmp_path / "acd_compare_Raw.exr", raw)
    (tmp_path / "region_metrics.json").write_text(json.dumps(region(.4,.2)))
    folder = tmp_path / "seed_911"
    folder.mkdir()
    save_exr(folder / "acd_compare_Raw.exr", different)
    (folder / "region_metrics.json").write_text(json.dumps(region(.5,.35)))
    result = aggregate_region_reports(tmp_path)
    assert result["passes_raw_diversity_heuristic"]
    assert result["candidate_improves_count"] == 2
    assert result["mean_baseline_rmse"] == pytest.approx(.45)
    assert result["mean_candidate_minus_baseline_rmse"] == pytest.approx(-.175)


def test_region_aggregate_rejects_same_raw_images(tmp_path):
    raw = np.zeros((5,5,3), dtype=np.float32)
    raw[0,0] = 1
    save_exr(tmp_path / "reference.exr", np.zeros_like(raw))
    save_exr(tmp_path / "acd_compare_Raw.exr", raw)
    (tmp_path / "region_metrics.json").write_text(json.dumps(region(.4,.2)))
    folder = tmp_path / "seed_911"
    folder.mkdir()
    save_exr(folder / "acd_compare_Raw.exr", raw)
    (folder / "region_metrics.json").write_text(json.dumps(region(.5,.35)))
    with pytest.raises(ValueError, match="not measurably different"):
        aggregate_region_reports(tmp_path)
