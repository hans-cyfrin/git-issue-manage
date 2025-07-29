"""GitHub Issue Manager - A comprehensive CLI tool for managing GitHub issues."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .api.github_client import GitHubClient
from .api.openrouter_client import OpenRouterClient
from .utils.config import Config

__all__ = ["GitHubClient", "OpenRouterClient", "Config"]