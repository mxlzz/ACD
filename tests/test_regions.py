import numpy as np
import pytest

from acd_lab.regions import aov_energy_masks, rectangle_mask, assess_regions, save_error_maps


def image(value, h=3, w=5):
    return np.full((h, w, 3), value, dtype=np.float32)


def test_component_masks_identify_reflection_dominated_pixels():
    passes = {
        "diffuse_direct": image(.7),
        "diffuse_indirect": image(0),
        "diffuse_color": image(1),
        "glossy_direct": image(.2),
        "glossy_indirect": image(0),
        "glossy_color": image(1),
    }
    passes["glossy_direct"][:, 0, :] = 20
    masks = aov_energy_masks(passes, threshold=.6)
    assert masks["glossy"][:, 0].all()
    assert not masks["glossy"][:, 1:].any()
    assert masks["diffuse"][:, 1:].all()


def test_missing_family_component_rejected():
    with pytest.raises(ValueError, match="incomplete family"):
        aov_energy_masks({"glossy_direct": image(1)})


def test_aov_masks_require_valid_threshold():
    with pytest.raises(ValueError, match="threshold"):
        aov_energy_masks({"emission": image(1)}, threshold=0)


def test_rectangles_are_top_left_and_half_open():
    mask = rectangle_mask((10, 20), (0.25, 0.2, 0.5, 0.6))
    assert mask.sum() == 5 * 4
    assert mask[2, 5] and mask[5, 9]
    assert not mask[6, 10]
    with pytest.raises(ValueError, match="ordered"):
        rectangle_mask((10, 20), (.7, .1, .3, .2))


def test_region_metric_samples_only_masked_pixels():
    ref = image(0)
    dirty = image(0)
    dirty[:, 0, :] = 1
    clean = image(0)
    mask = np.zeros((3, 5), dtype=bool)
    mask[:, 0] = True
    result = assess_regions(ref, {"dirty": dirty, "clean": clean}, {"left": mask})
    score = result["regions"]["left"]["metrics"]
    assert result["regions"]["left"]["pixels"] == 3
    assert score["dirty"]["rmse_linear"] == pytest.approx(1)
    assert score["clean"]["rmse_linear"] == 0


def test_empty_region_is_explicit_not_nan():
    ref = image(0)
    result = assess_regions(ref, {"same": ref}, {"empty": np.zeros((3, 5), dtype=bool)})
    assert result["regions"]["empty"]["metrics"] is None
    assert result["regions"]["empty"]["coverage"] == 0


def test_reject_mask_size_and_dtype():
    with pytest.raises(ValueError, match="boolean mask"):
        assess_regions(image(0), {"same": image(0)}, {"bad": np.ones((3, 5), dtype=np.uint8)})


def test_error_map_preserves_signed_hdr(tmp_path):
    target = image(8)
    noisy = image(5)
    outfile = tmp_path / "errors.npz"
    save_error_maps(str(outfile), target, {"noise": noisy})
    with np.load(outfile) as archive:
        assert np.all(archive["noise_signed"] == -3)
        assert np.all(archive["noise_absolute"] == 3)
