"""E0044 exact input and diagnostic grid tests."""
import numpy as np
import pytest
from scripts.analyze_current_detail_e0044 import score_arrays

def test_fixed_twelve_tiles_and_two_refs():
    h,w=240,320
    a=np.zeros((h,w,3),dtype=np.float32)
    a[:,w//2:]=0.6
    b=a.copy()
    b[:,w//2:]+=0.01
    noisy=a+0.05
    denoised=a+0.02
    report=score_arrays({"Raw":noisy,"NATIVE_COMP_OIDN":denoised},(a,b))
    assert len(report["tiles"])==12
    assert report["tiles"][0]["xywh"]==[0,0,80,80]
    assert report["tiles"][-1]["xywh"]==[240,160,80,80]
    assert report["whole_image"]["NATIVE_COMP_OIDN"]["ref1"]["color"]["rmse_linear"] < report["whole_image"]["Raw"]["ref1"]["color"]["rmse_linear"]

def test_reject_wrong_outputs():
    z=np.zeros((240,320,3),dtype=np.float32)
    with pytest.raises(ValueError,match="Only native OIDN"):
        score_arrays({"Raw":z,"OTHER":z},(z,z))
    with pytest.raises(ValueError,match="320x240"):
        score_arrays({"Raw":z,"NATIVE_COMP_OIDN":z},(z[:24],z))
