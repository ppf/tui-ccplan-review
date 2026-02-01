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

    def delete_comment_at_line(self, line: int) -> bool:
        """Delete first comment at specified line. Returns True if deleted."""
        for i, comment in enumerate(self.comments):
            if comment.line_number == line:
                self.comments.pop(i)
                return True
        return False

    def update_comment_at_line(self, line: int, new_text: str) -> bool:
        """Update first comment at specified line. Returns True if updated."""
        for comment in self.comments:
            if comment.line_number == line:
                comment.text = new_text
                comment.timestamp = datetime.now().isoformat()
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
        lines = [f"# Plan Review: {Path(self.plan_path).name}\n"]

        # Statistics
        approved = sum(1 for s in self.sections if s.status == "approved")
        rejected = sum(1 for s in self.sections if s.status == "rejected")
        pending = sum(1 for s in self.sections if s.status == "pending")

        lines.append("## Summary")
        if approved:
            lines.append(f"- ✅ {approved} section{'s' if approved != 1 else ''} approved")
        if rejected:
            lines.append(f"- ❌ {rejected} section{'s' if rejected != 1 else ''} needs revision")
        if pending:
            lines.append(f"- ⏳ {pending} section{'s' if pending != 1 else ''} pending")
        if self.comments:
            lines.append(f"- 💬 {len(self.comments)} comment{'s' if len(self.comments) != 1 else ''}")
        lines.append("")

        # Comments
        if self.comments:
            lines.append("## Comments\n")
            for comment in sorted(self.comments, key=lambda c: c.line_number):
                emoji = {"comment": "💬", "question": "❓", "suggestion": "💡"}.get(comment.type, "💬")
                lines.append(f"### Line {comment.line_number}")
                lines.append(f"{emoji} {comment.text}\n")

        # Approved sections
        approved_sections = [s for s in self.sections if s.status == "approved"]
        if approved_sections:
            lines.append("## Approved Sections\n")
            for section in approved_sections:
                lines.append(f"✅ {section.section_name}")
            lines.append("")

        # Rejected sections
        rejected_sections = [s for s in self.sections if s.status == "rejected"]
        if rejected_sections:
            lines.append("## Needs Revision\n")
            for section in rejected_sections:
                lines.append(f"### {section.section_name}")
                lines.append(f"❌ {section.reason or 'No reason provided'}\n")

        return "\n".join(lines)
