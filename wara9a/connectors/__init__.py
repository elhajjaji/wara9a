"""
Connectors for various data sources.

Two main categories:
- Ticketing connectors: Functional documentation (epics, features, stories)
- Git connectors: Technical documentation (commits, PRs, code)
"""

from wara9a.connectors.github import GitHubConnector
from wara9a.connectors.local_files import LocalFilesConnector
from wara9a.connectors.jira import JiraConnector

__all__ = [
    "GitHubConnector",
    "LocalFilesConnector", 
    "JiraConnector",
]