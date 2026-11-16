import pytest
from scripts.analyze_surat_pilot_e0060 import validate
def meta():
    return {
        "scene":"external","scene_name":"Scene","active_camera":"CAM Office",
        "source_blend_sha256":"a"*64,"resolution":[256,144],
        "samples":8,"reference_samples":64,"seed":539,
        "reference_seed":8819,"second_reference":True,
        "second_reference_seed":8922,"extra_input_seeds":[],"capture_aov":True,
        "blender":"5.2.4 LTS",
        "cycles":{"use_denoising":False,"use_adaptive_sampling":False},
        "native_compositor_oidn":{"quality":"High"}}
def test_exact_contract_accept():
    validate(meta(),"a"*64)
@pytest.mark.parametrize("key,value",[
    ("active_camera","CAM Aerial"),("reference_samples",8),
    ("samples",16),("scene_name","Scene.001"),
    ("resolution",[1920,1080]),("extra_input_seeds",[911])
])
def test_contract_rejects_mismatch(key,value):
    m=meta();m[key]=value
    with pytest.raises(ValueError):
        validate(m,"a"*64)
def test_reference_control():
    m=meta();m["cycles"]["use_adaptive_sampling"]=True
    with pytest.raises(ValueError):
        validate(m,"a"*64)
