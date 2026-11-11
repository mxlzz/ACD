import json

import pytest

from acd_lab.aggregate import aggregate_seed_reports
from acd_lab.cli import main


def report(rmse_raw, rmse_standard, rmse_super):
    def m(rmse):
        return {
            "rmse_linear": rmse,
            "mae_linear": rmse / 2,
            "log1p_luminance_rmse": rmse / 3,
            "pixel_rmse_p95": rmse * 2,
        }
    return {"measurements": {
        "Raw": m(rmse_raw),
        "STANDARD": m(rmse_standard),
        "SUPER": m(rmse_super),
    }}


def test_aggregate_seed_metrics(tmp_path):
    (tmp_path / "metrics.json").write_text(json.dumps(report(1, .5, .4)))
    child = tmp_path / "seed_911"
    child.mkdir()
    (child / "metrics.json").write_text(json.dumps(report(2, .7, .5)))
    aggregate = aggregate_seed_reports(tmp_path)
    assert aggregate["input_seed_count"] == 2
    assert aggregate["rank_by_mean_rmse"] is None
    assert not aggregate["independent_seeds_verified"]
    assert aggregate["methods"]["SUPER"]["rmse_linear"]["mean"] == pytest.approx(.45)
    assert aggregate["methods"]["SUPER"]["rmse_linear"]["population_std"] == pytest.approx(.05)
    assert aggregate["seed_rmse_wins"] is None
    assert main(["aggregate-seeds", "--directory", str(tmp_path)]) == 0


def test_aggregate_requires_multiple_seeds(tmp_path):
    (tmp_path / "metrics.json").write_text(json.dumps(report(1, 2, 3)))
    with pytest.raises(ValueError, match="two"):
        aggregate_seed_reports(tmp_path)
