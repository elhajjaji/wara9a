#!/usr/bin/env python3
"""
Script de démonstration Wara9a.

Montre les fonctionnalités principales avec un exemple concret.
"""

import sys
import tempfile
from pathlib import Path

# Add package to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from wara9a.core.config import create_default_config, LocalFilesSourceConfig
from wara9a.core.project import Project
from wara9a.core.generator import DocumentGenerator


def create_demo_project():
    """Crée un projet de démonstration temporaire."""
    print("🚀 Création du projet de démonstration...")
    
    # Create temporary folder
    demo_dir = Path(tempfile.mkdtemp(prefix="wara9a_demo_"))
    print(f"📁 Dossier de démonstration: {demo_dir}")
    
    # Create example files
    readme_content = """    readme_content = """# Wara9a Demo Project

This is an example project to demonstrate Wara9a capabilities.

## Features

- Automatic documentation
- Generation from multiple sources
- Customizable templates
- Multi-format support

## Installation

```bash
pip install wara9a
```

## Usage

See the automatically generated documentation for more details.

## Author

AbdERRAHMAN EL HAJJAJI
"""
"""
    
    changelog_content = """changelog_content = """# Changelog

## [1.0.0] - 2025-01-01

### Added
- Multi-source support
- Built-in templates
- HTML and Markdown generation
- Complete CLI interface

### Changed
- Performance improvements

### Fixed
- Minor bug fixes

## [0.9.0] - 2024-12-15

### Added
- First functional prototype

## [0.1.0] - 2024-12-01

### Changed
- Initial architecture

## [0.0.1] - 2024-11-15

### Added
- Initial project
"""
"""
    
    # Write files
    (demo_dir / "README.md").write_text(readme_content)
    (demo_dir / "CHANGELOG.md").write_text(changelog_content)
    
    return demo_dir


def demo_basic_generation():
    """Démonstration de la génération basique."""
    print("\n📝 Démonstration : Génération basique")
    
    demo_dir = create_demo_project()
    
    try:
        # Create configuration
        config = create_default_config("Projet Démonstration Wara9a")
        config.project.description = "Démonstration des capacités de Wara9a"
        config.project.author = "Équipe Wara9a"
        
        # Configure local source
        local_source = LocalFilesSourceConfig(
            name="Fichiers de démonstration",
            path=str(demo_dir),
            patterns=["README.md", "CHANGELOG.md"]
        )
        config.sources = [local_source]
        
        # Output directory
        output_dir = demo_dir / "generated"
        config.output.directory = str(output_dir)
        
        # Create project
        project = Project(config=config)
        generator = DocumentGenerator(project)
        
        # Preview
        print("\n🔍 Prévisualisation de la génération:")
        preview = generator.preview_generation()
        print(f"  • Projet: {preview['project_name']}")
        print(f"  • Sources: {len(preview['sources'])}")
        print(f"  • Templates: {len(preview['templates'])}")
        print(f"  • Fichiers estimés: {preview['estimated_files']}")
        
        # Generation
        print("\n⚙️ Generation in progress...")
        generated_files = generator.generate_documents()
        
        # Display results
        print(f"\n✅ Generation completed! {len(generated_files)} file(s) created")
        print(f"📁 Output directory: {output_dir}")
        
        for file_path in generated_files:
            print(f"  📄 {file_path.name}")
            
            # Show content preview
        
        return demo_dir, generated_files
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return demo_dir, []


def demo_dependency_management():
    """Demonstration of automatic dependency management."""
    print("\n📦 Demo: Automatic dependency management")
    
    from wara9a.core.dependencies import DependencyManager
    from wara9a.core.config import GitHubSourceConfig, LocalFilesSourceConfig
    
    # Create configuration with GitHub
    config = create_default_config("Dependencies Test")
    config.sources = [
        GitHubSourceConfig(
            name="Test GitHub",
            repo="elhajjaji/wara9a",
            enabled=True
        ),
        LocalFilesSourceConfig(
            name="Local files",
            path=".",
            enabled=True
        )
    ]
    
    manager = DependencyManager(auto_install=False, dry_run=True)
    
    print("🔍 Analyzing required dependencies...")
    missing = manager.check_config_dependencies(config)
    
    if missing["connectors"]:
        print(f"  🔌 Connectors requiring dependencies: {missing['connectors']}")
    else:
        print("  ✅ All connectors have their dependencies")
        
    if missing["packages"]:
        print(f"  📦 Packages to install: {len(missing['packages'])}")
        for pkg in missing["packages"][:3]:  # Show first 3
            print(f"    • {pkg}")
    else:
        print("  ✅ All dependencies are installed")
    
    suggestions = manager.suggest_manual_install(config)
    if suggestions:
        print(f"  💡 Suggested installation commands:")
        for suggestion in suggestions[:2]:  # Show first 2
            print(f"    {suggestion}")
    
    print("  🎯 With Wara9a, these dependencies are installed automatically!")


def demo_template_customization():
    """Demonstration of template customization."""
    print("\n🎨 Demo: Template customization")
    
    # Simple custom template
    custom_template = """# 📊 Rapport de Projet - {{ project.name }}

**Généré automatiquement le {{ now() | format_datetime }}**

## Informations Générales

- **Nom**: {{ project.name }}
- **Version**: {{ project.version }}
- **Description**: {{ project.description }}
- **Auteur**: {{ project.author }}

## Statistiques

{% if data.repository %}
- **Langage principal**: {{ data.repository.languages | first | default("Non détecté") }}
- **Nombre de commits**: {{ data.commits | length }}
- **Issues ouvertes**: {{ open_issues | length }}
{% endif %}

## Commits Récents

{% for commit in recent_commits[:3] %}
### {{ loop.index }}. {{ commit.message | truncate(60) }}
- **Auteur**: {{ commit.author.name }}
- **Date**: {{ commit.date | format_date }}
- **SHA**: `{{ commit.sha[:7] }}`
{% endfor %}

---
*Rapport généré par Wara9a*
"""
    
    print("Custom template created with variables:")
    print("  • project.*")
    print("  • data.*") 
    print("  • recent_commits")
    print("  • Filters: format_datetime, truncate, format_date")
    
    return custom_template


def main():
    """Main demonstration function."""
    print("🌟 Wara9a Demo - Automatic Documentation Framework")
    print("=" * 70)
    
    try:
        # Basic demonstration
        demo_dir, generated_files = demo_basic_generation()
        
        # Dependency management demonstration
        demo_dependency_management()
        
        # Custom templates demonstration
        demo_template_customization()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📁 Files in: {demo_dir}")
        
        if generated_files:
            print(f"\n💡 To view results:")
            for file_path in generated_files:
                print(f"   cat {file_path}")
        
        # Instructions to continue
        print(f"\n📚 To go further:")
        print(f"   • Check dependencies: wara9a deps check")
        print(f"   • View documentation: docs/")
        print(f"   • Examples: examples/")
        print(f"   • Tests: python -m pytest tests/")
        
    except KeyboardInterrupt:
        print("\n⛔ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())