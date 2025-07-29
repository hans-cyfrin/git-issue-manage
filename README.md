# GitHub Issue Manager

A comprehensive CLI tool for managing GitHub issues with AI-powered content rewriting, built with modern Python packaging using UV.

## Features

- **Label Management**: Add and remove labels from issues
- **AI-Powered Content Rewriting**: Use OpenRouter API with various AI models
- **Text Replacement**: Simple find-and-replace operations across issue content
- **Issue Export**: Download issues to markdown files with summary tables
- **Issue Analytics**: Generate summaries grouped by assignee and severity
- **Batch Operations**: Process specific issues or all repository issues
- **Rich CLI Interface**: Beautiful terminal output with progress indicators

## Installation

### Prerequisites

- Python 3.8 or higher
- UV package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- GitHub Personal Access Token with repo scope
- OpenRouter API key (optional, for AI features)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/git-issue-manager.git
cd git-issue-manager

# Install with UV
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### Install as Package

```bash
# Install directly from repository
uv add git+https://github.com/yourusername/git-issue-manager.git
```

## Configuration

Create a `.env` file in your project root:

```bash
# Copy the example configuration
cp .env.example .env
```

Edit the `.env` file with your credentials:

```env
# GitHub API Configuration
GITHUB_TOKEN=your_github_personal_access_token
REPO_OWNER=repository_owner
REPO_NAME=repository_name

# OpenRouter API Configuration (for content rewriting)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

## Usage

The tool provides two command aliases:
- `git-issue-manager` (full name)
- `gim` (short alias)

### Global Help

```bash
git-issue-manager --help
gim --version
```

### Label Management

**Add labels to issues:**
```bash
# Add label to specific issues
gim add-label "bug" --issues 1 2 3

# Add label to all open issues
gim add-label "needs-review"
```

**Remove labels from issues:**
```bash
# Remove label from specific issues
gim remove-label "bug" --issues 1 2 3

# Remove label from all open issues
gim remove-label "outdated"
```

### Content Rewriting

**AI-powered rewriting (OpenRouter):**
```bash
# Rewrite specific issues using AI
gim rewrite --mode openrouter --issues 1 2 3

# Rewrite all open issues with custom model
gim rewrite --model "openai/gpt-4o"

# Use custom prompt file
gim rewrite --prompt-file "custom_prompt.md"
```

**Text replacement:**
```bash
# Replace text in specific issues
gim rewrite --mode replace --search "old text" --replace "new text" --issues 1 2 3

# Replace text in all open issues
gim rewrite --mode replace --search "TODO" --replace "DONE"
```

### Issue Export

**Download issues to markdown:**
```bash
# Download specific issues
gim download --issues 1 2 3 --output "selected_issues.md"

# Download all open issues
gim download

# Include closed issues
gim download --include-closed --output "all_issues.md"
```

### Analytics and Reporting

**Generate issue summary:**
```bash
# Summary of all open issues
gim summary

# Summary of specific issues
gim summary --issues 1 2 3
```

**View configuration:**
```bash
gim config-info
```

## Project Structure

```
git-issue-manager/
├── src/
│   └── git_issue_manager/
│       ├── __init__.py              # Package initialization
│       ├── api/
│       │   ├── __init__.py
│       │   ├── github_client.py     # GitHub API integration
│       │   └── openrouter_client.py # OpenRouter API integration
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py              # CLI interface and commands
│       └── utils/
│           ├── __init__.py
│           ├── config.py            # Configuration management
│           └── file_operations.py   # File I/O utilities
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment template
├── rewrite_prompt.md               # AI prompt template
└── README.md                       # This file
```

## AI Content Rewriting

### Prompt Templates

Create a `rewrite_prompt.md` file with your rewriting instructions. Use `$##$` as a placeholder for the original issue content:

```markdown
Please rewrite the following GitHub issue to be clearer and more professional:

$##$

Make the content more concise while preserving all technical details.
```

### Supported Models

The tool supports any model available through OpenRouter. Popular choices include:

- **Claude Models**: `anthropic/claude-3.5-sonnet`, `anthropic/claude-3-haiku`
- **GPT Models**: `openai/gpt-4o`, `openai/gpt-4o-mini`
- **Open Source**: `meta-llama/llama-3.2-3b-instruct`, `mistralai/mistral-7b-instruct`

## Issue Summary Format

The summary command generates tables showing issue distribution:

```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━┳━━━━━━┳━━━━━┳━━━━━━━┓
┃ User          ┃ Critical ┃ High ┃ Medium ┃ Low ┃ Info ┃ Gas ┃ Total ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━╇━━━━━━╇━━━━━╇━━━━━━━┩
│ alice         │    2     │  3   │   1    │  0  │  1   │  0  │   7   │
│ bob           │    1     │  2   │   3    │  1  │  0   │  2  │   9   │
│ Unassigned    │    0     │  1   │   2    │  3  │  5   │  1  │  12   │
├───────────────┼──────────┼──────┼────────┼─────┼──────┼─────┼───────┤
│ Total         │    3     │  6   │   6    │  4  │  6   │  3  │  28   │
└───────────────┴──────────┴──────┴────────┴─────┴──────┴─────┴───────┘
```

## Development

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/git-issue-manager.git
cd git-issue-manager

# Install with development dependencies
uv sync --extra dev

# Activate environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### Code Quality Tools

```bash
# Format code
uv run black src/

# Type checking
uv run mypy src/

# Linting
uv run flake8 src/

# Run tests
uv run pytest
```

## Advanced Usage

### Custom Configuration Files

```bash
# Use different configuration file
gim --config-file /path/to/custom/.env summary
```

### Batch Processing

```bash
# Process multiple operations
gim add-label "priority:high" --issues 1 2 3
gim rewrite --mode openrouter --issues 1 2 3
gim download --issues 1 2 3
```

### Integration with CI/CD

```bash
# Generate reports in CI
gim summary > issue_report.txt
gim download --output "weekly_issues.md"
```

## Error Handling

The tool provides comprehensive error handling for:

- Invalid GitHub API responses and authentication issues
- Missing or malformed configuration files
- OpenRouter API failures and rate limiting
- Network connectivity issues
- File permission and I/O errors

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run black src/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial release with UV package management
- Modular architecture with separate API clients
- Rich CLI interface with Click and Rich
- Comprehensive error handling and user feedback
- Support for OpenRouter AI models
- Issue export and analytics features
