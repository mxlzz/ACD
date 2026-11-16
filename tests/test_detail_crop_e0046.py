import numpy as np
import pytest
from scripts.analyze_detail_crop_e0046 import evaluate

def test_only_512_crop_and_320_inner():
    ref=np.zeros((512,512,3),dtype=np.float32)
    ref[:,256:]=.5
    a=ref+.2
    b=ref+.05
    report=evaluate({"Raw":a,"NATIVE_COMP_OIDN":b},[ref,ref+.01])
    assert report["evaluation_interior_xywh"]==[96,96,320,320]
    assert len(report["quadrants"])==4
    assert report["full_interior_metrics"]["NATIVE_COMP_OIDN"]["ref1"]["color"]["rmse_linear"] < report["full_interior_metrics"]["Raw"]["ref1"]["color"]["rmse_linear"]

def test_reject_wrong_image_crop():
    a=np.zeros((512,512,3),dtype=np.float32)
    b=np.zeros((320,240,3),dtype=np.float32)
    with pytest.raises(ValueError,match="512x512"):
        evaluate({"Raw":a,"NATIVE_COMP_OIDN":b},[a,a])
