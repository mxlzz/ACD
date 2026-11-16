import pytest
from scripts.audit_detail_projection_e0045 import audit, project

def test_procedural_slat_period_sub_nyquist_at_old_benchmark_size():
    r=audit()
    assert r["num_slats"]==52
    assert 1.30<r["measures"]["slat_pitch_px_320"]["min"]<1.31
    assert 1.47<r["measures"]["slat_pitch_px_320"]["median"]<1.48
    assert r["measures"]["slat_pitch_px_320"]["max"]<2.0

def test_grout_lines_are_subpixel_not_a_raster_quality_claim():
    r=audit()
    assert .35 < r["measures"]["grout_width_px_320"]["min"] < .37
    assert r["minimum_full_frame_widths"]["grout_line_at_least_2px"]>1700
    assert r["at_1920px"]["min_grout_width_px"]>2

def test_camera_projection_scaling_at_same_aspect():
    xyz=(-.25,2.52,1.57)
    x,y=project(xyz,width=320,height=240)
    a,b=project(xyz,width=1920,height=1440)
    assert a==pytest.approx(6*x)
    assert b==pytest.approx(6*y)
