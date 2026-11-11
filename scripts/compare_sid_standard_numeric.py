"""M3.5 numerical analysis: identical inputs, raw-passthrough control, HDR RGB/alpha.

Does not claim identity or superiority. Cross-version backend differences are
measurements, not errors that should be silenced with a loose pixel tolerance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def rgba(path: Path):
    import OpenEXR

    with OpenEXR.File(str(path), separate_channels=True) as f:
        assert len(f.parts) == 1, (path, len(f.parts))
        channels = f.parts[0].channels
        arrays = []
        for comp in "RGBA":
            candidates = [np.asarray(obj.pixels, dtype=np.float32)
                          for label, obj in channels.items()
                          if str(label).rsplit(".", 1)[-1] == comp]
            if len(candidates) != 1:
                raise ValueError(f"{path} expected one {comp} channel; got {sorted(channels)}")
            arrays.append(candidates[0])
    data = np.stack(arrays, axis=-1)
    if data.ndim != 3 or data.shape[-1] != 4 or not np.all(np.isfinite(data)):
        raise ValueError(f"Invalid RGBA or nonfinite pixels: {path}")
    return data


def metrics(reference, candidate, mask=None):
    if reference.shape != candidate.shape:
        raise ValueError("Array dimensions differ")
    if mask is not None:
        reference, candidate = reference[mask], candidate[mask]
    if reference.size == 0:
        return {"pixels": 0, "mae": None, "rmse": None, "max_abs": None}
    diff = candidate.astype(np.float64) - reference.astype(np.float64)
    return {
        "pixels": int(np.prod(reference.shape[:2])) if reference.ndim == 3 else int(reference.shape[0]),
        "mae": float(np.abs(diff).mean()),
        "rmse": float(np.sqrt(np.mean(diff * diff))),
        "max_abs": float(np.max(np.abs(diff))),
        "mean_signed": float(diff.mean()),
        "exact_match": bool(np.array_equal(reference, candidate)),
    }


def compare(input_dir: Path, legacy_dir: Path, port_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    fixture = json.loads((input_dir / "input_manifest.json").read_text())
    legacy = json.loads((legacy_dir / "manifest.json").read_text())
    port = json.loads((port_dir / "manifest.json").read_text())
    if legacy["flavor"] != "legacy" or port["flavor"] != "port":
        raise ValueError("Wrong Blender flavors")
    if legacy["upstream_commit"] != port["upstream_commit"]:
        raise ValueError("Upstream source commit mismatch")
    for name, item in fixture["files"].items():
        path = input_dir / (name + ".exr")
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        if current != item["sha256"]:
            raise ValueError(f"Frozen input hash mismatch: {name}")
        if legacy["input_sha256"].get(name) != current or port["input_sha256"].get(name) != current:
            raise ValueError(f"Blenders did not read same bytes for: {name}")

    input_noisy = rgba(input_dir / "noisy.exr")
    old_sid, new_sid = rgba(legacy_dir / "sid.exr"), rgba(port_dir / "sid.exr")
    if input_noisy.shape != (64, 96, 4) or old_sid.shape != input_noisy.shape or new_sid.shape != input_noisy.shape:
        raise ValueError("Unexpected or unequal output dimensions")

    mask_hdr = np.max(input_noisy[..., :3], axis=-1) > 1.0
    mask_alpha = input_noisy[..., 3] < 0.999
    if not mask_hdr.any() or not mask_alpha.any():
        raise ValueError("Fixture lost its HDR/transparency controls")

    # The source EXR may be associated/premultiplied by the compositor even in
    # raw passthrough; that transformation alone is not a SID port mismatch.
    # Cross-version raw comparisons are the gate, separately for EVERY input
    # (noisy beauty, albedo, normal), including alpha.
    passthrough = {}
    for raw_name, source_name in (("raw", "noisy"), ("raw_albedo", "albedo"),
                                  ("raw_normal", "normal")):
        original = rgba(input_dir / (source_name + ".exr"))
        old = rgba(legacy_dir / (raw_name + ".exr"))
        new = rgba(port_dir / (raw_name + ".exr"))
        if not (original.shape == old.shape == new.shape == input_noisy.shape):
            raise ValueError("Different dimensions for passthrough " + raw_name)
        passthrough[source_name] = {
            "legacy_vs_input": metrics(original, old),
            "port_vs_input": metrics(original, new),
            "legacy_vs_port": metrics(old, new),
        }
    # Float32 roundtrip tolerance. Source-vs-pass-through deviations are
    # reported, not silently interpreted as OIDN differences.
    passthrough_ok = all(control["legacy_vs_port"]["max_abs"] <= 0.001
                         for control in passthrough.values())
    differences = {
        "rgb_full": metrics(old_sid[..., :3], new_sid[..., :3]),
        "alpha_full": metrics(old_sid[..., 3:4], new_sid[..., 3:4]),
        "rgb_hdr_pixels": metrics(old_sid[..., :3], new_sid[..., :3], mask_hdr),
        "rgb_translucent_pixels": metrics(old_sid[..., :3], new_sid[..., :3], mask_alpha),
    }
    report = {
        "test": "M3.5 Standard SID historical 3.6 vs independent Blender 5 port",
        "upstream_commit": legacy["upstream_commit"],
        "blender_legacy": legacy["version"],
        "blender_port": port["version"],
        "input_sha256": legacy["input_sha256"],
        "roi": {"hdr_pixels": int(mask_hdr.sum()), "partial_alpha_pixels": int(mask_alpha.sum())},
        "passthrough": {"valid": passthrough_ok, "controls": passthrough},
        "denoised_cross_version": differences,
        "warning": "Cross-version OIDN/backend and compositor settings differ; measured pixel difference is not necessarily a porting bug.",
        "not_proven": ["Pixel equivalence", "OIDN backend equivalence", "Quality ranking on real scenes", "High/Super numerical parity"],
    }
    (output_dir / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    np.savez_compressed(
        output_dir / "difference_maps.npz",
        rgb_delta=np.asarray(new_sid[..., :3] - old_sid[..., :3], dtype=np.float32),
        alpha_delta=np.asarray(new_sid[..., 3:4] - old_sid[..., 3:4], dtype=np.float32),
        hdr_mask=mask_hdr, partial_alpha_mask=mask_alpha,
    )
    print(json.dumps(report, indent=2))
    if not passthrough_ok:
        raise ValueError("Raw compositor passthrough mismatch; do not interpret SID output differences")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--legacy", type=Path, required=True)
    p.add_argument("--port", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    compare(args.input, args.legacy, args.port, args.output)


if __name__ == "__main__":
    main()
