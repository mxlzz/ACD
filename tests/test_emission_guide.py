import numpy as np
import pytest
from acd_lab.emission_guide import emission_guided_blend


def test_no_emission_yields_exact_oidn():
    raw=np.full((5,5,3),5,dtype="f4")
    oidn=np.ones_like(raw)
    e=np.zeros_like(raw)
    out,s=emission_guided_blend(raw,oidn,e)
    np.testing.assert_allclose(out,oidn)
    assert s["mean_raw_weight"]==0
    assert s["nonzero_emission_fraction"]==0


def test_emission_restores_some_raw_only_where_emission_present():
    raw=np.full((5,5,3),10,dtype="f4")
    oidn=np.zeros_like(raw)
    e=np.zeros_like(raw)
    e[0,0]=10
    out,s=emission_guided_blend(raw,oidn,e,max_raw_fraction=1)
    assert out[0,0,0]>9
    assert np.max(np.abs(out[1:]))==0
    assert s["nonzero_emission_fraction"]==pytest.approx(1/25)


def test_emission_guide_is_not_depends_on_denoised_output():
    raw=np.ones((4,4,3),dtype="f4")
    e=np.zeros_like(raw)
    e[0,0]=4
    a,aa=emission_guided_blend(raw,np.zeros_like(raw),e)
    b,bb=emission_guided_blend(raw,np.full_like(raw,2),e)
    assert aa["mean_raw_weight"]==bb["mean_raw_weight"]
    assert aa["nonzero_emission_fraction"]==bb["nonzero_emission_fraction"]


def test_negative_emission_weight_is_zero():
    raw=np.ones((4,4,3),dtype="f4")
    e=np.full_like(raw,-4)
    out,stats=emission_guided_blend(raw,np.zeros_like(raw),e)
    assert np.max(np.abs(out))==0
    assert stats["mean_raw_weight"]==0


def test_bad_aov_shape_and_nan_rejected():
    raw=np.ones((4,4,3),dtype="f4")
    with pytest.raises(ValueError,match="aligned"):
        emission_guided_blend(raw,raw,np.ones((3,4,3),dtype="f4"))
    bad=raw.copy()
    bad[0,0,0]=np.nan
    with pytest.raises(ValueError,match="NaN or infinite"):
        emission_guided_blend(raw,raw,bad)
    with pytest.raises(ValueError,match="scale"):
        emission_guided_blend(raw,raw,raw,scale=0)
