"""
Interface de base pour les connecteurs Wara9a.

Defines the contract that all connectors must respect
to ensure interoperability and data consistency.

Two main connector categories:
- TicketingConnector: For functional documentation (epics, features, stories)
- GitConnector: For technical documentation (commits, PRs, code)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum

from wara9a.core.models import ProjectData
from wara9a.core.config import SourceConfig


class ConnectorCategory(str, Enum):
    """Connector categories based on documentation type."""
    TICKETING = "ticketing"  # Functional documentation (Jira, Azure DevOps)
    GIT = "git"              # Technical documentation (GitHub, GitLab)
    FILES = "files"          # Local files and documents
    CUSTOM = "custom"        # Custom connectors


class ConnectorBase(ABC):
    """
    Classe de base abstraite pour tous les connecteurs Wara9a.
    
    Each connector must inherit from this class and implement
    abstract methods to collect and normalize data.
    """
    
    @property
    @abstractmethod
    def category(self) -> ConnectorCategory:
        """
        Returns the connector category.
        
        - TICKETING: Functional documentation from ticketing systems
        - GIT: Technical documentation from Git repositories
        - FILES: Documentation from local files
        """
        pass
    
    @property
    @abstractmethod
    def connector_type(self) -> str:
        """Retourne le type du connecteur (ex: 'github', 'jira')."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Retourne le nom d'affichage du connecteur."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Retourne la description du connecteur."""
        pass
    
    @property
    @abstractmethod
    def required_config_fields(self) -> List[str]:
        """Retourne la liste des champs obligatoires dans la configuration."""
        pass
    
    @property
    def optional_config_fields(self) -> List[str]:
        """Retourne la liste des champs optionnels dans la configuration."""
        return []
    
    @abstractmethod
    def validate_config(self, config: SourceConfig) -> List[str]:
        """
        Valide la configuration du connecteur.
        
        Args:
            config: Configuration de la source
            
        Returns:
            Liste des erreurs de validation (vide si OK)
        """
        pass
    
    @abstractmethod
    def collect(self, config: SourceConfig) -> ProjectData:
        """
        Collects data from configured source.
        
        Args:
            config: Configuration de la source
            
        Returns:
            Normalized project data
            
        Raises:
            ConnectionError: If unable to connect to source
            ValueError: Si la configuration est invalide
            Exception: Pour toute autre erreur
        """
        pass
    
    def test_connection(self, config: SourceConfig) -> bool:
        """
        Tests connection to source without collecting data.
        
        Args:
            config: Configuration de la source
            
        Returns:
            True if connection succeeds, False otherwise
        """
        try:
            # By default, try limited collection
            test_config = config.model_copy()
            # Limit data for test
            if hasattr(test_config, 'max_commits'):
                test_config.max_commits = 1
            if hasattr(test_config, 'max_issues'):
                test_config.max_issues = 1
                
            self.collect(test_config)
            return True
        except Exception:
            return False
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Returns JSON Schema configuration schema for this connector.
        
        Useful for validation and UI generation.
        """
        schema = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "const": self.connector_type
                },
                "name": {
                    "type": "string",
                    "description": "Nom de la source"
                },
                "enabled": {
                    "type": "boolean",
                    "default": True,
                    "description": "Source enabled"
                }
            },
            "required": ["type"] + self.required_config_fields
        }
        
        return schema
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.connector_type})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.connector_type}>"


class ConnectorError(Exception):
    """Exception de base pour les erreurs de connecteur."""
    pass


class ConnectorConfigError(ConnectorError):
    """Erreur de configuration d'un connecteur."""
    pass


class ConnectorConnectionError(ConnectorError):
    """Erreur de connexion d'un connecteur."""
    pass


class TicketingConnector(ConnectorBase):
    """
    Base class for ticketing system connectors.
    
    These connectors extract functional documentation:
    - Epics, features, user stories
    - Sprint planning and roadmap
    - Business requirements
    
    Examples: Jira, Azure DevOps, Linear, Asana
    
    IMPORTANT: All ticketing connectors must populate ProjectData.functional_data
    with standardized Epic, Feature, UserStory, and Requirement objects.
    """
    
    @property
    def category(self) -> ConnectorCategory:
        """Ticketing connectors provide functional documentation."""
        return ConnectorCategory.TICKETING
    
    @property
    def documentation_type(self) -> str:
        """Returns the documentation type provided by this connector."""
        return "Functional Documentation (Epics, Features, Stories)"
    
    @property
    def standard_output_fields(self) -> List[str]:
        """
        Returns the standard output fields that must be populated.
        
        All ticketing connectors should populate:
        - ProjectData.functional_data.epics
        - ProjectData.functional_data.features
        - ProjectData.functional_data.user_stories
        - ProjectData.functional_data.requirements
        """
        return ["functional_data.epics", "functional_data.features", 
                "functional_data.user_stories", "functional_data.requirements"]


class GitConnector(ConnectorBase):
    """
    Base class for Git repository connectors.
    
    These connectors extract technical documentation:
    - Commits history and code changes
    - Pull/Merge requests and code reviews
    - Repository structure and architecture
    - API documentation from code
    
    Examples: GitHub, GitLab, Bitbucket
    
    IMPORTANT: All Git connectors must populate ProjectData.technical_data
    with standardized TechnicalCommit, TechnicalPullRequest, CodeMetrics objects.
    """
    
    @property
    def category(self) -> ConnectorCategory:
        """Git connectors provide technical documentation."""
        return ConnectorCategory.GIT
    
    @property
    def documentation_type(self) -> str:
        """Returns the documentation type provided by this connector."""
        return "Technical Documentation (Commits, PRs, Code)"
    
    @property
    def standard_output_fields(self) -> List[str]:
        """
        Returns the standard output fields that must be populated.
        
        All Git connectors should populate:
        - ProjectData.technical_data.commits (TechnicalCommit objects)
        - ProjectData.technical_data.pull_requests (TechnicalPullRequest objects)
        - ProjectData.technical_data.code_metrics (CodeMetrics by language)
        - ProjectData.technical_data.technical_debt (Optional)
        """
        return ["technical_data.commits", "technical_data.pull_requests",
                "technical_data.code_metrics", "technical_data.technical_debt"]


class FilesConnector(ConnectorBase):
    """
    Base class for file-based connectors.
    
    These connectors extract documentation from files:
    - README, CHANGELOG
    - Documentation directories
    - Configuration files
    
    Examples: Local files, cloud storage
    """
    
    @property
    def category(self) -> ConnectorCategory:
        """Files connectors provide file-based documentation."""
        return ConnectorCategory.FILES
    
    @property
    def documentation_type(self) -> str:
        """Returns the documentation type provided by this connector."""
        return "File-based Documentation"