import numpy as np
import pytest
from scripts.analyze_classroom_seed_e0056 import score

def test_distinct_randomized_images_pass_variation_gate():
    a=np.ones((54,96,3),dtype=np.float32)
    b=a.copy()
    b[::2]=1.1
    d=score(a,b)
    assert d["measurably_distinct"] and d["changed_pixels_above_1e_minus_6"]==2592
    assert d["independent_samples_proven"] is False

def test_identical_images_do_not_prove_seed_variation():
    a=np.ones((54,96,3),dtype=np.float32)
    d=score(a,a.copy())
    assert d["measurably_distinct"] is False
    assert d["changed_pixels_above_1e_minus_6"]==0

def test_wrong_dimensions_fail():
    a=np.ones((54,96,3),dtype=np.float32)
    with pytest.raises(ValueError,match="96x54"):
        score(a,np.ones((54,95,3),dtype=np.float32))
