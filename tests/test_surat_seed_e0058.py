import pytest
from scripts.analyze_surat_seed_e0058 import validate_metadata,ZIP_SHA,CAMERA

def valid(seed):
    return {"active_scene":"Scene","active_camera":CAMERA,
            "requested_seed":seed,"sample_offset":0,
            "sampling_pattern":"TABULATED_SOBOL",
            "scene_variant":"external",
            "settings_all_scenes":[{"name":"Scene","samples":16,"seed":seed}]}

def test_frozen_camera_and_sampling():
    assert len(ZIP_SHA)==64
    validate_metadata(valid(539),539)

@pytest.mark.parametrize("field,value",[
    ("active_camera","CAM Aerial"),("requested_seed",911),
    ("sampling_pattern","BLUE_NOISE"),("sample_offset",16),
    ("scene_variant","interior")
])
def test_strict_source_contract(field,value):
    x=valid(539)
    x[field]=value
    with pytest.raises(ValueError):
        validate_metadata(x,539)

def test_detect_wrong_sample_budget():
    x=valid(539)
    x["settings_all_scenes"][0]["samples"]=4
    with pytest.raises(ValueError):
        validate_metadata(x,539)
