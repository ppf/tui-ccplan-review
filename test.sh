#!/bin/bash
# Quick test script for TUI plan review

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Testing TUI Plan Review Tool"
echo ""

# Ensure test plan exists
mkdir -p ~/.claude/plans
cat > ~/.claude/plans/test-plan.md << 'PLAN'
# Test Plan: Example Feature

## Overview
This is a test plan to verify the TUI tool works correctly.

## Technical Stack
**Framework**: Python + Textual
- Modern TUI framework
- Built on Rich for rendering

## Implementation
Build the core features and test thoroughly.

## Verification
Ensure all features work as expected.
PLAN

echo "✅ Test plan created: ~/.claude/plans/test-plan.md"
echo ""
echo "🚀 Launching TUI (press 'q' to quit)..."
echo ""

# Ensure venv exists, then install and run
if [ ! -d "venv" ]; then
    echo "ℹ️  Creating venv (./venv)..."
    python3 -m venv venv
fi

source venv/bin/activate
python -m pip install -e . >/dev/null
ccplan-review ~/.claude/plans/test-plan.md
