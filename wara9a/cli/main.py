"""
Main command line interface for Wara9a.

Entry point for all CLI commands of the framework.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

from wara9a.core.project import Project
from wara9a.core.generator import DocumentGenerator
from wara9a.core.config import create_default_config
from wara9a.core.dependencies import DependencyManager


# Rich console for display
console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Configure logs with Rich."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_time=False, show_path=False)]
    )


@click.group(invoke_without_command=True)
@click.option('--verbose', '-v', is_flag=True, help='Detailed output')
@click.option('--version', is_flag=True, help='Show version')
@click.pass_context
def main(ctx: click.Context, verbose: bool, version: bool) -> None:
    """
    🔄 Wara9a - Documentation IT automatique et intelligente
    
    Framework open-source Python qui transforme automatiquement 
    vos projets IT en documentation claire et professionnelle.
    """
    setup_logging(verbose)
    
    if version:
        from wara9a import __version__
        console.print(f"Wara9a version {__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        # Show help if no command
        console.print(ctx.get_help())


@main.command()
@click.option('--name', '-n', prompt='Project name', help='Project name')
@click.option('--dir', '-d', 'project_dir', type=click.Path(), 
              help='Project folder (default: current directory)')
@click.option('--github-repo', '-g', help='GitHub repository (format: owner/repo)')
@click.option('--output-dir', '-o', default='output', help='Output directory')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing files')
def init(name: str, project_dir: Optional[str], github_repo: Optional[str], 
         output_dir: str, force: bool) -> None:
    """
    🚀 Initialise un nouveau projet Wara9a
    
    Creates basic structure and wara9a.yml configuration file.
    """
    try:
        target_dir = Path(project_dir) if project_dir else Path.cwd()
        config_file = target_dir / "wara9a.yml"
        
        # Check if project already exists
        if config_file.exists() and not force:
            console.print(f"❌ Project already exists: {config_file}")
            console.print("Use --force to overwrite or 'wara9a generate' to generate documentation.")
            return
        
        console.print(f"📁 Creating project in: {target_dir}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Create configuration
            task = progress.add_task("Creating configuration...", total=None)
            
            config = create_default_config(name, output_dir)
            config.project.description = f"Documentation automatique pour {name}"
            
            # Add GitHub source if provided
            if github_repo:
                from wara9a.core.config import GitHubSourceConfig
                github_source = GitHubSourceConfig(
                    name=f"GitHub {github_repo}",
                    repo=github_repo
                )
                config.sources.append(github_source)
            
            # Save configuration
            progress.update(task, description="Saving wara9a.yml file...")
            config.save_to_file(config_file)
            
            # Create output directory
            progress.update(task, description="Creating directories...")
            output_path = target_dir / output_dir
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Display result
        panel = Panel.fit(
            f"""✅ Wara9a project created successfully!

📄 Configuration: {config_file}
📂 Sortie: {output_path}
🔧 Sources: {len(config.sources)} configured
📝 Templates: {len(config.templates)} disponible(s)

To generate documentation:
  [bold cyan]wara9a generate[/bold cyan]

Pour voir la configuration:
  [bold cyan]wara9a config show[/bold cyan]""",
            title="🎉 Initialization completed",
            border_style="green"
        )
        console.print(panel)
        
    except Exception as e:
        console.print(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (default: wara9a.yml)')
@click.option('--output', '-o', type=click.Path(), 
              help='Custom output directory')
@click.option('--template', '-t', 'templates', multiple=True, 
              help='Specific templates to generate')
@click.option('--force-refresh', '-f', is_flag=True, 
              help='Force data re-collection')
@click.option('--clean', is_flag=True, 
              help='Clean output directory before generation')
@click.option('--preview', '-p', is_flag=True, 
              help='Preview without generating')
def generate(config: Optional[str], output: Optional[str], templates: List[str], 
            force_refresh: bool, clean: bool, preview: bool) -> None:
    """
    📝 Generates project documentation
    
    Collects data from configured sources and generates
    all documents according to defined templates.
    """
    try:
        # Load project
        config_path = Path(config) if config else None
        project = Project(config_path=config_path)
        generator = DocumentGenerator(project)
        
        # Preview
        if preview:
            preview_data = generator.preview_generation()
            
            table = Table(title="🔍 Generation preview")
            table.add_column("Item", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Projet", preview_data["project_name"])
            table.add_row("Output directory", preview_data["output_directory"])
            table.add_row("Formats", ", ".join(preview_data["output_formats"]))
            table.add_row("Sources", str(len(preview_data["sources"])))
            table.add_row("Templates", str(len(preview_data["templates"])))
            table.add_row("Estimated files", str(preview_data["estimated_files"]))
            
            console.print(table)
            
            # Source details
            if preview_data["sources"]:
                sources_table = Table(title="Data sources")
                sources_table.add_column("Type", style="blue")
                sources_table.add_column("Name", style="yellow")
                sources_table.add_column("Enabled", style="green")
                
                for source in preview_data["sources"]:
                    sources_table.add_row(
                        source["type"], 
                        source["name"],
                        "✅" if source["enabled"] else "❌"
                    )
                console.print(sources_table)
            
            return
        
        # Clean if requested
        if clean:
            generator.clean_output()
            console.print("🧹 Output directory cleaned")
        
        # Generation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating...", total=None)
            
            if templates:
                # Specific template generation
                generated_files = []
                for template_name in templates:
                    progress.update(task, description=f"Generating template: {template_name}")
                    file_path = generator.generate_template(template_name, force_refresh=force_refresh)
                    generated_files.append(file_path)
            else:
                # Full generation
                progress.update(task, description="Collecting data...")
                output_path = Path(output) if output else None
                generated_files = generator.generate_all(
                    force_refresh=force_refresh, 
                    output_dir=output_path
                )
        
        # Display results
        stats = generator.get_generation_stats()
        
        duration_str = f"{stats['duration']:.1f}s" if stats else 'N/A'
        
        result_panel = Panel.fit(
            f"""✅ Generation completed successfully!

📄 Generated files: {len(generated_files)}
⏱️  Duration: {duration_str}
📊 Data processed:
  • {stats['commits_processed'] if stats else 0} commits
  • {stats['issues_processed'] if stats else 0} issues  
  • {stats['prs_processed'] if stats else 0} pull requests

📂 Files created:""",
            title="🎉 Generation completed",
            border_style="green"
        )
        console.print(result_panel)
        
        for file_path in generated_files:
            console.print(f"  📄 {file_path}")
        
    except FileNotFoundError:
        console.print("❌ wara9a.yml file not found")
        console.print("Use '[bold cyan]wara9a init[/bold cyan]' to create a new project.")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Generation error: {e}")
        logging.exception("Error details")
        sys.exit(1)


@main.group()
def config() -> None:
    """
    ⚙️ Gestion de la configuration
    
    Commandes pour visualiser et valider la configuration du projet.
    """
    pass


@config.command('show')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (default: wara9a.yml)')
def config_show(config: Optional[str]) -> None:
    """Affiche la configuration actuelle"""
    try:
        config_path = Path(config) if config else None
        project = Project(config_path=config_path)
        
        # Main table
        table = Table(title="⚙️ Configuration Wara9a")
        table.add_column("Section", style="cyan")
        table.add_column("Value", style="green")
        
        # Project information
        proj_config = project.config.project
        table.add_row("Name", proj_config.name)
        table.add_row("Version", proj_config.version or "Not defined")
        table.add_row("Description", proj_config.description or "Not defined")
        
        # Output configuration
        output_config = project.config.output
        table.add_row("Output directory", output_config.directory)
        table.add_row("Formats", ", ".join(output_config.formats))
        
        console.print(table)
        
        # Sources
        sources_table = Table(title="📡 Data sources")
        sources_table.add_column("Type", style="blue")
        sources_table.add_column("Name", style="yellow")
        sources_table.add_column("Enabled", style="green")
        
        for source in project.config.sources:
            sources_table.add_row(
                source.type,
                source.name or "Unnamed",
                "✅" if source.enabled else "❌"
            )
        
        console.print(sources_table)
        
        # Templates
        templates_table = Table(title="📝 Templates")
        templates_table.add_column("Name", style="magenta")
        templates_table.add_column("Sortie", style="cyan")
        templates_table.add_column("Custom", style="yellow")
        templates_table.add_column("Enabled", style="green")
        
        for template in project.config.templates:
            templates_table.add_row(
                template.name,
                template.output,
                "✅" if template.template_file else "❌",
                "✅" if template.enabled else "❌"
            )
        
        console.print(templates_table)
        
    except Exception as e:
        console.print(f"❌ Erreur lors de l'affichage de la configuration: {e}")
        sys.exit(1)


@config.command('validate')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (default: wara9a.yml)')
def config_validate(config: Optional[str]) -> None:
    """Valide la configuration"""
    try:
        config_path = Path(config) if config else None
        project = Project(config_path=config_path)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Validation en cours...", total=None)
            
            errors = project.validate_config()
        
        if errors:
            console.print("❌ Configuration invalide:")
            for error in errors:
                console.print(f"  • {error}")
            sys.exit(1)
        else:
            console.print("✅ Configuration valide !")
            
    except Exception as e:
        console.print(f"❌ Erreur lors de la validation: {e}")
        sys.exit(1)


@main.command()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (default: wara9a.yml)')
def connectors(config: Optional[str]) -> None:
    """
    🔌 Liste les connecteurs disponibles
    
    Display all installed connectors and their status.
    """
    try:
        # Charger le projet si config fournie, sinon juste le registre
        if config:
            project = Project(config_path=Path(config))
            registry = project.connector_registry
        else:
            from wara9a.core.connector_registry import get_global_registry
            registry = get_global_registry()
        
        connectors_list = registry.list_connectors()
        
        # Group connectors by category
        from wara9a.core.connector_base import ConnectorCategory
        
        # Ticketing connectors (functional documentation)
        ticketing = [c for c in connectors_list if c.category == ConnectorCategory.TICKETING]
        if ticketing:
            table = Table(title="� Ticketing Connectors (Functional Documentation)")
            table.add_column("Type", style="blue")
            table.add_column("Name", style="green")
            table.add_column("Description", style="cyan")
            
            for connector in ticketing:
                table.add_row(
                    connector.connector_type,
                    connector.display_name,
                    connector.description
                )
            console.print(table)
        
        # Git connectors (technical documentation)
        git = [c for c in connectors_list if c.category == ConnectorCategory.GIT]
        if git:
            table = Table(title="🔧 Git Connectors (Technical Documentation)")
            table.add_column("Type", style="blue")
            table.add_column("Name", style="green")
            table.add_column("Description", style="cyan")
            
            for connector in git:
                table.add_row(
                    connector.connector_type,
                    connector.display_name,
                    connector.description
                )
            console.print(table)
        
        # Files connectors
        files = [c for c in connectors_list if c.category == ConnectorCategory.FILES]
        if files:
            table = Table(title="📁 Files Connectors")
            table.add_column("Type", style="blue")
            table.add_column("Name", style="green")
            table.add_column("Description", style="cyan")
            
            for connector in files:
                table.add_row(
                    connector.connector_type,
                    connector.display_name,
                    connector.description
                )
            console.print(table)
        
        if not connectors_list:
            console.print("⚠️  No connector found")
        
    except Exception as e:
        console.print(f"❌ Erreur lors de la liste des connecteurs: {e}")
        sys.exit(1)


@main.command()
def templates() -> None:
    """
    📝 Liste les templates disponibles
    
    Display all available built-in templates.
    """
    from wara9a.core.template_engine import TemplateEngine
    
    try:
        engine = TemplateEngine()
        builtin_templates = engine.list_builtin_templates()
        
        table = Table(title="📝 Built-in templates")
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="cyan")
        
        descriptions = {
            "readme": "General project documentation",
            "changelog": "Journal des modifications",
            "release_notes": "Detailed release notes"
        }
        
        for template_name in builtin_templates:
            table.add_row(
                template_name,
                descriptions.get(template_name, "Custom template")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Erreur lors de la liste des templates: {e}")


@main.group()
def deps() -> None:
    """
    📦 Dependencies management
    
    Commands to check and install required dependencies
    according to connectors used in configuration.
    """
    pass


@deps.command('check')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (default: wara9a.yml)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def deps_check(config: Optional[str], verbose: bool) -> None:
    """Check required dependencies"""
    try:
        config_path = Path(config) if config else Path.cwd() / "wara9a.yml"
        
        if not config_path.exists():
            console.print(f"❌ Configuration file not found: {config_path}")
            console.print("Use '[bold cyan]wara9a init[/bold cyan]' to create a project.")
            return
        
        report = DependencyManager.check_project_dependencies(config_path)
        
        if report["status"] == "ok":
            console.print("✅ All dependencies are installed!")
            
        elif report["status"] == "missing_deps":
            missing = report["missing"]
            
            console.print("⚠️ Missing dependencies detected:")
            
            if missing["connectors"]:
                console.print(f"🔌 Connecteurs: [red]{', '.join(missing['connectors'])}[/red]")
            
            if missing["generators"]:
                console.print(f"📄 Generators: [red]{', '.join(missing['generators'])}[/red]")
            
            if verbose and missing["packages"]:
                console.print(f"\n📦 Required packages:")
                for package in missing["packages"]:
                    console.print(f"  • {package}")
            
            console.print(f"\n💡 Pour installer automatiquement:")
            console.print(f"  [bold cyan]wara9a deps install[/bold cyan]")
            
            console.print(f"\n📝 Ou manuellement:")
            for suggestion in report["suggestions"]:
                console.print(f"  [bold green]{suggestion}[/bold green]")
        
        else:
            console.print(f"❌ Erreur: {report.get('message', 'Erreur inconnue')}")
            
    except Exception as e:
        console.print(f"❌ Dependencies check error: {e}")
        sys.exit(1)


@deps.command('install')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Configuration file (default: wara9a.yml)')
@click.option('--dry-run', '-n', is_flag=True, 
              help='Simulation without actual installation')
@click.option('--force', '-f', is_flag=True,
              help='Force reinstallation')
def deps_install(config: Optional[str], dry_run: bool, force: bool) -> None:
    """Automatically install missing dependencies"""
    try:
        config_path = Path(config) if config else Path.cwd() / "wara9a.yml"
        
        if not config_path.exists():
            console.print(f"❌ Configuration file not found: {config_path}")
            return
        
        from wara9a.core.config import Wara9aConfig
        wara9a_config = Wara9aConfig.load_from_file(config_path)
        
        manager = DependencyManager(auto_install=True, dry_run=dry_run)
        
        if dry_run:
            console.print("🔄 Simulation mode activated")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            if not dry_run:
                task = progress.add_task("Installing dependencies...", total=None)
            
            success = manager.auto_install_dependencies(wara9a_config)
        
        if success:
            if dry_run:
                console.print("✅ Simulation completed - see logs above")
            else:
                console.print("✅ Dependencies installed successfully!")
                console.print("Vous pouvez maintenant utiliser '[bold cyan]wara9a generate[/bold cyan]'")
        else:
            console.print("❌ Dependencies installation failed")
            
            # Afficher les suggestions manuelles
            missing = manager.check_config_dependencies(wara9a_config)
            if any(missing.values()):
                suggestions = manager.suggest_manual_install(wara9a_config)
                console.print("\n💡 Essayez l'installation manuelle:")
                for suggestion in suggestions:
                    console.print(f"  [bold green]{suggestion}[/bold green]")
            
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Erreur lors de l'installation: {e}")
        sys.exit(1)


@deps.command('list')
def deps_list() -> None:
    """List all connectors and their dependencies"""
    
    table = Table(title="📦 Connectors and dependencies")
    table.add_column("Connector", style="blue")
    table.add_column("Packages", style="green") 
    table.add_column("Groupe optionnel", style="yellow")
    table.add_column("Disponible", style="magenta")
    
    manager = DependencyManager(auto_install=False)
    
    for connector, deps in manager.CONNECTOR_DEPENDENCIES.items():
        available = "✅" if manager._check_import(deps["test_import"]) else "❌"
        packages = ", ".join(deps["packages"])
        
        table.add_row(
            connector,
            packages,
            deps["optional_group"],
            available
        )
    
    console.print(table)
    
    # Generators table
    gen_table = Table(title="📄 Generators and dependencies")
    gen_table.add_column("Generator", style="blue")
    gen_table.add_column("Packages", style="green")
    gen_table.add_column("Groupe optionnel", style="yellow")
    gen_table.add_column("Disponible", style="magenta")
    
    for generator, deps in manager.GENERATOR_DEPENDENCIES.items():
        available = "✅" if manager._check_import(deps["test_import"]) else "❌"
        packages = ", ".join(deps["packages"])
        
        gen_table.add_row(
            generator,
            packages, 
            deps["optional_group"],
            available
        )
    
    console.print(gen_table)


if __name__ == '__main__':
    main()