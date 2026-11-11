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



def test_batch_with_two_references_reports_uncertainty_without_certifying_convergence(tmp_path):
    save(tmp_path / "reference.exr", 0.5)
    save(tmp_path / "reference_check.exr", 0.45)
    save(tmp_path / "acd_compare_Raw.exr", 0.9)
    save(tmp_path / "acd_compare_STANDARD.exr", 0.55)
    save(tmp_path / "acd_compare_HIGH.exr", 0.48)
    save(tmp_path / "acd_compare_SUPER.exr", 0.6)
    report = evaluate_batch(tmp_path)
    diag = report["reference_quality_diagnostic"]
    assert diag["pair_difference"]["rmse_linear"] == pytest.approx(0.05, rel=1e-5)
    assert diag["independent_sampling_proven"] is False
    assert diag["convergence_proven"] is False
    assert report["reference_ranking_consistent"] is True
    assert report["rank_by_rmse"][0] == report["rank_against_second_reference"][0] == "HIGH"


def test_batch_without_second_reference_remains_explicitly_unverified(tmp_path):
    save(tmp_path / "reference.exr", 0.5)
    for method, value in {
        "Raw": .9, "STANDARD": .53, "HIGH": .55, "SUPER": .51
    }.items():
        save(tmp_path / ("acd_compare_" + method + ".exr"), value)
    report = evaluate_batch(tmp_path)
    assert report["reference_quality_diagnostic"] is None
    assert report["reference_ranking_consistent"] is None



def test_batch_reports_optional_sid4_reference_variants(tmp_path):
    save(tmp_path / "reference.exr", 0.5)
    for name, value in {
        "Raw": 0.8, "STANDARD": 0.6, "HIGH": 0.65,
        "SUPER": 0.7, "SID4_STANDARD": 0.58,
        "SID4_HIGH": 0.57, "SID4_SUPER": 0.54,
    }.items():
        save(tmp_path / ("acd_compare_" + name + ".exr"), value)
    result = evaluate_batch(tmp_path)
    assert "SID4_STANDARD" in result["measurements"]
    assert "SID4_HIGH" in result["measurements"]
    assert "SID4_SUPER" in result["measurements"]
    assert result["rank_by_rmse"][0] == "SID4_SUPER"
