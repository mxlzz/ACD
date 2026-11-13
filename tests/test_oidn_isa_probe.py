import numpy as np
from scripts.oidn_isa_probe import make_inputs
from acd_lab.pfm import read_pfm

def test_fixed_synthetic_cpu_isa_probe_inputs(tmp_path):
    c,a,n=make_inputs(tmp_path)
    rgb=read_pfm(c)
    assert rgb.shape==(144,192,3)
    assert np.isfinite(rgb).all()
    assert float(rgb.max())>10
    np.testing.assert_array_equal(read_pfm(n)[...,2],np.ones((144,192),dtype="f4"))
    assert read_pfm(a).shape==rgb.shape
