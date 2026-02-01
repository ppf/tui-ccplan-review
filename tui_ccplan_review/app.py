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
        self.current_section_index = 0
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

        # Get current section for highlighting
        current_section = self.get_current_section()
        current_start = current_section[0] if current_section else -1

        for i, line in enumerate(lines, 1):
            # Check for section status
            section_status = ""
            is_current = False

            for section in self.review.sections:
                if section.start_line <= i <= section.end_line:
                    if section.status == "approved":
                        section_status = " ✅"
                    elif section.status == "rejected":
                        section_status = " ❌"
                    # Check if this is the current section
                    if section.start_line == current_start:
                        is_current = True
                    break

            # Add line with status and highlighting
            if line.startswith("## "):
                if is_current:
                    # Highlight current section
                    content_parts.append(f"**>>> {line}{section_status} <<<**")
                elif section_status:
                    content_parts.append(line + section_status)
                else:
                    content_parts.append(line)
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
        if not self.sections:
            return None
        # Return section at current index
        if 0 <= self.current_section_index < len(self.sections):
            return self.sections[self.current_section_index]
        return None

    def next_section(self) -> Optional[tuple[int, int, str]]:
        """Move to next section."""
        if not self.sections:
            return None
        self.current_section_index = min(
            self.current_section_index + 1,
            len(self.sections) - 1
        )
        return self.get_current_section()

    def previous_section(self) -> Optional[tuple[int, int, str]]:
        """Move to previous section."""
        if not self.sections:
            return None
        self.current_section_index = max(self.current_section_index - 1, 0)
        return self.get_current_section()


class StatusBar(Static):
    """Status bar showing review statistics."""

    def __init__(self, review: PlanReview, viewer: Optional["PlanViewer"] = None):
        super().__init__()
        self.review = review
        self.viewer = viewer

    def on_mount(self) -> None:
        """Initial render."""
        self.update_status()

    def update_status(self) -> None:
        """Update status display."""
        approved = sum(1 for s in self.review.sections if s.status == "approved")
        rejected = sum(1 for s in self.review.sections if s.status == "rejected")
        comments = len(self.review.comments)

        status_text = Text()

        # Show current section
        if self.viewer:
            section = self.viewer.get_current_section()
            if section:
                _, _, name = section
                idx = self.viewer.current_section_index + 1
                total = len(self.viewer.sections)
                status_text.append(f"📍 [{idx}/{total}] {name}  ", style="bold yellow")

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
        Binding("n", "next_section", "Next"),
        Binding("p", "prev_section", "Prev"),
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
        self.viewer = PlanViewer(self.plan_path, self.review)
        self.status_bar = StatusBar(self.review, self.viewer)
        yield self.status_bar
        yield self.viewer
        yield Footer()

    def on_mount(self) -> None:
        """Store widget references."""
        self.title = f"Plan Review: {Path(self.plan_path).name}"
        self.sub_title = "Interactive Plan Review Tool"
        # Trigger initial status update
        if self.status_bar:
            self.status_bar.update_status()

    def action_add_comment(self) -> None:
        """Add comment to current line."""
        # Get default line from current section
        default_line = 1
        if self.viewer:
            section = self.viewer.get_current_section()
            if section:
                default_line = section[0]  # Use section start line

        def handle_comment(result: Optional[tuple[int, str, str]]) -> None:
            if result:
                line_num, text, comment_type = result
                self.review.add_comment(line_num, text, comment_type)
                self.save_and_refresh()

        self.push_screen(CommentModal(default_line), handle_comment)

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

    def action_next_section(self) -> None:
        """Navigate to next section."""
        if self.viewer:
            section = self.viewer.next_section()
            if section:
                self.viewer.render_plan()  # Re-render to update highlighting
                if self.status_bar:
                    self.status_bar.update_status()
                _, _, name = section
                self.notify(f"→ {name}")

    def action_prev_section(self) -> None:
        """Navigate to previous section."""
        if self.viewer:
            section = self.viewer.previous_section()
            if section:
                self.viewer.render_plan()  # Re-render to update highlighting
                if self.status_bar:
                    self.status_bar.update_status()
                _, _, name = section
                self.notify(f"← {name}")

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
**Keyboard Shortcuts:**

- `c` - Add comment (with line number)
- `a` - Approve current section
- `r` - Reject current section
- `n` - Next section
- `p` - Previous section
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
