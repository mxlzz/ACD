import copy
import pytest
from scripts.lone_monk_crop_e0065 import contract, FULL, RECT, INNER, REGIONS, SOURCE_SHA
from scripts.analyze_lone_monk_portal_e0065 import inspect_meta, EXPECTED


def test_source_anchored_architecture_region():
    x=contract(*FULL)
    assert x["source_sha256"]==SOURCE_SHA
    assert x["crop_top_left_xywh"]==[700,430,512,512]
    assert INNER==(64,64,384,384)
    assert x["context_margin_pixels"]==64
    bounds=x["normalized_border"]
    assert round((bounds["max_x"]-bounds["min_x"])*FULL[0])==512
    assert round((bounds["max_y"]-bounds["min_y"])*FULL[1])==512
    assert set(REGIONS)==set(x["fixed_regions_xywh"])


def test_wrong_full_camera_resolution_rejected():
    with pytest.raises(ValueError,match="1920x1440"):
        contract(1920,1080)


def valid_meta():
    d=copy.deepcopy(EXPECTED)
    d.update({"blender":"5.2.4 LTS",
              "native_compositor_oidn":{"hdr":True},
              "cycles":{"use_adaptive_sampling":False,"use_denoising":False}})
    return d


def test_precise_blender_contract_accepts():
    inspect_meta(valid_meta())


@pytest.mark.parametrize("key,value",[
    ("scene_name","Main"),("source_blend_sha256","a"*64),
    ("resolution",[512,512]),("samples",16),
    ("reference_samples",64),("extra_input_seeds",[]),
    ("e0065_crop",None),("capture_aov",False)
])
def test_violation_fail_closed(key,value):
    meta=valid_meta()
    meta[key]=value
    with pytest.raises(ValueError):
        inspect_meta(meta)


def test_cycles_internal_filter_or_adaptive_disallowed():
    for key in ("use_adaptive_sampling","use_denoising"):
        meta=valid_meta()
        meta["cycles"][key]=True
        with pytest.raises(ValueError):
            inspect_meta(meta)
