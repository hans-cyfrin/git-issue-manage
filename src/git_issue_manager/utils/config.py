"""Configuration management for git-issue-manager."""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for git-issue-manager."""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.

        Args:
            env_file: Path to .env file. If None, uses default .env file.
        """
        load_dotenv(env_file)
        self._validate_required_vars()

    @property
    def github_token(self) -> str:
        """Get GitHub API token."""
        return os.getenv('GITHUB_TOKEN', '')

    @property
    def repo_owner(self) -> str:
        """Get repository owner."""
        return os.getenv('REPO_OWNER', '')

    @property
    def repo_name(self) -> str:
        """Get repository name."""
        return os.getenv('REPO_NAME', '')

    @property
    def openrouter_api_key(self) -> str:
        """Get OpenRouter API key."""
        return os.getenv('OPENROUTER_API_KEY', '')

    @property
    def openrouter_model(self) -> str:
        """Get OpenRouter model name."""
        return os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')

    @property
    def github_base_url(self) -> str:
        """Get GitHub API base URL for the configured repository."""
        return f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'

    def _validate_required_vars(self) -> None:
        """Validate that required environment variables are set."""
        required_vars = ['GITHUB_TOKEN', 'REPO_OWNER', 'REPO_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please check your .env file."
            )

    def has_openrouter_config(self) -> bool:
        """Check if OpenRouter configuration is available."""
        return bool(self.openrouter_api_key)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            'repo_owner': self.repo_owner,
            'repo_name': self.repo_name,
            'openrouter_model': self.openrouter_model,
            'has_github_token': bool(self.github_token),
            'has_openrouter_key': bool(self.openrouter_api_key),
        }