from scripts.analyze_reflections_e0048 import compare
from scripts.analyze_weighting_e0049 import run
import numpy as np
def test_inherited_causal_stop_for_changed_beauty():
    x=np.ones((512,512,3),dtype="f4")
    a={"raw":x,"oidn":x,"albedo":x,"normal":x}
    b={"raw":x+.5,"oidn":x,"albedo":x+.5,"normal":x}
    q=compare(a,b,{"ref1":x,"ref2":x})
    assert not q["causal_interpretation_allowed"] and not q["scores"]
