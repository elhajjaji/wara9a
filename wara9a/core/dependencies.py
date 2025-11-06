"""
Automatic dependency manager for Wara9a.

Automatically installs required dependencies according to
connectors and generators used in configuration.
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
    Automatic dependency manager.
    
    Analyse la configuration et installe automatiquement
    required dependencies for used connectors.
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
        Initializes dependency manager.
        
        Args:
            auto_install: Automatically installs missing dependencies
            dry_run: Mode simulation (n'installe rien)
        """
        self.auto_install = auto_install
        self.dry_run = dry_run
        self._missing_dependencies: Set[str] = set()
    
    def check_config_dependencies(self, config: Wara9aConfig) -> Dict[str, List[str]]:
        """
        Checks required dependencies for a configuration.
        
        Args:
            config: Configuration Wara9a
            
        Returns:
            Dictionary of missing dependencies by category
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
        Automatically installs missing dependencies.
        
        Args:
            config: Configuration Wara9a
            
        Returns:
            True if all dependencies are satisfied
        """
        missing = self.check_config_dependencies(config)
        
        if not any(missing.values()):
            logger.info("✅ All dependencies are already installed")
            return True
        
        logger.info("🔍 Missing dependencies detected:")
        if missing["connectors"]:
            logger.info(f"  • Connecteurs: {', '.join(missing['connectors'])}")
        if missing["generators"]: 
            logger.info(f"  • Generators: {', '.join(missing['generators'])}")
        
        if not self.auto_install:
            logger.warning("⚠️ Automatic installation disabled")
            return False
        
        if self.dry_run:
            logger.info("🔄 Simulation mode - packages to install:")
            for package in missing["packages"]:
                logger.info(f"  • {package}")
            return True
        
        # Installation des packages
        logger.info("📦 Installing missing dependencies...")
        success = self._install_packages(missing["packages"])
        
        if success:
            logger.info("✅ Dependencies installed successfully")
            # Check again
            missing_after = self.check_config_dependencies(config)
            return not any(missing_after.values())
        else:
            logger.error("❌ Dependencies installation failed")
            return False
    
    def _check_import(self, module_name: str) -> bool:
        """Checks if a module can be imported."""
        try:
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False
    
    def _install_packages(self, packages: List[str]) -> bool:
        """
        Installe une liste de packages avec pip.
        
        Args:
            packages: List of packages to install
            
        Returns:
            True if installation succeeds
        """
        if not packages:
            return True
        
        try:
            cmd = [sys.executable, "-m", "pip", "install"] + packages
            logger.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode == 0:
                logger.info("📦 Installation completed successfully")
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
        Generate manual installation suggestions.
        
        Args:
            config: Configuration Wara9a
            
        Returns:
            List of suggested installation commands
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
        Check dependencies for a Wara9a project.
        
        Args:
            config_path: Path to wara9a.yml (default: search automatically)
            
        Returns:
            Dependencies report
        """
        try:
            if config_path is None:
                config_path = Path.cwd() / "wara9a.yml"
            
            if not config_path.exists():
                return {
                    "status": "no_config",
                    "message": f"Configuration file not found: {config_path}"
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
                "message": f"Verification error: {e}"
            }


def auto_check_and_install(config: Optional[Wara9aConfig] = None, 
                          config_path: Optional[Path] = None,
                          auto_install: bool = True) -> bool:
    """
    Utility function to check and automatically install dependencies.
    
    Args:
        config: Configuration Wara9a (optionnel)
        config_path: Chemin vers wara9a.yml (optionnel)
        auto_install: Automatically install missing dependencies
        
    Returns:
        True if all dependencies are satisfied
    """
    if config is None:
        if config_path is None:
            config_path = Path.cwd() / "wara9a.yml"
        
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_path}")
            return True  # No config = no special dependencies
        
        config = Wara9aConfig.load_from_file(config_path)
    
    manager = DependencyManager(auto_install=auto_install)
    return manager.auto_install_dependencies(config)