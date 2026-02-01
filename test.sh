#!/bin/bash
# Quick test script for TUI plan review

set -e

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

# Activate venv and run
source venv/bin/activate
ccplan-review ~/.claude/plans/test-plan.md
