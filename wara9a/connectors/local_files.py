"""
Local files connector for Wara9a.

Collects information from the local file system:
- README, CHANGELOG files
- Project structure
- Basic Git metadata
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
import re
import subprocess

from wara9a.core.connector_base import ConnectorBase, ConnectorError
from wara9a.core.models import (
    ProjectData, Repository, Commit, Issue, PullRequest, Release,
    Author, SourceType
)
from wara9a.core.config import SourceConfig, LocalFilesSourceConfig


logger = logging.getLogger(__name__)


class LocalFilesConnector(ConnectorBase):
    """
    Connecteur pour les fichiers locaux.
    
    Collects information from the file system:
    - README.md, CHANGELOG.md
    - Git metadata if available
    - Structure du projet
    """
    
    @property
    def connector_type(self) -> str:
        return "local_files"
    
    @property
    def display_name(self) -> str:
        return "Fichiers locaux"
    
    @property
    def description(self) -> str:
        return "Connecteur pour collecter les informations depuis les fichiers locaux"
    
    @property
    def required_config_fields(self) -> List[str]:
        return ["path"]
    
    @property
    def optional_config_fields(self) -> List[str]:
        return ["patterns", "encoding"]
    
    def validate_config(self, config: SourceConfig) -> List[str]:
        """Valide la configuration du connecteur fichiers locaux."""
        errors = []
        
        if not hasattr(config, 'path') or not config.path:
            errors.append("Le champ 'path' est obligatoire")
            return errors
        
        path = Path(config.path)
        if not path.exists():
            errors.append(f"Le chemin n'existe pas: {config.path}")
        elif not path.is_dir():
            errors.append(f"Path must be a directory: {config.path}")
        
        return errors
    
    def collect(self, config: SourceConfig) -> ProjectData:
        """
        Collects data from local files.
        
        Args:
            config: Configuration LocalFilesSourceConfig
            
        Returns:
            Normalized project data
        """
        if not isinstance(config, LocalFilesSourceConfig):
            # Convert generic SourceConfig to LocalFilesSourceConfig
            local_config = LocalFilesSourceConfig(**config.model_dump())
        else:
            local_config = config
        
        # Valider la configuration
        errors = self.validate_config(local_config)
        if errors:
            raise ConnectorError(f"Configuration invalide: {errors}")
        
        project_path = Path(local_config.path)
        logger.info(f"Collecte depuis fichiers locaux: {project_path}")
        
        try:
            # Collect data
            repository = self._get_repository_info(project_path)
            commits = self._get_git_commits(project_path)
            issues = []  # Pas d'issues dans les fichiers locaux
            pull_requests = []  # Pas de PRs dans les fichiers locaux
            releases = self._parse_changelog_releases(project_path, local_config)
            
            project_data = ProjectData(
                repository=repository,
                commits=commits,
                issues=issues,
                pull_requests=pull_requests,
                releases=releases,
                source_type=SourceType.LOCAL_FILES,
                source_config=local_config.model_dump()
            )
            
            logger.info(f"Local collection completed: {len(commits)} commits, "
                       f"{len(releases)} releases")
            
            return project_data
            
        except Exception as e:
            raise ConnectorError(f"Erreur lors de la collecte locale: {e}")
    
    def _get_repository_info(self, project_path: Path) -> Repository:
        """Collecte les informations du repository depuis les fichiers locaux."""
        # Nom du projet = nom du dossier
        project_name = project_path.name
        
        # Essayer de lire README pour la description
        description = self._read_readme_description(project_path)
        
        # Detect main languages
        languages = self._detect_languages(project_path)
        
        # Git metadata if available
        git_info = self._get_git_info(project_path)
        
        return Repository(
            name=project_name,
            full_name=project_name,
            description=description,
            url=git_info.get('remote_url'),
            default_branch=git_info.get('branch', 'main'),
            languages=languages,
            topics=[],
            created_at=git_info.get('created_at'),
            updated_at=datetime.now(timezone.utc),
            stars_count=0,
            forks_count=0
        )
    
    def _read_readme_description(self, project_path: Path) -> Optional[str]:
        """Lit la description depuis le fichier README."""
        readme_files = ['README.md', 'README.txt', 'README.rst', 'README']
        
        for readme_name in readme_files:
            readme_path = project_path / readme_name
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')
                    # Extract first line after title
                    lines = content.strip().split('\n')
                    
                    # Ignorer le titre principal (commence par # ou =)
                    for line in lines[1:]:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('='):
                            return line
                            
                except Exception as e:
                    logger.warning(f"Impossible de lire {readme_path}: {e}")
        
        return None
    
    def _detect_languages(self, project_path: Path) -> List[str]:
        """Detects programming languages used."""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.hs': 'Haskell',
            '.ml': 'OCaml',
            '.r': 'R',
            '.m': 'MATLAB',
            '.sh': 'Shell',
            '.ps1': 'PowerShell',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.less': 'Less'
        }
        
        language_counts: Dict[str, int] = {}
        
        # Scan files (limited to first 1000 for performance)
        count = 0
        for file_path in project_path.rglob('*'):
            if count > 1000:
                break
            
            if file_path.is_file() and file_path.suffix in language_extensions:
                language = language_extensions[file_path.suffix]
                language_counts[language] = language_counts.get(language, 0) + 1
                count += 1
        
        # Sort by frequency
        return [lang for lang, _ in sorted(language_counts.items(), 
                                         key=lambda x: x[1], reverse=True)]
    
    def _get_git_info(self, project_path: Path) -> Dict[str, Any]:
        """Collecte les informations Git basiques."""
        git_info = {}
        
        if not (project_path / '.git').exists():
            return git_info
        
        try:
            # Branche actuelle
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                git_info['branch'] = result.stdout.strip()
            
            # URL du remote origin
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                git_info['remote_url'] = result.stdout.strip()
            
            # Date du premier commit
            result = subprocess.run(
                ['git', 'log', '--reverse', '--format=%cI', '--max-count=1'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                git_info['created_at'] = datetime.fromisoformat(
                    result.stdout.strip().replace('Z', '+00:00')
                )
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"Erreur lors de la collecte Git: {e}")
        
        return git_info
    
    def _get_git_commits(self, project_path: Path, max_commits: int = 50) -> List[Commit]:
        """Collects recent Git commits."""
        commits = []
        
        if not (project_path / '.git').exists():
            return commits
        
        try:
            # Format: hash|author_name|author_email|date|subject
            result = subprocess.run([
                'git', 'log', 
                f'--max-count={max_commits}',
                '--format=%H|%an|%ae|%cI|%s'
            ], 
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return commits
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|', 4)
                if len(parts) != 5:
                    continue
                
                sha, author_name, author_email, date_str, message = parts
                
                commit = Commit(
                    sha=sha,
                    message=message,
                    author=Author(
                        name=author_name,
                        email=author_email
                    ),
                    date=datetime.fromisoformat(date_str.replace('Z', '+00:00')),
                    url=None,  # Pas d'URL pour les commits locaux
                    files_changed=[],
                    additions=0,
                    deletions=0
                )
                commits.append(commit)
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"Erreur lors de la collecte des commits: {e}")
        
        return commits
    
    def _parse_changelog_releases(self, project_path: Path, 
                                 config: LocalFilesSourceConfig) -> List[Release]:
        """Parse les releases depuis un fichier CHANGELOG."""
        releases = []
        
        changelog_files = ['CHANGELOG.md', 'CHANGELOG.txt', 'CHANGELOG', 'HISTORY.md']
        
        for changelog_name in changelog_files:
            changelog_path = project_path / changelog_name
            if changelog_path.exists():
                try:
                    content = changelog_path.read_text(encoding=config.encoding)
                    releases.extend(self._parse_changelog_content(content))
                    break  # Use first found
                except Exception as e:
                    logger.warning(f"Erreur lors de la lecture de {changelog_path}: {e}")
        
        return releases
    
    def _parse_changelog_content(self, content: str) -> List[Release]:
        """Parse le contenu d'un changelog pour extraire les releases."""
        releases = []
        
        # Regex to detect versions (common formats)
        version_patterns = [
            r'^##?\s*\[?v?(\d+\.\d+\.\d+[^\]]*)\]?\s*-?\s*(\d{4}-\d{2}-\d{2})?',  # ## [1.0.0] - 2023-01-01
            r'^##?\s*Version\s+(\d+\.\d+\.\d+[^\s]*)\s*\((\d{4}-\d{2}-\d{2})\)?',  # ## Version 1.0.0 (2023-01-01)
            r'^##?\s*(\d+\.\d+\.\d+[^\s]*)\s*\((\d{4}-\d{2}-\d{2})\)?',  # ## 1.0.0 (2023-01-01)
        ]
        
        lines = content.split('\n')
        current_release = None
        current_description = []
        
        for line in lines:
            # Chercher un header de version
            version_found = False
            for pattern in version_patterns:
                match = re.match(pattern, line.strip(), re.IGNORECASE)
                if match:
                    # Save previous release
                    if current_release:
                        current_release.description = '\n'.join(current_description).strip()
                        releases.append(current_release)
                    
                    # Nouvelle release
                    version = match.group(1)
                    date_str = match.group(2) if match.lastindex >= 2 else None
                    
                    release_date = None
                    if date_str:
                        try:
                            release_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                        except ValueError:
                            pass
                    
                    current_release = Release(
                        tag=f"v{version}",
                        name=version,
                        description="",
                        author=Author(name="Unknown"),
                        created_at=release_date or datetime.now(timezone.utc),
                        published_at=release_date,
                        is_prerelease='alpha' in version.lower() or 'beta' in version.lower() or 'rc' in version.lower(),
                        is_draft=False,
                        url=None
                    )
                    
                    current_description = []
                    version_found = True
                    break
            
            if not version_found and current_release:
                # Add to current release description
                # Ignore lower level headers and empty lines at beginning
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('###'):
                    current_description.append(line)
        
        # Save last release
        if current_release:
            current_release.description = '\n'.join(current_description).strip()
            releases.append(current_release)
        
        return releases