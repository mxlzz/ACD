from pathlib import Path
import pytest
from scripts.analyze_oidn_standalone_e0037 import commands


def test_old_version_protocol_uses_identical_cli_flags(tmp_path):
    binary=Path("/some/old/oidnDenoise")
    modes=("raw_aux","accurate_like")
    for mode in modes:
        args=commands(binary,mode,tmp_path)
        assert len(args)==(3 if mode=="accurate_like" else 1)
        assert all(cmd[1:3]==["-d","cpu"] for cmd in args)
        assert all("-q" in cmd and "high" in cmd for cmd in args)
        assert ("--clean_aux" in args[-1]) == (mode=="accurate_like")
