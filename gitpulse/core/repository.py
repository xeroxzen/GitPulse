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
from .codebase import Codebase
from .contributor import Contributor
from .contributor_analyzer import ContributorAnalyzer

@dataclass
class ContributorStats:
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
    changes_count: int = 0
    percentage: float = 0.0
    total_lines: int = 0
    percentage_lines: float = 0.0
    percentage_languages: float = 0.0
    total_issues: int = 0
    percentage_issues: float = 0.0
    total_pull_requests: int = 0
    percentage_pull_requests: float = 0.0
    total_stars: int = 0
    percentage_stars: float = 0.0
    total_forks: int = 0
    percentage_forks: float = 0.0
    
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
        self.codebase = None
        self.contributor_analyzer = None
        
        # Files to exclude from analysis
        self.excluded_files = [
            "package-lock.json",
            "yarn.lock"
        ]
        
        if not is_remote:
            try:
                self.repo = Repo(path)
                self.codebase = Codebase(path)
                self.contributor_analyzer = ContributorAnalyzer(self.repo)
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
    
    def analyze_codebase(self):
        """Analyze the codebase/repository."""
        if self.is_remote:
            self.console.print("[yellow]Codebase analysis is limited for remote repositories.")
            # For remote repos, we can only show basic info from GitHub API
            repo_info = self.github_client._make_request(f'/repos/{self.owner}/{self.repo_name}')
            
            # Create a table for basic info
            table = Table(title="Repository Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value")
            
            # Add rows for basic info
            table.add_row("Name", repo_info.get('name', 'Unknown'))
            table.add_row("Owner", repo_info.get('owner', {}).get('login', 'Unknown'))
            table.add_row("Description", repo_info.get('description', 'No description'))
            table.add_row("Stars", str(repo_info.get('stargazers_count', 0)))
            table.add_row("Forks", str(repo_info.get('forks_count', 0)))
            table.add_row("Watchers", str(repo_info.get('watchers_count', 0)))
            table.add_row("Open Issues", str(repo_info.get('open_issues_count', 0)))
            table.add_row("Default Branch", repo_info.get('default_branch', 'Unknown'))
            table.add_row("Created At", repo_info.get('created_at', 'Unknown'))
            table.add_row("Updated At", repo_info.get('updated_at', 'Unknown'))
            
            self.console.print(table)
            
            # Show language distribution
            languages = self.github_client._make_request(f'/repos/{self.owner}/{self.repo_name}/languages')
            
            lang_table = Table(title="Language Distribution")
            lang_table.add_column("Language", style="green")
            lang_table.add_column("Bytes", justify="right")
            lang_table.add_column("Percentage", justify="right")
            
            total_bytes = sum(languages.values())
            for lang, bytes_count in languages.items():
                percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                lang_table.add_row(lang, str(bytes_count), f"{percentage:.1f}%")
            
            self.console.print(lang_table)
        else:
            # For local repos, use the Codebase class for detailed analysis
            self.codebase.display_codebase_stats()
    
    def analyze_contributors(self):
        """Analyze contributors to the repository."""
        if self.is_remote:
            # For remote repos, use the GitHub API
            contributors = self.github_client.get_contributor_stats(self.owner, self.repo_name)
            
            # Create a table for contributor stats
            table = Table(title="Contributor Statistics")
            table.add_column("Contributor", style="cyan")
            table.add_column("Commits", justify="right")
            table.add_column("Lines Added", justify="right")
            table.add_column("Lines Deleted", justify="right")
            table.add_column("Files Changed", justify="right")
            table.add_column("Total Changes", justify="right")
            
            # Only add PR and Issue columns for remote repositories
            if self.is_remote:
                table.add_column("Issues", justify="right")
                table.add_column("Pull Requests", justify="right")
            
            # Calculate total changes for percentage
            total_changes = sum(c.lines_added + c.lines_deleted for c in contributors)
            
            # Add rows for each contributor
            for contributor in contributors:
                total_changes_contributor = contributor.lines_added + contributor.lines_deleted
                percentage = (total_changes_contributor / total_changes) * 100 if total_changes > 0 else 0
                
                row_data = [
                    contributor.name,
                    str(contributor.commit_count),
                    str(contributor.lines_added),
                    str(contributor.lines_deleted),
                    str(contributor.files_changed),
                    str(total_changes_contributor),
                ]
                
                # Add PR and Issue data only for remote repositories
                if self.is_remote:
                    row_data.extend([
                        str(contributor.issues),
                        str(contributor.pull_requests),
                    ])
                
                table.add_row(*row_data)
            
            self.console.print(table)
        else:
            # For local repos, use the ContributorAnalyzer class
            self.contributor_analyzer.display_contributor_stats()
    
    def analyze(self):
        """Perform complete analysis of the repository."""
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing repository...", total=2)
            
            # Analyze codebase
            self.analyze_codebase()
            progress.update(task, advance=1)
            
            # Analyze contributors
            self.analyze_contributors()
            progress.update(task, advance=1)
    
    def get_contributor_stats(self) -> List[ContributorStats]:
        """Get statistics for all contributors."""
        if self.is_remote:
            return self._get_remote_contributor_stats()
        return self._get_local_contributor_stats()
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be excluded, False otherwise
        """
        file_name = Path(file_path).name
        return file_name in self.excluded_files
    
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
                    watchers=0,
                    changes_count=0,
                    percentage=0,
                    total_lines=0,
                    percentage_lines=0,
                    total_issues=0,
                    percentage_issues=0,
                    total_pull_requests=0,
                    percentage_pull_requests=0,
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
                            
                            # Skip excluded files
                            if self._should_exclude_file(filename):
                                continue
                            
                            contributor.lines_added += int(additions)
                            contributor.lines_deleted += int(deletions)
                            contributor.files_changed += 1
                            contributor.changes_count += int(additions) + int(deletions)
                            contributor.percentage = contributor.get_percentage(contributor.changes_count)
                            contributor.total_lines += int(additions) + int(deletions)
                            contributor.percentage_lines = contributor.get_percentage(contributor.total_lines)
                            contributor.total_issues += 1
                            contributor.percentage_issues = contributor.get_percentage(contributor.total_issues)
                            contributor.total_pull_requests += 1
                            contributor.percentage_pull_requests = contributor.get_percentage(contributor.total_pull_requests)
                            contributor.total_stars += 1
                            contributor.percentage_stars = contributor.get_percentage(contributor.total_stars)
                            contributor.total_forks += 1
                            contributor.percentage_forks = contributor.get_percentage(contributor.total_forks)
                            contributor.changes_count += int(additions) + int(deletions)
                            contributor.percentage = contributor.get_percentage(contributor.changes_count)
                            
                            # Track language contributions
                            if filename:
                                lang = self.codebase._map_extension_to_language(Path(filename).suffix.lower())
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
                watchers=stat.watchers,
                changes_count=stat.lines_added + stat.lines_deleted,
                percentage=0.0,  # Will be calculated later
                total_lines=stat.lines_added + stat.lines_deleted,
                percentage_lines=0.0,
                total_issues=stat.issues,
                percentage_issues=0.0,
                total_pull_requests=stat.pull_requests,
                percentage_pull_requests=0.0,
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
            if item and not self._should_exclude_file(item):
                lang = self.codebase._map_extension_to_language(Path(item).suffix.lower())
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
                'total_lines': stat.total_lines,
                'percentage_lines': stat.percentage_lines,
                'total_issues': stat.total_issues,
                'percentage_issues': stat.percentage_issues,
                'total_pull_requests': stat.total_pull_requests,
                'percentage_pull_requests': stat.percentage_pull_requests,
                'total_stars': stat.total_stars,
                'percentage_stars': stat.percentage_stars,
                'total_forks': stat.total_forks,
                'percentage_forks': stat.percentage_forks,
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
        
        # Only add PR and Issue columns for remote repositories
        if self.is_remote:
            table.add_column("Issues", justify="right")
            table.add_column("Pull Requests", justify="right")
        
        for stat in percentages:
            # Get top 3 languages
            top_languages = sorted(
                stat['languages'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            top_langs_str = ", ".join(f"{lang}({count})" for lang, count in top_languages)
            
            row_data = [
                stat['name'],
                str(stat['commit_count']),
                str(stat['lines_added']),
                str(stat['lines_deleted']),
                str(stat['files_changed']),
                str(stat['total_changes']),
                f"{stat['percentage']:.1f}%",
                top_langs_str,
            ]
            
            # Add PR and Issue data only for remote repositories
            if self.is_remote:
                row_data.extend([
                    str(stat['total_issues']),
                    str(stat['total_pull_requests']),
                ])
            
            table.add_row(*row_data)
        
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
    
    def get_lines_of_code_stats(self) -> Dict:
        """Get comprehensive lines of code statistics for the repository."""
        if self.is_remote:
            # For remote repos, we can't get detailed LOC stats from GitHub API
            # GitHub only provides language statistics in bytes
            return {
                "total_lines": "N/A (remote repository)",
                "by_language": {},
                "note": "Detailed LOC statistics not available for remote repositories via GitHub API"
            }
        else:
            # For local repos, use the Codebase class
            return self.codebase.get_lines_of_code_stats()
    
    def display_language_stats(self):
        """Display language statistics in a formatted table."""
        languages = self.get_top_languages()
        percentages = self.get_language_percentages()
        
        table = Table(title="Repository Language Statistics")
        table.add_column("Language", style="cyan")
        table.add_column("Lines of Code", justify="right")
        table.add_column("Percentage", justify="right")
        
        # Only add PR and Issue columns for remote repositories
        if self.is_remote:
            table.add_column("Issues", justify="right")
            table.add_column("Pull Requests", justify="right")
        
        for lang, count in languages.items():
            percentage = percentages.get(lang, 0)
            
            row_data = [
                lang,
                str(count),
                f"{percentage:.1f}%",
            ]
            
            # Add PR and Issue data only for remote repositories
            if self.is_remote:
                row_data.extend([
                    str(languages.get(lang, 0)),
                    str(languages.get(lang, 0)),
                ])
            
            table.add_row(*row_data)
        
        self.console.print(table) 