import numpy as np
import pytest
from scripts.analyze_italian_ladder_e0042 import evaluate_arrays

def test_finite_spread_and_ratios():
    x=np.ones((400,640,3),dtype="f4")
    d={s:(x,x+float(n)) for s,n in [(32,.4),(64,.2),(128,.1)]}
    a=evaluate_arrays(d)
    assert a["32"]["interseed_metrics"]["rmse_linear"] > a["128"]["interseed_metrics"]["rmse_linear"]
    assert a["128"]["spread_ratio_to_previous"] == pytest.approx(.5,rel=1e-4)

def test_identical_inputs_are_not_independence_proof():
    x=np.zeros((400,640,3),dtype="f4")
    a=evaluate_arrays({s:(x,x.copy()) for s in (32,64,128)})
    assert all(v["exact_match"] for v in a.values())

def test_reject_invalid_image_shape():
    x=np.zeros((400,640,3),dtype="f4")
    a={s:(x,x) for s in (32,64,128)}
    a[64]=(x,np.zeros((240,320,3),dtype="f4"))
    with pytest.raises(ValueError,match="shape"):
        evaluate_arrays(a)
