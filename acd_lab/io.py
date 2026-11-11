"""Explicit image interchange for the laboratory (linear float arrays only)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def read_arrays(path: str | Path, *, layer: str | None = None) -> dict[str, np.ndarray]:
    """Read .npy, .npz or a supported multi-layer Cycles .exr.

    EXR needs optional OpenEXR dependency. If the file has multiple view
    layers, pass the selected layer explicitly. All values are scene-linear.
    """
    file = Path(path)
    if file.suffix.lower() == ".exr":
        from .exr import read_exr
        return read_exr(file, layer=layer)
    if layer is not None:
        raise ValueError("--layer is only supported with .exr")
    if file.suffix.lower() == ".npy":
        return {"image": np.load(file, allow_pickle=False)}
    if file.suffix.lower() == ".npz":
        with np.load(file, allow_pickle=False) as archive:
            return {key: archive[key] for key in archive.files}
    raise ValueError("Unsupported format; provide .npy, .npz or .exr")


def write_report(path: str | Path, payload: dict) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
