"""Integrity of the permitted and vendored public Blender Cycles fixture."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "benchmarks" / "scenes" / "cozy_kitchen.blend"
AUDIT = SCENE.with_suffix(".audit.json")
SHA256 = "5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395"


def test_public_cozy_kitchen_fixture_is_pinned():
    assert SCENE.is_file(), "Cozy Kitchen public testdata should be versioned in Git"
    assert SCENE.stat().st_size == 7685702
    hasher = hashlib.sha256()
    with SCENE.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(block)
    assert hasher.hexdigest() == SHA256


def test_public_fixture_provenance_is_explicit():
    report = json.loads(AUDIT.read_text())
    assert report["sha256"] == SHA256
    assert report["size_bytes"] == 7685702
    assert report["source_url"] == (
        "https://download.blender.org/demo/splash/blender-3.5-splash.blend"
    )
    assert report["author"] == "Nicole Morena"
    assert "CC BY-SA" in report["licence"]
    assert report["smoke_render_success"] is True
    assert report["unbundled_missing_images"] == 0
    assert report["external_blend_libraries"] == 0
