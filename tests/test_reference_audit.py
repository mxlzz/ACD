"""Reference uncertainty diagnostics; no claims of Monte Carlo independence."""
import numpy as np
import pytest

from acd_lab.reference_audit import audit_reference_pair


def test_reference_audit_flags_material_disagreement():
    shape = (3, 4, 3)
    raw = np.ones(shape, dtype=np.float32)
    a = np.zeros(shape, dtype=np.float32)
    b = np.full(shape, 0.5, dtype=np.float32)
    result = audit_reference_pair(raw, a, b)
    assert result["large_reference_discrepancy_alert"]
    assert not result["almost_identical_reference_images"]
    assert result["reference_disagreement_over_raw_error"] > .25
    assert result["independent_sampling_proven"] is False
    assert result["convergence_proven"] is False


def test_nearly_equal_reference_does_not_claim_convergence():
    rng = np.random.default_rng(99)
    a = rng.random((6, 7, 3)).astype(np.float32)
    b = a.copy()
    result = audit_reference_pair(a + .1, a, b)
    assert result["almost_identical_reference_images"]
    assert not result["convergence_proven"]
    assert not result["independent_sampling_proven"]
    assert result["pair_difference"]["exact_match"]


def test_reference_audit_handles_same_noisy_reference():
    a = np.ones((3, 4, 3), dtype=np.float32)
    b = np.zeros_like(a)
    result = audit_reference_pair(a, a, b)
    assert result["reference_disagreement_over_raw_error"] == pytest.approx(2.0)


def test_reference_audit_rejects_wrong_dimensions_and_thresholds():
    raw = np.ones((3, 4, 3), dtype=np.float32)
    with pytest.raises(ValueError, match="shapes differ"):
        audit_reference_pair(raw, raw, raw[:2])
    with pytest.raises(ValueError, match="discrepancy_ratio_alert"):
        audit_reference_pair(raw, raw, raw, discrepancy_ratio_alert=0)
    with pytest.raises(ValueError, match="minimum_relative_variation"):
        audit_reference_pair(raw, raw, raw, minimum_relative_variation=float("nan"))
