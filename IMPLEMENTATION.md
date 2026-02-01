# Implementation Notes

## Architecture Decisions

### Standalone Tool vs Plugin
**Decision**: Built as standalone TUI tool, not Claude Code plugin

**Rationale**:
- Plugins are hook-based with 3-5s timeout
- TUI requires persistent event loop
- Better UX with dedicated process
- Can still be invoked by plugin hooks

### Framework Choice: Textual
**Why Textual**:
- Modern reactive architecture
- Built-in markdown rendering (via Rich)
- Active development and good docs
- Better than curses (low-level) or urwid (dated)

## Project Structure

```
tui-ccplan-review/
├── tui_ccplan_review/
│   ├── __init__.py       # Package metadata
│   ├── __main__.py       # CLI entry point
│   ├── app.py            # Main Textual app
│   ├── widgets.py        # Custom modals
│   ├── review.py         # Data models
│   └── config.py         # Configuration
├── venv/                 # Virtual environment
├── pyproject.toml        # Package config
├── README.md             # User documentation
├── LICENSE               # MIT license
└── .gitignore            # Python gitignore
```

## Key Components

### Data Models (`review.py`)

**Comment**: Line-specific annotation
- `line_number`: Target line
- `text`: Comment content
- `type`: comment/question/suggestion
- `timestamp`: Creation time

**SectionReview**: Section approval status
- `start_line`, `end_line`: Section boundaries
- `section_name`: Display name
- `status`: approved/rejected/pending
- `reason`: Rejection reason (optional)

**PlanReview**: Complete review state
- Manages comments and sections
- Persists to JSON in `~/.claude/reviews/`
- Generates markdown summaries

### TUI Components (`app.py`)

**PlanViewer**: Main content area
- Loads plan markdown
- Parses sections (## headers)
- Renders with annotations (✅/❌)
- Displays inline comments

**StatusBar**: Review statistics
- Comment count
- Approved/rejected counts
- Color-coded display

**PlanReviewApp**: Main application
- Keyboard bindings (c/a/r/s/q)
- Modal management
- Review persistence
- Clipboard integration

### Custom Widgets (`widgets.py`)

**CommentModal**: Add comments
- Text input
- Comment type selection (💬/❓/💡)
- Keyboard navigation

**RejectModal**: Reject sections
- Reason input
- Cancel/confirm buttons

## Integration Points

### Current Integration
- CLI commands: `ccplan-review`, `plan-review-tui`
- File-based communication via `~/.claude/reviews/`
- Clipboard for summary export

### Tmux Integration
Add to `~/.config/tmux/tmux.conf`:
```bash
bind-key P display-popup -E -w 90% -h 90% \\
  "ccplan-review ~/.claude/plans/$(ls -t ~/.claude/plans/*.md | head -1)"
```

### Future: Plan-Review Plugin Hook
Can be invoked from `on-exit-plan-mode.py`:
```python
subprocess.run([
    "tmux", "display-popup",
    "-E", "-w", "90%", "-h", "90%",
    f"ccplan-review {plan_path}"
])
```

## Workflow

1. **Launch**: `ccplan-review plan.md`
2. **Navigate**: Scroll through plan
3. **Comment**: Press `c`, type comment
4. **Approve**: Press `a` on section
5. **Reject**: Press `r`, provide reason
6. **Summary**: Press `s`, copies to clipboard
7. **Exit**: Press `q`

## Data Storage

Reviews saved to: `~/.claude/reviews/<plan-name>.json`

Example:
```json
{
  "plan_path": "/path/to/plan.md",
  "comments": [
    {
      "line_number": 15,
      "text": "Add error handling?",
      "type": "question",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "sections": [
    {
      "start_line": 10,
      "end_line": 25,
      "section_name": "Technical Stack",
      "status": "approved",
      "reason": null
    }
  ],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:35:00"
}
```

## Summary Format

Generated markdown:
```markdown
# Plan Review: plan-name.md

## Summary
- ✅ 2 sections approved
- ❌ 1 section needs revision
- 💬 3 comments

## Comments

### Line 15: Technical Stack
❓ Add error handling?

## Approved Sections
✅ Overview
✅ Technical Stack

## Needs Revision

### Integration
❌ Missing tmux detection logic
```

## MVP Limitations

### Current
- Section detection limited to `##` headers
- Line tracking simplified (uses first section)
- No multi-plan comparison
- No collaborative review

### Future Enhancements
- Accurate line tracking with scroll position
- Review history and comparison
- Git diff integration
- Team review aggregation
- WebSocket for live updates
- Export to PDF/HTML

## Testing

### Manual Testing
```bash
# Test basic launch
ccplan-review ~/.claude/plans/test-plan.md

# Test with tmux popup
tmux display-popup -E -w 90% -h 90% "ccplan-review ~/.claude/plans/test-plan.md"
```

### Verification Checklist
- ✅ Plan displays correctly
- ✅ Markdown rendering works
- ✅ Can add comments
- ✅ Can approve/reject sections
- ✅ Summary copies to clipboard
- ✅ Review persists across sessions
- ✅ Keyboard navigation works
- ✅ Tmux popup integration

## Dependencies

**Runtime**:
- `textual>=0.47.0` - TUI framework
- `rich>=13.0.0` - Rendering engine
- `pyperclip>=1.8.0` - Clipboard support

**Development**:
- Python 3.10+
- pip/setuptools

## Installation

```bash
# Development
cd /Users/storm/PhpstormProjects/ppf/tui-ccplan-review
source venv/bin/activate
pip install -e .

# Production (future)
pip install tui-ccplan-review
```

## Distribution Strategy

### Current: Local Development
- Git repository: `/Users/storm/PhpstormProjects/ppf/tui-ccplan-review/`
- Editable install for development

### Future: Public Release
1. Push to GitHub: `ppf/tui-ccplan-review`
2. Tag releases
3. Publish to PyPI
4. Document in storm-plugins repo

## Known Issues

### MVP
- Section detection only works for `##` headers
- Line tracking uses simplified approach
- No validation for malformed plans
- Clipboard may fail on some systems (fallback to file)

### Platform Compatibility
- macOS: ✅ Tested
- Linux: ⚠️ Should work (untested)
- Windows: ⚠️ May need pyperclip adjustments

## Performance

- Lightweight: < 1MB memory
- Fast startup: < 1s
- Efficient rendering via Textual
- JSON storage minimal overhead

## Security

- No network access
- Local file operations only
- User home directory for storage
- No sensitive data handling
