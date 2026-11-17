"""E0043 only checks the math/ROI contract on synthetic arrays."""
import numpy as np
import pytest
from scripts.analyze_guides_e0043 import compare
def test_tiles_fixed_and_ref_variability_not_ignored():
    base=np.ones((400,640,3),dtype=np.float32)
    refs={"ref8819":base,"ref8922":base+0.1}
    imgs={"Raw":base+0.5,"OIDN_RGB":base+0.2,
          "OIDN_Albedo":base+0.15,"OIDN_Both":base+0.3}
    d=compare(imgs,refs)
    assert len(d["tiles"])==16
    assert d["tiles"][0]["xywh"]==[0,0,160,100]
    assert d["tiles"][-1]["xywh"]==[480,300,160,100]
    assert d["reference_pair_disagreement"]["rmse_linear"]==pytest.approx(.1,abs=1e-5)
    assert d["tentative_guide_regression_tiles"]
def test_reject_nan_or_misaligned():
    a=np.ones((400,640,3),dtype=np.float32)
    img={"Raw":a,"OIDN_RGB":a,"OIDN_Albedo":a,"OIDN_Both":a}
    refs={"ref8819":a,"ref8922":a[:10]}
    with pytest.raises(ValueError,match="dimensions"):
        compare(img,refs)
