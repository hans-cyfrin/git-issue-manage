"""File operations utilities for git-issue-manager."""

import os
from typing import List, Dict, Any, Optional


def read_prompt_file(prompt_file: str = "rewrite_prompt.md") -> Optional[str]:
    """Read the prompt template file.

    Args:
        prompt_file: Path to the prompt file

    Returns:
        Prompt content or None if file not found
    """
    try:
        with open(prompt_file, "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: {prompt_file} not found.")
        return None
    except Exception as e:
        print(f"Error reading {prompt_file}: {str(e)}")
        return None


def write_issues_to_markdown(issues: List[Dict[str, Any]], output_file: str = "download.md",
                           repo_owner: str = "", repo_name: str = "") -> bool:
    """Write issues to a markdown file with summary table.

    Args:
        issues: List of issue dictionaries
        output_file: Output file path
        repo_owner: Repository owner name
        repo_name: Repository name

    Returns:
        True if successful, False otherwise
    """
    if not issues:
        print("No issues to write.")
        return False

    try:
        # Sort issues by number for consistency
        issues.sort(key=lambda x: x['number'])

        # Create summary information
        summary_entries = []

        for issue in issues:
            severity = _detect_severity_from_issue(issue)
            summary_entries.append({
                'id': issue['number'],
                'title': issue['title'],
                'severity': severity,
                'status': issue['state'].capitalize()
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            repo_info = f"{repo_owner}/{repo_name}" if repo_owner and repo_name else "Repository"
            f.write(f"# Issues from {repo_info}\n\n")

            # Write summary table
            f.write("## Summary\n\n")
            f.write("| ID | Title | Severity | Status |\n")
            f.write("|-----|-------|----------|--------|\n")

            for entry in summary_entries:
                f.write(f"| {entry['id']} | {entry['title']} | {entry['severity']} | {entry['status']} |\n")

            f.write("\n\n")

            # Write detailed issue information
            for issue in issues:
                issue_number = issue['number']
                issue_title = issue['title']
                issue_updated_at = issue['updated_at']

                f.write(f"## Issue #{issue_number}: {issue_title}\n\n")
                f.write(f"- **Updated at:** {issue_updated_at}\n")

                # Write labels if any
                if issue['labels']:
                    labels = ', '.join([label['name'] for label in issue['labels']])
                    f.write(f"- **Labels:** {labels}\n")

                # Write issue body
                f.write("\n### Description\n\n")
                if issue.get('body'):
                    f.write(f"{issue['body']}\n\n")
                else:
                    f.write("*No description provided*\n\n")

                # Write separator between issues
                f.write("---\n\n")

        print(f"Successfully wrote {len(issues)} issues to {output_file}")
        return True

    except Exception as e:
        print(f"Error writing issues to {output_file}: {str(e)}")
        return False


def _detect_severity_from_issue(issue: Dict[str, Any]) -> str:
    """Detect severity from issue labels and title.

    Args:
        issue: Issue dictionary

    Returns:
        Severity level string
    """
    # Check labels first
    label_names = [label['name'].lower() for label in issue['labels']]

    if any(s in label_names for s in ['high', 'critical', 'severe']):
        return "High"
    elif any(s in label_names for s in ['medium', 'moderate']):
        return "Medium"
    elif any(s in label_names for s in ['low', 'minor']):
        return "Low"

    # If no severity in labels, check title
    title_lower = issue['title'].lower()
    if any(s in title_lower for s in ['high', 'critical', 'severe']):
        return "High"
    elif any(s in title_lower for s in ['medium', 'moderate']):
        return "Medium"
    elif any(s in title_lower for s in ['low', 'minor']):
        return "Low"

    return "None"


def ensure_file_exists(file_path: str, default_content: str = "") -> bool:
    """Ensure a file exists, creating it with default content if it doesn't.

    Args:
        file_path: Path to the file
        default_content: Content to write if file doesn't exist

    Returns:
        True if file exists or was created successfully
    """
    if os.path.exists(file_path):
        return True

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
        return True
    except Exception as e:
        print(f"Error creating file {file_path}: {str(e)}")
        return False