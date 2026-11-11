"""Small, explicit interchange layer (EXR adapter remains future work)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def read_arrays(path: str | Path) -> dict[str, np.ndarray]:
    file = Path(path)
    if file.suffix.lower() == ".npy":
        return {"image": np.load(file, allow_pickle=False)}
    if file.suffix.lower() == ".npz":
        with np.load(file, allow_pickle=False) as archive:
            return {key: archive[key] for key in archive.files}
    raise ValueError("Unsupported format; provide .npy or .npz")


def write_report(path: str | Path, payload: dict) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
