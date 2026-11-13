import numpy as np
import pytest
from acd_lab.error_concentration import error_concentration

def test_isolated_hdr_outlier_dominates_squared_error():
    ref=np.zeros((10,10,3),np.float32)
    cand=ref.copy()
    cand[3,4,:]=10
    s=error_concentration(ref,cand)
    assert s["top_pixel_count"]==1
    assert s["fraction_squared_error_in_top_pixels"]==pytest.approx(1)
    assert s["max_pixel_rmse"]==pytest.approx(10)

def test_uniform_error_is_spread():
    ref=np.zeros((10,10,3),np.float32)
    s=error_concentration(ref,np.ones_like(ref))
    assert s["fraction_squared_error_in_top_pixels"]==pytest.approx(.01)

def test_identical_image_reports_no_error_fraction():
    ref=np.zeros((4,4,3),np.float32)
    s=error_concentration(ref,ref)
    assert s["fraction_squared_error_in_top_pixels"] is None
    assert s["linear_rgb_rmse"]==0

def test_bad_shapes_and_fraction_rejected():
    ref=np.zeros((4,4,3),np.float32)
    with pytest.raises(ValueError,match="shapes"):
        error_concentration(ref,ref[:2])
    with pytest.raises(ValueError,match="top_fraction"):
        error_concentration(ref,ref,top_fraction=0)
