"""Pure-Python cross-version graph contract checks."""
import copy

from scripts.compare_sid_contracts import contract


def baseline():
    s = {"denoisers": 1, "prefilters": ["FAST"], "mix_factors": [], "guide_links": {}}
    sub_high = {"denoisers": 1, "prefilters": ["ACCURATE"], "mix_factors": [1, 1], "guide_links": {}}
    sub_super = {"denoisers": 2, "prefilters": ["ACCURATE"] * 2, "mix_factors": [1, 1], "guide_links": {}}
    top = {"denoisers": 3, "prefilters": ["ACCURATE"] * 3,
           "mix_factors": [1] * 4,
           "guide_links": {
               "Denoise Emission": ["Image"],
               "Denoise Alpha": ["Image", "Normal", "Albedo"],
           }}
    old = {"source_commit": "frozen", "standard": s, "high_subgroup": sub_high,
           "super_subgroup": sub_super, "high_top": top, "super_top": top}
    new = {"source_commit": "frozen", "modes": {
        "standard": {"denoisers": 1, "prefilters": ["Fast"],
                     "mix_factors": [], "guide_links": {}},
        "high": {"denoisers": 6, "prefilters": ["Accurate"] * 6,
                 "mix_factors": [1] * 10,
                 "guide_links": {
                     "Emission | unguided OIDN": ["Image"],
                     "Alpha | independent guided OIDN": ["Image", "Normal", "Albedo"]}},
        "super": {"denoisers": 9, "prefilters": ["Accurate"] * 9,
                 "mix_factors": [1] * 10,
                 "guide_links": {
                     "Emission | unguided OIDN": ["Image"],
                     "Alpha | independent guided OIDN": ["Image", "Normal", "Albedo"]}},
    }}
    return old, new


def test_contract_accepts_correct_behavioral_signature():
    assert contract(*baseline()) == []


def test_contract_fails_half_factor():
    old, new = baseline()
    new["modes"]["high"]["mix_factors"][0] = .5
    assert any("factor" in e for e in contract(old, new))


def test_contract_fails_unexpected_emission_guides():
    old, new = baseline()
    new["modes"]["super"]["guide_links"]["Emission | unguided OIDN"].append("Normal")
    assert any("emission" in e for e in contract(old, new))


def test_contract_fails_mismatched_oidn_count():
    old, new = baseline()
    new["modes"]["high"]["denoisers"] = 7
    assert any("OIDN nodes" in e for e in contract(old, new))



def test_contract_detects_both_old_and_new_wrong_same_count():
    old, new = baseline()
    old["standard"]["denoisers"] = 2
    new["modes"]["standard"]["denoisers"] = 2
    assert any("Standard" in e for e in contract(old, new))
