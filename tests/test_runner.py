from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.run_scene_benchmark import parser, validate, make_command, main


@pytest.fixture
def paths(tmp_path):
    blender = tmp_path / "blender executable"
    blender.write_bytes(b"fake")
    scene = tmp_path / "scene.blend"
    scene.write_bytes(b"blend")
    return blender, scene, tmp_path / "bench"


def args(paths, *extra):
    blender, scene, output = paths
    return parser().parse_args(["--blender", str(blender), "--blend", str(scene),
                                "--output", str(output), *extra])


def test_dry_run_builds_safe_blender_command(paths, capsys):
    options = args(paths, "--samples", "64", "--device", "OPTIX", "--dry-run")
    command, env = make_command(options)
    assert command[1] == "-b"
    assert command[2].endswith("scene.blend")
    assert "--python-exit-code" in command
    assert env["ACD_DEVICE"] == "OPTIX"
    assert env["ACD_CAPTURE_AOV"] == "1"
    assert main(["--blender", str(paths[0]), "--blend", str(paths[1]),
                 "--output", str(paths[2]), "--dry-run"]) == 0
    assert "Blender:" in capsys.readouterr().out
    assert not paths[2].exists()


def test_preserve_scene_size_if_unspecified(paths):
    _, env = make_command(args(paths))
    assert "ACD_WIDTH" not in env and "ACD_HEIGHT" not in env


def test_prevent_overwriting_existing_directory(paths):
    paths[2].mkdir()
    (paths[2] / "metrics.json").write_text("existing")
    with pytest.raises(ValueError, match="not empty"):
        validate(args(paths))


def test_reference_seeds_must_be_independent(paths):
    with pytest.raises(ValueError, match="Reference seed"):
        validate(args(paths, "--seed", "8819"))
    with pytest.raises(ValueError, match="unique"):
        validate(args(paths, "--extra-seeds", "5,5"))


def test_method_set_required_for_batch_report(paths):
    with pytest.raises(ValueError, match="requires"):
        validate(args(paths, "--methods", "STANDARD"))


def test_no_unexpected_shell_invocations(paths, monkeypatch):
    seen = []
    def fake_run(cmd, **kw):
        seen.append((cmd,kw))
        raise RuntimeError("render stub")
    monkeypatch.setattr("subprocess.run", fake_run)
    with pytest.raises(RuntimeError, match="stub"):
        main(["--blender", str(paths[0]), "--blend", str(paths[1]),
              "--output", str(paths[2])])
    assert seen[0][1]["check"] is True
    assert isinstance(seen[0][0], list)
