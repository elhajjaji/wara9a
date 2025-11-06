"""
Configuration and validation of Wara9a parameters.

Manages the wara9a.yml file and configuration validation.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from enum import Enum

import yaml
from pydantic import BaseModel, Field, ConfigDict, validator


class OutputFormat(str, Enum):
    """Supported output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class SourceConfig(BaseModel):
    """Data source configuration."""
    model_config = ConfigDict(extra="allow")
    
    type: str = Field(description="Type de connecteur (github, jira, etc.)")
    name: Optional[str] = Field(default=None, description="Nom de la source")
    enabled: bool = Field(default=True, description="Source enabled")
    
    # Connector type specific configuration
    # Additional fields are accepted via extra="allow"


class GitHubSourceConfig(SourceConfig):
    """GitHub-specific configuration."""
    type: str = Field(default="github", const=True)
    repo: str = Field(description="Repository au format owner/repo")
    token: Optional[str] = Field(default=None, description="GitHub access token")
    branch: Optional[str] = Field(default=None, description="Branch to analyze")
    include_forks: bool = Field(default=False, description="Inclure les forks")
    max_commits: int = Field(default=100, description="Nombre max de commits")
    max_issues: int = Field(default=100, description="Nombre max d'issues")
    
    @validator('token', pre=True)
    def resolve_token(cls, v):
        """Resolves environment variables in token."""
        if v and v.startswith('${') and v.endswith('}'):
            env_var = v[2:-1]
            return os.getenv(env_var, v)
        return v


class LocalFilesSourceConfig(SourceConfig):
    """Configuration pour les fichiers locaux."""
    type: str = Field(default="local_files", const=True)
    path: str = Field(description="Chemin vers les fichiers")
    patterns: List[str] = Field(default=["**/*.md", "**/*.txt"], description="Patterns de fichiers")
    encoding: str = Field(default="utf-8", description="Encodage des fichiers")


class TemplateConfig(BaseModel):
    """Configuration d'un template."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Nom du template")
    output: str = Field(description="Fichier de sortie")
    template_file: Optional[str] = Field(default=None, description="Custom template file")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Custom variables")
    enabled: bool = Field(default=True, description="Template enabled")


class OutputConfig(BaseModel):
    """Configuration de la sortie."""
    model_config = ConfigDict(extra="allow")
    
    directory: str = Field(default="output", description="Dossier de sortie")
    formats: List[OutputFormat] = Field(default=[OutputFormat.MARKDOWN], description="Formats de sortie")
    clean_before: bool = Field(default=False, description="Clean before generation")


class ProjectConfig(BaseModel):
    """Configuration du projet."""
    model_config = ConfigDict(extra="allow")
    
    name: str = Field(description="Nom du projet")
    version: Optional[str] = Field(default="1.0.0", description="Version du projet")
    description: Optional[str] = Field(default=None, description="Description du projet")
    author: Optional[str] = Field(default=None, description="Auteur du projet")
    license: Optional[str] = Field(default=None, description="Licence du projet")
    homepage: Optional[str] = Field(default=None, description="Page d'accueil")
    repository: Optional[str] = Field(default=None, description="URL du repository")


class Wara9aConfig(BaseModel):
    """Complete Wara9a configuration."""
    model_config = ConfigDict(extra="allow")
    
    project: ProjectConfig = Field(description="Configuration du projet")
    sources: List[Union[GitHubSourceConfig, LocalFilesSourceConfig, SourceConfig]] = Field(
        description="List of data sources"
    )
    templates: List[TemplateConfig] = Field(description="Liste des templates")
    output: OutputConfig = Field(default_factory=OutputConfig, description="Configuration de sortie")
    
    # Configuration globale
    log_level: str = Field(default="INFO", description="Niveau de log")
    parallel: bool = Field(default=True, description="Parallel processing")
    cache_enabled: bool = Field(default=True, description="Cache enabled")
    cache_ttl: int = Field(default=3600, description="Cache TTL (seconds)")
    auto_install_deps: bool = Field(default=True, description="Automatic dependency installation")
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "Wara9aConfig":
        """Charge la configuration depuis un fichier YAML."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Sauvegarde la configuration dans un fichier YAML."""
        file_path = Path(file_path)
        
        # Convertir en dictionnaire et nettoyer
        data = self.model_dump(exclude_unset=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    def get_enabled_sources(self) -> List[SourceConfig]:
        """Returns enabled sources."""
        return [source for source in self.sources if source.enabled]
    
    def get_enabled_templates(self) -> List[TemplateConfig]:
        """Returns enabled templates."""
        return [template for template in self.templates if template.enabled]


def create_default_config(project_name: str, output_dir: str = "output") -> Wara9aConfig:
    """Creates a default configuration."""
    return Wara9aConfig(
        project=ProjectConfig(
            name=project_name,
            version="1.0.0",
            description=f"Documentation automatique pour {project_name}"
        ),
        sources=[
            LocalFilesSourceConfig(
                name="Documentation locale",
                path=".",
                patterns=["README.md", "CHANGELOG.md", "docs/**/*.md"]
            )
        ],
        templates=[
            TemplateConfig(
                name="readme",
                output="README_generated.md"
            )
        ],
        output=OutputConfig(
            directory=output_dir,
            formats=[OutputFormat.MARKDOWN]
        )
    )