import numpy as np
import pytest
from scripts.analyze_cozy_consensus_e0052 import inspect_region, SEEDS

def step(level):
    a=np.zeros((40,48,3),np.float32)
    a[:,24:]=level
    return a

def candidates(raw, filtered):
    return {s:{"Raw":raw.copy(),"STANDARD":filtered.copy(),
               "NATIVE_COMP_OIDN":filtered.copy()} for s in SEEDS}

def test_consensus_attenuation_screen_on_exact_edge():
    ref=step(2)
    r=inspect_region(ref,ref,candidates(ref,step(.5)),(0,0,48,40))
    assert r["selected_reference_consensus_pairs"]==40
    assert r["relative_reference_disagreement"]==0
    assert r["persistent_attenuation_screen"]
    assert r["scores"]["539"]["Raw"]["projected_edge_gain"]==pytest.approx(1)

def test_reference_conflict_does_not_create_false_edge():
    ref=step(2)
    r=inspect_region(ref,-ref,candidates(ref,ref),(0,0,48,40))
    assert r["selected_reference_consensus_pairs"]==0
    assert not r["persistent_attenuation_screen"]

def test_candidate_changes_cannot_select_different_edges():
    ref=step(2)
    a=inspect_region(ref,ref,candidates(ref,step(.3)),(0,0,48,40))
    b=inspect_region(ref,ref,candidates(ref,step(5)),(0,0,48,40))
    assert a["selected_reference_consensus_pairs"]==b["selected_reference_consensus_pairs"]
    assert a["reference_threshold"]==b["reference_threshold"]
    assert a["scores"]["539"]["NATIVE_COMP_OIDN"]["projected_edge_gain"]!=b["scores"]["539"]["NATIVE_COMP_OIDN"]["projected_edge_gain"]

def test_roi_and_alignment_are_strict():
    ref=step(2)
    with pytest.raises(ValueError,match="ROI"):
        inspect_region(ref,ref,candidates(ref,ref),(10,10,48,40))
    with pytest.raises(ValueError,match="candidate shape"):
        inspect_region(ref,ref,candidates(step(3),step(3)),(0,0,48,40))
