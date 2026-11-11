"""Build stable-name installable ZIP for the single-file Blender addon.

Packaging is not evidence of functional validation. Use after Blender smoke CI.
"""
from __future__ import annotations

import ast
import zipfile
from pathlib import Path


def build(destination: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[1]
    source = root / "addon" / "acd_blender.py"
    metadata = next(
        item.value for item in ast.parse(source.read_text(encoding="utf-8")).body
        if isinstance(item, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in item.targets)
    )
    details = ast.literal_eval(metadata)
    if details["blender"][0] < 5:
        raise ValueError("Expected Blender 5 minimum version")
    output = destination or (root / "dist" / "ACD_Blender5_experimental.zip")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(source, "acd_blender.py")
    return output


if __name__ == "__main__":
    print(build())
