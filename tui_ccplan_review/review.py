"""Review data models and persistence."""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional


@dataclass
class Comment:
    """Comment on a specific line."""
    line_number: int
    text: str
    timestamp: str
    type: Literal["comment", "question", "suggestion"] = "comment"


@dataclass
class SectionReview:
    """Review status for a section."""
    start_line: int
    end_line: int
    section_name: str
    status: Literal["approved", "rejected", "pending"] = "pending"
    reason: Optional[str] = None


@dataclass
class PlanReview:
    """Complete review data for a plan."""
    plan_path: str
    comments: list[Comment] = field(default_factory=list)
    sections: list[SectionReview] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def save(self, review_dir: Path) -> None:
        """Save review to JSON file."""
        review_dir.mkdir(parents=True, exist_ok=True)
        plan_name = Path(self.plan_path).stem
        review_file = review_dir / f"{plan_name}.json"

        self.updated_at = datetime.now().isoformat()
        with review_file.open("w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, plan_path: str, review_dir: Path) -> "PlanReview":
        """Load review from JSON file or create new."""
        plan_name = Path(plan_path).stem
        review_file = review_dir / f"{plan_name}.json"

        if review_file.exists():
            with review_file.open() as f:
                data = json.load(f)

            # Convert dicts back to dataclasses
            data["comments"] = [Comment(**c) for c in data["comments"]]
            data["sections"] = [SectionReview(**s) for s in data["sections"]]
            return cls(**data)

        return cls(plan_path=plan_path)

    def add_comment(self, line: int, text: str, comment_type: str = "comment") -> None:
        """Add a comment to the review."""
        self.comments.append(Comment(
            line_number=line,
            text=text,
            timestamp=datetime.now().isoformat(),
            type=comment_type  # type: ignore
        ))

    def get_comments_at_line(self, line: int) -> list[Comment]:
        """Get all comments at a specific line."""
        return [c for c in self.comments if c.line_number == line]

    def delete_comment_at_line(self, line: int, index: int = 0) -> bool:
        """Delete comment at specified line and index. Returns True if deleted."""
        line_comments = [c for c in self.comments if c.line_number == line]
        if index < len(line_comments):
            self.comments.remove(line_comments[index])
            return True
        return False

    def update_comment_at_line(self, line: int, new_text: str, index: int = 0) -> bool:
        """Update comment at specified line and index. Returns True if updated."""
        line_comments = [c for c in self.comments if c.line_number == line]
        if index < len(line_comments):
            line_comments[index].text = new_text
            line_comments[index].timestamp = datetime.now().isoformat()
            return True
        return False

    def update_section_status(
        self,
        start: int,
        end: int,
        name: str,
        status: Literal["approved", "rejected", "pending"],
        reason: Optional[str] = None
    ) -> None:
        """Update or add section review status."""
        # Find existing section or create new
        for section in self.sections:
            if section.start_line == start and section.end_line == end:
                section.status = status
                section.reason = reason
                return

        self.sections.append(SectionReview(
            start_line=start,
            end_line=end,
            section_name=name,
            status=status,
            reason=reason
        ))

    def generate_summary(self) -> str:
        """Generate markdown summary of review."""
        plan_name = Path(self.plan_path).name
        lines = [f"# Plan Review: {plan_name}\n"]

        sections_sorted = sorted(self.sections, key=lambda s: (s.start_line, s.end_line, s.section_name))

        def section_for_line(line_number: int) -> Optional[SectionReview]:
            # Prefer the smallest section that contains the line (most specific).
            containing = [s for s in sections_sorted if s.start_line <= line_number <= s.end_line]
            if containing:
                return min(containing, key=lambda s: (s.end_line - s.start_line, s.start_line))
            # Otherwise, use the latest section that starts before the line.
            previous = [s for s in sections_sorted if s.start_line <= line_number]
            if previous:
                return max(previous, key=lambda s: s.start_line)
            return None

        plan_lines: dict[int, str] = {}
        try:
            raw = Path(self.plan_path).read_text(encoding="utf-8").splitlines()
            plan_lines = {i + 1: line for i, line in enumerate(raw)}
        except (OSError, UnicodeDecodeError):
            plan_lines = {}

        def line_excerpt(line_number: int, limit: int = 120) -> Optional[str]:
            text = plan_lines.get(line_number)
            if not text:
                return None
            cleaned = text.rstrip()
            if len(cleaned) <= limit:
                return cleaned
            return f"{cleaned[:limit].rstrip()}..."

        # Statistics
        approved = sum(1 for s in self.sections if s.status == "approved")
        rejected = sum(1 for s in self.sections if s.status == "rejected")
        pending = sum(1 for s in self.sections if s.status == "pending")

        lines.append("## Summary")
        lines.append(f"- File: `{plan_name}`")
        lines.append(f"- Sections: ✅ {approved} approved, ❌ {rejected} needs revision, ⏳ {pending} pending")
        lines.append(f"- Comments: 💬 {len(self.comments)}")
        lines.append("")

        # Action items (quick to scan for another agent)
        rejected_sections = [s for s in sections_sorted if s.status == "rejected"]
        if rejected_sections:
            lines.append("## Action Items\n")
            for section in rejected_sections:
                reason = section.reason or "No reason provided"
                lines.append(
                    f"- Fix **{section.section_name}** (Lines {section.start_line}-{section.end_line}): {reason}"
                )
            lines.append("")

        # Comments (grouped by line, include section + excerpt when available)
        if self.comments:
            lines.append("## Comments\n")
            comments_by_line: dict[int, list[Comment]] = {}
            for comment in self.comments:
                comments_by_line.setdefault(comment.line_number, []).append(comment)

            for line_number in sorted(comments_by_line.keys()):
                section = section_for_line(line_number)
                section_label = f": {section.section_name}" if section else ""
                excerpt = line_excerpt(line_number)
                excerpt_label = f" — `{excerpt}`" if excerpt else ""
                lines.append(f"### Line {line_number}{section_label}{excerpt_label}")

                for i, comment in enumerate(comments_by_line[line_number], start=1):
                    emoji = {"comment": "💬", "question": "❓", "suggestion": "💡"}.get(comment.type, "💬")
                    prefix = f"{i}." if len(comments_by_line[line_number]) > 1 else "-"
                    lines.append(f"{prefix} {emoji} {comment.text}")
                lines.append("")

        # Sections (include line ranges for easy verification)
        approved_sections = [s for s in sections_sorted if s.status == "approved"]
        pending_sections = [s for s in sections_sorted if s.status == "pending"]

        if approved_sections:
            lines.append("## Approved Sections\n")
            for section in approved_sections:
                lines.append(f"- ✅ {section.section_name} (Lines {section.start_line}-{section.end_line})")
            lines.append("")

        if rejected_sections:
            lines.append("## Needs Revision\n")
            for section in rejected_sections:
                reason = section.reason or "No reason provided"
                lines.append(f"### {section.section_name} (Lines {section.start_line}-{section.end_line})")
                lines.append(f"❌ {reason}\n")

        if pending_sections:
            lines.append("## Pending Sections\n")
            for section in pending_sections:
                lines.append(f"- ⏳ {section.section_name} (Lines {section.start_line}-{section.end_line})")
            lines.append("")

        # Machine-readable payload (easy for Claude/Codex to parse)
        payload = {
            "plan": plan_name,
            "generated_at": datetime.now().isoformat(),
            "stats": {"approved": approved, "rejected": rejected, "pending": pending, "comments": len(self.comments)},
            "sections": [
                {
                    "name": s.section_name,
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "status": s.status,
                    "reason": s.reason,
                }
                for s in sections_sorted
            ],
            "comments": [
                {
                    "line": c.line_number,
                    "type": c.type,
                    "text": c.text,
                    "section": (section_for_line(c.line_number).section_name if section_for_line(c.line_number) else None),
                    "line_excerpt": line_excerpt(c.line_number),
                }
                for c in sorted(self.comments, key=lambda c: (c.line_number, c.timestamp))
            ],
        }
        lines.append("## Machine Readable\n")
        lines.append("```json")
        lines.append(json.dumps(payload, indent=2, ensure_ascii=True))
        lines.append("```")

        return "\n".join(lines)
