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


TERRACED = ROOT / "benchmarks" / "scenes" / "terraced_houses.blend"
TERRACED_SHA = "37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84"


def test_terraced_houses_heldout_mit_fixture_integrity():
    assert TERRACED.is_file()
    assert TERRACED.stat().st_size == 3044256
    sha = hashlib.sha256()
    with TERRACED.open("rb") as file:
        for part in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(part)
    assert sha.hexdigest() == TERRACED_SHA
    audit = json.loads(TERRACED.with_suffix(".audit.json").read_text())
    assert audit["sha256"] == TERRACED_SHA
    assert audit["source_url"].endswith(
        "36c46d3b49ea872f6039e07a5e4769b5f9443654/terraced-houses/terraced-house.blend"
    )
    assert audit["author"] == "Yunus Emre Karaman"
    assert audit["license"] == "MIT"
    assert audit["smoke_render_success"] is True
    assert audit["unbundled_missing_images"] == 0
