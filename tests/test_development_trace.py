"""Git-based regression tests for development-traceability discipline."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.check_development_trace import check_commits, get_anchor


def call(repo: Path, *args: str):
    p = subprocess.run(args, cwd=repo, check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.stdout.strip()


def commit(repo: Path, message: str, edits: dict[str, str]):
    for name, content in edits.items():
        f = repo / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    call(repo, "git", "add", ".")
    call(repo, "git", "commit", "-m", message)


@pytest.fixture
def local_repo(tmp_path):
    call(tmp_path, "git", "init", "-q")
    call(tmp_path, "git", "config", "user.email", "acd-test@example.test")
    call(tmp_path, "git", "config", "user.name", "ACD test")
    commit(tmp_path, "old unregulated code", {"addon/mod.py": "x = 1\n"})
    commit(tmp_path, "activate development protocol", {
        "docs/DEVELOPMENT_PROTOCOL.md": "# Protocol\n",
        "docs/ROADMAP.md": "M3\n",
        "STATUS.md": "M3 active\n",
        "docs/DECISION_LOG.md": "# Decisions\n",
    })
    return tmp_path


def test_historical_commits_and_anchor_exempt(local_repo):
    assert get_anchor(local_repo)
    assert check_commits(local_repo) == []


def test_code_change_requires_all_three_updates(local_repo):
    commit(local_repo, "change code only", {"addon/mod.py": "x = 2\n"})
    failures = check_commits(local_repo)
    assert len(failures) == 1
    assert "docs/ROADMAP.md" in failures[0]
    assert "STATUS.md" in failures[0]
    assert "docs/DECISION_LOG.md" in failures[0]


def test_documented_code_change_is_accepted(local_repo):
    commit(local_repo, "trace M3 change", {
        "addon/mod.py": "x = 2\n",
        "docs/ROADMAP.md": "M3 step 2\n",
        "STATUS.md": "M3 step 2 pending Blender\n",
        "docs/DECISION_LOG.md": "# Decisions\n\nDecision: next\n",
    })
    assert check_commits(local_repo) == []


def test_document_only_change_is_not_silently_exempt(local_repo):
    commit(local_repo, "research adjustment", {
        "docs/research.md": "new source\n",
        "docs/ROADMAP.md": "M3 update\n",
    })
    failures = check_commits(local_repo)
    assert len(failures) == 1
    assert "STATUS.md" in failures[0]
    assert "docs/DECISION_LOG.md" in failures[0]
