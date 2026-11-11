"""M3.8 matrix key contracts and numerical bookkeeping."""
import numpy as np
import pytest
from scripts.compare_sid_oidn_matrix import BASES,QUALITIES,HDRS,key
from scripts.compare_sid_standard_numeric import metrics

def test_exhaustive_matrix_key_set():
    new={key(b,q,h) for b in BASES for q in QUALITIES for h in HDRS}
    old={key(b,"legacy",h) for b in BASES for h in HDRS}
    assert len(new)==24 and len(old)==8
    assert not(new & old)
    assert "emission_accurate__balanced__h0" in new

def test_metric_is_not_rounded_or_normalized():
    a=np.zeros((2,4,3),dtype=np.float32)
    b=a.copy()
    b[1,3,0]=4.
    m=metrics(a,b)
    assert m["pixels"]==8
    assert m["rmse"]==pytest.approx(np.sqrt(2/3),abs=1e-8)
    assert m["max_abs"]==4.
