"""
Pydantic data models for Wara9a.

These models define the normalized structure that all connectors
must produce and that templates consume.

Standard outputs by documentation type:
- Functional: Epic, Feature, UserStory, Requirement
- Technical: Commit, PullRequest, CodeChange, TechnicalDebt
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class SourceType(str, Enum):
    """Supported source types."""
    GITHUB = "github"
    JIRA = "jira"
    AZURE_DEVOPS = "azure_devops"
    LOCAL_FILES = "local_files"
    CUSTOM = "custom"


class Priority(str, Enum):
    """Priority levels for functional items."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNDEFINED = "undefined"


class IssueStatus(str, Enum):
    """Normalized issue statuses."""
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class IssueType(str, Enum):
    """Normalized issue types."""
    BUG = "bug"
    FEATURE = "feature"
    ENHANCEMENT = "enhancement"
    TASK = "task"
    EPIC = "epic"
    STORY = "story"


# ============================================================================
# FUNCTIONAL DOCUMENTATION MODELS (from Ticketing Systems)
# ============================================================================

class Epic(BaseModel):
    """
    Represents a high-level business initiative (functional documentation).
    
    Standard output for all ticketing connectors (Jira, Azure DevOps, etc.)
    An Epic groups multiple Features or User Stories.
    """
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier")
    key: str = Field(description="Epic key (e.g., PROJ-123)")
    title: str = Field(description="Epic title")
    description: Optional[str] = Field(default=None, description="Detailed description")
    status: IssueStatus = Field(description="Current status")
    priority: Priority = Field(default=Priority.UNDEFINED, description="Priority level")
    author: "Author" = Field(description="Epic creator")
    assignee: Optional["Author"] = Field(default=None, description="Epic owner")
    labels: List["Label"] = Field(default_factory=list, description="Labels/tags")
    created_at: datetime = Field(description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    closed_at: Optional[datetime] = Field(default=None, description="Closing date")
    start_date: Optional[datetime] = Field(default=None, description="Planned start")
    due_date: Optional[datetime] = Field(default=None, description="Planned completion")
    url: Optional[str] = Field(default=None, description="Epic URL")
    business_value: Optional[str] = Field(default=None, description="Business value/impact")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Success criteria")


class Feature(BaseModel):
    """
    Represents a product feature (functional documentation).
    
    Standard output for all ticketing connectors.
    A Feature is part of an Epic and contains multiple User Stories.
    """
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier")
    key: str = Field(description="Feature key (e.g., PROJ-456)")
    title: str = Field(description="Feature title")
    description: Optional[str] = Field(default=None, description="Detailed description")
    status: IssueStatus = Field(description="Current status")
    priority: Priority = Field(default=Priority.UNDEFINED, description="Priority level")
    epic_id: Optional[str] = Field(default=None, description="Parent epic ID")
    epic_key: Optional[str] = Field(default=None, description="Parent epic key")
    author: "Author" = Field(description="Feature creator")
    assignee: Optional["Author"] = Field(default=None, description="Feature owner")
    labels: List["Label"] = Field(default_factory=list, description="Labels/tags")
    created_at: datetime = Field(description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    closed_at: Optional[datetime] = Field(default=None, description="Closing date")
    url: Optional[str] = Field(default=None, description="Feature URL")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Success criteria")


class UserStory(BaseModel):
    """
    Represents a user story (functional documentation).
    
    Standard output for all ticketing connectors.
    A User Story describes a specific user requirement.
    """
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier")
    key: str = Field(description="Story key (e.g., PROJ-789)")
    title: str = Field(description="Story title")
    description: Optional[str] = Field(default=None, description="Story description")
    user_persona: Optional[str] = Field(default=None, description="Target user (As a...)")
    user_goal: Optional[str] = Field(default=None, description="User goal (I want...)")
    user_benefit: Optional[str] = Field(default=None, description="Benefit (So that...)")
    status: IssueStatus = Field(description="Current status")
    priority: Priority = Field(default=Priority.UNDEFINED, description="Priority level")
    story_points: Optional[int] = Field(default=None, description="Effort estimation")
    epic_id: Optional[str] = Field(default=None, description="Parent epic ID")
    feature_id: Optional[str] = Field(default=None, description="Parent feature ID")
    author: "Author" = Field(description="Story creator")
    assignee: Optional["Author"] = Field(default=None, description="Story assignee")
    labels: List["Label"] = Field(default_factory=list, description="Labels/tags")
    created_at: datetime = Field(description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    closed_at: Optional[datetime] = Field(default=None, description="Closing date")
    sprint: Optional[str] = Field(default=None, description="Sprint name/number")
    url: Optional[str] = Field(default=None, description="Story URL")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance tests")
    test_scenarios: List[str] = Field(default_factory=list, description="Test scenarios")


class Requirement(BaseModel):
    """
    Represents a formal requirement (functional documentation).
    
    Standard output for requirement management systems.
    Can be functional or non-functional requirement.
    """
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier")
    key: str = Field(description="Requirement key")
    title: str = Field(description="Requirement title")
    description: str = Field(description="Detailed requirement")
    type: str = Field(description="functional, non-functional, constraint, etc.")
    status: IssueStatus = Field(description="Current status")
    priority: Priority = Field(default=Priority.UNDEFINED, description="Priority level")
    category: Optional[str] = Field(default=None, description="Security, Performance, etc.")
    author: "Author" = Field(description="Requirement creator")
    created_at: datetime = Field(description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    url: Optional[str] = Field(default=None, description="Requirement URL")
    verification_method: Optional[str] = Field(default=None, description="How to verify")
    linked_stories: List[str] = Field(default_factory=list, description="Related story IDs")


class FunctionalData(BaseModel):
    """
    Standardized functional documentation data structure.
    
    All ticketing connectors (Jira, Azure DevOps, etc.) must return this structure.
    """
    model_config = ConfigDict(extra="allow")
    
    epics: List[Epic] = Field(default_factory=list, description="Business epics")
    features: List[Feature] = Field(default_factory=list, description="Product features")
    user_stories: List[UserStory] = Field(default_factory=list, description="User stories")
    requirements: List[Requirement] = Field(default_factory=list, description="Formal requirements")
    
    # Metadata
    collected_at: datetime = Field(default_factory=datetime.now, description="Collection timestamp")
    source_type: SourceType = Field(description="Source system type")
    project_name: str = Field(description="Project/product name")
    project_key: Optional[str] = Field(default=None, description="Project key/identifier")
    
    def get_open_epics(self) -> List[Epic]:
        """Returns all open epics."""
        return [e for e in self.epics if e.status == IssueStatus.OPEN or e.status == IssueStatus.IN_PROGRESS]
    
    def get_stories_by_epic(self, epic_id: str) -> List[UserStory]:
        """Returns all user stories for a given epic."""
        return [s for s in self.user_stories if s.epic_id == epic_id]
    
    def get_features_by_epic(self, epic_id: str) -> List[Feature]:
        """Returns all features for a given epic."""
        return [f for f in self.features if f.epic_id == epic_id]


# ============================================================================
# TECHNICAL DOCUMENTATION MODELS (from Git Repositories)
# ============================================================================

class CodeChange(BaseModel):
    """
    Represents a code change with detailed metrics (technical documentation).
    
    Standard output for all Git connectors (GitHub, GitLab, etc.)
    """
    model_config = ConfigDict(extra="allow")
    
    file_path: str = Field(description="Path to changed file")
    change_type: str = Field(description="added, modified, deleted, renamed")
    additions: int = Field(default=0, description="Lines added")
    deletions: int = Field(default=0, description="Lines deleted")
    changes: int = Field(default=0, description="Total changes")
    language: Optional[str] = Field(default=None, description="Programming language")
    diff: Optional[str] = Field(default=None, description="Diff content (optional)")


class TechnicalCommit(BaseModel):
    """
    Enhanced commit model for technical documentation.
    
    Standard output for all Git connectors.
    """
    model_config = ConfigDict(extra="allow")
    
    sha: str = Field(description="Commit hash")
    short_sha: str = Field(description="Short commit hash (7 chars)")
    message: str = Field(description="Commit message")
    message_subject: str = Field(description="First line of message")
    message_body: Optional[str] = Field(default=None, description="Detailed message")
    author: "Author" = Field(description="Commit author")
    committer: Optional["Author"] = Field(default=None, description="Committer (if different)")
    date: datetime = Field(description="Commit date")
    url: Optional[str] = Field(default=None, description="Commit URL")
    
    # Code changes
    files_changed: List[CodeChange] = Field(default_factory=list, description="Changed files")
    total_additions: int = Field(default=0, description="Total lines added")
    total_deletions: int = Field(default=0, description="Total lines deleted")
    
    # Metadata
    branch: Optional[str] = Field(default=None, description="Branch name")
    tags: List[str] = Field(default_factory=list, description="Git tags")
    is_merge: bool = Field(default=False, description="Is merge commit")
    parent_shas: List[str] = Field(default_factory=list, description="Parent commit hashes")
    
    # Linked items
    linked_issues: List[str] = Field(default_factory=list, description="Referenced issue IDs")
    linked_prs: List[str] = Field(default_factory=list, description="Referenced PR IDs")


class TechnicalPullRequest(BaseModel):
    """
    Enhanced pull request model for technical documentation.
    
    Standard output for all Git connectors.
    """
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier")
    number: int = Field(description="PR number")
    title: str = Field(description="PR title")
    description: Optional[str] = Field(default=None, description="PR description")
    author: "Author" = Field(description="PR author")
    status: str = Field(description="open, closed, merged, draft")
    state: str = Field(description="Current state")
    
    # Branches
    source_branch: str = Field(description="Source branch")
    target_branch: str = Field(description="Target branch (usually main/master)")
    
    # Dates
    created_at: datetime = Field(description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    merged_at: Optional[datetime] = Field(default=None, description="Merge date")
    closed_at: Optional[datetime] = Field(default=None, description="Close date")
    
    # Code review
    reviewers: List["Author"] = Field(default_factory=list, description="Assigned reviewers")
    approved_by: List["Author"] = Field(default_factory=list, description="Approvers")
    review_comments_count: int = Field(default=0, description="Number of review comments")
    
    # Changes
    commits: List[TechnicalCommit] = Field(default_factory=list, description="Included commits")
    files_changed: int = Field(default=0, description="Number of changed files")
    additions: int = Field(default=0, description="Total lines added")
    deletions: int = Field(default=0, description="Total lines deleted")
    
    # Metadata
    url: Optional[str] = Field(default=None, description="PR URL")
    labels: List["Label"] = Field(default_factory=list, description="PR labels")
    milestone: Optional[str] = Field(default=None, description="Associated milestone")
    linked_issues: List[str] = Field(default_factory=list, description="Linked issue IDs")


class CodeMetrics(BaseModel):
    """
    Code metrics and statistics (technical documentation).
    
    Standard output for code analysis.
    """
    model_config = ConfigDict(extra="allow")
    
    language: str = Field(description="Programming language")
    files_count: int = Field(default=0, description="Number of files")
    lines_of_code: int = Field(default=0, description="Total lines of code")
    lines_blank: int = Field(default=0, description="Blank lines")
    lines_comment: int = Field(default=0, description="Comment lines")
    complexity: Optional[float] = Field(default=None, description="Cyclomatic complexity")


class TechnicalDebt(BaseModel):
    """
    Technical debt item (technical documentation).
    
    Can be extracted from code analysis, TODOs, or technical issues.
    """
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Unique identifier")
    title: str = Field(description="Debt title")
    description: str = Field(description="Detailed description")
    severity: str = Field(description="critical, high, medium, low")
    type: str = Field(description="code_smell, bug, vulnerability, etc.")
    file_path: Optional[str] = Field(default=None, description="Affected file")
    line_number: Optional[int] = Field(default=None, description="Line number")
    estimated_effort: Optional[str] = Field(default=None, description="Estimated fix time")
    created_at: datetime = Field(description="Detection date")
    url: Optional[str] = Field(default=None, description="Reference URL")


class TechnicalData(BaseModel):
    """
    Standardized technical documentation data structure.
    
    All Git connectors (GitHub, GitLab, etc.) must return this structure.
    """
    model_config = ConfigDict(extra="allow")
    
    commits: List[TechnicalCommit] = Field(default_factory=list, description="Code commits")
    pull_requests: List[TechnicalPullRequest] = Field(default_factory=list, description="Pull/merge requests")
    code_metrics: Dict[str, CodeMetrics] = Field(default_factory=dict, description="Metrics by language")
    technical_debt: List[TechnicalDebt] = Field(default_factory=list, description="Technical debt items")
    
    # Repository info
    repository_name: str = Field(description="Repository name")
    repository_url: Optional[str] = Field(default=None, description="Repository URL")
    default_branch: str = Field(default="main", description="Default branch")
    
    # Metadata
    collected_at: datetime = Field(default_factory=datetime.now, description="Collection timestamp")
    source_type: SourceType = Field(description="Source system type")
    
    def get_merged_prs(self) -> List[TechnicalPullRequest]:
        """Returns all merged pull requests."""
        return [pr for pr in self.pull_requests if pr.status == "merged"]
    
    def get_commits_by_author(self, author_name: str) -> List[TechnicalCommit]:
        """Returns all commits by a specific author."""
        return [c for c in self.commits if c.author.name == author_name]
    
    def get_total_additions(self) -> int:
        """Returns total lines added across all commits."""
        return sum(c.total_additions for c in self.commits)
    
    def get_total_deletions(self) -> int:
        """Returns total lines deleted across all commits."""
        return sum(c.total_deletions for c in self.commits)


class Author(BaseModel):
    """Represents an author (commit, issue, etc.)."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Full name")
    email: Optional[str] = Field(default=None, description="Email address")
    username: Optional[str] = Field(default=None, description="Username")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")


class Label(BaseModel):
    """Represents a label/tag."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Label name")
    color: Optional[str] = Field(default=None, description="Hexadecimal color")
    description: Optional[str] = Field(default=None, description="Description")


class Release(BaseModel):
    """Represents a release/version."""
    model_config = ConfigDict(extra="allow")
    
    tag: str = Field(description="Version tag")
    name: str = Field(description="Release name")
    description: Optional[str] = Field(default=None, description="Release notes")
    author: Author = Field(description="Release author")
    created_at: datetime = Field(description="Creation date")
    published_at: Optional[datetime] = Field(default=None, description="Publication date")
    is_prerelease: bool = Field(default=False, description="Pre-release")
    is_draft: bool = Field(default=False, description="Draft")
    url: Optional[str] = Field(default=None, description="Release URL")


class Repository(BaseModel):
    """Represents a code repository."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Repository name")
    full_name: str = Field(description="Full name (org/repo)")
    description: Optional[str] = Field(default=None, description="Description")
    url: Optional[str] = Field(default=None, description="Repository URL")
    default_branch: str = Field(default="main", description="Default branch")
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    topics: List[str] = Field(default_factory=list, description="Topics/tags")
    created_at: Optional[datetime] = Field(default=None, description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    stars_count: int = Field(default=0, description="Number of stars")
    forks_count: int = Field(default=0, description="Number of forks")


# ============================================================================
# UNIFIED PROJECT DATA (Combines Functional + Technical)
# ============================================================================

class ProjectData(BaseModel):
    """
    Unified project data structure combining functional and technical documentation.
    
    All connectors must return this structure:
    - Ticketing connectors: Populate functional_data
    - Git connectors: Populate technical_data
    - Hybrid connectors: Can populate both
    
    This allows templates to access standardized data regardless of source.
    """
    model_config = ConfigDict(extra="allow")
    
    # Standardized outputs by documentation type
    functional_data: Optional[FunctionalData] = Field(
        default=None, 
        description="Functional documentation (epics, features, stories) from ticketing systems"
    )
    technical_data: Optional[TechnicalData] = Field(
        default=None,
        description="Technical documentation (commits, PRs, code) from Git repositories"
    )
    
    # Repository and releases (common to both types)
    repository: Repository = Field(description="Repository information")
    releases: List[Release] = Field(default_factory=list, description="List of releases")
    
    # Collection metadata
    collected_at: datetime = Field(default_factory=datetime.now, description="Collection timestamp")
    source_type: SourceType = Field(description="Source type")
    source_config: Dict[str, Any] = Field(default_factory=dict, description="Connector config")
    
    def has_functional_data(self) -> bool:
        """Checks if functional documentation is available."""
        return self.functional_data is not None
    
    def has_technical_data(self) -> bool:
        """Checks if technical documentation is available."""
        return self.technical_data is not None
    
    def get_documentation_types(self) -> List[str]:
        """Returns available documentation types."""
        types = []
        if self.has_functional_data():
            types.append("functional")
        if self.has_technical_data():
            types.append("technical")
        if not types:
            types.append("legacy")
        return types
    
    def get_latest_release(self) -> Optional[Release]:
        """Returns the latest published release."""
        published_releases = [r for r in self.releases if r.published_at and not r.is_draft]
        if not published_releases:
            return None
        return max(published_releases, key=lambda r: r.published_at)