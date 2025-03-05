import os
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class GitHubContributor:
    name: str
    email: str
    commit_count: int
    lines_added: int
    lines_deleted: int
    files_changed: int
    languages: Dict[str, int]
    issues: int = 0
    pull_requests: int = 0
    stars: int = 0
    forks: int = 0
    watchers: int = 0

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token (optional)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitPulse'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the GitHub API."""
        url = f'https://api.github.com{endpoint}'
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_contributor_stats(self, owner: str, repo: str) -> List[GitHubContributor]:
        """Get contributor statistics for a repository."""
        # Get repository info for stars, forks, watchers
        repo_info = self._make_request(f'/repos/{owner}/{repo}')
        
        # Get contributors list
        contributors = self._make_request(f'/repos/{owner}/{repo}/contributors')
        
        stats = []
        for contributor in contributors:
            # Get detailed contributor stats
            contributor_stats = self._make_request(
                f'/repos/{owner}/{repo}/stats/contributors'
            )
            
            # Find the contributor's stats
            user_stats = next(
                (stat for stat in contributor_stats if stat['author']['id'] == contributor['id']),
                None
            )
            
            if user_stats:
                # Calculate total changes
                total_additions = sum(week['a'] for week in user_stats['weeks'])
                total_deletions = sum(week['d'] for week in user_stats['weeks'])
                total_commits = sum(week['c'] for week in user_stats['weeks'])
                
                # Get language stats
                languages = self._get_contributor_languages(owner, repo, contributor['login'])
                
                # Get issues and PRs created by the contributor
                issues = self._make_request(
                    f'/repos/{owner}/{repo}/issues',
                    params={'creator': contributor['login'], 'state': 'all'}
                )
                pull_requests = self._make_request(
                    f'/repos/{owner}/{repo}/pulls',
                    params={'creator': contributor['login'], 'state': 'all'}
                )
                
                # Generate a default email if not available
                email = f"{contributor['login']}@users.noreply.github.com"
                
                stats.append(GitHubContributor(
                    name=contributor['login'],
                    email=email,
                    commit_count=total_commits,
                    lines_added=total_additions,
                    lines_deleted=total_deletions,
                    files_changed=0,  # GitHub API doesn't provide this directly
                    languages=languages,
                    issues=len(issues),
                    pull_requests=len(pull_requests),
                    stars=repo_info['stargazers_count'],
                    forks=repo_info['forks_count'],
                    watchers=repo_info['watchers_count']
                ))
        
        return stats
    
    def _get_contributor_languages(self, owner: str, repo: str, username: str) -> Dict[str, int]:
        """Get language statistics for a specific contributor."""
        # Get all commits by the contributor
        commits = self._make_request(
            f'/repos/{owner}/{repo}/commits',
            params={'author': username}
        )
        
        languages = {}
        for commit in commits:
            # Get the commit details
            commit_details = self._make_request(
                f'/repos/{owner}/{repo}/commits/{commit["sha"]}'
            )
            
            # Get the files changed
            for file in commit_details['files']:
                if file['filename']:
                    lang = self._detect_language(file['filename'])
                    languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get language statistics for the entire repository."""
        languages = self._make_request(f'/repos/{owner}/{repo}/languages')
        return languages
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        # Map file extensions to languages
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.m': 'MATLAB',
            '.sh': 'Shell',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.txt': 'Text',
        }
        
        ext = filename.lower()
        for extension, language in extension_map.items():
            if ext.endswith(extension):
                return language
        
        return 'Unknown' 