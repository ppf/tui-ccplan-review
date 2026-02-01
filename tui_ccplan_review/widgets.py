"""Custom Textual widgets."""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button, RadioSet, RadioButton


class CommentModal(ModalScreen[str]):
    """Modal for adding/editing comments."""

    CSS = """
    CommentModal {
        align: center middle;
    }

    #comment-dialog {
        width: 70;
        height: auto;
        border: round $primary;
        background: $surface;
        padding: 2 3;
    }

    #comment-dialog > Label {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
    }

    #comment-input {
        margin: 1 0 2 0;
        height: 3;
        border: round $primary-darken-1;
    }

    #comment-input:focus {
        border: round $primary;
    }

    #buttons {
        width: 100%;
        height: 3;
        layout: horizontal;
        align: right middle;
        margin-top: 1;
    }

    #buttons Button {
        margin-left: 1;
        min-width: 12;
        height: 3;
    }
    """

    def __init__(self, line_number: int = 1, existing_text: str = ""):
        super().__init__()
        self.line_number = line_number
        self.existing_text = existing_text
        self.is_edit = bool(existing_text)

    def compose(self) -> ComposeResult:
        """Compose modal."""
        title = f"Edit Comment - Line {self.line_number}" if self.is_edit else f"Add Comment - Line {self.line_number}"
        button_text = "Update" if self.is_edit else "Add"

        with Container(id="comment-dialog"):
            yield Label(title)
            yield Input(
                placeholder="Enter your comment...",
                value=self.existing_text,
                id="comment-input"
            )
            with Container(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button(button_text, variant="primary", id="add")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "add":
            comment_input = self.query_one("#comment-input", Input)
            comment_text = comment_input.value.strip()
            if comment_text:
                self.dismiss(comment_text)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "comment-input":
            # Trigger add button
            self.query_one("#add", Button).press()


class RejectModal(ModalScreen[str]):
    """Modal for rejecting a section."""

    CSS = """
    RejectModal {
        align: center middle;
    }

    #reject-dialog {
        width: 70;
        height: auto;
        border: round $primary;
        background: $surface;
        padding: 2 3;
    }

    #reject-dialog > Label {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
    }

    #reason-input {
        margin: 1 0 2 0;
        height: 3;
        border: round $primary-darken-1;
    }

    #reason-input:focus {
        border: round $primary;
    }

    #buttons {
        width: 100%;
        height: 3;
        layout: horizontal;
        align: right middle;
        margin-top: 1;
    }

    #buttons Button {
        margin-left: 1;
        min-width: 12;
        height: 3;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose modal."""
        with Container(id="reject-dialog"):
            yield Label("Reject Section - Provide Reason")
            yield Input(placeholder="Why does this need revision?", id="reason-input")
            with Container(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Reject", variant="error", id="reject")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "reject":
            input_widget = self.query_one("#reason-input", Input)
            reason = input_widget.value.strip()
            if reason:
                self.dismiss(reason)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "reason-input":
            self.query_one("#reject", Button).press()


class LineJumpModal(ModalScreen[int]):
    """Modal for jumping to a specific line."""

    CSS = """
    LineJumpModal {
        align: center middle;
    }

    #jump-dialog {
        width: 50;
        height: auto;
        border: round $primary;
        background: $surface;
        padding: 2 3;
    }

    #jump-dialog > Label {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
    }

    #line-input {
        margin: 1 0 2 0;
        height: 3;
        border: round $primary-darken-1;
    }

    #line-input:focus {
        border: round $primary;
    }

    #buttons {
        width: 100%;
        height: 3;
        layout: horizontal;
        align: right middle;
        margin-top: 1;
    }

    #buttons Button {
        margin-left: 1;
        min-width: 12;
        height: 3;
    }
    """

    def __init__(self, max_line: int):
        super().__init__()
        self.max_line = max_line

    def compose(self) -> ComposeResult:
        """Compose modal."""
        with Container(id="jump-dialog"):
            yield Label(f"Jump to Line (1-{self.max_line})")
            yield Input(placeholder="Line number", id="line-input")
            with Container(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Go", variant="primary", id="go")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "go":
            input_widget = self.query_one("#line-input", Input)
            try:
                line_num = int(input_widget.value.strip())
                if 1 <= line_num <= self.max_line:
                    self.dismiss(line_num)
            except ValueError:
                pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "line-input":
            self.query_one("#go", Button).press()


class CommentSelectorModal(ModalScreen[int]):
    """Modal for selecting which comment to edit/delete."""

    CSS = """
    CommentSelectorModal {
        align: center middle;
    }

    #selector-dialog {
        width: 80;
        max-height: 30;
        border: round $primary;
        background: $surface;
        padding: 2 3;
    }

    #selector-dialog > Label {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
    }

    .comment-option {
        margin: 0 0 1 0;
        padding: 1 2;
        background: $panel;
        border: round $primary-darken-1;
        width: 100%;
        text-align: left;
    }

    .comment-option:hover {
        background: $primary-darken-1;
        border: round $primary;
    }

    .comment-option:focus {
        background: $primary;
    }

    #buttons {
        width: 100%;
        height: 3;
        layout: horizontal;
        align: right middle;
        margin-top: 2;
    }

    #buttons Button {
        margin-left: 1;
        min-width: 12;
        height: 3;
    }
    """

    def __init__(self, comments: list, action: str = "select"):
        super().__init__()
        self.comments = comments
        self.action = action
        self.selected_index: Optional[int] = None

    def compose(self) -> ComposeResult:
        """Compose modal."""
        with Container(id="selector-dialog"):
            yield Label(f"Select comment to {self.action}:")
            for i, comment in enumerate(self.comments):
                btn = Button(
                    f"{i+1}. {comment.text[:50]}{'...' if len(comment.text) > 50 else ''}",
                    id=f"comment-{i}",
                    classes="comment-option"
                )
                yield btn
            with Container(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id and event.button.id.startswith("comment-"):
            # Extract index from button id
            index = int(event.button.id.split("-")[1])
            self.dismiss(index)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        # Check if it's a number key
        if event.key in "123456789":
            num = int(event.key)
            # Check if this number is valid (within range of comments)
            if 1 <= num <= len(self.comments):
                self.dismiss(num - 1)  # Convert 1-based to 0-based index
                event.prevent_default()
        elif event.key == "escape":
            self.dismiss(None)
            event.prevent_default()
