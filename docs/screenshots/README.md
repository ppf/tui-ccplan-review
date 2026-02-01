# Screenshots

Add screenshots here for README documentation.

## Needed Screenshots

1. **plan-review-main.png** - Main interface showing:
   - Line numbers with current line indicator (→)
   - Section highlighting
   - Inline comments (💬)
   - Status bar with stats
   - Section approval indicators (✅)

2. **comment-modal.png** - Comment modal showing:
   - Rounded border styling
   - Input field
   - Add/Cancel buttons

3. **section-nav.png** - Section navigation showing:
   - Current section highlighting
   - Navigation position in status bar
   - Multiple sections visible

## How to Capture

Use terminal screenshot tools or tmux capture:
```bash
# In tmux popup with plan review open
tmux capture-pane -e -p > screenshot.txt
# Or use macOS/Linux screenshot tools
```
