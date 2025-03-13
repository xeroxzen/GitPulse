from typing import Dict, List, Optional
from pathlib import Path
import git
from git import Repo
from datetime import datetime
from rich.console import Console
from rich.table import Table

class Codebase:
    """Class representing a codebase/repository for analysis."""
    
    def __init__(self, path: str):
        """Initialize the codebase analyzer.
        
        Args:
            path: Local path to the repository
        """
        self.path = path
        self.repo = None
        self.console = Console()
        
        # Files to exclude from analysis
        self.excluded_files = [
            "package-lock.json",
            "yarn.lock"
        ]
        
        try:
            self.repo = Repo(path)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Invalid Git repository at {path}")
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if a file should be excluded from analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be excluded, False otherwise
        """
        file_name = Path(file_path).name
        return file_name in self.excluded_files
    
    def get_basic_info(self) -> Dict:
        """Get basic information about the repository."""
        try:
            # Get the remote URL if available
            remote_url = ""
            if self.repo.remotes:
                remote_url = self.repo.remotes.origin.url
            
            # Get the default branch
            default_branch = self.repo.active_branch.name
            
            # Get the first and last commit dates
            commits = list(self.repo.iter_commits())
            first_commit_date = datetime.fromtimestamp(commits[-1].committed_date).isoformat()
            last_commit_date = datetime.fromtimestamp(commits[0].committed_date).isoformat()
            
            # Count total commits
            total_commits = len(commits)
            
            # Count total files (excluding specified files)
            files = self.repo.git.ls_files().split('\n')
            total_files = sum(1 for f in files if f and not self._should_exclude_file(f))
            
            return {
                "name": Path(self.path).name,
                "path": self.path,
                "remote_url": remote_url,
                "default_branch": default_branch,
                "first_commit_date": first_commit_date,
                "last_commit_date": last_commit_date,
                "total_commits": total_commits,
                "total_files": total_files
            }
        except Exception as e:
            self.console.print(f"[red]Error getting repository info: {str(e)}")
            return {}
    
    def get_language_stats(self) -> Dict[str, int]:
        """Get statistics about programming languages in the repository."""
        languages = {}
        
        try:
            # Get all files in the repository
            files = self.repo.git.ls_files().split('\n')
            
            for file_path in files:
                if file_path and not self._should_exclude_file(file_path):
                    # Get the file extension
                    ext = Path(file_path).suffix.lower()
                    
                    # Map extensions to languages
                    language = self._map_extension_to_language(ext)
                    
                    # Update language count
                    languages[language] = languages.get(language, 0) + 1
        except Exception as e:
            self.console.print(f"[red]Error analyzing languages: {str(e)}")
        
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
    
    def get_commit_activity(self) -> Dict:
        """Get commit activity over time."""
        activity = {
            "by_month": {},
            "by_day_of_week": {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
            "by_hour": {h: 0 for h in range(24)}
        }
        
        try:
            for commit in self.repo.iter_commits():
                date = datetime.fromtimestamp(commit.committed_date)
                
                # By month
                month_key = f"{date.year}-{date.month:02d}"
                activity["by_month"][month_key] = activity["by_month"].get(month_key, 0) + 1
                
                # By day of week (0 = Monday, 6 = Sunday)
                day_of_week = date.weekday()
                activity["by_day_of_week"][day_of_week] += 1
                
                # By hour
                activity["by_hour"][date.hour] += 1
        except Exception as e:
            self.console.print(f"[red]Error analyzing commit activity: {str(e)}")
        
        return activity
    
    def get_file_stats(self) -> Dict:
        """Get statistics about files in the repository."""
        stats = {
            "file_count": 0,
            "by_extension": {},
            "largest_files": [],
            "most_changed_files": []
        }
        
        try:
            # Get all files
            files = self.repo.git.ls_files().split('\n')
            # Filter out excluded files
            filtered_files = [f for f in files if f and not self._should_exclude_file(f)]
            stats["file_count"] = len(filtered_files)
            
            # Count by extension
            for file_path in filtered_files:
                if file_path:
                    ext = Path(file_path).suffix.lower() or "no_extension"
                    stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1
            
            # Get largest files (by line count)
            file_sizes = []
            for file_path in filtered_files:
                if file_path and Path(self.path, file_path).exists():
                    try:
                        with open(Path(self.path, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                            line_count = sum(1 for _ in f)
                            file_sizes.append((file_path, line_count))
                    except:
                        # Skip files that can't be read
                        pass
            
            # Sort by size and get top 10
            stats["largest_files"] = sorted(file_sizes, key=lambda x: x[1], reverse=True)[:10]
            
            # Get most changed files
            file_changes = {}
            for commit in self.repo.iter_commits():
                if commit.parents:
                    diffs = commit.parents[0].diff(commit)
                    for diff in diffs:
                        if diff.a_path:
                            file_changes[diff.a_path] = file_changes.get(diff.a_path, 0) + 1
            
            # Sort by change count and get top 10
            stats["most_changed_files"] = sorted(
                [(path, count) for path, count in file_changes.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        except Exception as e:
            self.console.print(f"[red]Error analyzing file stats: {str(e)}")
        
        return stats
    
    def display_codebase_stats(self):
        """Display codebase statistics in a formatted table."""
        info = self.get_basic_info()
        languages = self.get_language_stats()
        file_stats = self.get_file_stats()
        
        # Basic info table
        info_table = Table(title="Repository Information")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value")
        
        for key, value in info.items():
            info_table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(info_table)
        
        # Language stats table
        lang_table = Table(title="Language Distribution")
        lang_table.add_column("Language", style="green")
        lang_table.add_column("Files", justify="right")
        lang_table.add_column("Percentage", justify="right")
        
        total_files = sum(languages.values())
        for lang, count in languages.items():
            percentage = (count / total_files) * 100 if total_files > 0 else 0
            lang_table.add_row(lang, str(count), f"{percentage:.1f}%")
        
        self.console.print(lang_table)
        
        # File stats table
        file_table = Table(title="File Statistics")
        file_table.add_column("Metric", style="cyan")
        file_table.add_column("Value")
        
        file_table.add_row("Total Files", str(file_stats["file_count"]))
        
        # Add top 5 extensions
        extensions = sorted(
            [(ext, count) for ext, count in file_stats["by_extension"].items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        ext_str = ", ".join([f"{ext} ({count})" for ext, count in extensions])
        file_table.add_row("Top Extensions", ext_str)
        
        self.console.print(file_table)
        
        # Largest files table
        largest_table = Table(title="Largest Files (by line count)")
        largest_table.add_column("File", style="cyan")
        largest_table.add_column("Lines", justify="right")
        
        for file_path, line_count in file_stats["largest_files"]:
            largest_table.add_row(file_path, str(line_count))
        
        self.console.print(largest_table)
        
        # Most changed files table
        changed_table = Table(title="Most Changed Files")
        changed_table.add_column("File", style="cyan")
        changed_table.add_column("Changes", justify="right")
        
        for file_path, change_count in file_stats["most_changed_files"]:
            changed_table.add_row(file_path, str(change_count))
        
        self.console.print(changed_table)
    
    def _map_extension_to_language(self, ext: str) -> str:
        """Map file extension to programming language."""
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
        
        return extension_map.get(ext, 'Other') 