"""
Main Project class for managing a Wara9a project.

Main entry point that orchestrates data collection,
template application and document generation.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from wara9a.core.config import Wara9aConfig, create_default_config
from wara9a.core.models import ProjectData
from wara9a.core.connector_registry import ConnectorRegistry
from wara9a.core.template_engine import TemplateEngine
from wara9a.core.dependencies import auto_check_and_install
from wara9a.generators.markdown import MarkdownGenerator
from wara9a.generators.html import HTMLGenerator


logger = logging.getLogger(__name__)


class Project:
    """
    Represents a complete Wara9a project.
    
    Orchestrates data collection from various sources,
    template application and final document generation.
    """
    
    def __init__(self, config_path: Optional[Path] = None, config: Optional[Wara9aConfig] = None):
        """
        Initialize a Wara9a project.
        
        Args:
            config_path: Path to the wara9a.yml file
            config: Direct Wara9aConfig configuration (alternative to config_path)
        """
        if config:
            self.config = config
            self.config_path = None
        elif config_path:
            self.config_path = Path(config_path)
            self.config = Wara9aConfig.load_from_file(self.config_path)
        else:
            # Look for wara9a.yml in current directory
            default_path = Path.cwd() / "wara9a.yml"
            if default_path.exists():
                self.config_path = default_path
                self.config = Wara9aConfig.load_from_file(default_path)
            else:
                raise FileNotFoundError(
                    "No configuration file found. "
                    "Use 'wara9a init' to create a project or specify the path."
                )
        
        # Initialize components
        self.connector_registry = ConnectorRegistry()
        self.template_engine = TemplateEngine()
        self.generators = {
            "markdown": MarkdownGenerator(),
            "html": HTMLGenerator(),
        }
        
        # Collected data
        self._project_data: Optional[ProjectData] = None
        
        # Log configuration
        logging.basicConfig(level=getattr(logging, self.config.log_level.upper()))
        
        # Check and install dependencies automatically
        logger.info(f"Wara9a project initialized: {self.config.project.name}")
        logger.debug("Checking dependencies...")
        
        try:
            auto_install = getattr(self.config, 'auto_install_deps', True)
            auto_check_and_install(config=self.config, auto_install=auto_install)
        except Exception as e:
            logger.warning(f"Unable to check dependencies automatically: {e}")
            logger.info("You can check them manually with 'wara9a deps check'")
    
    @classmethod
    def create_new(cls, 
                   project_name: str,
                   project_dir: Optional[Path] = None,
                   config_dict: Optional[Dict[str, Any]] = None) -> "Project":
        """
        Creates a new Wara9a project with default configuration.
        
        Args:
            project_name: Nom du projet
            project_dir: Project directory (default: current directory)
            config_dict: Custom configuration to merge
        
        Returns:
            Configured Project instance
        """
        if project_dir is None:
            project_dir = Path.cwd()
        
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default configuration
        config = create_default_config(project_name, project_dir)
        
        # Merge custom configuration if provided
        if config_dict:
            # TODO: Implement smart merge
            pass
        
        # Save configuration
        config_path = project_dir / "wara9a.yml"
        config.save_to_file(config_path)
        
        logger.info(f"New project created: {config_path}")
        return cls(config_path=config_path)
    
    def collect_data(self, force_refresh: bool = False) -> ProjectData:
        """
        Collects data from all configured sources.
        
        Args:
            force_refresh: Force collection even if cache is valid
        
        Returns:
            Normalized project data
        """
        logger.info("Starting data collection")
        
        # TODO: Implement cache
        if not force_refresh and self._project_data:
            logger.info("Using cached data")
            return self._project_data
        
        all_data = []
        
        # Collect from each enabled source
        for source_config in self.config.get_enabled_sources():
            logger.info(f"Collecting from {source_config.type}: {source_config.name or 'Unnamed'}")
            
            try:
                # Get appropriate connector
                connector = self.connector_registry.get_connector(source_config.type)
                
                # Collect data
                source_data = connector.collect(source_config)
                all_data.append(source_data)
                
                logger.info(f"Collection complete: {len(source_data.commits)} commits, "
                          f"{len(source_data.issues)} issues, "
                          f"{len(source_data.pull_requests)} PRs")
                
            except Exception as e:
                logger.error(f"Erreur lors de la collecte depuis {source_config.type}: {e}")
                if not self.config.get("continue_on_error", True):
                    raise
        
        # Merge all data
        # For now, we take the first source as base
        # TODO: Implement real smart merge
        if all_data:
            self._project_data = all_data[0]
            logger.info("Data collection completed successfully")
        else:
            logger.warning("No data collected")
            # Create empty data to avoid errors
            from wara9a.core.models import Repository, ProjectData, SourceType
            self._project_data = ProjectData(
                repository=Repository(
                    name=self.config.project.name,
                    full_name=self.config.project.name,
                    description=self.config.project.description
                ),
                source_type=SourceType.LOCAL_FILES
            )
        
        return self._project_data
    
    def generate_documents(self, 
                          templates: Optional[List[str]] = None,
                          output_dir: Optional[Path] = None) -> List[Path]:
        """
        Generates all documents according to configuration.
        
        Args:
            templates: List of templates to use (default: all enabled)
            output_dir: Output directory (default: config.output.directory)
        
        Returns:
            List of generated files
        """
        if not self._project_data:
            self.collect_data()
        
        if output_dir is None:
            output_dir = Path(self.config.output.directory)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean directory if requested
        if self.config.output.clean_before:
            logger.info(f"Nettoyage du dossier de sortie: {output_dir}")
            for file in output_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        
        generated_files = []
        templates_to_use = templates or [t.name for t in self.config.get_enabled_templates()]
        
        logger.info(f"Generating {len(templates_to_use)} documents")
        
        for template_name in templates_to_use:
            # Trouver la configuration du template
            template_config = next(
                (t for t in self.config.templates if t.name == template_name),
                None
            )
            
            if not template_config:
                logger.warning(f"Template not found in configuration: {template_name}")
                continue
            
            if not template_config.enabled:
                logger.info(f"Template disabled: {template_name}")
                continue
            
            try:
                logger.info(f"Generating template: {template_name}")
                
                # Prepare context for template
                context = self._prepare_template_context(template_config)
                
                # Rendre le template
                content = self.template_engine.render(template_name, context, template_config)
                
                # Generate files in requested formats
                for format_name in self.config.output.formats:
                    output_file = output_dir / template_config.output
                    
                    # Ajuster l'extension selon le format
                    if format_name != "markdown":
                        output_file = output_file.with_suffix(f".{format_name}")
                    
                    generator = self.generators.get(format_name)
                    if generator:
                        final_path = generator.generate(content, output_file, context)
                        generated_files.append(final_path)
                        logger.info(f"Document generated: {final_path}")
                    else:
                        logger.error(f"Generator not found for format: {format_name}")
                
            except Exception as e:
                logger.error(f"Error generating template {template_name}: {e}")
                if not self.config.get("continue_on_error", True):
                    raise
        
        logger.info(f"Generation completed: {len(generated_files)} files created")
        return generated_files
    
    def _prepare_template_context(self, template_config) -> Dict[str, Any]:
        """Prepares variable context for a template."""
        context = {
            # Project data
            "project": self.config.project.model_dump(),
            "data": self._project_data.model_dump() if self._project_data else {},
            
            # Helpers et filtres
            "config": self.config.model_dump(),
            "template": template_config.model_dump(),
            
            # Custom template variables
            **template_config.variables,
        }
        
        # Ajouter des helpers utiles
        if self._project_data:
            context.update({
                "latest_release": self._project_data.get_latest_release(),
                "open_issues": self._project_data.get_open_issues(),
                "recent_commits": self._project_data.commits[:10] if self._project_data.commits else [],
            })
        
        return context
    
    def validate_config(self) -> List[str]:
        """
        Valide la configuration actuelle.
        
        Returns:
            List of errors found (empty if all OK)
        """
        errors = []
        
        # Valider les sources
        for source in self.config.sources:
            if not self.connector_registry.has_connector(source.type):
                errors.append(f"Connecteur non disponible: {source.type}")
        
        # Valider les templates
        for template in self.config.templates:
            if not self.template_engine.has_template(template.name):
                if not template.template_file:
                    errors.append(f"Template not found: {template.name}")
        
        # Validate generators
        for format_name in self.config.output.formats:
            if format_name not in self.generators:
                errors.append(f"Generator not available: {format_name}")
        
        return errors
    
    def reload_config(self) -> None:
        """Recharge la configuration depuis le fichier."""
        if self.config_path:
            self.config = Wara9aConfig.load_from_file(self.config_path)
            logger.info("Configuration reloaded")
        else:
            logger.warning("Cannot reload: configuration not linked to file")