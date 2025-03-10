from typing import Dict, List, Optional
from pathlib import Path
import git
from git import Repo
from datetime import datetime
import requests
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from .github import GitHubClient, GitHubContributor
from ..utils.language import LanguageDetector

@dataclass
class ContributorStats:
    name: str
    email: str
    commit_count: int
    lines_added: int
    lines_deleted: int
    files_changed: int
    languages: Dict[str, int]
    issues: int
    pull_requests: int
    stars: int
    forks: int
    watchers: int
    
    @property
    def total_changes(self) -> int:
        """Calculate total number of changes (additions + deletions)."""
        return self.lines_added + self.lines_deleted
    
    def get_percentage(self, total: int) -> float:
        """Calculate percentage of total changes."""
        if total == 0:
            return 0.0
        return (self.total_changes / total) * 100

class Repository:
    def __init__(self, path: str, is_remote: bool = False):
        """Initialize the repository analyzer.
        
        Args:
            path: Local path or GitHub repository URL
            is_remote: Whether the repository is remote (GitHub)
        """
        self.path = path
        self.is_remote = is_remote
        self.repo = None
        self.console = Console()
        self.language_detector = LanguageDetector()
        
        if not is_remote:
            try:
                self.repo = Repo(path)
            except git.InvalidGitRepositoryError:
                raise ValueError(f"Invalid Git repository at {path}")
        else:
            # For remote repositories, we'll use the GitHub API
            self.github_url = path
            self.owner, self.repo_name = self._parse_github_url(path)
            self.github_client = GitHubClient()
    
    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """Parse GitHub URL to get owner and repository name."""
        parts = url.rstrip('/').split('/')
        if len(parts) < 4:
            raise ValueError("Invalid GitHub URL")
        return parts[-2], parts[-1]
    
    def get_contributor_stats(self) -> List[ContributorStats]:
        """Get statistics for all contributors."""
        if self.is_remote:
            return self._get_remote_contributor_stats()
        return self._get_local_contributor_stats()
    
    def _get_local_contributor_stats(self) -> List[ContributorStats]:
        """Get contributor statistics from local repository."""
        stats = {}
        
        for commit in self.repo.iter_commits():
            author = commit.author
            if author.email not in stats:
                stats[author.email] = ContributorStats(
                    name=author.name,
                    email=author.email,
                    commit_count=0,
                    lines_added=0,
                    lines_deleted=0,
                    files_changed=0,
                    languages={},
                    issues=0,
                    pull_requests=0,
                    stars=0,
                    forks=0,
                    watchers=0
                )
            
            contributor = stats[author.email]
            contributor.commit_count += 1
            
            # Get diff stats
            if commit.parents:
                # Get the diff between this commit and its parent
                diff = self.repo.git.diff(
                    commit.parents[0].hexsha,
                    commit.hexsha,
                    '--numstat'
                ).split('\n')
                
                for line in diff:
                    if line.strip():
                        try:
                            # Parse numstat output: additions deletions filename
                            additions, deletions, filename = line.split('\t')
                            contributor.lines_added += int(additions)
                            contributor.lines_deleted += int(deletions)
                            contributor.files_changed += 1
                            
                            # Track language contributions
                            if filename:
                                lang = self.language_detector.detect_language(filename)
                                contributor.languages[lang] = contributor.languages.get(lang, 0) + 1
                        except (ValueError, IndexError):
                            # Skip malformed lines
                            continue
        
        return list(stats.values())
    
    def _get_remote_contributor_stats(self) -> List[ContributorStats]:
        """Get contributor statistics from GitHub repository."""
        github_stats = self.github_client.get_contributor_stats(self.owner, self.repo_name)
        
        # Convert GitHub stats to our format
        return [
            ContributorStats(
                name=stat.name,
                email=stat.email,
                commit_count=stat.commit_count,
                lines_added=stat.lines_added,
                lines_deleted=stat.lines_deleted,
                files_changed=stat.files_changed,
                languages=stat.languages,
                issues=stat.issues,
                pull_requests=stat.pull_requests,
                stars=stat.stars,
                forks=stat.forks,
                watchers=stat.watchers
            )
            for stat in github_stats
        ]
    
    def get_top_languages(self) -> Dict[str, int]:
        """Get top programming languages in the repository."""
        if self.is_remote:
            return self._get_remote_top_languages()
        return self._get_local_top_languages()
    
    def _get_local_top_languages(self) -> Dict[str, int]:
        """Get top languages from local repository."""
        languages = {}
        for item in self.repo.git.ls_tree('-r', '--name-only', 'HEAD').split('\n'):
            if item:
                lang = self.language_detector.detect_language(item)
                languages[lang] = languages.get(lang, 0) + 1
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
    
    def _get_remote_top_languages(self) -> Dict[str, int]:
        """Get top languages from GitHub repository."""
        return self.github_client.get_repository_languages(self.owner, self.repo_name)
    
    def get_contribution_percentages(self) -> List[Dict]:
        """Get contribution percentages for all contributors."""
        stats = self.get_contributor_stats()
        total_changes = sum(stat.total_changes for stat in stats)
        
        percentages = []
        for stat in stats:
            percentage = stat.get_percentage(total_changes)
            percentages.append({
                'name': stat.name,
                'email': stat.email,
                'commit_count': stat.commit_count,
                'lines_added': stat.lines_added,
                'lines_deleted': stat.lines_deleted,
                'files_changed': stat.files_changed,
                'total_changes': stat.total_changes,
                'percentage': percentage,
                'languages': stat.languages
            })
        
        return sorted(percentages, key=lambda x: x['percentage'], reverse=True)
    
    def display_contribution_stats(self):
        """Display contribution statistics in a formatted table."""
        percentages = self.get_contribution_percentages()
        
        table = Table(title="Repository Contribution Statistics")
        table.add_column("Contributor", style="cyan")
        table.add_column("Commits", justify="right")
        table.add_column("Lines Added", justify="right")
        table.add_column("Lines Deleted", justify="right")
        table.add_column("Files Changed", justify="right")
        table.add_column("Total Changes", justify="right")
        table.add_column("Percentage", justify="right")
        table.add_column("Top Languages", style="green")
        
        for stat in percentages:
            # Get top 3 languages
            top_languages = sorted(
                stat['languages'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            top_langs_str = ", ".join(f"{lang}({count})" for lang, count in top_languages)
            
            table.add_row(
                stat['name'],
                str(stat['commit_count']),
                str(stat['lines_added']),
                str(stat['lines_deleted']),
                str(stat['files_changed']),
                str(stat['total_changes']),
                f"{stat['percentage']:.1f}%",
                top_langs_str
            )
        
        self.console.print(table)
    
    def get_language_percentages(self) -> Dict[str, float]:
        """Calculate percentage of code in each language."""
        languages = self.get_top_languages()
        total_lines = sum(languages.values())
        
        if total_lines == 0:
            return {}
            
        return {
            lang: (count / total_lines) * 100
            for lang, count in languages.items()
        }
    
    def display_language_stats(self):
        """Display language statistics in a formatted table."""
        languages = self.get_top_languages()
        percentages = self.get_language_percentages()
        
        table = Table(title="Repository Language Statistics")
        table.add_column("Language", style="cyan")
        table.add_column("Lines of Code", justify="right")
        table.add_column("Percentage", justify="right")
        
        for lang, count in languages.items():
            percentage = percentages.get(lang, 0)
            table.add_row(
                lang,
                str(count),
                f"{percentage:.1f}%"
            )
        
        self.console.print(table) 