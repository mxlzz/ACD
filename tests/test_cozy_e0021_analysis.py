import numpy as np
import pytest
from scripts.analyze_cozy_exr import summarize_all_seeds

def test_requires_per_seed_output(tmp_path,monkeypatch):
    ref={"first":np.zeros((4,4,3),np.float32)}
    with pytest.raises(Exception):
        summarize_all_seeds(tmp_path,ref)

def test_ref_only_roi_select_is_not_affected_by_candidate():
    from scripts.analyze_cozy_e0020 import choose_reference_rois
    ref=np.zeros((80,100,3))
    ref[:40,:40]=2
    first=choose_reference_rois(ref,ref,size=24,count=2)
    assert first==choose_reference_rois(ref.copy(),ref.copy(),size=24,count=2)
