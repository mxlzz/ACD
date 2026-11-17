import numpy as np
import pytest

from acd_lab.hdr_tail import hdr_tail_breakdown


def sample():
    ref = np.zeros((4, 4, 3), dtype=np.float32)
    ref[0, 0] = 30.0
    ref[0, 1] = 20.0
    raw = ref.copy()
    raw[0, 0] = 25
    raw[3, 3] = 1
    return ref, raw


def test_identity_has_zero_error_with_fixed_masks():
    ref, raw = sample()
    r = hdr_tail_breakdown(ref, raw, {"Exact": ref}, top_fraction=.125)
    assert r["masks"]["reference_brightest"]["pixel_count"] == 2
    assert r["masks"]["raw_largest_errors"]["pixel_count"] == 2
    for mask in r["masks"].values():
        assert mask["methods"]["Exact"]["rmse_inside"] == 0
        assert mask["methods"]["Exact"]["rmse_outside"] == 0
        assert mask["methods"]["Exact"]["sse_fraction_inside"] is None


def test_suppression_of_large_raw_spike_reduces_sse_in_common_mask():
    ref, raw = sample()
    better = raw.copy()
    better[0, 0] = ref[0, 0]
    r = hdr_tail_breakdown(ref, raw, {"CorrectHighlight": better}, top_fraction=.0625)
    d = r["masks"]["reference_brightest"]["methods"]
    assert d["CorrectHighlight"]["rmse_inside"] < d["Raw"]["rmse_inside"]
    assert r["masks"]["raw_largest_errors"]["methods"]["CorrectHighlight"]["sse_inside"] == 0


def test_candidate_cannot_move_reference_selected_mask():
    ref, raw = sample()
    constant = np.zeros_like(raw)
    blowout = constant.copy()
    blowout[2, 3] = 10000
    a = hdr_tail_breakdown(ref, raw, {"A": constant})
    b = hdr_tail_breakdown(ref, raw, {"B": blowout})
    for m in a["masks"]:
        assert a["masks"][m]["mask_coordinate_hash"] == b["masks"][m]["mask_coordinate_hash"]


def test_all_zero_reference_sse_does_not_divide_by_zero():
    z = np.zeros((3, 3, 3), dtype=float)
    r = hdr_tail_breakdown(z, z, {"Same": z})
    assert r["masks"]["raw_largest_errors"]["methods"]["Raw"]["sse_fraction_inside"] is None


def test_invalid_fraction_and_shape():
    ref, raw = sample()
    with pytest.raises(ValueError, match="top_fraction"):
        hdr_tail_breakdown(ref, raw, {}, top_fraction=1)
    with pytest.raises(ValueError, match="aligned"):
        hdr_tail_breakdown(ref, raw[:-1], {})
    with pytest.raises(ValueError, match="candidate"):
        hdr_tail_breakdown(ref, raw, {"Bad": np.zeros((2, 3, 3))})
    raw[0, 0, 0] = np.nan
    with pytest.raises(ValueError, match="NaN or infinite"):
        hdr_tail_breakdown(ref, raw, {})


def test_exact_selection_count_with_ties():
    ref = np.zeros((10, 10, 3))
    result = hdr_tail_breakdown(ref, ref, {"X": ref}, top_fraction=.03)
    assert all(v["pixel_count"] == 3 for v in result["masks"].values())


def test_sum_of_shared_mask_sse_is_total_sse():
    ref, raw = sample()
    r = hdr_tail_breakdown(ref, raw, {"X": raw * .5})
    for mask in r["masks"].values():
        for metrics in mask["methods"].values():
            assert metrics["sse_inside"] + metrics["sse_outside"] == pytest.approx(
                metrics["total_rgb_mean_sse"]
            )


def test_brightness_signed_bias_direction_is_detected_without_candidates_changing_mask():
    from acd_lab.hdr_tail import highlight_signed_bias
    ref=np.zeros((4, 4, 3), dtype=float)
    ref[0, 0] = 10
    raw=ref.copy()
    raw[0, 0]=5
    high=ref.copy()
    high[0, 0]=20
    result=highlight_signed_bias(ref,raw,{"High":high},top_fraction=.0625)
    assert result["selected_pixel_count"] == 1
    assert result["methods"]["Raw"]["candidate_to_reference_sum_ratio"] == pytest.approx(.5)
    assert result["methods"]["High"]["candidate_to_reference_sum_ratio"] == pytest.approx(2)
    assert result["methods"]["Raw"]["mean_signed_luminance_delta"] < 0
    assert result["methods"]["High"]["mean_signed_luminance_delta"] > 0
    assert result["methods"]["High"]["fraction_above_reference"] == 1


def test_signed_bias_zero_reference_does_not_divide_by_zero():
    from acd_lab.hdr_tail import highlight_signed_bias
    zeros=np.zeros((2, 4, 3))
    result=highlight_signed_bias(zeros,zeros,{"X":zeros})
    assert result["methods"]["X"]["candidate_to_reference_sum_ratio"] is None


def test_signed_bias_rejects_misregistration_and_nonfinite():
    from acd_lab.hdr_tail import highlight_signed_bias
    a,b=sample()
    with pytest.raises(ValueError,match="aligned"):
        highlight_signed_bias(a,b[:-1],{})
    bad=a.copy()
    bad[0,0,0]=np.inf
    with pytest.raises(ValueError,match="NaN or infinite"):
        highlight_signed_bias(a,b,{"bad":bad})
