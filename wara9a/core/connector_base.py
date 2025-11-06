"""
Interface de base pour les connecteurs Wara9a.

Defines the contract that all connectors must respect
to ensure interoperability and data consistency.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from wara9a.core.models import ProjectData
from wara9a.core.config import SourceConfig


class ConnectorBase(ABC):
    """
    Classe de base abstraite pour tous les connecteurs Wara9a.
    
    Each connector must inherit from this class and implement
    abstract methods to collect and normalize data.
    """
    
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