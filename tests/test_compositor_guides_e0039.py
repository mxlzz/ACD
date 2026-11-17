import json
import pytest
from scripts.analyze_compositor_guides_e0039 import analyze


def test_reject_mismatched_source_before_exr(tmp_path):
    (tmp_path/"metadata.json").write_text(json.dumps({
      "scene":"detail_target","blender":"5.3.0","samples":16,
      "resolution":[128,96],"capture_aov":True,
      "native_compositor_oidn":{"quality":"High"}}))
    with pytest.raises(ValueError,match="pinned"):
        analyze(tmp_path)
