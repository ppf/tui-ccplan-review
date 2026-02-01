"""Main TUI application."""

import re
from pathlib import Path
from typing import Optional

import pyperclip
from rich.text import Text
from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Footer, Header, Static
from textual.binding import Binding

from .review import PlanReview
from .widgets import CommentModal, RejectModal, LineJumpModal


class PlanViewer(VerticalScroll):
    """Widget for viewing plan with annotations."""

    def __init__(self, plan_path: str, review: PlanReview):
        super().__init__()
        self.plan_path = plan_path
        self.review = review
        self.plan_content = ""
        self.current_line = 1
        self.current_section_index = 0
        self.sections: list[tuple[int, int, str]] = []
        self.total_lines = 0

    def on_mount(self) -> None:
        """Load and display plan."""
        self.load_plan()
        # Mount initial Static widget
        self.mount(Static(""))
        self.render_plan()

    def load_plan(self) -> None:
        """Load plan content."""
        with Path(self.plan_path).open() as f:
            self.plan_content = f.read()

        # Parse sections (lines starting with ##)
        lines = self.plan_content.split("\n")
        self.total_lines = len(lines)
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

    def jump_to_line(self, line_num: int) -> None:
        """Jump to a specific line."""
        if 1 <= line_num <= self.total_lines:
            self.current_line = line_num
            # Update current section based on line
            for idx, section in enumerate(self.sections):
                start, end, _ = section
                if start <= line_num <= end:
                    self.current_section_index = idx
                    break
            # Scroll to line
            self.scroll_to(y=max(0, line_num - 3), animate=True)

    def render_plan(self) -> None:
        """Render plan with Rich Text for better styling."""
        lines = self.plan_content.split("\n")

        # Get current section for highlighting
        current_section = self.get_current_section()
        current_start = current_section[0] if current_section else -1
        current_end = current_section[2] if current_section else -1

        # Build Rich Text with line numbers and backgrounds
        text = Text()
        line_num_width = len(str(len(lines)))

        for i, line in enumerate(lines, 1):
            # Check for section status
            section_status = ""
            is_current_section = False

            for section in self.review.sections:
                if section.start_line <= i <= section.end_line:
                    if section.status == "approved":
                        section_status = " ✅"
                    elif section.status == "rejected":
                        section_status = " ❌"
                    # Check if this is the current section
                    if section.start_line == current_start:
                        is_current_section = True
                    break

            # Line number
            line_num = f"{i:>{line_num_width}} "

            # Determine styles based on context
            is_current_line = (i == self.current_line)
            is_header = line.startswith("#")

            # Add line number
            if is_current_line:
                text.append(f"→{i:<{line_num_width}} ", style="bold yellow")
            else:
                text.append(line_num, style="dim")

            # Add content with appropriate styling
            if line.startswith("## "):
                # Section header
                if is_current_section:
                    text.append(line + section_status, style="bold white on blue")
                else:
                    text.append(line + section_status, style="bold cyan")
            elif line.startswith("# "):
                # Main title
                text.append(line, style="bold magenta")
            elif line.startswith("### "):
                # Subsection
                text.append(line, style="bold green")
            elif is_current_line:
                # Current line highlight
                text.append(line, style="on dark_blue")
            elif line.startswith("- ") or line.startswith("* "):
                # Bullet points
                text.append(line, style="cyan")
            elif line.startswith("**") or "**" in line:
                # Bold text
                text.append(line, style="bold")
            else:
                # Regular text
                text.append(line)

            text.append("\n")

            # Add comments after line
            line_comments = [c for c in self.review.comments if c.line_number == i]
            for comment in line_comments:
                emoji = {"comment": "💬", "question": "❓", "suggestion": "💡"}.get(comment.type, "💬")
                text.append(f"   {emoji} [Line {i}] {comment.text}\n", style="italic yellow")

        # Update display with Static widget
        self.query(Static).remove()
        static = Static(text)
        static.styles.height = "auto"
        self.mount(static)

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
        section = self.get_current_section()
        if section:
            self.scroll_to_section(section[0])
        return section

    def previous_section(self) -> Optional[tuple[int, int, str]]:
        """Move to previous section."""
        if not self.sections:
            return None
        self.current_section_index = max(self.current_section_index - 1, 0)
        section = self.get_current_section()
        if section:
            self.scroll_to_section(section[0])
        return section

    def scroll_to_section(self, line_num: int) -> None:
        """Scroll to make section visible."""
        # Estimate y position based on line number
        # Assuming ~1 line height per line (rough estimate)
        # Scroll to that position
        self.scroll_to(y=max(0, line_num - 3), animate=True)


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
        Binding("l", "jump_to_line", "Jump"),
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
        # Use current line
        current_line = self.viewer.current_line if self.viewer else 1

        def handle_comment(comment_text: Optional[str]) -> None:
            if comment_text:
                self.review.add_comment(current_line, comment_text, "comment")
                self.save_and_refresh()
                self.notify(f"💬 Comment added to line {current_line}")

        self.push_screen(CommentModal(current_line), handle_comment)

    def action_jump_to_line(self) -> None:
        """Jump to a specific line."""
        if not self.viewer:
            return

        max_line = self.viewer.total_lines

        def handle_jump(line_num: Optional[int]) -> None:
            if line_num and self.viewer:
                self.viewer.jump_to_line(line_num)
                self.viewer.render_plan()
                if self.status_bar:
                    self.status_bar.update_status()
                self.notify(f"→ Line {line_num}")

        self.push_screen(LineJumpModal(max_line), handle_jump)

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
        if not self.viewer:
            return

        old_index = self.viewer.current_section_index
        section = self.viewer.next_section()

        if section:
            self.viewer.render_plan()  # Re-render to update highlighting
            if self.status_bar:
                self.status_bar.update_status()

            # Only notify if we actually moved
            if self.viewer.current_section_index != old_index:
                _, _, name = section
                self.notify(f"→ {name}")
            elif self.viewer.current_section_index == len(self.viewer.sections) - 1:
                # At last section
                self.notify("Already at last section", severity="warning")

    def action_prev_section(self) -> None:
        """Navigate to previous section."""
        if not self.viewer:
            return

        old_index = self.viewer.current_section_index
        section = self.viewer.previous_section()

        if section:
            self.viewer.render_plan()  # Re-render to update highlighting
            if self.status_bar:
                self.status_bar.update_status()

            # Only notify if we actually moved
            if self.viewer.current_section_index != old_index:
                _, _, name = section
                self.notify(f"← {name}")
            elif self.viewer.current_section_index == 0:
                # At first section
                self.notify("Already at first section", severity="warning")

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
**Keyboard Shortcuts:**

- `l` - Jump to line (shows line picker)
- `c` - Add comment (defaults to current line)
- `a` - Approve current section
- `r` - Reject current section
- `n` - Next section
- `p` - Previous section
- `s` - Generate summary
- `q` - Quit

**Navigation:**
- `↑/↓` or `j/k` - Scroll
- `Home/End` or `g/G` - Top/Bottom

**Workflow:**
1. Press `l` to jump to a line
2. Press `c` to comment on that line
        """
        self.notify(help_text.strip(), title="Help", timeout=10)

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
