"""Disk-oriented ACD localized comparison. Calls independent numerical primitives."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .core import compare_images, rgb
from .io import read_arrays
from .regions import aov_energy_masks, rectangle_mask, assess_regions, save_error_maps


def compare_regions_from_files(
    directory: str | Path,
    *,
    passes_file: str | Path | None = None,
    passes_layer: str | None = None,
    regions_file: str | Path | None = None,
    energy_fraction: float = 0.35,
    min_signal: float = 0.01,
    error_maps: str | Path | None = None,
) -> dict:
    """Compare all candidate EXRs in an ACD batch in fixed, auditable regions."""
    root = Path(directory)
    reference_file = root / "reference.exr"
    reference = read_arrays(reference_file)["image"]
    methods = (
        "Raw", "STANDARD", "HIGH", "SUPER", "STANDARD_emission_preserved",
        "HIGH_no_final", "SUPER_no_final", "HIGH_no_guides", "SUPER_no_guides",
        "STANDARD_no_guides",
        "HIGH_component_no_guides", "SUPER_component_no_guides",
        "HIGH_component_albedo", "SUPER_component_albedo",
        "HIGH_component_normal", "SUPER_component_normal",
    )
    candidates = {}
    for method in methods:
        candidate_path = root / ("acd_compare_" + method + ".exr")
        if candidate_path.is_file():
            candidates[method] = read_arrays(candidate_path)["image"]
    if not candidates:
        raise ValueError(f"{root}: no ACD candidate EXRs found")

    height, width = rgb(reference).shape[:2]
    masks = {"whole_image": np.ones((height, width), dtype=bool)}
    definitions = {"whole_image": "All pixels, unmasked"}

    if regions_file is not None:
        settings = json.loads(Path(regions_file).read_text(encoding="utf-8"))
        if not isinstance(settings, dict) or not isinstance(settings.get("regions"), list):
            raise ValueError("ROI JSON must contain a 'regions' array")
        for region in settings["regions"]:
            if not isinstance(region, dict) or not isinstance(region.get("name"), str):
                raise ValueError("Each region must have a name and normalized rectangle")
            name = region["name"]
            if not name or name in masks:
                raise ValueError(f"Duplicate or invalid region name: {name!r}")
            rect = region.get("rect_norm")
            if not isinstance(rect, list):
                raise ValueError(f"{name}: expected rect_norm list [x0,y0,x1,y1]")
            masks[name] = rectangle_mask((height, width), rect, normalized=True)
            definitions[name] = {"type": "manual_rect_norm", "rect": rect}

    if passes_file is not None:
        if passes_layer is None:
            metadata_file = root / "metadata.json"
            if metadata_file.is_file():
                info = json.loads(metadata_file.read_text(encoding="utf-8"))
                passes_layer = info.get("view_layer")
        raw = read_arrays(passes_file, layer=passes_layer)
        aov_masks = aov_energy_masks(raw, threshold=energy_fraction, min_signal=min_signal)
        for name, mask in aov_masks.items():
            tag = "aov_" + name
            if tag in masks:
                raise ValueError(f"Duplicate ROI or AOV name: {tag}")
            masks[tag] = mask
            definitions[tag] = {
                "type": "relative_aov_magnitude", "fraction_threshold": energy_fraction,
                "minimum_signal": min_signal, "warning": "Not a material/object ID mask"
            }

    result = assess_regions(reference, candidates, masks)
    result.update({
        "reference": str(reference_file),
        "candidates": sorted(candidates),
        "region_definitions": definitions,
        "warning": (
            "Metrics use a finite-spp reference; no automatic perceptual quality "
            "or material classification is implied. ROI coordinates use top-left origin."
        ),
    })
    if error_maps is not None:
        save_error_maps(str(error_maps), reference, candidates)
        result["error_maps_npz"] = str(error_maps)
    return result
