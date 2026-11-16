import numpy as np
from scripts.analyze_reflections_e0048 import compare
def data(raw_shift=0.,guide_shift=0.):
    x=np.ones((512,512,3),dtype="f4")
    a={"raw":x,"oidn":x,"albedo":x,"normal":x}
    b={"raw":x+raw_shift,"oidn":x*.9,"albedo":x+guide_shift,"normal":x}
    return a,b,{"ref1":x,"ref2":x}
def test_fail_closed_changed_raw():
    a,b,refs=data(raw_shift=.02,guide_shift=.3)
    result=compare(a,b,refs)
    assert not result["causal_interpretation_allowed"] and not result["scores"]
def test_no_guide_effect_stops():
    a,b,refs=data()
    assert not compare(a,b,refs)["causal_interpretation_allowed"]
def test_guide_only_metrics_fixed_rois():
    a,b,refs=data(guide_shift=.1)
    r=compare(a,b,refs)
    assert r["causal_interpretation_allowed"]
    assert set(r["scores"]["follow_false"])=={"glass_overlap","uncovered_slats","interior"}
