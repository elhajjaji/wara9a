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
    
    Crée la structure de base et le fichier de configuration wara9a.yml.
    """
    try:
        target_dir = Path(project_dir) if project_dir else Path.cwd()
        config_file = target_dir / "wara9a.yml"
        
        # Check if project already exists
        if config_file.exists() and not force:
            console.print(f"❌ Project already exists: {config_file}")
            console.print("Use --force to overwrite or 'wara9a generate' to generate documentation.")
            return
        
        console.print(f"📁 Création du projet dans: {target_dir}")
        
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
            f"""✅ Projet Wara9a créé avec succès !

📄 Configuration: {config_file}
📂 Sortie: {output_path}
🔧 Sources: {len(config.sources)} configurée(s)
📝 Templates: {len(config.templates)} disponible(s)

Pour générer la documentation:
  [bold cyan]wara9a generate[/bold cyan]

Pour voir la configuration:
  [bold cyan]wara9a config show[/bold cyan]""",
            title="🎉 Initialisation terminée",
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
    📝 Génère la documentation du projet
    
    Collecte les données depuis les sources configurées et génère
    tous les documents selon les templates définis.
    """
    try:
        # Load project
        config_path = Path(config) if config else None
        project = Project(config_path=config_path)
        generator = DocumentGenerator(project)
        
        # Preview
        if preview:
            preview_data = generator.preview_generation()
            
            table = Table(title="🔍 Prévisualisation de la génération")
            table.add_column("Élément", style="cyan")
            table.add_column("Valeur", style="green")
            
            table.add_row("Projet", preview_data["project_name"])
            table.add_row("Dossier de sortie", preview_data["output_directory"])
            table.add_row("Formats", ", ".join(preview_data["output_formats"]))
            table.add_row("Sources", str(len(preview_data["sources"])))
            table.add_row("Templates", str(len(preview_data["templates"])))
            table.add_row("Fichiers estimés", str(preview_data["estimated_files"]))
            
            console.print(table)
            
            # Source details
            if preview_data["sources"]:
                sources_table = Table(title="Sources de données")
                sources_table.add_column("Type", style="blue")
                sources_table.add_column("Nom", style="yellow")
                sources_table.add_column("Activée", style="green")
                
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
            task = progress.add_task("Génération en cours...", total=None)
            
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
            f"""✅ Génération terminée avec succès !

📄 Fichiers générés: {len(generated_files)}
⏱️  Durée: {duration_str}
📊 Données traitées:
  • {stats['commits_processed'] if stats else 0} commits
  • {stats['issues_processed'] if stats else 0} issues  
  • {stats['prs_processed'] if stats else 0} pull requests

📂 Fichiers créés:""",
            title="🎉 Génération terminée",
            border_style="green"
        )
        console.print(result_panel)
        
        for file_path in generated_files:
            console.print(f"  📄 {file_path}")
        
    except FileNotFoundError:
        console.print("❌ Fichier wara9a.yml non trouvé")
        console.print("Utilisez '[bold cyan]wara9a init[/bold cyan]' pour créer un nouveau projet.")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Erreur lors de la génération: {e}")
        logging.exception("Détails de l'erreur")
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
              help='Fichier de configuration (défaut: wara9a.yml)')
def config_show(config: Optional[str]) -> None:
    """Affiche la configuration actuelle"""
    try:
        config_path = Path(config) if config else None
        project = Project(config_path=config_path)
        
        # Main table
        table = Table(title="⚙️ Configuration Wara9a")
        table.add_column("Section", style="cyan")
        table.add_column("Valeur", style="green")
        
        # Project information
        proj_config = project.config.project
        table.add_row("Nom", proj_config.name)
        table.add_row("Version", proj_config.version or "Not defined")
        table.add_row("Description", proj_config.description or "Not defined")
        
        # Output configuration
        output_config = project.config.output
        table.add_row("Dossier de sortie", output_config.directory)
        table.add_row("Formats", ", ".join(output_config.formats))
        
        console.print(table)
        
        # Sources
        sources_table = Table(title="📡 Sources de données")
        sources_table.add_column("Type", style="blue")
        sources_table.add_column("Nom", style="yellow")
        sources_table.add_column("Activée", style="green")
        
        for source in project.config.sources:
            sources_table.add_row(
                source.type,
                source.name or "Unnamed",
                "✅" if source.enabled else "❌"
            )
        
        console.print(sources_table)
        
        # Templates
        templates_table = Table(title="📝 Templates")
        templates_table.add_column("Nom", style="magenta")
        templates_table.add_column("Sortie", style="cyan")
        templates_table.add_column("Personnalisé", style="yellow")
        templates_table.add_column("Activé", style="green")
        
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
              help='Fichier de configuration (défaut: wara9a.yml)')
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
              help='Fichier de configuration (défaut: wara9a.yml)')
def connectors(config: Optional[str]) -> None:
    """
    🔌 Liste les connecteurs disponibles
    
    Affiche tous les connecteurs installés et leur statut.
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
        
        table = Table(title="🔌 Connecteurs disponibles")
        table.add_column("Type", style="blue")
        table.add_column("Nom", style="green")
        table.add_column("Description", style="cyan")
        
        for connector in connectors_list:
            table.add_row(
                connector.connector_type,
                connector.display_name,
                connector.description
            )
        
        console.print(table)
        
        if not connectors_list:
            console.print("⚠️  Aucun connecteur trouvé")
        
    except Exception as e:
        console.print(f"❌ Erreur lors de la liste des connecteurs: {e}")
        sys.exit(1)


@main.command()
def templates() -> None:
    """
    📝 Liste les templates disponibles
    
    Affiche tous les templates intégrés disponibles.
    """
    from wara9a.core.template_engine import TemplateEngine
    
    try:
        engine = TemplateEngine()
        builtin_templates = engine.list_builtin_templates()
        
        table = Table(title="📝 Templates intégrés")
        table.add_column("Nom", style="magenta")
        table.add_column("Description", style="cyan")
        
        descriptions = {
            "readme": "Documentation générale du projet",
            "changelog": "Journal des modifications",
            "release_notes": "Notes de version détaillées"
        }
        
        for template_name in builtin_templates:
            table.add_row(
                template_name,
                descriptions.get(template_name, "Template personnalisé")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Erreur lors de la liste des templates: {e}")


@main.group()
def deps() -> None:
    """
    📦 Gestion des dépendances
    
    Commandes pour vérifier et installer les dépendances nécessaires
    selon les connecteurs utilisés dans la configuration.
    """
    pass


@deps.command('check')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Fichier de configuration (défaut: wara9a.yml)')
@click.option('--verbose', '-v', is_flag=True, help='Affichage détaillé')
def deps_check(config: Optional[str], verbose: bool) -> None:
    """Vérifie les dépendances nécessaires"""
    try:
        config_path = Path(config) if config else Path.cwd() / "wara9a.yml"
        
        if not config_path.exists():
            console.print(f"❌ Fichier de configuration non trouvé: {config_path}")
            console.print("Utilisez '[bold cyan]wara9a init[/bold cyan]' pour créer un projet.")
            return
        
        report = DependencyManager.check_project_dependencies(config_path)
        
        if report["status"] == "ok":
            console.print("✅ Toutes les dépendances sont installées !")
            
        elif report["status"] == "missing_deps":
            missing = report["missing"]
            
            console.print("⚠️ Dépendances manquantes détectées:")
            
            if missing["connectors"]:
                console.print(f"🔌 Connecteurs: [red]{', '.join(missing['connectors'])}[/red]")
            
            if missing["generators"]:
                console.print(f"📄 Générateurs: [red]{', '.join(missing['generators'])}[/red]")
            
            if verbose and missing["packages"]:
                console.print(f"\n📦 Packages nécessaires:")
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
        console.print(f"❌ Erreur lors de la vérification des dépendances: {e}")
        sys.exit(1)


@deps.command('install')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Fichier de configuration (défaut: wara9a.yml)')
@click.option('--dry-run', '-n', is_flag=True, 
              help='Simulation sans installation réelle')
@click.option('--force', '-f', is_flag=True,
              help='Forcer la réinstallation')
def deps_install(config: Optional[str], dry_run: bool, force: bool) -> None:
    """Installe automatiquement les dépendances manquantes"""
    try:
        config_path = Path(config) if config else Path.cwd() / "wara9a.yml"
        
        if not config_path.exists():
            console.print(f"❌ Fichier de configuration non trouvé: {config_path}")
            return
        
        from wara9a.core.config import Wara9aConfig
        wara9a_config = Wara9aConfig.load_from_file(config_path)
        
        manager = DependencyManager(auto_install=True, dry_run=dry_run)
        
        if dry_run:
            console.print("🔄 Mode simulation activé")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            if not dry_run:
                task = progress.add_task("Installation des dépendances...", total=None)
            
            success = manager.auto_install_dependencies(wara9a_config)
        
        if success:
            if dry_run:
                console.print("✅ Simulation terminée - voir les logs ci-dessus")
            else:
                console.print("✅ Dépendances installées avec succès !")
                console.print("Vous pouvez maintenant utiliser '[bold cyan]wara9a generate[/bold cyan]'")
        else:
            console.print("❌ Échec de l'installation des dépendances")
            
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
    """Liste tous les connecteurs et leurs dépendances"""
    
    table = Table(title="📦 Connecteurs et dépendances")
    table.add_column("Connecteur", style="blue")
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
    
    # Table des générateurs
    gen_table = Table(title="📄 Générateurs et dépendances")
    gen_table.add_column("Générateur", style="blue")
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