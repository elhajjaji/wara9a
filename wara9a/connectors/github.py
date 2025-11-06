"""
Connecteur GitHub pour Wara9a.

Collecte les données depuis l'API GitHub REST v4 :
- Repository metadata
- Commits récents
- Issues et pull requests  
- Releases
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import os

import requests
from requests.adapters import HTTPAdapter
try:
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    from urllib3.util.retry import Retry

from wara9a.core.connector_base import ConnectorBase, ConnectorError, ConnectorConnectionError
from wara9a.core.models import (
    ProjectData, Repository, Commit, Issue, PullRequest, Release,
    Author, Label, SourceType, IssueStatus, IssueType
)
from wara9a.core.config import SourceConfig, GitHubSourceConfig


logger = logging.getLogger(__name__)


class GitHubConnector(ConnectorBase):
    """
    Connecteur pour l'API GitHub REST.
    
    Collecte les données d'un repository GitHub via l'API REST v4.
    Supporte l'authentification par token pour augmenter les limites de taux.
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.session = self._create_session()
    
    @property
    def connector_type(self) -> str:
        return "github"
    
    @property
    def display_name(self) -> str:
        return "GitHub"
    
    @property
    def description(self) -> str:
        return "Connecteur pour les repositories GitHub via API REST"
    
    @property
    def required_config_fields(self) -> List[str]:
        return ["repo"]
    
    @property
    def optional_config_fields(self) -> List[str]:
        return ["token", "branch", "max_commits", "max_issues", "include_forks"]
    
    def validate_config(self, config: SourceConfig) -> List[str]:
        """Valide la configuration du connecteur GitHub."""
        errors = []
        
        if not hasattr(config, 'repo') or not config.repo:
            errors.append("Le champ 'repo' est obligatoire (format: owner/repo)")
            return errors
        
        # Valider le format du repo
        if '/' not in config.repo or len(config.repo.split('/')) != 2:
            errors.append("Le format du repo doit être 'owner/repo'")
        
        # Valider les limites numériques
        if hasattr(config, 'max_commits') and config.max_commits < 1:
            errors.append("max_commits doit être >= 1")
        
        if hasattr(config, 'max_issues') and config.max_issues < 1:
            errors.append("max_issues doit être >= 1")
        
        return errors
    
    def collect(self, config: SourceConfig) -> ProjectData:
        """
        Collecte les données depuis GitHub.
        
        Args:
            config: Configuration GitHub (GitHubSourceConfig)
            
        Returns:
            Données normalisées du projet
            
        Raises:
            ConnectorError: Si erreur lors de la collecte
        """
        if not isinstance(config, GitHubSourceConfig):
            # Convertir SourceConfig générique vers GitHubSourceConfig
            github_config = GitHubSourceConfig(**config.model_dump())
        else:
            github_config = config
        
        # Valider la configuration
        errors = self.validate_config(github_config)
        if errors:
            raise ConnectorError(f"Configuration invalide: {errors}")
        
        logger.info(f"Collecte depuis GitHub: {github_config.repo}")
        
        try:
            # Configurer l'authentification si token fourni
            if github_config.token:
                self.session.headers['Authorization'] = f"token {github_config.token}"
            
            # Collecter les données
            repository = self._get_repository(github_config)
            commits = self._get_commits(github_config)
            issues = self._get_issues(github_config)
            pull_requests = self._get_pull_requests(github_config)
            releases = self._get_releases(github_config)
            
            project_data = ProjectData(
                repository=repository,
                commits=commits,
                issues=issues,
                pull_requests=pull_requests,
                releases=releases,
                source_type=SourceType.GITHUB,
                source_config=github_config.model_dump()
            )
            
            logger.info(f"Collecte GitHub terminée: {len(commits)} commits, "
                       f"{len(issues)} issues, {len(pull_requests)} PRs, "
                       f"{len(releases)} releases")
            
            return project_data
            
        except requests.exceptions.RequestException as e:
            raise ConnectorConnectionError(f"Erreur de connexion GitHub: {e}")
        except Exception as e:
            raise ConnectorError(f"Erreur lors de la collecte GitHub: {e}")
    
    def _create_session(self) -> requests.Session:
        """Crée une session HTTP avec retry automatique."""
        session = requests.Session()
        
        # Configuration retry
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers par défaut
        session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Wara9a/1.0.0'
        })
        
        return session
    
    def _get_repository(self, config: GitHubSourceConfig) -> Repository:
        """Collecte les métadonnées du repository."""
        url = f"{self.BASE_URL}/repos/{config.repo}"
        response = self._make_request(url)
        
        repo_data = response.json()
        
        return Repository(
            name=repo_data['name'],
            full_name=repo_data['full_name'],
            description=repo_data.get('description'),
            url=repo_data['html_url'],
            default_branch=repo_data['default_branch'],
            languages=self._get_languages(config),
            topics=repo_data.get('topics', []),
            created_at=self._parse_github_date(repo_data['created_at']),
            updated_at=self._parse_github_date(repo_data['updated_at']),
            stars_count=repo_data['stargazers_count'],
            forks_count=repo_data['forks_count']
        )
    
    def _get_languages(self, config: GitHubSourceConfig) -> List[str]:
        """Collecte les langages du repository."""
        url = f"{self.BASE_URL}/repos/{config.repo}/languages"
        response = self._make_request(url)
        
        languages_data = response.json()
        # Trier par nombre de bytes (plus utilisé en premier)
        return list(languages_data.keys())
    
    def _get_commits(self, config: GitHubSourceConfig) -> List[Commit]:
        """Collecte les commits récents."""
        url = f"{self.BASE_URL}/repos/{config.repo}/commits"
        params = {
            'per_page': min(config.max_commits or 100, 100),
            'sha': config.branch or None
        }
        
        response = self._make_request(url, params=params)
        commits_data = response.json()
        
        commits = []
        for commit_data in commits_data:
            commit = Commit(
                sha=commit_data['sha'],
                message=commit_data['commit']['message'],
                author=self._parse_author(commit_data),
                date=self._parse_github_date(commit_data['commit']['author']['date']),
                url=commit_data['html_url'],
                # Note: files_changed nécessite une requête supplémentaire par commit
                # On le fera seulement pour les quelques commits les plus récents
                files_changed=[],
                additions=0,
                deletions=0
            )
            commits.append(commit)
        
        # Enrichir les 5 premiers commits avec les détails de fichiers
        for commit in commits[:5]:
            self._enrich_commit_details(config, commit)
        
        return commits
    
    def _enrich_commit_details(self, config: GitHubSourceConfig, commit: Commit) -> None:
        """Enrichit un commit avec les détails de fichiers modifiés."""
        try:
            url = f"{self.BASE_URL}/repos/{config.repo}/commits/{commit.sha}"
            response = self._make_request(url)
            commit_details = response.json()
            
            commit.files_changed = [f['filename'] for f in commit_details.get('files', [])]
            
            stats = commit_details.get('stats', {})
            commit.additions = stats.get('additions', 0)
            commit.deletions = stats.get('deletions', 0)
            
        except Exception as e:
            logger.warning(f"Impossible d'enrichir le commit {commit.sha[:7]}: {e}")
    
    def _get_issues(self, config: GitHubSourceConfig) -> List[Issue]:
        """Collecte les issues du repository."""
        url = f"{self.BASE_URL}/repos/{config.repo}/issues"
        params = {
            'state': 'all',
            'per_page': min(config.max_issues or 100, 100),
            'sort': 'updated',
            'direction': 'desc'
        }
        
        response = self._make_request(url, params=params)
        issues_data = response.json()
        
        issues = []
        for issue_data in issues_data:
            # Ignorer les pull requests (GitHub les retourne dans /issues)
            if 'pull_request' in issue_data:
                continue
            
            issue = Issue(
                id=str(issue_data['number']),
                title=issue_data['title'],
                description=issue_data.get('body'),
                status=IssueStatus.OPEN if issue_data['state'] == 'open' else IssueStatus.CLOSED,
                type=self._guess_issue_type(issue_data),
                author=self._parse_user_as_author(issue_data['user']),
                assignee=self._parse_user_as_author(issue_data['assignee']) if issue_data.get('assignee') else None,
                labels=self._parse_labels(issue_data.get('labels', [])),
                created_at=self._parse_github_date(issue_data['created_at']),
                updated_at=self._parse_github_date(issue_data['updated_at']),
                closed_at=self._parse_github_date(issue_data['closed_at']) if issue_data.get('closed_at') else None,
                url=issue_data['html_url'],
                comments_count=issue_data['comments']
            )
            issues.append(issue)
        
        return issues
    
    def _get_pull_requests(self, config: GitHubSourceConfig) -> List[PullRequest]:
        """Collecte les pull requests du repository."""
        url = f"{self.BASE_URL}/repos/{config.repo}/pulls"
        params = {
            'state': 'all',
            'per_page': min(config.max_issues or 50, 100),  # Réutiliser max_issues
            'sort': 'updated',
            'direction': 'desc'
        }
        
        response = self._make_request(url, params=params)
        prs_data = response.json()
        
        pull_requests = []
        for pr_data in prs_data:
            pr = PullRequest(
                id=str(pr_data['number']),
                title=pr_data['title'],
                description=pr_data.get('body'),
                author=self._parse_user_as_author(pr_data['user']),
                status=pr_data['state'],  # open, closed
                source_branch=pr_data['head']['ref'],
                target_branch=pr_data['base']['ref'],
                created_at=self._parse_github_date(pr_data['created_at']),
                merged_at=self._parse_github_date(pr_data['merged_at']) if pr_data.get('merged_at') else None,
                url=pr_data['html_url'],
                commits=[],  # Pourrait être enrichi avec une requête supplémentaire
                files_changed=pr_data.get('changed_files', 0),
                additions=pr_data.get('additions', 0),
                deletions=pr_data.get('deletions', 0)
            )
            pull_requests.append(pr)
        
        return pull_requests
    
    def _get_releases(self, config: GitHubSourceConfig) -> List[Release]:
        """Collecte les releases du repository."""
        url = f"{self.BASE_URL}/repos/{config.repo}/releases"
        params = {'per_page': 50}
        
        response = self._make_request(url, params=params)
        releases_data = response.json()
        
        releases = []
        for release_data in releases_data:
            release = Release(
                tag=release_data['tag_name'],
                name=release_data['name'] or release_data['tag_name'],
                description=release_data.get('body'),
                author=self._parse_user_as_author(release_data['author']) if release_data.get('author') else Author(name="Unknown"),
                created_at=self._parse_github_date(release_data['created_at']),
                published_at=self._parse_github_date(release_data['published_at']) if release_data.get('published_at') else None,
                is_prerelease=release_data['prerelease'],
                is_draft=release_data['draft'],
                url=release_data['html_url']
            )
            releases.append(release)
        
        return releases
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Effectue une requête HTTP avec gestion d'erreurs."""
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Vérifier les limites de taux
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-Remaining'])
                if remaining < 10:
                    logger.warning(f"Limite de taux GitHub basse: {remaining} requêtes restantes")
            
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ConnectorError(f"Repository non trouvé ou non accessible: {url}")
            elif e.response.status_code == 403:
                raise ConnectorError("Accès refusé. Vérifiez votre token GitHub.")
            elif e.response.status_code == 401:
                raise ConnectorError("Authentification échouée. Token GitHub invalide.")
            else:
                raise ConnectorConnectionError(f"Erreur HTTP {e.response.status_code}: {url}")
        except requests.exceptions.Timeout:
            raise ConnectorConnectionError(f"Timeout lors de la requête: {url}")
        except requests.exceptions.RequestException as e:
            raise ConnectorConnectionError(f"Erreur de requête: {e}")
    
    def _parse_github_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse une date GitHub au format ISO 8601."""
        if not date_str:
            return None
        try:
            # GitHub utilise le format ISO avec Z pour UTC
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            logger.warning(f"Format de date invalide: {date_str}")
            return None
    
    def _parse_author(self, commit_data: Dict[str, Any]) -> Author:
        """Parse les informations d'auteur d'un commit."""
        commit_info = commit_data['commit']
        author_info = commit_info['author']
        github_user = commit_data.get('author')
        
        return Author(
            name=author_info['name'],
            email=author_info['email'],
            username=github_user['login'] if github_user else None,
            avatar_url=github_user['avatar_url'] if github_user else None
        )
    
    def _parse_user_as_author(self, user_data: Optional[Dict[str, Any]]) -> Author:
        """Parse un utilisateur GitHub en Author."""
        if not user_data:
            return Author(name="Unknown")
        
        return Author(
            name=user_data.get('name') or user_data['login'],
            username=user_data['login'],
            avatar_url=user_data.get('avatar_url')
        )
    
    def _parse_labels(self, labels_data: List[Dict[str, Any]]) -> List[Label]:
        """Parse les labels GitHub."""
        return [
            Label(
                name=label['name'],
                color=f"#{label['color']}",
                description=label.get('description')
            )
            for label in labels_data
        ]
    
    def _guess_issue_type(self, issue_data: Dict[str, Any]) -> IssueType:
        """Devine le type d'issue basé sur les labels et le titre."""
        labels = [label['name'].lower() for label in issue_data.get('labels', [])]
        title_lower = issue_data['title'].lower()
        
        # Chercher dans les labels d'abord
        if any(label in ['bug', 'defect', 'error'] for label in labels):
            return IssueType.BUG
        elif any(label in ['enhancement', 'feature', 'new-feature'] for label in labels):
            return IssueType.FEATURE
        elif any(label in ['task', 'chore', 'maintenance'] for label in labels):
            return IssueType.TASK
        elif any(label in ['epic'] for label in labels):
            return IssueType.EPIC
        
        # Fallback sur le titre
        if any(word in title_lower for word in ['bug', 'fix', 'error', 'issue']):
            return IssueType.BUG
        elif any(word in title_lower for word in ['feature', 'add', 'implement']):
            return IssueType.FEATURE
        
        return IssueType.TASK  # Par défaut