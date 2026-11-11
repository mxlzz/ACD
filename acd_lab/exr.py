"""Read linear Cycles multi-layer OpenEXR passes with explicit channel mapping.

Uses the OpenEXR 3.3+ File API (optional pip extra: acd-lab[exr]).
Reads each file into memory; not a streaming solution for large EXRs.
This module deliberately does not infer color management or sample counts.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from typing import Any

import numpy as np

# Canonical ACD key -> known Cycles pass label aliases (not position dependent).
# Both historic compact socket labels and newer full labels are accepted.
PASS_ALIASES = {
    "image": ("Combined", "Image", "Noisy Image"),
    "diffuse_direct": ("DiffDir", "Diffuse Direct", "DiffuseDirect"),
    "diffuse_indirect": ("DiffInd", "Diffuse Indirect", "DiffuseIndirect"),
    "diffuse_color": ("DiffCol", "Diffuse Color", "DiffuseColor"),
    "glossy_direct": ("GlossDir", "Glossy Direct", "GlossyDirect"),
    "glossy_indirect": ("GlossInd", "Glossy Indirect", "GlossyIndirect"),
    "glossy_color": ("GlossCol", "Glossy Color", "GlossyColor"),
    "transmission_direct": ("TransDir", "Transmission Direct", "TransmissionDirect"),
    "transmission_indirect": ("TransInd", "Transmission Indirect", "TransmissionIndirect"),
    "transmission_color": ("TransCol", "Transmission Color", "TransmissionColor"),
    "volume_direct": ("VolumeDir", "Volume Direct"),
    "volume_indirect": ("VolumeInd", "Volume Indirect"),
    "emission": ("Emit", "Emission"),
    "environment": ("Env", "Environment"),
    "denoising_albedo": ("Denoising Albedo", "DenoisingAlbedo"),
    "denoising_normal": ("Denoising Normal", "DenoisingNormal"),
    "depth": ("Depth", "Z"),
    "vector": ("Vector", "Speed"),
}

def _norm(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", label.casefold())


_LOOKUP = {
    _norm(alias): canonical
    for canonical, aliases in PASS_ALIASES.items() for alias in aliases
}

_COMPONENTS = frozenset(("R", "G", "B", "A", "X", "Y", "Z", "W"))


def _channel_identity(channel_name: str, part_name: str | None) -> tuple[str, str, str] | None:
    """Return view layer, Cycles pass label, component from EXR channel name."""
    tokens = channel_name.rsplit(".", 1)
    if len(tokens) == 2 and tokens[-1] in _COMPONENTS:
        base, component = tokens
    elif channel_name in _COMPONENTS:
        base, component = (part_name or "Combined"), channel_name
    else:
        return None
    path = base.split(".")
    if len(path) > 1:
        layer, pass_label = ".".join(path[:-1]), path[-1]
    else:
        layer, pass_label = (part_name or ""), path[0]
    return layer, pass_label, component


def read_exr(path: str | Path, *, layer: str | None = None) -> dict[str, np.ndarray]:
    """Return recognized raw Cycles passes in linear float32 without tone mapping.

    A multi-view-layer EXR requires selecting layer='ViewLayerName'.
    Unknown pass labels are ignored, *not silently mapped to other AOVs*.
    Missing RGB channels and multiple aliases for the same pass are errors.
    """
    try:
        import OpenEXR
    except ImportError as error:
        raise ImportError('Install EXR support: pip install "acd-lab[exr]"') from error

    source = str(path)
    entries: dict[tuple[str, str], dict[str, np.ndarray]] = defaultdict(dict)
    with OpenEXR.File(source, separate_channels=True) as image:
        for part in image.parts:
            part_name = str(part.header.get("name", "")) or None
            for name, channel in part.channels.items():
                identity = _channel_identity(str(name), part_name)
                if identity is None:
                    continue
                source_layer, pass_label, component = identity
                canonical = _LOOKUP.get(_norm(pass_label))
                if canonical is None:
                    continue
                key = (source_layer, canonical)
                if component in entries[key]:
                    raise ValueError(f"Duplicate EXR channel {key!r} component {component}")
                values = np.asarray(channel.pixels)
                if values.ndim != 2 or not np.issubdtype(values.dtype, np.number):
                    raise ValueError(f"Non-flat numerical EXR channel {name!r} is unsupported")
                entries[key][component] = np.asarray(values, dtype=np.float32)

    if not entries:
        raise ValueError("No recognized Cycles image passes; inspect the EXR channel labels")
    layers = sorted({key[0] for key in entries})
    if layer is None:
        if len(layers) != 1:
            raise ValueError(f"EXR contains multiple layers {layers}; choose --layer")
        layer = layers[0]
    if layer not in layers:
        raise ValueError(f"Layer {layer!r} not found; available: {layers}")

    result: dict[str, np.ndarray] = {}
    for (entry_layer, canonical), channels in entries.items():
        if entry_layer != layer:
            continue
        if canonical == "depth":
            if "Z" in channels:
                result[canonical] = channels["Z"][..., None]
            elif "R" in channels:
                result[canonical] = channels["R"][..., None]
            continue
        if canonical == "vector":
            # Motion vector encodings vary; expose only if all four exist.
            components = ("R", "G", "B", "A")
            if all(c in channels for c in components):
                result[canonical] = np.stack([channels[c] for c in components], axis=-1)
            continue
        components = ("X", "Y", "Z") if canonical == "denoising_normal" and "X" in channels else ("R", "G", "B")
        if not all(channel in channels for channel in components):
            raise ValueError(
                f"EXR {canonical} incomplete: expected {components}, got {sorted(channels)}"
            )
        triplet = np.stack([channels[c] for c in components], axis=-1)
        if canonical == "image" and "A" in channels:
            result["alpha"] = channels["A"][..., None]
        result[canonical] = triplet
    if "image" not in result:
        raise ValueError(f"Layer {layer!r} lacks raw Combined/Image RGB")
    if len({array.shape[:2] for array in result.values()}) != 1:
        raise ValueError("EXR passes have inconsistent dimensions")
    return result


def describe_exr(path: str | Path) -> dict[str, Any]:
    """Report raw EXR header/channel names without pretending to identify AOVs."""
    try:
        import OpenEXR
    except ImportError as error:
        raise ImportError('Install EXR support: pip install "acd-lab[exr]"') from error
    result: list[dict[str, Any]] = []
    with OpenEXR.File(str(path), separate_channels=True) as image:
        for part in image.parts:
            result.append({
                "part_name": str(part.header.get("name", "")),
                "width": int(part.width()),
                "height": int(part.height()),
                "channels": sorted(str(name) for name in part.channels),
            })
    return {"path": str(path), "parts": result}
