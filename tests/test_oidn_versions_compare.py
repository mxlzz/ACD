from pathlib import Path
from scripts.oidn_versions_compare import args_for

def test_cli_arguments_fixed_identically_for_versions():
    one=args_for(Path("/v233/bin/oidnDenoise"),Path("in.pfm"),Path("a.pfm"),Path("n.pfm"),Path("o1.pfm"))
    two=args_for(Path("/v251/bin/oidnDenoise"),Path("in.pfm"),Path("a.pfm"),Path("n.pfm"),Path("o2.pfm"))
    assert one[1:-1] == two[1:-1]
    assert one[1:7] == ["-d","cpu","--hdr","in.pfm","--alb","a.pfm"]
    assert "--nrm" in one and "-q" in one and "high" in one
