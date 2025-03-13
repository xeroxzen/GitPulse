from typing import Dict, List, Optional
import git
from git import Repo
from rich.console import Console
from rich.table import Table
from pathlib import Path
from .contributor import Contributor, ContributorStats

class ContributorAnalyzer:
    """Class for analyzing contributors to a repository."""
    
    def __init__(self, repo: Repo):
        """Initialize the contributor analyzer.
        
        Args:
            repo: Git repository object
        """
        self.repo = repo
        self.console = Console()
        self.contributors: Dict[str, Contributor] = {}
        
        # Files to exclude from analysis
        self.excluded_files = [
            "package-lock.json",
            "yarn.lock"
        ]
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be excluded, False otherwise
        """
        file_name = Path(file_path).name
        return file_name in self.excluded_files
    
    def analyze(self) -> List[Contributor]:
        """Analyze all contributors to the repository."""
        try:
            # Process all commits
            for commit in self.repo.iter_commits():
                author = commit.author
                email = author.email
                
                # Create contributor if not exists
                if email not in self.contributors:
                    self.contributors[email] = Contributor(author.name, email)
                
                # Update commit count
                self.contributors[email].update_stats(commit_count=1)
                
                # Get diff stats if commit has parents
                if commit.parents:
                    # Get the diff between this commit and its parent
                    diff = self.repo.git.diff(
                        commit.parents[0].hexsha,
                        commit.hexsha,
                        '--numstat'
                    ).split('\n')
                    
                    # Process each changed file
                    for line in diff:
                        if line.strip():
                            try:
                                # Parse numstat output: additions deletions filename
                                additions, deletions, filename = line.split('\t')
                                
                                # Skip excluded files
                                if self._should_exclude_file(filename):
                                    continue
                                
                                # Update contributor stats
                                self.contributors[email].update_stats(
                                    lines_added=int(additions) if additions != '-' else 0,
                                    lines_deleted=int(deletions) if deletions != '-' else 0,
                                    files_changed=1,
                                    languages={self._detect_language(filename): 1}
                                )
                            except (ValueError, IndexError):
                                # Skip malformed lines
                                continue
            
            # Calculate percentages
            self._calculate_percentages()
            
            return list(self.contributors.values())
        except Exception as e:
            self.console.print(f"[red]Error analyzing contributors: {str(e)}")
            return []
    
    def get_top_contributors(self, limit: int = 10) -> List[Contributor]:
        """Get top contributors by total changes."""
        contributors = list(self.contributors.values())
        return sorted(
            contributors,
            key=lambda c: c.stats.total_changes,
            reverse=True
        )[:limit]
    
    def display_contributor_stats(self):
        """Display contributor statistics in a formatted table."""
        # Analyze contributors if not already done
        if not self.contributors:
            self.analyze()
        
        # Create table
        table = Table(title="Contributor Statistics")
        table.add_column("Contributor", style="cyan")
        table.add_column("Email")
        table.add_column("Commits", justify="right")
        table.add_column("Lines Added", justify="right")
        table.add_column("Lines Deleted", justify="right")
        table.add_column("Files Changed", justify="right")
        table.add_column("Total Changes", justify="right")
        table.add_column("Percentage", justify="right")
        table.add_column("Top Languages", style="green")
        
        # Sort contributors by total changes
        sorted_contributors = sorted(
            self.contributors.values(),
            key=lambda c: c.stats.total_changes,
            reverse=True
        )
        
        # Add rows for each contributor
        for contributor in sorted_contributors:
            stats = contributor.stats
            
            # Get top 3 languages
            top_languages = sorted(
                stats.languages.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            top_langs_str = ", ".join(f"{lang}({count})" for lang, count in top_languages)
            
            table.add_row(
                stats.name,
                stats.email,
                str(stats.commit_count),
                str(stats.lines_added),
                str(stats.lines_deleted),
                str(stats.files_changed),
                str(stats.total_changes),
                f"{stats.percentage:.1f}%",
                top_langs_str
            )
        
        self.console.print(table)
    
    def _calculate_percentages(self):
        """Calculate percentage contributions for all contributors."""
        total_changes = sum(c.stats.total_changes for c in self.contributors.values())
        
        for contributor in self.contributors.values():
            contributor.stats.calculate_percentage(total_changes)
    
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
        
        ext = Path(filename).suffix.lower()
        for extension, language in extension_map.items():
            if ext.endswith(extension):
                return language
        
        return 'Unknown' 