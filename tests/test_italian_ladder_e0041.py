import numpy as np
import pytest

from scripts.analyze_italian_ladder_e0041 import summarize_pairs


def test_ladder_reports_decrease_without_claiming_convergence():
    base=np.full((200,320,3),1.0,dtype=np.float32)
    pairs={}
    for spp,delta in ((8,.4),(16,.2),(32,.1)):
        pairs[spp]=(base,base+delta)
    r=summarize_pairs(pairs)
    assert r["8"]["interseed_difference"]["rmse_linear"] > r["16"]["interseed_difference"]["rmse_linear"]
    assert r["16"]["interseed_difference"]["rmse_linear"] > r["32"]["interseed_difference"]["rmse_linear"]
    assert r["32"]["ratio_to_previous_spp"] == pytest.approx(.5,rel=1e-5)
    assert all(not x["identical_references"] for x in r.values())


def test_identical_references_do_not_establish_independence():
    zeros=np.zeros((200,320,3),dtype="f4")
    r=summarize_pairs({n:(zeros,zeros.copy()) for n in (8,16,32)})
    assert all(x["identical_references"] for x in r.values())


def test_shape_mismatch_is_rejected():
    base=np.zeros((200,320,3),dtype="f4")
    pair={n:(base,base.copy()) for n in (8,16,32)}
    pair[16]=(base,base[:10])
    with pytest.raises(ValueError,match="Misaligned"):
        summarize_pairs(pair)
