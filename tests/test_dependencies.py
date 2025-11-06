"""
Tests pour le gestionnaire de dépendances Wara9a.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from wara9a.core.dependencies import DependencyManager, auto_check_and_install
from wara9a.core.config import create_default_config, GitHubSourceConfig, LocalFilesSourceConfig


class TestDependencyManager:
    """Tests pour le gestionnaire de dépendances."""
    
    def test_manager_initialization(self):
        """Test initialisation du gestionnaire."""
        manager = DependencyManager()
        
        assert manager.auto_install is True
        assert manager.dry_run is False
        assert len(manager.CONNECTOR_DEPENDENCIES) > 0
        assert "github" in manager.CONNECTOR_DEPENDENCIES
    
    def test_check_import_existing_module(self):
        """Test vérification d'un module existant."""
        manager = DependencyManager()
        
        # sys est toujours disponible
        assert manager._check_import("sys") is True
        assert manager._check_import("os") is True
    
    def test_check_import_nonexistent_module(self):
        """Test vérification d'un module inexistant."""
        manager = DependencyManager()
        
        assert manager._check_import("nonexistent_module_123456") is False
    
    def test_check_config_with_local_files_only(self):
        """Test configuration avec seulement des fichiers locaux."""
        config = create_default_config("Test Project")
        config.sources = [
            LocalFilesSourceConfig(
                name="Local files",
                path=".",
                patterns=["README.md"]
            )
        ]
        
        manager = DependencyManager()
        missing = manager.check_config_dependencies(config)
        
        # Pas de dépendances manquantes pour les fichiers locaux
        assert len(missing["connectors"]) == 0
        assert len(missing["packages"]) == 0
    
    def test_check_config_with_github(self):
        """Test configuration avec GitHub."""
        config = create_default_config("Test Project")
        config.sources = [
            GitHubSourceConfig(
                name="GitHub repo",
                repo="test/repo",
                token="fake_token"
            )
        ]
        
        manager = DependencyManager()
        
        with patch.object(manager, '_check_import', return_value=False):
            missing = manager.check_config_dependencies(config)
            
            assert "github" in missing["connectors"]
            assert any("pygithub" in pkg for pkg in missing["packages"])
    
    def test_suggest_manual_install(self):
        """Test génération des suggestions d'installation manuelle."""
        config = create_default_config("Test Project")
        config.sources = [
            GitHubSourceConfig(repo="test/repo"),
            LocalFilesSourceConfig(path=".")
        ]
        
        manager = DependencyManager()
        
        with patch.object(manager, '_check_import', return_value=False):
            suggestions = manager.suggest_manual_install(config)
            
            assert len(suggestions) > 0
            assert any("connectors-github" in suggestion for suggestion in suggestions)
    
    def test_check_project_dependencies_no_config(self, tmp_path):
        """Test vérification sans fichier de configuration."""
        nonexistent_path = tmp_path / "nonexistent.yml"
        
        report = DependencyManager.check_project_dependencies(nonexistent_path)
        
        assert report["status"] == "no_config"
        assert "non trouvé" in report["message"]
    
    @patch('subprocess.run')
    def test_install_packages_success(self, mock_run):
        """Test installation réussie de packages."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        
        manager = DependencyManager(dry_run=False)
        result = manager._install_packages(["fake-package>=1.0.0"])
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_install_packages_failure(self, mock_run):
        """Test échec d'installation de packages."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")
        
        manager = DependencyManager(dry_run=False)
        result = manager._install_packages(["nonexistent-package"])
        
        assert result is False
        mock_run.assert_called_once()
    
    def test_dry_run_mode(self):
        """Test mode simulation."""
        config = create_default_config("Test Project")
        config.sources = [GitHubSourceConfig(repo="test/repo")]
        
        manager = DependencyManager(auto_install=True, dry_run=True)
        
        with patch.object(manager, '_check_import', return_value=False):
            # En mode dry-run, ça devrait toujours retourner True
            result = manager.auto_install_dependencies(config)
            assert result is True


class TestAutoCheckAndInstall:
    """Tests pour la fonction utilitaire auto_check_and_install."""
    
    def test_auto_check_no_config_file(self, tmp_path):
        """Test sans fichier de configuration."""
        # Changer vers un dossier temporaire sans wara9a.yml
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            
            # Devrait retourner True (pas d'erreur) car pas de config = pas de dépendances
            result = auto_check_and_install()
            assert result is True
            
        finally:
            os.chdir(original_cwd)
    
    def test_auto_check_with_config(self, tmp_path):
        """Test avec configuration fournie."""
        config = create_default_config("Test Project")
        
        # Avec seulement des fichiers locaux, ça devrait toujours passer
        result = auto_check_and_install(config=config, auto_install=False)
        assert result is True
    
    @patch('wara9a.core.dependencies.DependencyManager.auto_install_dependencies')
    def test_auto_check_delegates_to_manager(self, mock_auto_install):
        """Test que la fonction délègue au manager."""
        mock_auto_install.return_value = True
        
        config = create_default_config("Test Project")
        result = auto_check_and_install(config=config, auto_install=True)
        
        assert result is True
        mock_auto_install.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])