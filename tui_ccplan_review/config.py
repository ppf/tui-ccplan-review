"""Configuration management."""

from pathlib import Path


class Config:
    """Application configuration."""

    # Default review storage directory
    REVIEW_DIR = Path.home() / ".claude" / "reviews"

    # Default plans directory
    PLANS_DIR = Path.home() / ".claude" / "plans"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Ensure required directories exist."""
        cls.REVIEW_DIR.mkdir(parents=True, exist_ok=True)
        cls.PLANS_DIR.mkdir(parents=True, exist_ok=True)
