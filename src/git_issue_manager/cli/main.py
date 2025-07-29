"""Main CLI interface for git-issue-manager."""

import click
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..api.github_client import GitHubClient
from ..api.openrouter_client import OpenRouterClient
from ..utils.config import Config
from ..utils.file_operations import read_prompt_file, write_issues_to_markdown

console = Console()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def main(ctx, version):
    """GitHub Issue Manager - A comprehensive CLI tool for managing GitHub issues.

    Manage GitHub issues with features like label management, AI-powered content
    rewriting, issue downloading, and summary generation.
    """
    if version:
        from .. import __version__
        console.print(f"git-issue-manager version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@main.command()
@click.argument('label')
@click.option('--issues', '-i', multiple=True, type=int,
              help='Issue numbers to add labels to (default: all open issues)')
@click.option('--config-file', help='Path to .env configuration file')
def add_label(label: str, issues: tuple, config_file: Optional[str]):
    """Add a label to one or more issues.

    LABEL: The label to add to the issues
    """
    try:
        config = Config(config_file)
        github = GitHubClient(config)

        issue_numbers = list(issues) if issues else None
        issues_data = github.get_issues(issue_numbers)

        if not issues_data:
            console.print("[yellow]No issues found to process.[/yellow]")
            return

        console.print(f"[blue]Adding label '{label}' to {len(issues_data)} issue(s)...[/blue]")

        success_count = 0
        for issue in issues_data:
            if github.add_label(issue['number'], label):
                success_count += 1

        console.print(f"[green]Successfully added label to {success_count}/{len(issues_data)} issues.[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.argument('label')
@click.option('--issues', '-i', multiple=True, type=int,
              help='Issue numbers to remove labels from (default: all open issues)')
@click.option('--config-file', help='Path to .env configuration file')
def remove_label(label: str, issues: tuple, config_file: Optional[str]):
    """Remove a label from one or more issues.

    LABEL: The label to remove from the issues
    """
    try:
        config = Config(config_file)
        github = GitHubClient(config)

        issue_numbers = list(issues) if issues else None
        issues_data = github.get_issues(issue_numbers)

        if not issues_data:
            console.print("[yellow]No issues found to process.[/yellow]")
            return

        console.print(f"[blue]Removing label '{label}' from {len(issues_data)} issue(s)...[/blue]")

        success_count = 0
        for issue in issues_data:
            if github.remove_label(issue['number'], label):
                success_count += 1

        console.print(f"[green]Successfully removed label from {success_count}/{len(issues_data)} issues.[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.option('--mode', type=click.Choice(['openrouter', 'replace']), default='openrouter',
              help='Rewriting mode: openrouter (AI) or replace (text replacement)')
@click.option('--issues', '-i', multiple=True, type=int,
              help='Issue numbers to rewrite (default: all open issues)')
@click.option('--search', help='Text to search for (required for replace mode)')
@click.option('--replace', help='Text to replace with (required for replace mode)')
@click.option('--prompt-file', default='rewrite_prompt.md',
              help='Path to prompt template file (for openrouter mode)')
@click.option('--model', help='OpenRouter model to use (overrides config)')
@click.option('--config-file', help='Path to .env configuration file')
def rewrite(mode: str, issues: tuple, search: Optional[str], replace: Optional[str],
           prompt_file: str, model: Optional[str], config_file: Optional[str]):
    """Rewrite issue content using AI or text replacement.

    Use OpenRouter AI models or simple text replacement to modify issue content.
    """
    try:
        config = Config(config_file)
        github = GitHubClient(config)

        # Validate mode-specific requirements
        if mode == 'replace':
            if not search or not replace:
                console.print("[red]Error: --search and --replace are required for replace mode[/red]")
                return

        issue_numbers = list(issues) if issues else None
        issues_data = github.get_issues(issue_numbers)

        if not issues_data:
            console.print("[yellow]No issues found to process.[/yellow]")
            return

        console.print(f"[blue]Rewriting content for {len(issues_data)} issue(s) using {mode} mode...[/blue]")

        success_count = 0

        # Initialize OpenRouter client if needed
        openrouter = None
        if mode == 'openrouter':
            if not config.has_openrouter_config():
                console.print("[red]Error: OpenRouter API key not configured[/red]")
                return

            try:
                openrouter = OpenRouterClient(config)
                if model:
                    openrouter.set_model(model)
                console.print(f"[blue]Using model: {openrouter.get_model()}[/blue]")
            except ValueError as e:
                console.print(f"[red]Error initializing OpenRouter: {str(e)}[/red]")
                return

        for issue in issues_data:
            if not issue.get('body'):
                console.print(f"[yellow]Issue #{issue['number']} has no content to rewrite. Skipping.[/yellow]")
                continue

            new_content = None

            if mode == 'openrouter':
                prompt_content = read_prompt_file(prompt_file)
                if not prompt_content:
                    console.print(f"[red]Could not read prompt file: {prompt_file}[/red]")
                    break

                full_prompt = prompt_content.replace("$##$", issue['body'])
                new_content = openrouter.rewrite_content(full_prompt)

                if not new_content:
                    console.print(f"[red]Failed to rewrite content for issue #{issue['number']}[/red]")
                    continue

            elif mode == 'replace':
                new_content = issue['body'].replace(search, replace)
                if new_content == issue['body']:
                    console.print(f"[yellow]No occurrences of '{search}' found in issue #{issue['number']}. Skipping.[/yellow]")
                    continue

            if new_content and github.update_issue_content(issue['number'], new_content):
                success_count += 1

        console.print(f"[green]Successfully rewrote content for {success_count}/{len(issues_data)} issues.[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.option('--issues', '-i', multiple=True, type=int,
              help='Issue numbers to download (default: all open issues)')
@click.option('--include-closed', is_flag=True,
              help='Include closed issues in the output')
@click.option('--output', '-o', default='download.md',
              help='Output file path')
@click.option('--config-file', help='Path to .env configuration file')
def download(issues: tuple, include_closed: bool, output: str, config_file: Optional[str]):
    """Download issues to a markdown file.

    Creates a comprehensive markdown file with issue summaries and full content.
    """
    try:
        config = Config(config_file)
        github = GitHubClient(config)

        issue_numbers = list(issues) if issues else None

        # Determine state based on options
        if issue_numbers:
            # For specific issues, get them regardless of state
            issues_data = github.get_issues(issue_numbers)
        else:
            # Get open issues
            issues_data = github.get_issues(state='open')

            # Add closed issues if requested
            if include_closed:
                console.print("[blue]Fetching closed issues...[/blue]")
                closed_issues = github.get_issues(state='closed')
                issues_data.extend(closed_issues)

        if not issues_data:
            console.print("[yellow]No issues found to download.[/yellow]")
            return

        console.print(f"[blue]Downloading {len(issues_data)} issue(s) to {output}...[/blue]")

        if write_issues_to_markdown(issues_data, output, config.repo_owner, config.repo_name):
            console.print(f"[green]Successfully downloaded issues to {output}[/green]")
        else:
            console.print(f"[red]Failed to write issues to {output}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.option('--issues', '-i', multiple=True, type=int,
              help='Issue numbers to summarize (default: all open issues)')
@click.option('--config-file', help='Path to .env configuration file')
def summary(issues: tuple, config_file: Optional[str]):
    """Generate a summary of issues grouped by assignee and severity.

    Creates a table showing issue counts by assignee and severity level.
    """
    try:
        config = Config(config_file)
        github = GitHubClient(config)

        issue_numbers = list(issues) if issues else None
        issues_data = github.get_issues(issue_numbers)

        if not issues_data:
            console.print("[yellow]No issues found to summarize.[/yellow]")
            return

        summary_data = github.generate_summary(issues_data)

        if not summary_data:
            console.print("[yellow]No summary data generated.[/yellow]")
            return

        # Create a rich table
        table = Table(title=f"Issue Summary for {config.repo_owner}/{config.repo_name}")

        table.add_column("User", style="cyan", no_wrap=True)
        table.add_column("Critical", justify="center")
        table.add_column("High", justify="center")
        table.add_column("Medium", justify="center")
        table.add_column("Low", justify="center")
        table.add_column("Info", justify="center")
        table.add_column("Gas", justify="center")
        table.add_column("Total", justify="center", style="bold")

        # Calculate totals
        totals = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0, 'Gas': 0, 'Total': 0}

        # Add rows for each assignee
        for assignee, counts in sorted(summary_data.items()):
            table.add_row(
                assignee,
                str(counts['Critical']),
                str(counts['High']),
                str(counts['Medium']),
                str(counts['Low']),
                str(counts['Info']),
                str(counts['Gas']),
                str(counts['Total'])
            )

            # Add to totals
            for severity in totals:
                totals[severity] += counts[severity]

        # Add totals row
        table.add_section()
        table.add_row(
            "Total",
            str(totals['Critical']),
            str(totals['High']),
            str(totals['Medium']),
            str(totals['Low']),
            str(totals['Info']),
            str(totals['Gas']),
            str(totals['Total']),
            style="bold"
        )

        console.print(table)
        console.print(f"\n[blue]Total open issues: {totals['Total']}[/blue]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@main.command()
@click.option('--config-file', help='Path to .env configuration file')
def config_info(config_file: Optional[str]):
    """Show current configuration information."""
    try:
        config = Config(config_file)
        config_dict = config.to_dict()

        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in config_dict.items():
            table.add_row(key.replace('_', ' ').title(), str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == '__main__':
    main()