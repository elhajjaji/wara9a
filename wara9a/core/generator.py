"""
Main document generator for Wara9a.

Orchestrates complete document generation
from data collection to final output.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from wara9a.core.project import Project


logger = logging.getLogger(__name__)


class DocumentGenerator:
    """
    Main document generator.
    
    High-level entry point for generating all documents
    of a Wara9a project according to its configuration.
    """
    
    def __init__(self, project: Project):
        """
        Initialize the generator.
        
        Args:
            project: Configured Wara9a project instance
        """
        self.project = project
        self._generation_stats: Optional[Dict[str, Any]] = None
    
    def generate_all(self, 
                     force_refresh: bool = False,
                     output_dir: Optional[Path] = None) -> List[Path]:
        """
        Generate all project documents.
        
        Args:
            force_refresh: Force data re-collection
            output_dir: Custom output directory
            
        Returns:
            List of generated files
            
        Raises:
            Exception: If error during generation
        """
        start_time = datetime.now()
        
        logger.info(f"Starting complete generation for {self.project.config.project.name}")
        
        try:
            # 1. Validate configuration
            errors = self.project.validate_config()
            if errors:
                raise ValueError(f"Invalid configuration: {errors}")
            
            # 2. Collect data
            logger.info("Collecting data...")
            project_data = self.project.collect_data(force_refresh=force_refresh)
            
            # 3. Generate documents
            logger.info("Generating documents...")
            generated_files = self.project.generate_documents(output_dir=output_dir)
            
            # 4. Calculate statistics
            end_time = datetime.now()
            duration = end_time - start_time
            
            self._generation_stats = {
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration.total_seconds(),
                "files_generated": len(generated_files),
                "data_sources": len(self.project.config.get_enabled_sources()),
                "templates_used": len(self.project.config.get_enabled_templates()),
                "commits_processed": len(project_data.commits) if project_data else 0,
                "issues_processed": len(project_data.issues) if project_data else 0,
                "prs_processed": len(project_data.pull_requests) if project_data else 0,
            }
            
            logger.info(f"Generation completed successfully in {duration.total_seconds():.1f}s")
            logger.info(f"Generated files: {len(generated_files)}")
            
            return generated_files
            
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            raise
    
    def generate_template(self, 
                         template_name: str,
                         output_file: Optional[Path] = None,
                         force_refresh: bool = False) -> Path:
        """
        Generate a single specific template.
        
        Args:
            template_name: Name of template to generate
            output_file: Custom output file
            force_refresh: Force data re-collection
            
        Returns:
            Path of generated file
        """
        logger.info(f"Generating template: {template_name}")
        
        # Collect data if necessary
        if not self.project._project_data or force_refresh:
            self.project.collect_data(force_refresh=force_refresh)
        
        # Generate specific template
        generated_files = self.project.generate_documents(templates=[template_name])
        
        if not generated_files:
            raise ValueError(f"No file generated for template: {template_name}")
        
        generated_file = generated_files[0]
        
        # Rename if custom output file is specified
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            generated_file.rename(output_file)
            generated_file = output_file
        
        logger.info(f"Template generated: {generated_file}")
        return generated_file
    
    def get_generation_stats(self) -> Optional[Dict[str, Any]]:
        """
        Return statistics from last generation.
        
        Returns:
            Statistics dictionary or None if no generation
        """
        return self._generation_stats
    
    def preview_generation(self) -> Dict[str, Any]:
        """
        Preview what will be generated without executing generation.
        
        Returns:
            Information about what will be generated
        """
        enabled_sources = self.project.config.get_enabled_sources()
        enabled_templates = self.project.config.get_enabled_templates()
        
        preview = {
            "project_name": self.project.config.project.name,
            "output_directory": self.project.config.output.directory,
            "output_formats": self.project.config.output.formats,
            "sources": [
                {
                    "type": source.type,
                    "name": source.name or "Unnamed",
                    "enabled": source.enabled
                }
                for source in enabled_sources
            ],
            "templates": [
                {
                    "name": template.name,
                    "output": template.output,
                    "custom_template": template.template_file is not None
                }
                for template in enabled_templates
            ],
            "estimated_files": len(enabled_templates) * len(self.project.config.output.formats)
        }
        
        return preview
    
    @classmethod
    def quick_generate(cls,
                      config_path: Optional[Path] = None,
                      project_name: Optional[str] = None,
                      github_repo: Optional[str] = None,
                      output_dir: Optional[Path] = None) -> List[Path]:
        """
        Quick generation with minimal configuration.
        
        Args:
            config_path: Path to wara9a.yml (optional)
            project_name: Project name if no config
            github_repo: GitHub repository in owner/repo format
            output_dir: Output directory
            
        Returns:
            List of generated files
        """
        if config_path and Path(config_path).exists():
            # Use existing configuration
            project = Project(config_path=config_path)
        elif project_name:
            # Create minimal configuration
            from wara9a.core.config import create_default_config, GitHubSourceConfig
            
            config = create_default_config(project_name)
            
            if github_repo:
                # Add GitHub source
                github_source = GitHubSourceConfig(
                    name=f"GitHub {github_repo}",
                    repo=github_repo
                )
                config.sources.append(github_source)
            
            if output_dir:
                config.output.directory = str(output_dir)
            
            project = Project(config=config)
        else:
            raise ValueError("You must provide config_path or project_name")
        
        generator = cls(project)
        return generator.generate_all()
    
    def clean_output(self) -> None:
        """Clean the output directory."""
        output_dir = Path(self.project.config.output.directory)
        
        if not output_dir.exists():
            logger.info(f"Output directory does not exist: {output_dir}")
            return
        
        files_removed = 0
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                file_path.unlink()
                files_removed += 1
        
        logger.info(f"Output directory cleaned: {files_removed} files removed")