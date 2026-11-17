"""Synthetic falsification tests for reference-driven detail fidelity."""
import numpy as np
import pytest

from acd_lab.detail import detail_fidelity
from acd_lab.regions import assess_regions


def edge_image():
    x = np.zeros((8, 12, 3), dtype=np.float64)
    x[:, 6:, :] = 1.0
    return x


def test_exact_reference_has_zero_errors_and_unit_contrast():
    ref = edge_image()
    metric = detail_fidelity(ref, ref)
    assert metric["edge_pair_count"] > 0
    assert metric["edge_gradient_rmse"] == 0
    assert metric["edge_contrast_ratio"] == pytest.approx(1)
    assert metric["flat_gradient_rmse"] == 0


def test_blurred_boundary_loses_reference_detail():
    ref = edge_image()
    blurred = ref.copy()
    blurred[:, 5, :] = .25
    blurred[:, 6, :] = .75
    m = detail_fidelity(ref, blurred)
    assert m["edge_gradient_rmse"] > 0
    assert m["edge_contrast_ratio"] < 1


def test_sharpened_boundary_cannot_win_on_contrast_alone():
    ref = edge_image()
    oversharpened = ref.copy()
    oversharpened[:, 5, :] = -.4
    oversharpened[:, 6, :] = 1.4
    m = detail_fidelity(ref, oversharpened)
    assert m["edge_contrast_ratio"] > 1
    assert m["edge_gradient_rmse"] > 0


def test_flat_reference_has_no_edge_score_but_detects_spurious_texture():
    ref = np.ones((7, 8, 3), dtype=np.float64)
    output = ref.copy()
    output[:, ::2, :] += .1
    m = detail_fidelity(ref, output)
    assert m["edge_pair_count"] == 0
    assert m["edge_gradient_rmse"] is None
    assert m["edge_contrast_ratio"] is None
    assert m["flat_gradient_rmse"] > 0


def test_roi_boundaries_do_not_create_artificial_adjacencies():
    ref = edge_image()
    cand = ref.copy()
    cand[:, 9, :] += 20
    roi = np.zeros(ref.shape[:2], dtype=bool)
    roi[:, :5] = True
    local = detail_fidelity(ref, cand, mask=roi)
    assert local["flat_gradient_rmse"] == 0
    assert local["edge_gradient_rmse"] is None
    assert detail_fidelity(ref, cand)["flat_gradient_rmse"] > 0


def test_isoluminant_color_edge_is_detected():
    ref = np.zeros((8, 8, 3), dtype=np.float64)
    ref[:, :4, 1] = 1
    ref[:, 4:, 0] = .7152 / .2126
    cand = np.zeros_like(ref)
    m = detail_fidelity(ref, cand)
    assert m["edge_pair_count"] > 0
    assert m["edge_gradient_rmse"] > 0


def test_signed_hdr_values_remain_valid_and_finite():
    ref = edge_image() * 200 - 10
    cand = ref.copy()
    cand[2, 2, :] = -100
    m = detail_fidelity(ref, cand)
    assert np.isfinite(m["flat_gradient_rmse"])


def test_empty_and_noncontiguous_roi():
    ref = edge_image()
    empty = detail_fidelity(ref, ref, mask=np.zeros(ref.shape[:2], bool))
    assert empty["eligible_pair_count"] == 0
    assert empty["edge_gradient_rmse"] is None
    assert empty["flat_gradient_rmse"] is None
    roi = np.zeros(ref.shape[:2], bool)
    roi[0, 0] = True
    roi[7, 11] = True
    isolated = detail_fidelity(ref, ref, mask=roi)
    assert isolated["eligible_pair_count"] == 0


def test_invalid_configuration_and_images_rejected():
    ref = edge_image()
    with pytest.raises(ValueError, match="aligned"):
        detail_fidelity(ref, ref[:-1])
    with pytest.raises(ValueError, match="fractions"):
        detail_fidelity(ref, ref, edge_fraction=0)
    with pytest.raises(ValueError, match="boolean"):
        detail_fidelity(ref, ref, mask=np.ones(ref.shape[:2], dtype=np.uint8))
    invalid = ref.copy()
    invalid[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="Nonfinite"):
        detail_fidelity(ref, invalid)


def test_regional_metrics_use_original_spatial_neighborhood():
    ref = edge_image()
    cand = ref.copy()
    cand[:, 9, :] += 4
    mask = np.zeros(ref.shape[:2], bool)
    mask[:, :5] = True
    report = assess_regions(ref, {"candidate": cand}, {"roi": mask, "whole": np.ones(ref.shape[:2], bool)})
    assert report["regions"]["roi"]["metrics"]["candidate"]["detail"]["flat_gradient_rmse"] == 0
    assert report["regions"]["whole"]["metrics"]["candidate"]["detail"]["flat_gradient_rmse"] > 0
