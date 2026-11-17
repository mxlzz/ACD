import numpy as np
import pytest
from scripts.analyze_cozy_crossfit_e0059 import crossfit_region
from scripts.analyze_cozy_consensus_e0052 import SEEDS

def edge(level=1.0):
    a=np.zeros((24,32,3),np.float32)
    a[:,16:]=level
    return a

def seeds(raw,oidn):
    return {s:{"Raw":raw.copy(),"NATIVE_COMP_OIDN":oidn.copy()} for s in SEEDS}

def test_good_filter_improves_heldout_reference_error():
    r=edge()
    noisy=r.copy()
    noisy[::2,::2]+=.4
    scored=crossfit_region(r,r,seeds(noisy,r),(0,0,32,24))
    assert scored["selected_pair_count"]==24
    assert not scored["oidn_worse_than_raw_in_all_three_seeds"]
    assert scored["539"]["NATIVE_COMP_OIDN"]["heldout_gradient_rmse"]==0

def test_blur_regression_detected_with_raw_reference_match():
    r=edge()
    flat=edge(.1)
    scored=crossfit_region(r,r,seeds(r,flat),(0,0,32,24))
    assert scored["selected_pair_count"]==24
    assert scored["oidn_worse_than_raw_in_all_three_seeds"]

def test_heldout_reference_does_not_change_selection_mask():
    select=edge()
    one=crossfit_region(select,edge(.7),seeds(select,select),(0,0,32,24))
    two=crossfit_region(select,edge(1.3),seeds(select,select),(0,0,32,24))
    assert one["selected_pair_count"]==two["selected_pair_count"]
    assert one["source_gradient_threshold"]==two["source_gradient_threshold"]

def test_invalid_roi_rejected():
    a=edge()
    with pytest.raises(ValueError,match="ROI"):
        crossfit_region(a,a,seeds(a,a),(25,0,12,24))
