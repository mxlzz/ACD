"""E0063: pinned Lone Monk original scene, two-process Cycles noisy seed screen.

Only checks that labeled seeds produce measurably different noisy Raw arrays.
Do not infer statistical independence, reference convergence, or OIDN quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from acd_lab.io import read_arrays, write_report
from scripts.analyze_classroom_seed_e0056 import score

SOURCE_SHA = "eea2bbfb3f9271050f523c8351fca40f2f559ce84b42b0143e949ecdb4594c3b"
SOURCE_BYTES = 33452252
SEEDS = (539, 911)
SCENE = "daylight"
CAMERA = "cam.001"
SOURCE_URL = "https://mirror.blender.org/demo/cycles/lone-monk_cycles_and_exposure-node_demo.blend"


def source_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_meta(meta: dict, seed: int) -> None:
    expected = {
        "active_scene": SCENE,
        "active_camera": CAMERA,
        "requested_seed": seed,
        "sample_offset": 0,
        "sampling_pattern": "TABULATED_SOBOL",
        "scene_variant": "external",
    }
    for k, value in expected.items():
        if meta.get(k) != value:
            raise ValueError(f"Lone Monk E0063 metadata mismatch {k}: {meta.get(k)!r}")
    scene = [x for x in meta["settings_all_scenes"] if x["name"] == SCENE]
    if len(scene) != 1 or scene[0]["samples"] != 16 or scene[0]["seed"] != seed:
        raise ValueError("Cycles samples and requested seed not retained")


def analyze(source: Path, root: Path):
    if source.stat().st_size != SOURCE_BYTES or source_sha(source) != SOURCE_SHA:
        raise ValueError("Lone Monk binary identity mismatch; stop and re-audit")
    data = []
    details = {}
    for seed in SEEDS:
        prefix = f"monk_seed{seed}"
        meta = json.loads((root / (prefix + ".json")).read_text())
        check_meta(meta, seed)
        path = root / (prefix + ".exr")
        rgb = read_arrays(path)["image"]
        if rgb.shape[:2] != (54, 96):
            raise ValueError(f"Unexpected EXR resolution {rgb.shape}")
        data.append(rgb)
        details[str(seed)] = {"output_sha256": source_sha(path), "metadata": meta}
    metrics = score(*data)
    return {
        "experiment": "E0063",
        "source": "Official Blender Lone Monk, Carlo Bergonzini/Monorender CC BY",
        "source_sha256": SOURCE_SHA,
        "source_bytes": SOURCE_BYTES,
        "source_url": SOURCE_URL,
        "scene": SCENE,
        "camera": CAMERA,
        "blender": "5.2.4",
        "resolution": [96, 54],
        "samples": 16,
        "sampler": "TABULATED_SOBOL",
        "seed_values": list(SEEDS),
        "raw_seed_variation": metrics,
        "sources": details,
        "measurably_distinct": metrics["measurably_distinct"],
        "statistical_independence_proven": False,
        "reference_convergence_proven": False,
        "oidn_or_acd_tested": False,
        "quality_holdout": False,
        "new_algorithm": False,
        "decision": (
            "PASS first noisy-input diversity gate. Source is usable for next pre-registered "
            "development benchmark after adequate reference uncertainty and architecture ROI protocol."
            if metrics["measurably_distinct"] else
            "STOP: source/camera does not produce sufficiently varying seed input in current Cycles setup. "
            "Not admitted for multi-seed denoiser benchmarks."
        ),
    }


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--source", required=True, type=Path)
    a.add_argument("--directory", required=True, type=Path)
    a.add_argument("--output", required=True, type=Path)
    args = a.parse_args()
    d = analyze(args.source, args.directory)
    args.output.mkdir(parents=True, exist_ok=True)
    write_report(args.output / "E0063_RESULTS.json", d)
    m = d["raw_seed_variation"]
    lines = [
        "# E0063 — Lone Monk, original native-Cycles seed diversity",
        "",
        "Official Blender Cycles demo, Carlo Bergonzini/Monorender CC BY, source SHA pinned in E0062.",
        "Blender 5.2.4, daylight/cam.001, 96×54, 16 spp seeds 539 and 911 in separate processes.",
        "Neither OIDN nor any ACD method has been executed.",
        "",
        f"- Interseed Raw RGB RMSE: {m['rmse']:.9f}.",
        f"- Relative input difference: {m['relative_rmse']:.9f}.",
        f"- Changed pixels above 1e-6: {m['changed_pixels_above_1e_minus_6']}/5184.",
        f"- Measurably distinct Raw inputs: **{m['measurably_distinct']}**.",
        "",
        "**Decision:** " + d["decision"],
        "A nonzero Raw difference is not proof of independent Monte Carlo estimators. "
        "Still need paired references, delivery-scale pixels and independent-scene holdout. "
        "No algorithm changes, no binary, EXR, or derivatives redistributed.",
        "",
        "[Numbers and original hashes](E0063_RESULTS.json).",
        "",
    ]
    (args.output / "E0063.md").write_text("\n".join(lines))
    print("E0063_ONLY_RAW_SEED_VARIATION", json.dumps(m, sort_keys=True))


if __name__ == "__main__":
    main()
