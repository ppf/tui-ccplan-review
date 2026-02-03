# Installation & Setup

## Quick Install

```bash
# 1. Install the package
cd /Users/storm/PhpstormProjects/ppf/tui-ccplan-review
source venv/bin/activate
pip install -e .

# 2. Make the helper scripts executable
chmod +x bin/ccplan-review-latest bin/ccplan-review-pick

# 3. Add bin to your PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$PATH:/Users/storm/PhpstormProjects/ppf/tui-ccplan-review/bin"
```

## Tmux Integration

### Automatic Setup

```bash
# Append tmux config to your tmux.conf
cat tmux-integration.conf >> ~/.config/tmux/tmux.conf

# Reload tmux config
tmux source-file ~/.config/tmux/tmux.conf
```

### Manual Setup

Add to `~/.config/tmux/tmux.conf`:

```bash
# Plan review popup (latest plan across Claude + Codex)
bind-key P display-popup -E -w 90% -h 90% "ccplan-review-latest"

# Optional: picker popup (requires fzf)
# bind-key p display-popup -E -w 90% -h 90% "ccplan-review-pick"
```

Reload tmux:
```bash
tmux source-file ~/.config/tmux/tmux.conf
```

## Usage

### In Tmux

1. Press `<leader> + Shift + P` (default: `Ctrl+b` then `Shift+P`)
2. Plan review TUI opens in popup (90% screen)
3. Review the plan:
   - Navigate: `n`/`p` (sections), `l` (jump to line)
   - Comment: `c`
   - Approve: `a`, Reject: `r`
4. Generate summary: `s` (copies to clipboard)
5. Close: `q` or `Esc`
6. Paste summary back to Claude

### Standalone

```bash
# Review specific plan
ccplan-review ~/.claude/plans/my-plan.md

# Review latest plan across Claude + Codex
ccplan-review-latest

# Pick a plan with fzf (requires fzf)
ccplan-review-pick
```

## Workflow Integration

### With Claude Code Plan Mode

1. **Exit plan mode** in Claude Code
2. **Review in tmux**: `<leader> + P`
3. **Add comments/approvals** in TUI
4. **Generate summary**: Press `s`
5. **Paste to Claude**: Summary in clipboard
6. **Claude incorporates feedback**

### Directory Structure

```
~/.claude/
├── plans/              # Plan files (default when not set in settings)
│   ├── plan-2024-01.md
│   └── plan-2024-02.md
└── reviews/            # Review data (auto-created)
    ├── plan-2024-01.json
    └── plan-2024-02.json
```

## Configuration

### Custom Plans Directory

Set `plansDirectory` in Claude settings:

```bash
cat > ~/.claude/settings.json << 'JSON'
{
  "plansDirectory": "/path/to/claude-plans"
}
JSON
```

Relative paths are resolved against the current working directory. If not set,
`ccplan-review-latest` defaults to `~/.claude/plans`.

### Codex Plans Directory

If a `.codex/plans` directory exists in the current directory or a parent,
`ccplan-review-latest` and `ccplan-review-pick` will include those plans.

### Custom Keybinding

Change `P` to another key in tmux config:

```bash
# Use lowercase 'r' instead
bind-key r display-popup -E -w 90% -h 90% "ccplan-review-latest"
```

## Troubleshooting

### "Command not found: ccplan-review"

Make sure package is installed:
```bash
cd /path/to/tui-ccplan-review
pip install -e .
```

### "Command not found: ccplan-review-latest"

Add bin directory to PATH:
```bash
export PATH="$PATH:/path/to/tui-ccplan-review/bin"
```

### "Command not found: ccplan-review-pick"

Add bin directory to PATH:
```bash
export PATH="$PATH:/path/to/tui-ccplan-review/bin"
```

### "fzf not found"

Install fzf, for example:
```bash
brew install fzf
```

### No plans found

Create plans directory:
```bash
mkdir -p ~/.claude/plans
```

Or set `plansDirectory` in `~/.claude/settings.json` to a different path.

### Tmux keybinding not working

Reload tmux config:
```bash
tmux source-file ~/.config/tmux/tmux.conf
```

Or restart tmux.
