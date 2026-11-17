import numpy as np
from scripts.analyze_replayed_guides_e0050 import assess
def test_reject_bad_raw():
    x=np.ones((4,4,3),dtype="f4")
    d=assess(x,x+.1,x,x,{"ref1":x,"ref2":x})
    assert d["raw_passthrough_verified"] is False and d["scores"]=={}
def test_reject_replay_mismatch_even_if_raw_exact():
    x=np.ones((4,4,3),dtype="f4")
    d=assess(x,x,x+.2,x,{"ref1":x,"ref2":x})
    assert d["raw_passthrough_verified"] is True
    assert d["native_replay_verified"] is False
def test_accept_identical_baseline():
    x=np.ones((4,4,3),dtype="f4")
    d=assess(x,x,x,x,{"ref1":x,"ref2":x})
    assert d["raw_passthrough_verified"] and d["native_replay_verified"]
