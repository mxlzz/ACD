import numpy as np
import pytest
from scripts.visualize_hall_e0034 import select_disjoint_rois

def test_disjoint_and_reference_only():
    x=np.zeros((256,256,3),dtype="f4")
    x[10:26,10:26]=40
    x[120:180,120:180]=2
    rois=select_disjoint_rois(x,x,size=64,count=4)
    assert rois==select_disjoint_rois(x.copy(),x.copy(),size=64,count=4)
    assert rois[0][0]=="brightest"
    for i,(_, (cx,cy,w,h)) in enumerate(rois):
        assert 0<=cx<=256-w and 0<=cy<=256-h
        for _,(xx,yy,ww,hh) in rois[:i]:
            assert cx+w<=xx or xx+ww<=cx or cy+h<=yy or yy+hh<=cy

def test_invalid_reference_input():
    r=np.zeros((64,64,3),dtype="f4")
    with pytest.raises(ValueError,match="aligned"):
        select_disjoint_rois(r,r[:10])
    bad=r.copy();bad[0,0,0]=np.nan
    with pytest.raises(ValueError,match="finite"):
        select_disjoint_rois(r,bad)
    with pytest.raises(ValueError,match="size"):
        select_disjoint_rois(r,r,size=128)
