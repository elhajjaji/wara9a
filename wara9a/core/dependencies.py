"""
Gestionnaire automatique des dépendances Wara9a.

Installe automatiquement les dépendances nécessaires selon
les connecteurs et générateurs utilisés dans la configuration.
"""

import subprocess
import sys
import logging
from typing import Dict, List, Set, Optional
from pathlib import Path
import importlib.util

from wara9a.core.config import Wara9aConfig


logger = logging.getLogger(__name__)


class DependencyManager:
    """
    Gestionnaire des dépendances automatiques.
    
    Analyse la configuration et installe automatiquement
    les dépendances nécessaires pour les connecteurs utilisés.
    """
    
    # Mapping of connectors to their dependencies
    CONNECTOR_DEPENDENCIES = {
        "github": {
            "packages": ["pygithub>=1.58.0", "requests>=2.28.0"],
            "optional_group": "connectors-github",
            "test_import": "github"
        },
        "jira": {
            "packages": ["jira>=3.4.0", "requests>=2.28.0"],
            "optional_group": "connectors-jira", 
            "test_import": "jira"
        },
        "azure_devops": {
            "packages": ["azure-devops>=7.0.0"],
            "optional_group": "connectors-azure",
            "test_import": "azure.devops"
        }
    }
    
    # Mapping of generators to their dependencies  
    GENERATOR_DEPENDENCIES = {
        "pdf": {
            "packages": ["reportlab>=4.0.0", "weasyprint>=59.0"],
            "optional_group": "generators-pdf",
            "test_import": "reportlab"
        },
        "advanced_markdown": {
            "packages": ["markdown>=3.5.0", "python-markdown-math>=0.8"],
            "optional_group": "generators-advanced",
            "test_import": "markdown"
        },
        "docx": {
            "packages": ["python-docx>=0.8.11"],
            "optional_group": "generators-advanced", 
            "test_import": "docx"
        }
    }
    
    def __init__(self, auto_install: bool = True, dry_run: bool = False):
        """
        Initialise le gestionnaire de dépendances.
        
        Args:
            auto_install: Installe automatiquement les dépendances manquantes
            dry_run: Mode simulation (n'installe rien)
        """
        self.auto_install = auto_install
        self.dry_run = dry_run
        self._missing_dependencies: Set[str] = set()
    
    def check_config_dependencies(self, config: Wara9aConfig) -> Dict[str, List[str]]:
        """
        Vérifie les dépendances nécessaires pour une configuration.
        
        Args:
            config: Configuration Wara9a
            
        Returns:
            Dictionnaire des dépendances manquantes par catégorie
        """
        missing = {
            "connectors": [],
            "generators": [],
            "packages": []
        }
        
        # Check connectors
        for source in config.sources:
            if source.enabled and source.type in self.CONNECTOR_DEPENDENCIES:
                deps = self.CONNECTOR_DEPENDENCIES[source.type]
                if not self._check_import(deps["test_import"]):
                    missing["connectors"].append(source.type)
                    missing["packages"].extend(deps["packages"])
        
        # Check generators according to output formats
        for format_name in config.output.formats:
            format_str = str(format_name).lower()
            
            if format_str == "pdf" and "pdf" in self.GENERATOR_DEPENDENCIES:
                deps = self.GENERATOR_DEPENDENCIES["pdf"]
                if not self._check_import(deps["test_import"]):
                    missing["generators"].append("pdf")
                    missing["packages"].extend(deps["packages"])
            
            elif format_str in ["html", "markdown"]:
                # Check if we need advanced markdown support
                if "advanced_markdown" in self.GENERATOR_DEPENDENCIES:
                    deps = self.GENERATOR_DEPENDENCIES["advanced_markdown"]
                    if not self._check_import(deps["test_import"]):
                        missing["generators"].append("advanced_markdown")
                        missing["packages"].extend(deps["packages"])
        
        # Deduplicate packages
        missing["packages"] = list(set(missing["packages"]))
        
        return missing
    
    def auto_install_dependencies(self, config: Wara9aConfig) -> bool:
        """
        Installe automatiquement les dépendances manquantes.
        
        Args:
            config: Configuration Wara9a
            
        Returns:
            True si toutes les dépendances sont satisfaites
        """
        missing = self.check_config_dependencies(config)
        
        if not any(missing.values()):
            logger.info("✅ Toutes les dépendances sont déjà installées")
            return True
        
        logger.info("🔍 Dépendances manquantes détectées:")
        if missing["connectors"]:
            logger.info(f"  • Connecteurs: {', '.join(missing['connectors'])}")
        if missing["generators"]: 
            logger.info(f"  • Générateurs: {', '.join(missing['generators'])}")
        
        if not self.auto_install:
            logger.warning("⚠️ Installation automatique désactivée")
            return False
        
        if self.dry_run:
            logger.info("🔄 Mode simulation - packages à installer:")
            for package in missing["packages"]:
                logger.info(f"  • {package}")
            return True
        
        # Installation des packages
        logger.info("📦 Installation des dépendances manquantes...")
        success = self._install_packages(missing["packages"])
        
        if success:
            logger.info("✅ Dépendances installées avec succès")
            # Check again
            missing_after = self.check_config_dependencies(config)
            return not any(missing_after.values())
        else:
            logger.error("❌ Échec de l'installation des dépendances")
            return False
    
    def _check_import(self, module_name: str) -> bool:
        """Vérifie si un module peut être importé."""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False
    
    def _install_packages(self, packages: List[str]) -> bool:
        """
        Installe une liste de packages avec pip.
        
        Args:
            packages: Liste des packages à installer
            
        Returns:
            True si l'installation réussit
        """
        if not packages:
            return True
        
        try:
            cmd = [sys.executable, "-m", "pip", "install"] + packages
            logger.info(f"Exécution: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode == 0:
                logger.info("📦 Installation terminée avec succès")
                if result.stdout:
                    logger.debug(f"Sortie pip: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Erreur pip (code {result.returncode})")
                if result.stderr:
                    logger.error(f"Erreur: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout lors de l'installation")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue lors de l'installation: {e}")
            return False
    
    def suggest_manual_install(self, config: Wara9aConfig) -> List[str]:
        """
        Génère des suggestions d'installation manuelle.
        
        Args:
            config: Configuration Wara9a
            
        Returns:
            Liste des commandes d'installation suggérées
        """
        missing = self.check_config_dependencies(config)
        suggestions = []
        
        if not any(missing.values()):
            return suggestions
        
        # Grouper par optional groups pour des installations plus efficaces
        groups_needed = set()
        
        for connector in missing["connectors"]:
            if connector in self.CONNECTOR_DEPENDENCIES:
                group = self.CONNECTOR_DEPENDENCIES[connector]["optional_group"]
                groups_needed.add(group)
        
        for generator in missing["generators"]:
            if generator in self.GENERATOR_DEPENDENCIES:
                group = self.GENERATOR_DEPENDENCIES[generator]["optional_group"]
                groups_needed.add(group)
        
        if groups_needed:
            # Installation by optional groups (recommended)
            groups_list = ",".join(sorted(groups_needed))
            suggestions.append(f"pip install wara9a[{groups_list}]")
        
        if missing["packages"]:
            # Installation directe des packages (fallback)
            packages_str = " ".join(missing["packages"])
            suggestions.append(f"pip install {packages_str}")
        
        return suggestions
    
    @classmethod
    def check_project_dependencies(cls, config_path: Optional[Path] = None) -> Dict[str, any]:
        """
        Vérifie les dépendances d'un projet Wara9a.
        
        Args:
            config_path: Chemin vers wara9a.yml (défaut: cherche automatiquement)
            
        Returns:
            Rapport des dépendances
        """
        try:
            if config_path is None:
                config_path = Path.cwd() / "wara9a.yml"
            
            if not config_path.exists():
                return {
                    "status": "no_config",
                    "message": f"Fichier de configuration non trouvé: {config_path}"
                }
            
            config = Wara9aConfig.load_from_file(config_path)
            manager = cls(auto_install=False)
            missing = manager.check_config_dependencies(config)
            
            return {
                "status": "ok" if not any(missing.values()) else "missing_deps",
                "config_path": str(config_path),
                "missing": missing,
                "suggestions": manager.suggest_manual_install(config)
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Erreur lors de la vérification: {e}"
            }


def auto_check_and_install(config: Optional[Wara9aConfig] = None, 
                          config_path: Optional[Path] = None,
                          auto_install: bool = True) -> bool:
    """
    Fonction utilitaire pour vérifier et installer automatiquement les dépendances.
    
    Args:
        config: Configuration Wara9a (optionnel)
        config_path: Chemin vers wara9a.yml (optionnel)
        auto_install: Installer automatiquement les dépendances manquantes
        
    Returns:
        True si toutes les dépendances sont satisfaites
    """
    if config is None:
        if config_path is None:
            config_path = Path.cwd() / "wara9a.yml"
        
        if not config_path.exists():
            logger.warning(f"Fichier de configuration non trouvé: {config_path}")
            return True  # No config = no special dependencies
        
        config = Wara9aConfig.load_from_file(config_path)
    
    manager = DependencyManager(auto_install=auto_install)
    return manager.auto_install_dependencies(config)