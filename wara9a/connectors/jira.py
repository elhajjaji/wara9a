"""
Jira connector for Wara9a.

Collects functional documentation from Jira:
- Epics, features, user stories
- Sprint planning and roadmap
- Business requirements
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from wara9a.core.connector_base import TicketingConnector, ConnectorError, ConnectorConnectionError
from wara9a.core.models import (
    ProjectData, Repository, Commit, Issue, Author, Label,
    SourceType, IssueStatus, IssueType
)
from wara9a.core.config import SourceConfig


logger = logging.getLogger(__name__)


class JiraConnector(TicketingConnector):
    """
    Jira connector for functional documentation extraction.
    
    Extracts functional documentation from Jira:
    - Epics: High-level business initiatives
    - Features: Major product capabilities
    - User Stories: Specific user requirements
    - Sprint planning and roadmap
    
    Category: TICKETING (Functional Documentation)
    Data Source: Jira REST API v3
    Authentication: API Token or OAuth
    """
    
    BASE_URL_TEMPLATE = "https://{domain}.atlassian.net"
    
    @property
    def connector_type(self) -> str:
        return "jira"
    
    @property
    def display_name(self) -> str:
        return "Jira"
    
    @property
    def description(self) -> str:
        return "Connector for functional documentation from Jira (epics, features, stories)"
    
    @property
    def required_config_fields(self) -> List[str]:
        return ["domain", "project"]
    
    @property
    def optional_config_fields(self) -> List[str]:
        return ["token", "email", "max_issues", "include_epics", "include_stories"]
    
    def validate_config(self, config: SourceConfig) -> List[str]:
        """
        Validates Jira configuration.
        
        Args:
            config: Source configuration
            
        Returns:
            List of validation errors (empty if OK)
        """
        errors = []
        
        if not config.config.get("domain"):
            errors.append("Jira domain is required (e.g., 'mycompany')")
        
        if not config.config.get("project"):
            errors.append("Jira project key is required (e.g., 'PROJ')")
        
        # Recommend authentication
        if not config.config.get("token") and not config.config.get("email"):
            logger.warning("Jira authentication not configured - may have limited access")
        
        return errors
    
    def collect(self, config: SourceConfig) -> ProjectData:
        """
        Collects functional documentation from Jira.
        
        Args:
            config: Source configuration
            
        Returns:
            Normalized project data with functional documentation
            
        Raises:
            ConnectorConnectionError: If unable to connect to Jira
            ConnectorError: For other errors
        """
        logger.info(f"🔍 Collecting functional documentation from Jira project: {config.config.get('project')}")
        
        # Validate configuration
        errors = self.validate_config(config)
        if errors:
            raise ConnectorError(f"Invalid configuration: {', '.join(errors)}")
        
        domain = config.config["domain"]
        project_key = config.config["project"]
        
        try:
            # TODO: Implement Jira API calls
            # This is a placeholder implementation
            
            # Create repository placeholder
            repository = Repository(
                name=project_key,
                full_name=f"{domain}/{project_key}",
                description=f"Jira project {project_key}",
                default_branch="main"
            )
            
            # Collect issues (epics, stories, features)
            issues = self._collect_issues(config, project_key)
            
            logger.info(f"✅ Collected {len(issues)} functional items from Jira")
            
            return ProjectData(
                repository=repository,
                issues=issues,
                commits=[],  # Jira doesn't have commits
                pull_requests=[],  # Jira doesn't have PRs
                releases=[],
                source_type=SourceType.JIRA,
                source_config={
                    "domain": domain,
                    "project": project_key,
                    "documentation_type": "functional"
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to collect from Jira: {e}")
            raise ConnectorConnectionError(f"Failed to connect to Jira: {e}")
    
    def _collect_issues(self, config: SourceConfig, project_key: str) -> List[Issue]:
        """
        Collects issues (epics, stories, features) from Jira.
        
        Args:
            config: Source configuration
            project_key: Jira project key
            
        Returns:
            List of normalized issues
        """
        # TODO: Implement actual Jira API calls
        # For now, return empty list as placeholder
        
        logger.info(f"📋 Collecting epics, features, and stories from {project_key}")
        
        # Placeholder implementation
        issues = []
        
        # Example: How issues would be created from Jira data
        # issue = Issue(
        #     id=jira_issue["key"],
        #     title=jira_issue["fields"]["summary"],
        #     description=jira_issue["fields"]["description"],
        #     status=self._normalize_status(jira_issue["fields"]["status"]["name"]),
        #     type=self._normalize_type(jira_issue["fields"]["issuetype"]["name"]),
        #     author=Author(name=jira_issue["fields"]["creator"]["displayName"]),
        #     created_at=datetime.fromisoformat(jira_issue["fields"]["created"]),
        #     url=f"https://{config.config['domain']}.atlassian.net/browse/{jira_issue['key']}"
        # )
        # issues.append(issue)
        
        return issues
    
    def _normalize_status(self, jira_status: str) -> IssueStatus:
        """Normalizes Jira status to standard status."""
        status_map = {
            "to do": IssueStatus.OPEN,
            "in progress": IssueStatus.IN_PROGRESS,
            "done": IssueStatus.CLOSED,
            "resolved": IssueStatus.RESOLVED,
        }
        return status_map.get(jira_status.lower(), IssueStatus.OPEN)
    
    def _normalize_type(self, jira_type: str) -> IssueType:
        """Normalizes Jira issue type to standard type."""
        type_map = {
            "epic": IssueType.EPIC,
            "story": IssueType.STORY,
            "task": IssueType.TASK,
            "bug": IssueType.BUG,
            "feature": IssueType.FEATURE,
        }
        return type_map.get(jira_type.lower(), IssueType.TASK)
