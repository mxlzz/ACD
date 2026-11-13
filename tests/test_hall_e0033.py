"""Synthetic checks for E0033 score and input-only emission gating."""
import numpy as np
import pytest
from scripts.analyze_hall_e0033 import (METHODS, METRICS, build_candidates,
                                        score_against_reference)


def test_emission50_exact_oidn_when_no_emissive_aov():
    raw = np.ones((10, 10, 3), dtype=np.float32) * 2
    oidn = np.ones_like(raw)
    zeros = np.zeros_like(raw)
    values, info = build_candidates(raw, oidn, oidn, oidn, oidn, zeros)
    assert set(values) == set(METHODS)
    np.testing.assert_array_equal(values["Emission50"], oidn)
    np.testing.assert_array_equal(values["Emission100"], oidn)
    np.testing.assert_array_equal(values["ConstantMatched50"], oidn)
    assert info["Emission50"]["mean_raw_weight"] == 0


def test_emission50_localized_and_reference_used_only_for_scores():
    raw = np.ones((10, 10, 3), dtype=np.float32) * 4
    oidn = np.ones_like(raw)
    emission = np.zeros_like(raw)
    emission[0, 0] = 10
    values, info = build_candidates(raw, oidn, oidn, oidn, oidn, emission)
    assert values["Emission50"][0, 0, 0] > 1
    np.testing.assert_array_equal(values["Emission50"][1:], oidn[1:])
    assert info["Emission50"]["nonzero_emission_fraction"] == pytest.approx(0.01)
    # Reference alters only evaluation, not the already-computed candidate.
    before = values["Emission50"].copy()
    score = score_against_reference(raw, values)
    assert set(score) == set(METHODS)
    assert set(score["OIDN"]) == set(METRICS)
    np.testing.assert_array_equal(before, values["Emission50"])
    another = score_against_reference(oidn, values)
    assert another["Emission50"]["rmse_hdr"] != score["Emission50"]["rmse_hdr"]
