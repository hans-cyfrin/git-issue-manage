"""GitHub API client for issue management."""

import requests
from typing import List, Dict, Optional, Any
from collections import defaultdict
from ..utils.config import Config


class GitHubClient:
    """GitHub API client for issue management."""

    def __init__(self, config: Optional[Config] = None, token: Optional[str] = None,
                 repo_owner: Optional[str] = None, repo_name: Optional[str] = None):
        """Initialize GitHub API client.

        Args:
            config: Configuration object. If provided, other params are ignored.
            token: GitHub API token. Used only if config is None.
            repo_owner: Repository owner. Used only if config is None.
            repo_name: Repository name. Used only if config is None.

        Raises:
            ValueError: If required parameters are missing.
        """
        if config:
            self.token = config.github_token
            self.repo_owner = config.repo_owner
            self.repo_name = config.repo_name
            self.base_url = config.github_base_url
        else:
            self.token = token or ""
            self.repo_owner = repo_owner or ""
            self.repo_name = repo_name or ""
            self.base_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}'

        if not all([self.token, self.repo_owner, self.repo_name]):
            raise ValueError("GitHub token, repository owner, and repository name are required")

        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def get_issues(self, issue_numbers: Optional[List[int]] = None,
                   state: str = 'open', per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch issues from the repository.

        Args:
            issue_numbers: Specific issue numbers to fetch. If None, fetches all issues.
            state: Issue state ('open', 'closed', 'all')
            per_page: Number of issues per page (max 100)

        Returns:
            List of issue dictionaries
        """
        try:
            if issue_numbers:
                return [self.get_issue(num) for num in issue_numbers if self.get_issue(num)]
            else:
                return self._fetch_all_issues(state=state, per_page=per_page)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues: {str(e)}")
            return []

    def get_issue(self, issue_number: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific issue from the repository.

        Args:
            issue_number: The issue number to fetch

        Returns:
            Issue dictionary or None if not found
        """
        try:
            response = requests.get(f'{self.base_url}/issues/{issue_number}', headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issue #{issue_number}: {str(e)}")
            return None

    def _fetch_all_issues(self, state: str = 'open', per_page: int = 100) -> List[Dict[str, Any]]:
        """Fetch all issues with pagination.

        Args:
            state: Issue state ('open', 'closed', 'all')
            per_page: Number of issues per page

        Returns:
            List of all issues
        """
        issues = []
        page = 1

        while True:
            response = requests.get(
                f'{self.base_url}/issues',
                headers=self.headers,
                params={'state': state, 'page': page, 'per_page': per_page}
            )
            response.raise_for_status()
            page_issues = response.json()

            if not page_issues:
                break

            issues.extend(page_issues)

            if len(page_issues) < per_page:
                break

            page += 1

        if not issues:
            print(f"No {state} issues found in the repository.")
        else:
            print(f"Found {len(issues)} {state} issues to process.")

        return issues

    def add_label(self, issue_number: int, label: str) -> bool:
        """Add a label to an issue.

        Args:
            issue_number: The issue number
            label: The label to add

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f'{self.base_url}/issues/{issue_number}/labels'
            response = requests.post(url, headers=self.headers, json={'labels': [label]})
            response.raise_for_status()
            print(f"Added label '{label}' to issue #{issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error adding label to issue #{issue_number}: {str(e)}")
            return False

    def remove_label(self, issue_number: int, label: str) -> bool:
        """Remove a label from an issue.

        Args:
            issue_number: The issue number
            label: The label to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            # First check if the label exists on the issue
            issue = self.get_issue(issue_number)
            if not issue:
                return False

            existing_labels = [l['name'] for l in issue['labels']]
            if label not in existing_labels:
                print(f"Label '{label}' does not exist on issue #{issue_number}. Skipping.")
                return True

            url = f'{self.base_url}/issues/{issue_number}/labels/{label}'
            response = requests.delete(url, headers=self.headers)

            if response.status_code == 404:
                print(f"Label '{label}' not found on issue #{issue_number}. Skipping.")
                return True

            response.raise_for_status()
            print(f"Removed label '{label}' from issue #{issue_number}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error removing label from issue #{issue_number}: {str(e)}")
            return False

    def update_issue_content(self, issue_number: int, new_content: str) -> bool:
        """Update the content (body) of an issue.

        Args:
            issue_number: The issue number
            new_content: The new content for the issue

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f'{self.base_url}/issues/{issue_number}'
            response = requests.patch(url, headers=self.headers, json={'body': new_content})
            response.raise_for_status()
            print(f"Successfully updated content of issue #{issue_number}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error updating issue #{issue_number}: {str(e)}")
            return False

    def generate_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of issues grouped by assignee and severity.

        Args:
            issues: List of issue dictionaries

        Returns:
            Summary dictionary with counts by assignee and severity
        """
        if not issues:
            return {}

        summary = defaultdict(lambda: {
            'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Info': 0, 'Gas': 0, 'Total': 0
        })

        for issue in issues:
            assignee = issue['assignee']['login'] if issue.get('assignee') else "Unassigned"
            severity = self._extract_severity(issue)

            summary[assignee][severity] += 1
            summary[assignee]['Total'] += 1

        return dict(summary)

    def _extract_severity(self, issue: Dict[str, Any]) -> str:
        """Extract severity from issue labels.

        Args:
            issue: Issue dictionary

        Returns:
            Severity level string
        """
        for label in issue['labels']:
            label_name = label['name']
            if "Severity: Critical Risk" in label_name:
                return "Critical"
            elif "Severity: High Risk" in label_name:
                return "High"
            elif "Severity: Medium Risk" in label_name:
                return "Medium"
            elif "Severity: Low Risk" in label_name:
                return "Low"
            elif "Severity: Informational" in label_name:
                return "Info"
            elif "Severity: Gas Optimization" in label_name:
                return "Gas"

        return "Info"  # Default severity