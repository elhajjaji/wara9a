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
    readme_content = """# Projet Démonstration Wara9a

Ce projet démontre les capacités de Wara9a pour générer automatiquement
de la documentation à partir des sources existantes.

## Fonctionnalités

- Génération automatique de documentation
- Support multi-sources (GitHub, fichiers locaux, etc.)
- Templates flexibles avec Jinja2
- Sortie multi-formats (Markdown, HTML, PDF)

## Installation

```bash
pip install wara9a
```

## Utilisation

```bash
wara9a init --name "Mon Projet"
wara9a generate
```

## Auteur

Équipe Wara9a
"""
    
    changelog_content = """# Changelog

## [1.0.0] - 2025-11-05

### Ajouté
- Framework principal Wara9a
- Connecteurs GitHub et fichiers locaux
- Templates intégrés (README, changelog, release notes)
- Interface CLI complète
- Générateurs Markdown et HTML

### Changé
- Architecture modulaire avec système de plugins

### Corrigé
- Gestion des erreurs de connexion
- Parsing des dates GitHub

## [0.9.0] - 2025-10-20

### Ajouté
- Prototype initial
- Système de configuration YAML
- Modèles de données normalisés

### Changé
- Migration vers Pydantic v2

## [0.1.0] - 2025-10-01

### Ajouté
- Première version de développement
- Concepts de base du framework
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
        print("\n⚙️ Génération en cours...")
        generated_files = generator.generate_documents()
        
        # Display results
        print(f"\n✅ Génération terminée ! {len(generated_files)} fichier(s) créé(s)")
        print(f"📁 Dossier de sortie: {output_dir}")
        
        for file_path in generated_files:
            print(f"  📄 {file_path.name}")
            
            # Show content preview
        
        return demo_dir, generated_files
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return demo_dir, []


def demo_dependency_management():
    """Demonstration of automatic dependency management."""
    print("\n📦 Demo: Automatic dependency management")
    
    from wara9a.core.dependencies import DependencyManager
    from wara9a.core.config import GitHubSourceConfig, LocalFilesSourceConfig
    
    # Create configuration with GitHub
    config = create_default_config("Test Dépendances")
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
    
    print("  🎯 Avec Wara9a, ces dépendances sont installées automatiquement !")


def demo_template_customization():
    """Démonstration de la personnalisation de templates."""
    print("\n🎨 Démonstration : Personnalisation de templates")
    
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
    
    print("Template personnalisé créé avec les variables :")
    print("  • project.*")
    print("  • data.*") 
    print("  • recent_commits")
    print("  • Filtres : format_datetime, truncate, format_date")
    
    return custom_template


def main():
    """Fonction principale de démonstration."""
    print("🌟 Démonstration Wara9a - Framework de Documentation Automatique")
    print("=" * 70)
    
    try:
        # Démonstration basique
        demo_dir, generated_files = demo_basic_generation()
        
        # Démonstration gestion des dépendances
        demo_dependency_management()
        
        # Démonstration templates personnalisés
        demo_template_customization()
        
        print(f"\n🎉 Démonstration terminée avec succès !")
        print(f"📁 Fichiers dans: {demo_dir}")
        
        if generated_files:
            print(f"\n💡 Pour voir les résultats :")
            for file_path in generated_files:
                print(f"   cat {file_path}")
        
        # Instructions pour continuer
        print(f"\n📚 Pour aller plus loin :")
        print(f"   • Vérifier les dépendances: wara9a deps check")
        print(f"   • Consulter la documentation: docs/")
        print(f"   • Exemples: examples/")
        print(f"   • Tests: python -m pytest tests/")
        
    except KeyboardInterrupt:
        print("\n⛔ Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())