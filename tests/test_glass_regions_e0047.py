import numpy as np
import pytest
from scripts.analyze_glass_regions_e0047 import ROIS,analyze_arrays,corr_h_luma

def test_two_fixed_nonoverlapping_regions():
    assert ROIS["glass_overlap"]==(8,96,80,160)
    assert ROIS["uncovered_slats"]==(232,96,80,160)
    assert ROIS["glass_overlap"][0]+ROIS["glass_overlap"][2] < ROIS["uncovered_slats"][0]

def test_gradient_correlation_same_signal_and_inverted_signal():
    x=np.arange(100,dtype=np.float32)[None,:,None]
    a=np.tile(x,(30,1,3))/100.
    assert corr_h_luma(a,a)==pytest.approx(1.0,abs=1e-12)

def test_synthetic_guide_masks_and_finite_refs():
    h,w=512,512
    xx=np.arange(w,dtype=np.float32)
    slats=((np.arange(w)%10)<5).astype(np.float32)
    val=np.tile(slats,(h,1))[...,None]
    base=np.repeat(val,3,axis=-1)
    ref1=base+0.03
    ref2=base+0.05
    obj={"raw":base+0.2,"oidn":base*.8,"ref1":ref1,"ref2":ref2,
         "albedo":base,"normal":base}
    result=analyze_arrays(obj)
    assert set(result)==set(ROIS)
    assert all(result[k]["ref_horizontal_luma_gradient_corr"]>0.99 for k in result)
    assert all(result[k]["absolute_exr_xywh"][2:]==[80,160] for k in result)

def test_wrong_shape():
    z=np.zeros((512,512,3),dtype=np.float32)
    d={k:z for k in ("raw","oidn","ref1","ref2","albedo","normal")}
    d["normal"]=z[:200]
    with pytest.raises(ValueError,match="512x512"):
        analyze_arrays(d)
