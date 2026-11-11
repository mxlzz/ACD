"""Check behavior-level SID graph invariants across original 3.6 and port 5.x.

Not a pixel-equivalence, OIDN-version or UI-equivalence certification.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def contract(legacy, adapter):
    problems = []
    if legacy["source_commit"] != adapter["source_commit"]:
        problems.append("Upstream source commit differs between original and port")

    # For 3 families, the legacy plugin constructs the subgroup three times
    # inside the outer high/super tree. Therefore count the nested nodes.
    for mode in ("high", "super"):
        old_sub = legacy[mode + "_subgroup"]
        old_top = legacy[mode + "_top"]
        new = adapter["modes"][mode]
        denoise_count = old_top["denoisers"] + 3 * old_sub["denoisers"]
        mix_count = len(old_top["mix_factors"]) + 3 * len(old_sub["mix_factors"])
        if new["denoisers"] != denoise_count:
            problems.append(f"{mode} OIDN nodes: old {denoise_count}, new {new['denoisers']}")
        if len(new["mix_factors"]) != mix_count:
            problems.append(f"{mode} Mix nodes: old {mix_count}, new {len(new['mix_factors'])}")
        if any(abs(x - 1.0) > 1e-6 for x in old_top["mix_factors"] + old_sub["mix_factors"] + new["mix_factors"]):
            problems.append(f"{mode} non-unit MixRGB factor in legacy/port")
        if any(x != "ACCURATE" for x in old_top["prefilters"] + old_sub["prefilters"]):
            problems.append(f"{mode} legacy OIDN prefilter not ACCURATE")
        if any(x != "Accurate" for x in new["prefilters"]):
            problems.append(f"{mode} Blender 5 OIDN prefilter not Accurate")
        old_em = old_top["guide_links"].get("Denoise Emission")
        new_em = new["guide_links"].get("Emission | unguided OIDN")
        if old_em is None or new_em is None:
            problems.append(f"{mode} emission OIDN missing")
        elif any(x in ("Denoising Normal", "Denoising Albedo", "Normal", "Albedo") for x in old_em + new_em):
            problems.append(f"{mode} emission OIDN has unexpected guides")
        old_alpha = old_top["guide_links"].get("Denoise Alpha")
        new_alpha = new["guide_links"].get("Alpha | independent guided OIDN")
        if old_alpha is None or new_alpha is None or len(old_alpha) != 3 or len(new_alpha) != 3:
            problems.append(f"{mode} independent guided alpha OIDN missing")

    old_standard = legacy["standard"]
    new_standard = adapter["modes"]["standard"]
    if old_standard["denoisers"] != 1 or new_standard["denoisers"] != 1:
        problems.append("Standard OIDN node count mismatch")
    if old_standard["prefilters"] != ["FAST"] or new_standard["prefilters"] != ["Fast"]:
        problems.append("Standard FAST prefilter mismatch")
    if len(new_standard["mix_factors"]) != 0 or len(old_standard["mix_factors"]) != 0:
        problems.append("Standard must not contain a mixing node")
    return problems


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: compare_sid_contracts.py OLD.json PORT.json")
    old = json.loads(Path(sys.argv[1]).read_text())
    new = json.loads(Path(sys.argv[2]).read_text())
    errors = contract(old, new)
    report = {"passed": not errors, "errors": errors,
              "scope": "Node counts, factor, prefilter, emission and alpha guidance only",
              "not_proven": ["Pixel identity", "OIDN backend equivalence", "Alpha RGB/bit-depth numerical parity"]}
    output = Path(sys.argv[2]).with_name("sid_contract_comparison.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
