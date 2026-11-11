"""Pure numerical guardrail tests for the SID cross-version report."""
import numpy as np
import pytest

from scripts.compare_sid_standard_numeric import metrics
from scripts.sid_standard_numeric_fixture import make_arrays


def test_fixture_determinism_and_signal():
    first, second = make_arrays(), make_arrays()
    for key in first:
        np.testing.assert_array_equal(first[key], second[key])
        assert first[key].shape == (64, 96, 4)
    assert first["noisy"][..., :3].max() > 7.0
    assert np.any(first["noisy"][..., 3] < 1.0)
    assert np.isfinite(first["normal"]).all()


def test_metrics_are_signed_and_region_scoped():
    a = np.zeros((2, 2, 3), dtype=np.float32)
    b = a.copy()
    b[0, 1] = 2.0
    data = metrics(a, b)
    assert data["pixels"] == 4
    assert data["rmse"] > 0
    assert data["max_abs"] == 2.0
    assert not data["exact_match"]
    roi = metrics(a, b, np.array([[True, False], [False, False]]))
    assert roi["pixels"] == 1
    assert roi["rmse"] == 0.0
    assert metrics(a, a)["exact_match"]


def test_wrong_shapes_are_rejected():
    with pytest.raises(ValueError, match="dimensions"):
        metrics(np.zeros((2, 2, 3)), np.zeros((2, 3, 3)))
