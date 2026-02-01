# TUI Claude Code Plan Review

Terminal TUI application for interactive Claude Code plan reviews.

## Features

- 📄 Syntax-highlighted markdown rendering
- 💬 Add inline comments (comments, questions, suggestions)
- ✅ Approve/reject sections with reasons
- 📋 Generate markdown review summaries
- 🔄 Auto-save review state
- ⌨️ Keyboard-driven workflow

## Installation

### Development Install

```bash
cd /Users/storm/PhpstormProjects/ppf/tui-ccplan-review
source venv/bin/activate
pip install -e .
```

### Usage

```bash
ccplan-review ~/.claude/plans/my-plan.md
```

Or:

```bash
plan-review-tui ~/.claude/plans/my-plan.md
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `c` | Add comment at current line |
| `a` | Approve current section |
| `r` | Reject current section (with reason) |
| `s` | Generate summary and copy to clipboard |
| `?` | Show help |
| `q` | Quit |
| `↑/↓` or `j/k` | Scroll |
| `Home/End` or `g/G` | Jump to top/bottom |

## Tmux Integration

**Quick setup:**
```bash
# 1. Add bin to PATH (add to ~/.zshrc)
export PATH="$PATH:/path/to/tui-ccplan-review/bin"

# 2. Add to ~/.config/tmux/tmux.conf
cat tmux-integration.conf >> ~/.config/tmux/tmux.conf

# 3. Reload tmux
tmux source-file ~/.config/tmux/tmux.conf
```

**Usage:**
- Press `<leader> + Shift + P` in tmux
- Plan opens in 90% popup
- Review, comment, approve/reject
- Press `s` to generate summary
- Summary copied to clipboard
- Paste back to Claude

**See [INSTALL.md](INSTALL.md) for detailed setup.**

## Review Workflow

1. Launch TUI with plan file
2. Navigate through plan sections
3. Add comments (`c` key)
4. Approve (`a`) or reject (`r`) sections
5. Generate summary (`s`) - copied to clipboard
6. Paste summary back into Claude conversation
7. Quit (`q`)

## Review Data Storage

Reviews are saved to `~/.claude/reviews/<plan-name>.json`:

```json
{
  "plan_path": "/path/to/plan.md",
  "comments": [
    {
      "line_number": 15,
      "text": "Should we add error handling?",
      "type": "question",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "sections": [
    {
      "start_line": 10,
      "end_line": 25,
      "section_name": "Technical Stack",
      "status": "approved"
    }
  ]
}
```

## Requirements

- Python 3.10+
- textual
- rich
- pyperclip

## License

MIT
