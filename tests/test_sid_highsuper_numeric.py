"""Pure fixture determinism tests for cross-Blender High/Super inputs."""
import numpy as np
from scripts.sid_highsuper_numeric_fixture import make_aovs

def test_aov_inputs_are_repeatable():
    a,b=make_aovs(),make_aovs()
    assert len(a)==15
    for key in a:
        assert a[key].shape==(64,96,4)
        assert a[key].dtype==np.float32
        assert np.isfinite(a[key]).all()
        np.testing.assert_array_equal(a[key],b[key])
    assert a["emission"][...,:3].max()>=6
    np.testing.assert_array_equal(a["alpha"][...,0],a["noisy"][...,3])
