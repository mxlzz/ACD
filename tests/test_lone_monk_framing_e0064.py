"""E0064 fixed original source/camera/aspect and no algorithm modification."""
import pytest
from scripts.lone_monk_contract_e0064 import frame_size, WIDTH, SOURCE_SHA, SAMPLES, SEED

def test_preview_preserves_original_camera_fov_shape():
    assert frame_size(1920,1080)==(960,540)
    assert frame_size(1600,900)==(960,540)
    assert frame_size(2000,1600)==(960,768)

@pytest.mark.parametrize("width,height",[(0,200),(400,0),(10000,16),(1000,10000)])
def test_bad_source_dimensions_fail(width,height):
    with pytest.raises(ValueError):
        frame_size(width,height)

def test_source_fixture_identity_is_frozen():
    assert len(SOURCE_SHA)==64
    assert WIDTH==960 and SAMPLES==8 and SEED==539
