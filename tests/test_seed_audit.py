import numpy as np
import pytest

OpenEXR = pytest.importorskip("OpenEXR")

from acd_lab.seed_audit import audit_noisy_seed_diversity


def save_exr(path, arr):
    with OpenEXR.File({}, {
        channel: np.ascontiguousarray(arr[..., idx], dtype=np.float32)
        for idx, channel in enumerate("RGB")
    }) as f:
        f.write(str(path))


def layout(tmp_path, second_raw):
    original = np.zeros((3, 4, 3), dtype=np.float32)
    original[:, 0, :] = 1
    reference = np.zeros_like(original)
    folder = tmp_path / "seed_911"
    folder.mkdir()
    save_exr(tmp_path / "acd_compare_Raw.exr", original)
    save_exr(tmp_path / "reference.exr", reference)
    save_exr(folder / "acd_compare_Raw.exr", second_raw)
    return original


def test_nearly_identical_seeds_flagged(tmp_path):
    raw = np.zeros((3, 4, 3), dtype=np.float32)
    raw[:, 0, :] = 1
    layout(tmp_path, raw.copy())
    report = audit_noisy_seed_diversity(tmp_path)
    assert not report["passes_diversity_check"]
    assert report["comparisons"][0]["raw_pair_rmse"] == 0


def test_genuinely_different_raw_inputs_pass_heuristic(tmp_path):
    second = np.zeros((3, 4, 3), dtype=np.float32)
    second[:, 1, :] = 2
    layout(tmp_path, second)
    report = audit_noisy_seed_diversity(tmp_path)
    assert report["passes_diversity_check"]
    assert report["comparisons"][0]["raw_pair_vs_raw_reference_rmse_ratio"] > 1


def test_identical_reference_returns_indeterminate(tmp_path):
    raw = np.ones((2, 2, 3), dtype=np.float32)
    folder = tmp_path / "seed_23"
    folder.mkdir()
    for name, data in (
        ("acd_compare_Raw.exr", raw), ("reference.exr", raw)
    ):
        save_exr(tmp_path / name, data)
    save_exr(folder / "acd_compare_Raw.exr", raw)
    assert audit_noisy_seed_diversity(tmp_path)["passes_diversity_check"] is None


from acd_lab.seed_audit import verify_sample_variation


def test_verify_sample_variation_rejects_near_identical_samples():
    one = np.ones((4, 5, 3), dtype=np.float32)
    two = one + 1e-7
    result = verify_sample_variation(one, two)
    assert not result["meaningfully_different"]


def test_verify_sample_variation_accepts_distinct_noise_patterns():
    rng = np.random.default_rng(123)
    one = np.ones((8, 9, 3), dtype=np.float32)
    two = one + rng.normal(0, .05, one.shape).astype(np.float32)
    result = verify_sample_variation(one, two)
    assert result["meaningfully_different"]
    assert result["pair_rmse_over_signal_rms"] > .01


def test_verify_sample_variation_rejects_mismatched_dimensions():
    with pytest.raises(ValueError, match="different resolutions"):
        verify_sample_variation(np.ones((4, 5, 3)), np.ones((4, 6, 3)))


def test_audit_checks_pairs_of_extra_seeds_not_just_baseline(tmp_path):
    raw = np.zeros((4, 5, 3), dtype=np.float32)
    raw[:, 0, :] = 1
    save_exr(tmp_path / "acd_compare_Raw.exr", raw)
    save_exr(tmp_path / "reference.exr", np.zeros_like(raw))
    different = np.zeros_like(raw)
    different[:, 1, :] = 2
    for name in ("seed_911", "seed_1337"):
        folder = tmp_path / name
        folder.mkdir()
        save_exr(folder / "acd_compare_Raw.exr", different)
    report = audit_noisy_seed_diversity(tmp_path)
    assert not report["passes_diversity_check"]
    duplicate = [pair for pair in report["all_pairs"]
                 if {pair["first"], pair["second"]} == {"seed_911", "seed_1337"}]
    assert len(duplicate) == 1
    assert duplicate[0]["rmse"] == 0
