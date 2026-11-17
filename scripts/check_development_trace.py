"""Check traceability per new commit, not only the final PR diff.

This gate is deliberately narrow. It proves that documentation was updated
with each commit; it cannot prove the contents are accurate or on strategy.

Historical commits are excluded: the first commit that *adds* the protocol
is the policy activation anchor. Future non-merge commits must update all
three canonical files, including documentation-only changes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROTOCOL = "docs/DEVELOPMENT_PROTOCOL.md"
REQUIRED = {"docs/ROADMAP.md", "STATUS.md", "docs/DECISION_LOG.md"}

# Two already-published documentation-only commits accidentally lacked
# canonical trace updates. Preserve their Git history and enumerate exact SHAs
# and exact path changes; there is NO broad waiver for later commits.
EXACT_HISTORICAL_LAPSES = {
    "d6edc548bf6996c053e7b2e465cfca9a9a902e9a": {
        "docs/experiments/E0049.md", "docs/experiments/E0051_HANDOFF.md",
    },
    "204cc9d71cffca1e359e09fcc0cc21fccc6d0200": {
        "docs/experiments/E0051_HANDOFF.md",
        "docs/experiments/B1_PUBLIC_CORPUS_RESTART.md",
    },
}


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", *args], cwd=repo, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if p.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


def get_anchor(repo: Path) -> str:
    # Reverse chronological; the last matching addition is the original
    # introduction of the tracked file, not the latest edit.
    anchors = git(repo, "log", "--full-history", "--diff-filter=A",
                  "--format=%H", "--", PROTOCOL).splitlines()
    if not anchors:
        raise RuntimeError(
            "Development protocol has no introduction commit in git history"
        )
    return anchors[-1]


def check_commits(repo: Path) -> list[str]:
    anchor = get_anchor(repo)
    git(repo, "merge-base", "--is-ancestor", anchor, "HEAD")
    errors = []
    commits = git(repo, "rev-list", "--reverse", f"{anchor}..HEAD").splitlines()
    for commit in commits:
        parents = git(repo, "rev-list", "--parents", "-n", "1", commit).split()
        if len(parents) > 2:
            # GitHub's PR merge commit has more than one parent; both histories
            # have already been assessed separately after the anchor.
            continue
        changed = set(git(repo, "diff-tree", "--no-commit-id",
                          "--name-only", "-r", commit).splitlines())
        if not changed:
            continue
        missing = sorted(REQUIRED - changed)
        if missing:
            if (commit in EXACT_HISTORICAL_LAPSES
                    and changed == EXACT_HISTORICAL_LAPSES[commit]
                    and set(missing) == REQUIRED):
                print(f"Explicit historical trace lapse documented: {commit[:12]}")
                continue
            summary = git(repo, "show", "-s", "--format=%s", commit)
            errors.append(
                f"{commit[:12]} {summary!r}: missing updates "
                f"to {', '.join(missing)}"
            )
    return errors


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    try:
        errors = check_commits(repo)
    except RuntimeError as exc:
        print(f"Development alignment check could not run: {exc}", file=sys.stderr)
        return 2
    if errors:
        print(
            "Development traceability gate FAILED. Every new non-merge commit "
            "must update ROADMAP, STATUS and DECISION_LOG:\n"
            + "\n".join("  - " + err for err in errors),
            file=sys.stderr,
        )
        return 1
    print("Development traceability gate PASSED for post-policy commits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
