"""Custom Textual widgets."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button, RadioSet, RadioButton


class CommentModal(ModalScreen[tuple[str, str]]):
    """Modal for adding comments."""

    CSS = """
    CommentModal {
        align: center middle;
    }

    #comment-dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #comment-input {
        margin: 1 0;
    }

    #comment-type {
        margin: 1 0;
    }

    #buttons {
        width: 100%;
        height: auto;
        align: right middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose modal."""
        with Container(id="comment-dialog"):
            yield Label("Add Comment")
            yield Input(placeholder="Enter your comment...", id="comment-input")
            with RadioSet(id="comment-type"):
                yield RadioButton("💬 Comment", value=True)
                yield RadioButton("❓ Question")
                yield RadioButton("💡 Suggestion")
            with Container(id="buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Add", variant="primary", id="add")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "add":
            input_widget = self.query_one("#comment-input", Input)
            radio = self.query_one("#comment-type", RadioSet)

            comment_text = input_widget.value.strip()
            if not comment_text:
                return

            # Determine comment type
            pressed_index = radio.pressed_index
            comment_type = ["comment", "question", "suggestion"][pressed_index]

            self.dismiss((comment_text, comment_type))

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
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #reason-input {
        margin: 1 0;
    }

    #buttons {
        width: 100%;
        height: auto;
        align: right middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
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
