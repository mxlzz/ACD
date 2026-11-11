"""Deterministic linear HDR EXR inputs for M3.5, not a rendered quality dataset.

Create once, then both Blender versions read the *same exact files*.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def make_arrays(width: int = 96, height: int = 64):
    yy, xx = np.mgrid[0:height, 0:width]
    x = xx.astype(np.float32) / (width - 1)
    y = yy.astype(np.float32) / (height - 1)
    rng = np.random.default_rng(31057)

    edge = (x > 0.48).astype(np.float32)
    emission = ((x > 0.69) & (x < 0.87) & (y > 0.18) & (y < 0.52)).astype(np.float32)
    rgb = np.stack(
        [0.08 + 0.95 * x + 1.75 * edge + 7.0 * emission,
         0.10 + 0.7 * (1.0 - y) + 1.10 * edge + 3.0 * emission,
         0.06 + 0.55 * y + 0.65 * edge + 1.5 * emission],
        axis=-1,
    )
    noisy = np.clip(rgb + rng.normal(0, 0.11, rgb.shape), 0, None).astype(np.float32)
    # Partly transparent regions reveal any RGBA/compositor mapping differences.
    alpha = np.where(x < 0.30, 0.15, np.where(x < 0.72, 0.7, 1.0)).astype(np.float32)
    albedo = np.stack(
        [0.3 + 0.5 * x, 0.2 + 0.65 * y, 0.2 + 0.35 * (1.0 - x)],
        axis=-1,
    ).astype(np.float32)
    nx = (x - 0.5) * 0.6
    ny = (y - 0.5) * 0.6
    nz = np.sqrt(np.maximum(0.0, 1.0 - nx * nx - ny * ny))
    normal = np.stack([nx, ny, nz], axis=-1).astype(np.float32)
    return {
        "noisy": np.concatenate([noisy, alpha[..., None]], axis=-1),
        "albedo": np.concatenate([albedo, np.ones_like(alpha)[..., None]], axis=-1),
        "normal": np.concatenate([normal, np.ones_like(alpha)[..., None]], axis=-1),
    }


def save_fixture(directory: Path):
    import OpenEXR

    directory.mkdir(parents=True, exist_ok=True)
    images = make_arrays()
    manifests = {}
    for name, values in images.items():
        channels = {key: np.ascontiguousarray(values[..., i], dtype=np.float32)
                    for i, key in enumerate("RGBA")}
        path = directory / (name + ".exr")
        with OpenEXR.File({}, channels) as file:
            file.write(str(path))
        manifests[name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "shape": list(values.shape),
            "rgb_min": float(values[..., :3].min()),
            "rgb_max": float(values[..., :3].max()),
        }
    result = {
        "source": "deterministic synthetic linear HDR, seed 31057",
        "reference_type": "compositor fixture, NOT a converged Cycles reference",
        "width": 96,
        "height": 64,
        "files": manifests,
    }
    (directory / "input_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = save_fixture(args.output)
    assert result["files"]["noisy"]["rgb_max"] > 1.0
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
