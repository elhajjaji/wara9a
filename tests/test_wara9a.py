"""
Tests basiques pour Wara9a.

Tests unitaires pour valider les composants principaux.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone

from wara9a.core.config import create_default_config, Wara9aConfig
from wara9a.core.models import Repository, Author, Commit, SourceType
from wara9a.core.connector_registry import ConnectorRegistry
from wara9a.connectors.local_files import LocalFilesConnector


class TestConfig:
    """Tests pour la configuration Wara9a."""
    
    def test_create_default_config(self):
        """Test creating a default configuration."""
        config = create_default_config("Test Project")
        
        assert config.project.name == "Test Project"
        assert config.project.version == "1.0.0"
        assert len(config.sources) >= 1
        assert len(config.templates) >= 1
        assert config.output.directory == "output"
    
    def test_config_serialization(self, tmp_path):
        """Test configuration serialization/deserialization."""
        config = create_default_config("Test Project")
        config_file = tmp_path / "test_wara9a.yml"
        
        # Sauvegarder
        config.save_to_file(config_file)
        assert config_file.exists()
        
        # Recharger
        loaded_config = Wara9aConfig.load_from_file(config_file)
        assert loaded_config.project.name == config.project.name
        assert len(loaded_config.sources) == len(config.sources)


class TestModels:
    """Tests for data models."""
    
    def test_author_model(self):
        """Test Author model."""
        author = Author(
            name="John Doe",
            email="john@example.com",
            username="johndoe"
        )
        
        assert author.name == "John Doe"
        assert author.email == "john@example.com"
        assert author.username == "johndoe"
    
    def test_commit_model(self):
        """Test Commit model."""
        author = Author(name="Jane Doe", email="jane@example.com")
        commit = Commit(
            sha="abc123",
            message="Initial commit",
            author=author,
            date=datetime.now(timezone.utc)
        )
        
        assert commit.sha == "abc123"
        assert commit.message == "Initial commit"
        assert commit.author.name == "Jane Doe"
    
    def test_repository_model(self):
        """Test Repository model."""
        repo = Repository(
            name="test-repo",
            full_name="user/test-repo",
            description="A test repository"
        )
        
        assert repo.name == "test-repo"
        assert repo.full_name == "user/test-repo"
        assert repo.description == "A test repository"


class TestConnectorRegistry:
    """Tests pour le registre des connecteurs."""
    
    def test_registry_initialization(self):
        """Test initialisation du registre."""
        registry = ConnectorRegistry()
        
        # Check that connectors are loaded
        connector_types = registry.list_connector_types()
        assert len(connector_types) >= 1
    
    def test_get_local_connector(self):
        """Test getting local connector."""
        registry = ConnectorRegistry()
        
        connector = registry.get_connector("local_files")
        assert isinstance(connector, LocalFilesConnector)
        assert connector.connector_type == "local_files"


class TestLocalFilesConnector:
    """Tests pour le connecteur fichiers locaux."""
    
    def test_connector_properties(self):
        """Test connector properties."""
        connector = LocalFilesConnector()
        
        assert connector.connector_type == "local_files"
        assert connector.display_name == "Fichiers locaux"
        assert "path" in connector.required_config_fields
    
    def test_validate_config(self, tmp_path):
        """Test validation de la configuration."""
        connector = LocalFilesConnector()
        
        # Configuration valide
        from wara9a.core.config import SourceConfig
        valid_config = SourceConfig(type="local_files", path=str(tmp_path))
        errors = connector.validate_config(valid_config)
        assert len(errors) == 0
        
        # Configuration invalide
        invalid_config = SourceConfig(type="local_files", path="/nonexistent/path")
        errors = connector.validate_config(invalid_config)
        assert len(errors) > 0


class TestTemplateEngine:
    """Tests pour le moteur de templates."""
    
    def test_builtin_templates(self):
        """Test built-in templates."""
        from wara9a.core.template_engine import TemplateEngine
        
        engine = TemplateEngine()
        builtin_templates = engine.list_builtin_templates()
        
        assert "readme" in builtin_templates
        assert "changelog" in builtin_templates
    
    def test_template_rendering(self):
        """Test rendu d'un template."""
        from wara9a.core.template_engine import TemplateEngine
        
        engine = TemplateEngine()
        
        context = {
            "project": {"name": "Test Project"},
            "data": {"repository": {"languages": ["Python"]}},
            "open_issues": [],
            "recent_commits": []
        }
        
        # Rendre le template README
        rendered = engine.render("readme", context)
        assert "Test Project" in rendered
        assert len(rendered) > 0


if __name__ == "__main__":
    pytest.main([__file__])