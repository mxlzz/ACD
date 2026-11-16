from copy import deepcopy
import pytest
from scripts.analyze_lone_monk_seeds_e0063 import check_meta, SCENE, CAMERA


def fixture(seed=539):
    return {
        "active_scene": SCENE, "active_camera": CAMERA,
        "requested_seed": seed, "sample_offset": 0,
        "sampling_pattern": "TABULATED_SOBOL", "scene_variant": "external",
        "settings_all_scenes": [{"name": SCENE, "samples": 16, "seed": seed}],
    }


def test_valid_fixed_seed_metadata():
    check_meta(fixture(539), 539)
    check_meta(fixture(911), 911)


@pytest.mark.parametrize("field,invalid", [
    ("active_scene", "other"), ("active_camera", "other"),
    ("requested_seed", 1337), ("sample_offset", 16),
    ("sampling_pattern", "BLUE_NOISE"), ("scene_variant", "interior")
])
def test_mismatched_scene_or_sampler_fails(field, invalid):
    meta = fixture()
    meta[field] = invalid
    with pytest.raises(ValueError):
        check_meta(meta, 539)


def test_missing_samples_is_rejected():
    m = fixture()
    m["settings_all_scenes"][0]["samples"] = 8
    with pytest.raises(ValueError):
        check_meta(m, 539)
