import numpy as np
import pytest
from scripts.analyze_cycles_internal_e0036 import scores


def test_exact_compositor_internal():
    raw=np.zeros((8,8,3),dtype=np.float32)
    denoised=np.ones_like(raw)
    a=scores(raw,denoised,denoised.copy())
    assert a["internal_compositor_exact_match"] is True
    assert a["internal_vs_compositor"]["rmse_linear"]==0
    assert a["raw_vs_internal"]["rmse_linear"]==1


def test_different_outputs_and_shape_guard():
    x=np.zeros((8,8,3),dtype=np.float32)
    y=x.copy();y[0,0]=1
    assert scores(x,y,x)["internal_compositor_exact_match"] is False
    with pytest.raises(ValueError,match="identical dimensions"):
        scores(x,y,x[:5])
