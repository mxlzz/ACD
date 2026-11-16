import pytest
from scripts.cozy_crop_e0053 import contract, FULL, RECT, INNER

def test_crop_geometry_and_margin():
    c=contract(*FULL)
    x,y,w,h=RECT
    b=c["normalized_border"]
    assert 0<b["min_x"]<b["max_x"]<1
    assert 0<b["min_y"]<b["max_y"]<1
    assert (round((b["max_x"]-b["min_x"])*FULL[0]),
            round((b["max_y"]-b["min_y"])*FULL[1]))==(512,512)
    assert INNER==(76,76,360,360)
    assert (x+INNER[0],y+INNER[1])==(1200,720)

def test_wrong_resolution_fails_closed():
    with pytest.raises(ValueError,match="1920x1808"):
        contract(512,482)
