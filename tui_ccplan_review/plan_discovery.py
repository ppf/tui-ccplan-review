"""Plan discovery helpers for Claude and Codex plans."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


CLAUDE_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
DEFAULT_CLAUDE_PLANS_DIR = Path.home() / ".claude" / "plans"


@dataclass(frozen=True)
class PlanInfo:
    """Plan metadata for display and selection."""

    path: Path
    source: str
    mtime: float

    @property
    def filename(self) -> str:
        return self.path.name


def _warn(message: str) -> None:
    print(message, file=sys.stderr)


def resolve_claude_plans_dir(cwd: Path) -> Path:
    """Resolve Claude plans directory from settings.json or fallback."""
    if not CLAUDE_SETTINGS_PATH.exists():
        return DEFAULT_CLAUDE_PLANS_DIR

    try:
        content = CLAUDE_SETTINGS_PATH.read_text()
    except OSError as exc:
        print(
            f"Error: Unable to read settings file: {CLAUDE_SETTINGS_PATH} ({exc})",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        print(
            f"Error: Invalid JSON in settings file: {CLAUDE_SETTINGS_PATH} ({exc})",
            file=sys.stderr,
        )
        sys.exit(1)

    if not isinstance(data, dict):
        return DEFAULT_CLAUDE_PLANS_DIR

    value = data.get("plansDirectory")
    if value is None:
        return DEFAULT_CLAUDE_PLANS_DIR
    if not isinstance(value, str) or not value.strip():
        _warn(
            f"Warning: Invalid plansDirectory in {CLAUDE_SETTINGS_PATH}; "
            "falling back to defaults."
        )
        return DEFAULT_CLAUDE_PLANS_DIR

    expanded = os.path.expandvars(os.path.expanduser(value))
    path = Path(expanded)
    if not path.is_absolute():
        path = cwd / path
    try:
        path = path.resolve()
    except OSError:
        path = path.absolute()
    return path


def find_codex_plans_dir(cwd: Path) -> Optional[Path]:
    """Find nearest parent .codex/plans directory, starting from cwd."""
    for base in [cwd, *cwd.parents]:
        candidate = base / ".codex" / "plans"
        if candidate.is_dir():
            return candidate
    return None


def _collect_from_dir(plans_dir: Path, source: str) -> list[PlanInfo]:
    if not plans_dir.exists():
        _warn(f"Warning: Plans directory not found: {plans_dir}")
        return []
    if not plans_dir.is_dir():
        _warn(f"Warning: Plans path is not a directory: {plans_dir}")
        return []

    plans: list[PlanInfo] = []
    try:
        with os.scandir(plans_dir) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue
                if not entry.name.lower().endswith(".md"):
                    continue
                try:
                    stat = entry.stat()
                except OSError as exc:
                    _warn(
                        f"Warning: Unable to stat plan file: {entry.path} ({exc})"
                    )
                    continue
                plans.append(PlanInfo(Path(entry.path), source, stat.st_mtime))
    except OSError as exc:
        _warn(f"Warning: Unable to read plans directory: {plans_dir} ({exc})")
        return []

    return plans


def collect_plans(cwd: Path) -> tuple[list[PlanInfo], list[str]]:
    """Collect plans from Claude and Codex sources."""
    checked: list[str] = []
    plans: list[PlanInfo] = []

    claude_dir = resolve_claude_plans_dir(cwd)
    checked.append(f"Claude: {claude_dir}")
    plans.extend(_collect_from_dir(claude_dir, "Claude"))

    codex_dir = find_codex_plans_dir(cwd)
    if codex_dir is None:
        _warn(
            "Warning: Codex plans directory not found (searched upward from "
            "current directory)."
        )
        checked.append("Codex: (not found)")
    else:
        checked.append(f"Codex: {codex_dir}")
        plans.extend(_collect_from_dir(codex_dir, "Codex"))

    return plans, checked


def _format_timestamp(mtime: float) -> str:
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")


def _print_no_plans(checked: Iterable[str]) -> None:
    print(
        "Error: No plan files found in Claude or Codex plans directories.",
        file=sys.stderr,
    )
    print("Checked:", file=sys.stderr)
    for item in checked:
        print(f"  - {item}", file=sys.stderr)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Discover Claude and Codex plan files."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--latest",
        action="store_true",
        help="Print the most recent plan file path.",
    )
    mode.add_argument(
        "--list",
        action="store_true",
        help="List plans for selection.",
    )
    args = parser.parse_args(argv)

    cwd = Path.cwd()
    plans, checked = collect_plans(cwd)
    if not plans:
        _print_no_plans(checked)
        return 1

    plans.sort(key=lambda item: item.mtime, reverse=True)

    if args.latest:
        print(plans[0].path)
        return 0

    for plan in plans:
        print(
            f"{_format_timestamp(plan.mtime)}\t{plan.source}\t"
            f"{plan.filename}\t{plan.path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
