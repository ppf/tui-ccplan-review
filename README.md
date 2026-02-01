# TUI Claude Code Plan Review

Interactive terminal TUI for reviewing Claude Code implementation plans with rich features and tmux integration.

## Features

- 📄 **Rich text rendering** with syntax highlighting
- 🔢 **Line numbers** with current line indicator (→)
- 📍 **Section navigation** with visual highlighting
- 💬 **Inline comments** - add, edit, delete (multiple per line supported)
- ✅ **Approve/reject sections** with optional reasons
- 📋 **Summary generation** - auto-copy to clipboard
- 🔄 **Auto-save** - review state persists across sessions
- 🎨 **Theme support** - respects Textual theme (dracula, monokai, nord, etc.)
- ⚡ **Tmux popup** - one-key launch from tmux
- ⌨️ **Keyboard-driven** - fast, efficient workflow

## Why This Tool?

When Claude Code generates implementation plans, you need a fast way to:
- **Review** sections for feasibility and clarity
- **Comment** on specific lines with questions or suggestions
- **Approve/reject** entire sections with reasons
- **Generate feedback** that Claude can incorporate

This TUI provides a **keyboard-driven, terminal-native workflow** that integrates seamlessly with your existing tmux setup. No context switching, no browser tabs—just press a key and start reviewing.

## Installation

### Development Install

```bash
# Clone the repository
git clone https://github.com/ppf/tui-ccplan-review.git
cd tui-ccplan-review

# Create virtual environment and install
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Standalone Usage

```bash
# Review specific plan
ccplan-review ~/.claude/plans/my-plan.md

# Or use the alias
plan-review-tui ~/.claude/plans/my-plan.md
```

### Tmux Usage (Recommended)

After setup (see Tmux Integration section), just press:
```
<leader> + Shift+P
```

Latest plan opens instantly in popup! 🎉

*Note: Default tmux leader is `Ctrl+b`, but yours may be different.*

## Keyboard Shortcuts

### Navigation
| Key | Action |
|-----|--------|
| `n` | Next section (auto-scroll to section start) |
| `p` | Previous section (auto-scroll to section start) |
| `l` | Jump to specific line number |
| `↑/↓` or `j/k` | Scroll line by line |
| `Home/End` or `g/G` | Jump to top/bottom of plan |

### Comments
| Key | Action |
|-----|--------|
| `c` | Add comment at current line |
| `e` | Edit comment (select if multiple on same line) |
| `d` | Delete comment (select if multiple on same line) |

### Section Actions
| Key | Action |
|-----|--------|
| `a` | Approve current section |
| `r` | Reject current section (with reason) |

### Review
| Key | Action |
|-----|--------|
| `s` | Generate summary and copy to clipboard |
| `?` | Show help |
| `q` | Quit |
| `ESC` | Close modals |

### Theme
| Key | Action |
|-----|--------|
| `Ctrl+P` | Open command palette (theme switcher) |

## Tmux Integration

One-key access to plan reviews from tmux popup!

### Quick Setup

**Add to `~/.zshrc`:**
```bash
# Replace <install-path> with where you cloned the repo
export PATH="$PATH:<install-path>/tui-ccplan-review/bin"

# Example:
# export PATH="$PATH:$HOME/projects/tui-ccplan-review/bin"
```

**Add to `~/.tmux.conf`:**
```bash
# Replace <install-path> with where you cloned the repo
bind-key P display-popup -E -w 90% -h 90% \
  "<install-path>/tui-ccplan-review/bin/ccplan-review-latest"

# Or if you added bin to PATH (recommended):
# bind-key P display-popup -E -w 90% -h 90% "ccplan-review-latest"
```

**Reload tmux:**
```bash
tmux source-file ~/.tmux.conf
```

### Usage

1. **In tmux**: Press `<leader> + Shift+P`
2. **Review opens** in 90% popup with latest plan
3. **Navigate** with `n/p`, **comment** with `c`, **approve/reject** with `a/r`
4. **Generate summary**: Press `s` (auto-copied to clipboard)
5. **Close**: Press `q`
6. **Paste** summary back to Claude conversation

*Note: Default tmux leader is `Ctrl+b`, but check your `~/.tmux.conf` if you've customized it.*

**Note**: The `ccplan-review-latest` script automatically:
- Activates the venv
- Finds the most recent plan in `~/.claude/plans/`
- Launches the TUI

**See [INSTALL.md](INSTALL.md) for alternative setups and troubleshooting.**

## UI Overview

```
┌─ Plan Review: my-plan.md - Interactive Plan Review Tool ─────────────┐
│ ↑ [3/4] Implementation Steps  💬 Comments: 7  Approved: 4  Rejected: 0│
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│    10  ## Technical Stack                                            │
│ →  11  - Modern TUI framework                                        │
│    12  - Built on Rich for rendering                                 │
│    13  - Reactive architecture                                       │
│    14  ## Implementation Steps ✅                                     │
│        💬 [Line 14] comment line 14 - editedheheh                    │
│        💬 [Line 14] comment 3                                        │
│    15                                                                 │
│    16  ### Step 1: Setup                                             │
│    17  - Create project structure                                    │
│        💬 [Line 17] comment 17                                       │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│ q Quit  c Comment  e Edit  d Delete  l Jump  a Approve  r Reject ... │
└───────────────────────────────────────────────────────────────────────┘
```

**Features visible in UI:**
- **→** Current line indicator
- **Line numbers** on left side
- **Section name** in header with navigation position [3/4]
- **Status indicators**: ✅ (approved), ❌ (rejected) after section headers
- **Comment indicators**: 💬 inline with line references
- **Stats bar**: Live counts of comments and section approvals
- **Footer**: Quick reference for all keyboard shortcuts

## Review Workflow

1. **Launch** TUI with plan file (or use tmux `<leader> + Shift+P`)
2. **Navigate** sections with `n/p` (auto-scrolls to section start)
3. **Jump** to specific line with `l` for precise navigation
4. **Add comments** at any line with `c` key
5. **Edit/delete** comments with `e/d` (handles multiple per line)
6. **Approve/reject** entire sections with `a/r` keys
7. **Generate summary** with `s` (auto-copied to clipboard)
8. **Paste** summary back into Claude conversation
9. **Quit** with `q` (review auto-saves)

## Screenshots

*Screenshots coming soon! See [UI Overview](#ui-overview) section below for a text representation of the interface.*

Want to contribute screenshots? Add them to `docs/screenshots/`:
- `plan-review-main.png` - Main interface
- `comment-modal.png` - Comment modal
- `section-nav.png` - Section navigation

## Review Data Storage

Reviews auto-save to `~/.claude/reviews/<plan-name>.json`:

```json
{
  "plan_path": "/Users/storm/.claude/plans/my-plan.md",
  "comments": [
    {
      "line_number": 14,
      "text": "comment line 14 - editedheheh",
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "line_number": 14,
      "text": "comment 3",
      "timestamp": "2024-01-15T10:32:00"
    },
    {
      "line_number": 17,
      "text": "comment 17",
      "timestamp": "2024-01-15T10:35:00"
    }
  ],
  "sections": [
    {
      "start_line": 14,
      "end_line": 20,
      "section_name": "Implementation Steps",
      "status": "approved",
      "reason": null
    },
    {
      "start_line": 31,
      "end_line": 36,
      "section_name": "Verification",
      "status": "approved",
      "reason": null
    }
  ]
}
```

**Features:**
- Multiple comments per line supported
- Comments persist across sessions
- Section approval/rejection with optional reasons
- Timestamps for tracking review progression

## Tips & Tricks

### Fast Navigation
- Use `n/p` to jump between sections (auto-scrolls)
- Press `l` and type a line number for precise jumps
- Current section name shows in status bar

### Multiple Comments Per Line
- Add multiple comments to the same line
- Use `e` to select which comment to edit
- Use `d` to choose which to delete
- Number keys (1-9) for quick selection

### Theme Customization
- Press `Ctrl+P` to open theme switcher
- Choose from: dracula, monokai, nord, textual-dark, etc.
- Theme applies to all widgets and modals

### Efficient Review
1. Scan with `n/p` for quick section overview
2. Jump to specific lines with `l` for detailed review
3. Comment as you go with `c`
4. Approve obvious sections with `a`
5. Reject and explain with `r` for issues
6. Generate summary with `s` when done

### Tmux Workflow
- Review plans without leaving terminal
- Summary auto-copies to clipboard
- Paste directly into Claude conversation
- No context switching needed

## Technical Details

### Architecture
- **Framework**: Python + Textual (Rich-based TUI)
- **Rendering**: Rich Text widget for styled content
- **Persistence**: JSON-based review storage
- **Clipboard**: pyperclip for cross-platform support
- **Themes**: Textual built-in theme system

### File Locations
```
~/.claude/
├── plans/                    # Plan markdown files
│   └── my-plan.md
└── reviews/                  # Review data (auto-created)
    └── my-plan.json
```

### Data Format
- Comments stored with line numbers, text, timestamps
- Sections tracked by start/end lines, status, optional reasons
- Reviews persist across sessions (auto-save on changes)
- Multiple reviews can exist for different plans

## Requirements

- **Python**: 3.10+
- **Dependencies**:
  - `textual` - TUI framework
  - `rich` - Text rendering and styling
  - `pyperclip` - Clipboard integration

## Contributing

Contributions welcome! This tool is designed for Claude Code plan reviews but can be adapted for other markdown review workflows.

## License

MIT
