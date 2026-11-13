import json
from pathlib import Path
import pytest
from scripts.analyze_oidn_standalone_e0037 import commands, only, source_arrays


def test_accurate_like_prefilters_before_clean_aux(tmp_path):
    exe=Path("/bin/oidnDenoise")
    raw=commands(exe,"raw_aux",tmp_path)
    accurate=commands(exe,"accurate_like",tmp_path)
    assert len(raw)==1 and "--clean_aux" not in raw[0]
    assert len(accurate)==3 and "--clean_aux" in accurate[-1]
    assert "--hdr" not in accurate[0] and "--hdr" not in accurate[1]
    assert "--alb" in accurate[0] and "--nrm" in accurate[1]
    assert "--hdr" in accurate[2] and "-q" in accurate[2]
    with pytest.raises(ValueError, match="Unknown mode"):
        commands(exe, "bad_mode", tmp_path)


def test_reject_ambiguous_files_and_wrong_versions(tmp_path):
    (tmp_path/"one").mkdir()
    (tmp_path/"two").mkdir()
    for name in ("one", "two"):
        (tmp_path/name/"metadata.json").write_text("{}")
    with pytest.raises(ValueError,match="Expected unique"):
        only(tmp_path,"metadata.json")
    (tmp_path/"two"/"metadata.json").unlink()
    (tmp_path/"one"/"metadata.json").write_text(json.dumps({"blender":"5.3.0","resolution":[128,96],"seed":539,"samples":16}))
    fixed={"reports_by_version":{"5.2.4":{"blender":"5.2.4 LTS","raw_multilayer_max_abs_delta":0,"standard_vs_native_compositor_rmse":0}}}
    with pytest.raises(ValueError,match="frozen E0035"):
        source_arrays(tmp_path,fixed,"5.2.4")
