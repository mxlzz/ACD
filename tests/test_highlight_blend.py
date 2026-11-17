import numpy as np
import pytest

from acd_lab.highlight_blend import blend_input_highlights, blend_constant


def test_uses_raw_only_and_preserves_nonhighlight_output():
    raw=np.zeros((10,10,3),dtype="f4")
    raw[0,0]=100
    raw[0,1]=40
    denoised=np.full_like(raw,2)
    out,info=blend_input_highlights(raw,denoised)
    assert out.shape==raw.shape
    np.testing.assert_allclose(out[5,5],denoised[5,5],atol=1e-6)
    assert 0 <= info["mean_raw_weight"] <= 1
    assert info["selection"].startswith("Only RAW")


def test_zero_max_mix_is_exact_denoised():
    x=np.arange(48,dtype="f4").reshape(4,4,3)
    d=x*0.4
    z,_=blend_input_highlights(x,d,max_raw_fraction=0)
    np.testing.assert_allclose(z,d,atol=1e-6)


def test_raw_selection_independent_of_filtered_image():
    x=np.zeros((8,8,3),dtype="f4")
    x[:2,0]=40
    a=np.ones_like(x)
    b=np.full_like(x,90)
    _,ma=blend_input_highlights(x,a)
    _,mb=blend_input_highlights(x,b)
    assert ma["threshold_low"]==mb["threshold_low"]
    assert ma["threshold_high"]==mb["threshold_high"]
    assert ma["mean_raw_weight"]==mb["mean_raw_weight"]


def test_constant_blend_controls_endpoints():
    x=np.zeros((6,6,3),dtype="f4")
    d=np.ones_like(x)
    np.testing.assert_allclose(blend_constant(x,d,raw_fraction=0),d)
    np.testing.assert_allclose(blend_constant(x,d,raw_fraction=1),x)


def test_uniform_brightness_has_safe_zero_weights():
    x=np.ones((6,6,3),dtype="f4")
    d=np.zeros_like(x)
    out,st=blend_input_highlights(x,d)
    assert st["mean_raw_weight"]==0
    assert np.max(np.abs(out))==0


def test_invalid_config_and_nan_fail():
    raw=np.ones((8,8,3),dtype="f4")
    with pytest.raises(ValueError,match="quantiles"):
        blend_input_highlights(raw,raw,low_quantile=.999,high_quantile=.9)
    with pytest.raises(ValueError,match="max_raw_fraction"):
        blend_input_highlights(raw,raw,max_raw_fraction=2)
    with pytest.raises(ValueError,match="aligned"):
        blend_input_highlights(raw,raw[:3])
    bad=raw.copy()
    bad[1,1,1]=float("nan")
    with pytest.raises(ValueError,match="NaN or infinite"):
        blend_input_highlights(bad,raw)
