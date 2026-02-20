#!/usr/bin/env python3
"""Sync GitHub issues into local markdown snapshots under docs/issues."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List
from urllib.request import Request, urlopen


def _slugify(text: str) -> str:
    """Create a filesystem-safe slug from issue title text."""
    s = (text or "").strip().lower()

    # Strip issue prefix like "MS-1:" or "MS-1 -"
    s = re.sub(r"^\s*ms-?\d+[a-z]?\s*[:\-]\s*", "", s)

    # Remove parenthetical endings like "(Foundation)"
    s = re.sub(r"\s*\(.*?\)\s*$", "", s)

    # Replace separators/punctuation with spaces, then collapse to hyphens
    s = s.replace("&", " ")
    s = s.replace("—", " ")
    s = s.replace("–", " ")
    s = s.replace("/", " ")
    s = s.replace("|", " ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", "-", s).strip("-")

    if not s:
        return "untitled"
    return s[:90]


def _ms_part(title: str, number: int) -> str:
    m = re.search(r"ms-?(\d+[a-z]?)", (title or "").lower())
    if m:
        return f"ms{m.group(1)}"
    return f"issue-{number:03d}"


def _labels_text(issue: dict) -> str:
    labels = [l.get("name", "") for l in issue.get("labels", [])]
    return ", ".join(labels) if labels else "—"


def _assignees_text(issue: dict) -> str:
    assignees = [a.get("login", "") for a in issue.get("assignees", [])]
    return ", ".join(assignees) if assignees else "—"


@dataclass
class Issue:
    number: int
    title: str
    body: str
    state: str
    created_at: str
    updated_at: str
    labels: str
    assignees: str
    url: str

    @classmethod
    def from_api(cls, payload: dict) -> "Issue":
        return cls(
            number=payload["number"],
            title=payload.get("title", ""),
            body=(payload.get("body") or "_No description provided._").strip(),
            state=(payload.get("state") or "").lower().capitalize(),
            created_at=payload.get("created_at") or "",
            updated_at=payload.get("updated_at") or "",
            labels=_labels_text(payload),
            assignees=_assignees_text(payload),
            url=payload.get("html_url", ""),
        )

    def filename(self) -> str:
        return (
            f"issue-{self.number:03d}-{_ms_part(self.title, self.number)}-"
            f"{_slugify(self.title)}.md"
        )

    def render(self) -> str:
        return (
            f"# Issue #{self.number} — {self.title}\n\n"
            f"**State:** {self.state}\n"
            f"**Created:** {self.created_at}\n"
            f"**Updated:** {self.updated_at}\n"
            f"**Labels:** {self.labels}\n"
            f"**Assignees:** {self.assignees}\n"
            f"**Source:** {self.url}\n\n"
            f"---\n\n"
            f"{self.body}\n"
        )


def _fetch_issues(owner: str, repo: str, state: str) -> List[dict]:
    base = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = f"state={state}&per_page=100"
    url = f"{base}?{params}"

    issues: List[dict] = []
    while url:
        req = Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "rag-mmm-platform-issue-sync")

        with urlopen(req) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            issues.extend(payload)

            next_url = None
            links = resp.headers.get("Link", "")
            if links:
                for chunk in links.split(","):
                    if "rel=\"next\"" in chunk:
                        next_url = chunk.split(";")[0].strip()[1:-1]
                        break

        if next_url:
            page += 1
            url = next_url
        else:
            url = None

    # Filter out pull requests that GitHub returns in this endpoint.
    return [i for i in issues if not i.get("pull_request")]


def sync_issues(owner: str, repo: str, state: str, out_dir: Path, prune: bool = True) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = _fetch_issues(owner=owner, repo=repo, state=state)
    issue_paths = []

    for item in raw:
        issue = Issue.from_api(item)
        target = out_dir / issue.filename()
        target.write_text(issue.render(), encoding="utf-8")
        issue_paths.append(str(target))

    if prune:
        active = {Path(p).name for p in issue_paths}
        for existing in out_dir.glob("issue-*.md"):
            if existing.name.startswith("issue-"):
                # Keep only open-issues snapshots for this run.
                # Heuristic: this repo currently snapshots issues in this style only.
                if re.match(r"issue-\d{3}-", existing.name) and existing.name not in active:
                    existing.unlink()

    return len(issue_paths)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync GitHub issues to docs/issues")
    parser.add_argument("--owner", default="tkhongsap")
    parser.add_argument("--repo", default="rag-mmm-platform")
    parser.add_argument("--state", default="open", choices=["open", "closed", "all"])
    parser.add_argument("--out", default="docs/issues")
    parser.add_argument("--prune", action="store_true", help="Delete existing issue snapshots not found in fetch")
    args = parser.parse_args()

    synced = sync_issues(
        owner=args.owner,
        repo=args.repo,
        state=args.state,
        out_dir=Path(args.out),
        prune=args.prune,
    )

    print(f"Synced {synced} {args.state} issues into {args.out}")


if __name__ == "__main__":
    main()
