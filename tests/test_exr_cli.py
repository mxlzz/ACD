import json

import numpy as np
import pytest

OpenEXR = pytest.importorskip("OpenEXR")
from acd_lab.cli import main


def test_inspect_and_check_exr_cli(tmp_path, capsys):
    channels = {}
    for c in "RGB":
        channels[f"ViewLayer.Combined.{c}"] = np.ones((2, 3), dtype=np.float32)
        channels[f"ViewLayer.DiffDir.{c}"] = np.ones((2, 3), dtype=np.float32)
        channels[f"ViewLayer.DiffInd.{c}"] = np.zeros((2, 3), dtype=np.float32)
        channels[f"ViewLayer.DiffCol.{c}"] = np.ones((2, 3), dtype=np.float32)
    file = tmp_path / "full.exr"
    with OpenEXR.File({}, channels) as output:
        output.write(str(file))
    assert main(["inspect-exr", "--input", str(file)]) == 0
    assert "ViewLayer.Combined.R" in capsys.readouterr().out
    report = tmp_path / "result.json"
    assert main(["check-passes", "--input", str(file), "--output", str(report)]) == 0
    metrics = json.loads(report.read_text())
    assert metrics["metrics"]["exact_match"]
