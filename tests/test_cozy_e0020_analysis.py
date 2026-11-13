import numpy as np
import pytest
from scripts.analyze_cozy_e0020 import choose_reference_rois

def test_reference_only_roi_deterministic_and_no_overlaps():
    base=np.zeros((240,320,3),dtype=np.float64)
    base[10:80,40:110]=3
    base[110:180,130:200]=2
    regions=choose_reference_rois(base,base,size=80,count=3)
    assert regions == choose_reference_rois(base.copy(),base.copy(),size=80,count=3)
    assert len(regions)==3
    for i,(x,y,w,h) in enumerate(regions):
        assert 0<=x<=320-w and 0<=y<=240-h
        for xx,yy,ww,hh in regions[:i]:
            assert (x+w<=xx or xx+ww<=x or y+h<=yy or yy+hh<=y)

def test_reject_invalid_reference_data():
    r=np.zeros((32,32,3),np.float32)
    with pytest.raises(ValueError,match="aligned"):
        choose_reference_rois(r,r[:15])
    bad=r.copy();bad[0,0,0]=np.nan
    with pytest.raises(ValueError,match="finite"):
        choose_reference_rois(r,bad)
