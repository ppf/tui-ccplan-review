"""CLI entry point."""

import sys
from pathlib import Path

from .app import run_app


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ccplan-review <plan-file.md>")
        print("\nExample:")
        print("  ccplan-review ~/.claude/plans/latest-plan.md")
        sys.exit(1)

    plan_path = sys.argv[1]

    # Validate plan file
    plan_file = Path(plan_path)
    if not plan_file.exists():
        print(f"Error: Plan file not found: {plan_path}")
        sys.exit(1)

    if not plan_file.is_file():
        print(f"Error: Not a file: {plan_path}")
        sys.exit(1)

    # Run the app
    run_app(str(plan_file.absolute()))


if __name__ == "__main__":
    main()
