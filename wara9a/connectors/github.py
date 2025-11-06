"""
Connecteur GitHub pour Wara9a.

Collects data from GitHub REST API v4:
- Repository metadata
- Recent commits
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

from wara9a.core.connector_base import GitConnector, ConnectorError, ConnectorConnectionError
from wara9a.core.models import (
    ProjectData, TechnicalData, Repository, Release,
    TechnicalCommit, TechnicalPullRequest, CodeChange, CodeMetrics,
    Author, Label, SourceType
)
from wara9a.core.config import SourceConfig, GitHubSourceConfig


logger = logging.getLogger(__name__)


class GitHubConnector(GitConnector):
    """
    GitHub connector for technical documentation extraction.
    
    Extracts technical documentation from GitHub repositories:
    - Commits history and code changes
    - Pull requests and code reviews
    - Repository structure and metadata
    - Releases and tags
    
    Category: GIT (Technical Documentation)
    Data Source: GitHub REST API v4
    Authentication: Personal Access Token (optional but recommended)
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
            errors.append("Repo format must be 'owner/repo'")
        
        # Validate numeric limits
        if hasattr(config, 'max_commits') and config.max_commits < 1:
            errors.append("max_commits must be >= 1")
        
        if hasattr(config, 'max_issues') and config.max_issues < 1:
            errors.append("max_issues must be >= 1")
        
        return errors
    
    def collect(self, config: SourceConfig) -> ProjectData:
        """
        Collects data from GitHub.
        
        Args:
            config: Configuration GitHub (GitHubSourceConfig)
            
        Returns:
            Normalized project data
            
        Raises:
            ConnectorError: Si erreur lors de la collecte
        """
        if not isinstance(config, GitHubSourceConfig):
            # Convert generic SourceConfig to GitHubSourceConfig
            github_config = GitHubSourceConfig(**config.model_dump())
        else:
            github_config = config
        
        # Valider la configuration
        errors = self.validate_config(github_config)
        if errors:
            raise ConnectorError(f"Configuration invalide: {errors}")
        
        logger.info(f"🔍 Collecting technical documentation from GitHub: {github_config.repo}")
        
        try:
            # Configure authentication if token provided
            if github_config.token:
                self.session.headers['Authorization'] = f"token {github_config.token}"
            
            # Collect repository info and releases
            repository = self._get_repository(github_config)
            releases = self._get_releases(github_config)
            
            # Collect technical data (new standardized format)
            technical_commits = self._get_technical_commits(github_config)
            technical_prs = self._get_technical_pull_requests(github_config)
            code_metrics = self._get_code_metrics(github_config)
            
            # Create TechnicalData structure
            technical_data = TechnicalData(
                commits=technical_commits,
                pull_requests=technical_prs,
                code_metrics=code_metrics,
                technical_debt=[],  # Can be implemented later
                repository_name=github_config.repo,
                repository_url=repository.url,
                default_branch=repository.default_branch,
                source_type=SourceType.GITHUB
            )
            
            # Create ProjectData with new structure
            project_data = ProjectData(
                functional_data=None,  # GitHub doesn't provide functional data
                technical_data=technical_data,
                repository=repository,
                releases=releases,
                source_type=SourceType.GITHUB,
                source_config=github_config.model_dump()
            )
            
            logger.info(f"✅ GitHub collection completed: {len(technical_commits)} commits, "
                       f"{len(technical_prs)} PRs, {len(releases)} releases")
            
            return project_data
            
        except requests.exceptions.RequestException as e:
            raise ConnectorConnectionError(f"Erreur de connexion GitHub: {e}")
        except Exception as e:
            raise ConnectorError(f"Erreur lors de la collecte GitHub: {e}")
    
    def _create_session(self) -> requests.Session:
        """Creates HTTP session with automatic retry."""
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
        
        # Default headers
        session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Wara9a/1.0.0'
        })
        
        return session
    
    def _get_repository(self, config: GitHubSourceConfig) -> Repository:
        """Collects repository metadata."""
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
        # Sort by byte count (most used first)
        return list(languages_data.keys())
    
    def _get_technical_commits(self, config: GitHubSourceConfig) -> List[TechnicalCommit]:
        """Collects commits with detailed technical information."""
        url = f"{self.BASE_URL}/repos/{config.repo}/commits"
        params = {
            'per_page': min(config.max_commits or 100, 100),
            'sha': config.branch or None
        }
        
        response = self._make_request(url, params=params)
        commits_data = response.json()
        
        commits = []
        for commit_data in commits_data:
            # Get detailed commit info (includes file changes)
            detailed_url = f"{self.BASE_URL}/repos/{config.repo}/commits/{commit_data['sha']}"
            try:
                detailed_response = self._make_request(detailed_url)
                detailed_data = detailed_response.json()
            except Exception as e:
                logger.warning(f"Could not get details for commit {commit_data['sha'][:7]}: {e}")
                detailed_data = commit_data
            
            # Parse commit message
            message = commit_data['commit']['message']
            message_lines = message.split('\n')
            message_subject = message_lines[0]
            message_body = '\n'.join(message_lines[1:]).strip() if len(message_lines) > 1 else None
            
            # Extract linked issues from message (#123)
            import re
            linked_issues = re.findall(r'#(\d+)', message)
            
            # Parse file changes
            files_changed = []
            for file_data in detailed_data.get('files', []):
                change = CodeChange(
                    file_path=file_data['filename'],
                    change_type=file_data['status'],  # added, modified, deleted
                    additions=file_data.get('additions', 0),
                    deletions=file_data.get('deletions', 0),
                    changes=file_data.get('changes', 0),
                    language=self._detect_language(file_data['filename'])
                )
                files_changed.append(change)
            
            commit = TechnicalCommit(
                sha=commit_data['sha'],
                short_sha=commit_data['sha'][:7],
                message=message,
                message_subject=message_subject,
                message_body=message_body,
                author=self._parse_author(commit_data),
                date=self._parse_github_date(commit_data['commit']['author']['date']),
                url=commit_data['html_url'],
                files_changed=files_changed,
                total_additions=detailed_data.get('stats', {}).get('additions', 0),
                total_deletions=detailed_data.get('stats', {}).get('deletions', 0),
                linked_issues=linked_issues,
                linked_prs=[]
            )
            commits.append(commit)
        
        return commits
    
    def _detect_language(self, filename: str) -> Optional[str]:
        """Detects programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.cs': 'csharp',
        }
        import os
        _, ext = os.path.splitext(filename)
        return ext_map.get(ext.lower())
    
    def _get_technical_pull_requests(self, config: GitHubSourceConfig) -> List[TechnicalPullRequest]:
        """Collects pull requests with review information."""
        url = f"{self.BASE_URL}/repos/{config.repo}/pulls"
        params = {
            'state': 'all',
            'per_page': min(config.max_issues or 50, 100),
            'sort': 'updated',
            'direction': 'desc'
        }
        
        response = self._make_request(url, params=params)
        prs_data = response.json()
        
        pull_requests = []
        for pr_data in prs_data:
            # Get review information
            reviewers = []
            approved_by = []
            review_comments_count = 0
            
            try:
                reviews_url = f"{self.BASE_URL}/repos/{config.repo}/pulls/{pr_data['number']}/reviews"
                reviews_response = self._make_request(reviews_url)
                reviews = reviews_response.json()
                
                review_comments_count = len(reviews)
                seen_reviewers = set()
                
                for review in reviews:
                    reviewer_login = review['user']['login']
                    if reviewer_login not in seen_reviewers:
                        reviewers.append(reviewer_login)
                        seen_reviewers.add(reviewer_login)
                    
                    if review['state'] == 'APPROVED':
                        if reviewer_login not in approved_by:
                            approved_by.append(reviewer_login)
                            
            except Exception as e:
                logger.warning(f"Could not get reviews for PR #{pr_data['number']}: {e}")
            
            # Extract linked issues from PR body and title
            import re
            pr_text = f"{pr_data['title']} {pr_data.get('body', '')}"
            linked_issues = re.findall(r'#(\d+)', pr_text)
            
            # Determine merge status
            is_merged = pr_data.get('merged_at') is not None
            state = 'merged' if is_merged else pr_data['state']
            
            pr = TechnicalPullRequest(
                id=str(pr_data['number']),
                number=pr_data['number'],
                title=pr_data['title'],
                description=pr_data.get('body'),
                author=self._parse_user_as_author(pr_data['user']),
                state=state,
                is_merged=is_merged,
                source_branch=pr_data['head']['ref'],
                target_branch=pr_data['base']['ref'],
                created_at=self._parse_github_date(pr_data['created_at']),
                updated_at=self._parse_github_date(pr_data['updated_at']),
                merged_at=self._parse_github_date(pr_data['merged_at']) if pr_data.get('merged_at') else None,
                closed_at=self._parse_github_date(pr_data['closed_at']) if pr_data.get('closed_at') else None,
                url=pr_data['html_url'],
                commits=[],  # Could be enriched but would require many API calls
                files_changed_count=pr_data.get('changed_files', 0),
                additions=pr_data.get('additions', 0),
                deletions=pr_data.get('deletions', 0),
                reviewers=reviewers,
                approved_by=approved_by,
                review_comments_count=review_comments_count,
                linked_issues=linked_issues,
                labels=[label['name'] for label in pr_data.get('labels', [])]
            )
            pull_requests.append(pr)
        
        return pull_requests
    
    def _get_code_metrics(self, config: GitHubSourceConfig) -> Dict[str, CodeMetrics]:
        """Collects code metrics from repository languages statistics."""
        url = f"{self.BASE_URL}/repos/{config.repo}/languages"
        response = self._make_request(url)
        
        languages_data = response.json()
        
        # Convert byte counts to metrics
        metrics = {}
        total_bytes = sum(languages_data.values())
        
        for language, bytes_count in languages_data.items():
            # Estimate lines of code (rough average: 50 bytes per line)
            estimated_lines = bytes_count // 50
            percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            
            metrics[language] = CodeMetrics(
                language=language,
                files_count=0,  # GitHub API doesn't provide this easily
                lines_of_code=estimated_lines,
                percentage=round(percentage, 2),
                complexity=None  # Would require code analysis
            )
        
        return metrics
    
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
        """Performs HTTP request with error handling."""
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Check rate limits
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = int(response.headers['X-RateLimit-Remaining'])
                if remaining < 10:
                    logger.warning(f"GitHub rate limit low: {remaining} requests remaining")
            
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ConnectorError(f"Repository not found or not accessible: {url}")
            elif e.response.status_code == 403:
                raise ConnectorError("Access denied. Check your GitHub token.")
            elif e.response.status_code == 401:
                raise ConnectorError("Authentication failed. Invalid GitHub token.")
            else:
                raise ConnectorConnectionError(f"Erreur HTTP {e.response.status_code}: {url}")
        except requests.exceptions.Timeout:
            raise ConnectorConnectionError(f"Timeout during request: {url}")
        except requests.exceptions.RequestException as e:
            raise ConnectorConnectionError(f"Request error: {e}")
    
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