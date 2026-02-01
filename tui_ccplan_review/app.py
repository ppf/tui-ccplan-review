"""Main TUI application."""

import re
from pathlib import Path
from typing import Optional

import pyperclip
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Footer, Header, Markdown, Static
from textual.binding import Binding

from .review import PlanReview
from .widgets import CommentModal, RejectModal


class PlanViewer(VerticalScroll):
    """Widget for viewing plan with annotations."""

    def __init__(self, plan_path: str, review: PlanReview):
        super().__init__()
        self.plan_path = plan_path
        self.review = review
        self.plan_content = ""
        self.current_line = 0
        self.sections: list[tuple[int, int, str]] = []

    def on_mount(self) -> None:
        """Load and display plan."""
        self.load_plan()
        self.render_plan()

    def load_plan(self) -> None:
        """Load plan content."""
        with Path(self.plan_path).open() as f:
            self.plan_content = f.read()

        # Parse sections (lines starting with ##)
        lines = self.plan_content.split("\n")
        current_section: Optional[tuple[int, str]] = None

        for i, line in enumerate(lines, 1):
            if line.startswith("## "):
                if current_section:
                    # Close previous section
                    self.sections.append((current_section[0], i - 1, current_section[1]))
                current_section = (i, line[3:].strip())

        # Close final section
        if current_section:
            self.sections.append((current_section[0], len(lines), current_section[1]))

    def render_plan(self) -> None:
        """Render plan with annotations."""
        lines = self.plan_content.split("\n")
        content_parts = []

        for i, line in enumerate(lines, 1):
            # Check for section status
            section_status = ""
            for section in self.review.sections:
                if section.start_line <= i <= section.end_line:
                    if section.status == "approved":
                        section_status = " ✅"
                    elif section.status == "rejected":
                        section_status = " ❌"
                    break

            # Add line with status
            if line.startswith("## ") and section_status:
                content_parts.append(line + section_status)
            else:
                content_parts.append(line)

            # Add comments after line
            line_comments = [c for c in self.review.comments if c.line_number == i]
            for comment in line_comments:
                emoji = {"comment": "💬", "question": "❓", "suggestion": "💡"}.get(comment.type, "💬")
                content_parts.append(f"\n> {emoji} **[Line {i}]** {comment.text}\n")

        # Update markdown
        self.query(Markdown).remove()
        self.mount(Markdown("\n".join(content_parts)))

    def get_current_section(self) -> Optional[tuple[int, int, str]]:
        """Get section at current scroll position."""
        # Approximate line from scroll position
        # This is a simplification - in real impl would track actual line
        for section in self.sections:
            # Return first section for now
            return section
        return None


class StatusBar(Static):
    """Status bar showing review statistics."""

    def __init__(self, review: PlanReview):
        super().__init__()
        self.review = review

    def on_mount(self) -> None:
        """Initial render."""
        self.update_status()

    def update_status(self) -> None:
        """Update status display."""
        approved = sum(1 for s in self.review.sections if s.status == "approved")
        rejected = sum(1 for s in self.review.sections if s.status == "rejected")
        comments = len(self.review.comments)

        status_text = Text()
        status_text.append("📊 ", style="bold")
        status_text.append(f"Comments: {comments}  ", style="cyan")
        status_text.append(f"Approved: {approved}  ", style="green")
        status_text.append(f"Rejected: {rejected}", style="red")

        self.update(status_text)


class PlanReviewApp(App):
    """Plan review TUI application."""

    CSS = """
    StatusBar {
        height: 1;
        background: $boost;
        color: $text;
        padding: 0 1;
    }

    PlanViewer {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "add_comment", "Comment"),
        Binding("a", "approve_section", "Approve"),
        Binding("r", "reject_section", "Reject"),
        Binding("s", "generate_summary", "Summary"),
        Binding("?", "show_help", "Help"),
    ]

    def __init__(self, plan_path: str):
        super().__init__()
        self.plan_path = plan_path
        self.review_dir = Path.home() / ".claude" / "reviews"
        self.review = PlanReview.load(plan_path, self.review_dir)
        self.viewer: Optional[PlanViewer] = None
        self.status_bar: Optional[StatusBar] = None

    def compose(self) -> ComposeResult:
        """Compose app layout."""
        yield Header(show_clock=True)
        yield StatusBar(self.review)
        yield PlanViewer(self.plan_path, self.review)
        yield Footer()

    def on_mount(self) -> None:
        """Store widget references."""
        self.viewer = self.query_one(PlanViewer)
        self.status_bar = self.query_one(StatusBar)
        self.title = f"Plan Review: {Path(self.plan_path).name}"
        self.sub_title = "Interactive Plan Review Tool"

    def action_add_comment(self) -> None:
        """Add comment to current line."""
        def handle_comment(result: Optional[tuple[str, str]]) -> None:
            if result:
                text, comment_type = result
                # For MVP, use line 1 (would track actual line in full impl)
                self.review.add_comment(1, text, comment_type)
                self.save_and_refresh()

        self.push_screen(CommentModal(), handle_comment)

    def action_approve_section(self) -> None:
        """Approve current section."""
        section = self.viewer.get_current_section() if self.viewer else None
        if section:
            start, end, name = section
            self.review.update_section_status(start, end, name, "approved")
            self.save_and_refresh()
            self.notify(f"✅ Approved: {name}")

    def action_reject_section(self) -> None:
        """Reject current section with reason."""
        section = self.viewer.get_current_section() if self.viewer else None
        if not section:
            return

        def handle_rejection(reason: Optional[str]) -> None:
            if reason and section:
                start, end, name = section
                self.review.update_section_status(start, end, name, "rejected", reason)
                self.save_and_refresh()
                self.notify(f"❌ Rejected: {name}")

        self.push_screen(RejectModal(), handle_rejection)

    def action_generate_summary(self) -> None:
        """Generate and copy summary to clipboard."""
        summary = self.review.generate_summary()

        try:
            pyperclip.copy(summary)
            self.notify("📋 Summary copied to clipboard!", severity="information")
        except Exception as e:
            self.notify(f"⚠️ Failed to copy: {e}", severity="error")

            # Save to file as fallback
            summary_file = Path(self.plan_path).with_suffix(".review.md")
            summary_file.write_text(summary)
            self.notify(f"💾 Saved to: {summary_file}", severity="information")

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
**Keyboard Shortcuts:**

- `c` - Add comment
- `a` - Approve section
- `r` - Reject section
- `s` - Generate summary
- `q` - Quit

**Navigation:**
- `↑/↓` or `j/k` - Scroll
- `Home/End` or `g/G` - Top/Bottom
        """
        self.notify(help_text.strip(), title="Help", timeout=8)

    def save_and_refresh(self) -> None:
        """Save review and refresh display."""
        self.review.save(self.review_dir)
        if self.viewer:
            self.viewer.render_plan()
        if self.status_bar:
            self.status_bar.update_status()


def run_app(plan_path: str) -> None:
    """Run the plan review app."""
    app = PlanReviewApp(plan_path)
    app.run()
