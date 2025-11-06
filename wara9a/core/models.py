"""
Pydantic data models for Wara9a.

These models define the normalized structure that all connectors
must produce and that templates consume.
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


class Author(BaseModel):
    """Represents an author (commit, issue, etc.)."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Nom complet de l'auteur")
    email: Optional[str] = Field(default=None, description="Email de l'auteur")
    username: Optional[str] = Field(default=None, description="Nom d'utilisateur")
    avatar_url: Optional[str] = Field(default=None, description="URL de l'avatar")


class Label(BaseModel):
    """Represents a label/tag."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Nom du label")
    color: Optional[str] = Field(default=None, description="Hexadecimal color")
    description: Optional[str] = Field(default=None, description="Description")


class Commit(BaseModel):
    """Represents a git commit."""
    model_config = ConfigDict(extra="allow")
    
    sha: str = Field(description="Hash du commit")
    message: str = Field(description="Message de commit")
    author: Author = Field(description="Auteur du commit")
    date: datetime = Field(description="Date du commit")
    url: Optional[str] = Field(default=None, description="URL du commit")
    files_changed: List[str] = Field(default_factory=list, description="Modified files")
    additions: int = Field(default=0, description="Added lines")
    deletions: int = Field(default=0, description="Deleted lines")


class Issue(BaseModel):
    """Represents an issue/ticket."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Identifiant unique")
    title: str = Field(description="Issue title")
    description: Optional[str] = Field(default=None, description="Description")
    status: IssueStatus = Field(description="Current status")
    type: IssueType = Field(description="Issue type")
    author: Author = Field(description="Issue creator")
    assignee: Optional[Author] = Field(default=None, description="Assignee")
    labels: List[Label] = Field(default_factory=list, description="Labels")
    created_at: datetime = Field(description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last update")
    closed_at: Optional[datetime] = Field(default=None, description="Closing date")
    url: Optional[str] = Field(default=None, description="Issue URL")
    comments_count: int = Field(default=0, description="Nombre de commentaires")


class PullRequest(BaseModel):
    """Represents a pull/merge request."""
    model_config = ConfigDict(extra="allow")
    
    id: str = Field(description="Identifiant unique")
    title: str = Field(description="Titre de la PR")
    description: Optional[str] = Field(default=None, description="Description")
    author: Author = Field(description="Auteur de la PR")
    status: str = Field(description="Statut (open, closed, merged)")
    source_branch: str = Field(description="Branche source")
    target_branch: str = Field(description="Branche cible")
    created_at: datetime = Field(description="Creation date")
    merged_at: Optional[datetime] = Field(default=None, description="Date de merge")
    url: Optional[str] = Field(default=None, description="URL de la PR")
    commits: List[Commit] = Field(default_factory=list, description="Commits inclus")
    files_changed: int = Field(default=0, description="Number of modified files")
    additions: int = Field(default=0, description="Added lines")
    deletions: int = Field(default=0, description="Deleted lines")


class Release(BaseModel):
    """Represents a release/version."""
    model_config = ConfigDict(extra="allow")
    
    tag: str = Field(description="Tag de version")
    name: str = Field(description="Nom de la release")
    description: Optional[str] = Field(default=None, description="Notes de release")
    author: Author = Field(description="Auteur de la release")
    created_at: datetime = Field(description="Creation date")
    published_at: Optional[datetime] = Field(default=None, description="Date de publication")
    is_prerelease: bool = Field(default=False, description="Pre-release")
    is_draft: bool = Field(default=False, description="Brouillon")
    url: Optional[str] = Field(default=None, description="URL de la release")


class Repository(BaseModel):
    """Represents a code repository."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Nom du repository")
    full_name: str = Field(description="Nom complet (org/repo)")
    description: Optional[str] = Field(default=None, description="Description")
    url: Optional[str] = Field(default=None, description="URL du repository")
    default_branch: str = Field(default="main", description="Branche par défaut")
    languages: List[str] = Field(default_factory=list, description="Langages de programmation")
    topics: List[str] = Field(default_factory=list, description="Topics/tags")
    created_at: Optional[datetime] = Field(default=None, description="Creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Dernière mise à jour")
    stars_count: int = Field(default=0, description="Nombre d'étoiles")
    forks_count: int = Field(default=0, description="Nombre de forks")


class ProjectData(BaseModel):
    """Données normalisées d'un projet, collectées par tous les connecteurs."""
    model_config = ConfigDict(extra="allow")
    
    repository: Repository = Field(description="Informations du repository")
    commits: List[Commit] = Field(default_factory=list, description="Liste des commits")
    issues: List[Issue] = Field(default_factory=list, description="Liste des issues")
    pull_requests: List[PullRequest] = Field(default_factory=list, description="Liste des PRs")
    releases: List[Release] = Field(default_factory=list, description="Liste des releases")
    
    # Collection metadata
    collected_at: datetime = Field(default_factory=datetime.now, description="Date de collecte")
    source_type: SourceType = Field(description="Type de source")
    source_config: Dict[str, Any] = Field(default_factory=dict, description="Config du connecteur")
    
    def get_latest_release(self) -> Optional[Release]:
        """Retourne la dernière release publiée."""
        published_releases = [r for r in self.releases if r.published_at and not r.is_draft]
        if not published_releases:
            return None
        return max(published_releases, key=lambda r: r.published_at)
    
    def get_commits_since(self, date: datetime) -> List[Commit]:
        """Retourne les commits depuis une date donnée."""
        return [c for c in self.commits if c.date >= date]
    
    def get_open_issues(self) -> List[Issue]:
        """Retourne les issues ouvertes."""
        return [i for i in self.issues if i.status == IssueStatus.OPEN]
    
    def get_closed_issues_since(self, date: datetime) -> List[Issue]:
        """Retourne les issues fermées depuis une date."""
        return [
            i for i in self.issues 
            if i.status == IssueStatus.CLOSED and i.closed_at and i.closed_at >= date
        ]