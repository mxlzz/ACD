"""Make missing candidate/ref evidence fail loudly rather than fabricate rankings."""
import json
import pytest
from scripts.summarize_sid_realbench import NAMES,summarize

def test_expected_bench_methods():
    assert len(NAMES)==8 and len(set(NAMES))==8
    assert "NATIVE_COMP_OIDN" in NAMES

def test_missing_candidates_rejected(tmp_path):
    (tmp_path/"metrics.json").write_text(json.dumps({
        "measurements":{"Raw":{}},"reference_quality_diagnostic":None}))
    (tmp_path/"metadata.json").write_text("{}")
    with pytest.raises(ValueError,match="Missing candidates"): summarize(tmp_path)
