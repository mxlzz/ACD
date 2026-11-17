import pytest
from scripts.analyze_cozy_hires_e0054 import validate_meta
from scripts.cozy_crop_e0053 import contract,SOURCE_SHA

def valid():
    return {
        "scene":"external", "scene_name":"Main", "source_blend_sha256":SOURCE_SHA,
        "resolution":[1920,1808], "samples":24, "reference_samples":512,
        "seed":539, "extra_input_seeds":[911,1337],
        "reference_seed":8819, "second_reference":True, "capture_aov":True,
        "e0053_crop":contract(1920,1808),
        "blender":"5.2.4 LTS", "native_compositor_oidn":{"quality":"High"}
    }

def test_exact_meta_accepts_preregistered_geometry_and_samples():
    validate_meta(valid())

@pytest.mark.parametrize("field,value",[
    ("samples",8),("reference_samples",32),("resolution",[512,512]),
    ("second_reference",False),("extra_input_seeds",[]),
    ("source_blend_sha256","wrong"),("scene_name","Other")
])
def test_meta_rejects_different_source_or_protocol(field,value):
    m=valid()
    m[field]=value
    with pytest.raises(ValueError):
        validate_meta(m)
