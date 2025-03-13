from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ContributorStats:
    """Statistics for an individual contributor."""
    name: str
    email: str
    commit_count: int
    lines_added: int
    lines_deleted: int
    files_changed: int
    languages: Dict[str, int]
    issues: int = 0
    pull_requests: int = 0
    
    # Calculated fields
    percentage: float = 0.0
    
    @property
    def total_changes(self) -> int:
        """Calculate total number of changes (additions + deletions)."""
        return self.lines_added + self.lines_deleted
    
    def calculate_percentage(self, total_changes: int) -> float:
        """Calculate percentage of total changes."""
        if total_changes == 0:
            return 0.0
        percentage = (self.total_changes / total_changes) * 100
        self.percentage = percentage
        return percentage

class Contributor:
    """Class representing a contributor to a repository."""
    
    def __init__(self, name: str, email: str):
        """Initialize a contributor.
        
        Args:
            name: Contributor's name
            email: Contributor's email
        """
        self.name = name
        self.email = email
        self.stats = ContributorStats(
            name=name,
            email=email,
            commit_count=0,
            lines_added=0,
            lines_deleted=0,
            files_changed=0,
            languages={}
        )
    
    def update_stats(self, 
                    commit_count: int = 0, 
                    lines_added: int = 0, 
                    lines_deleted: int = 0,
                    files_changed: int = 0,
                    languages: Optional[Dict[str, int]] = None,
                    issues: int = 0,
                    pull_requests: int = 0) -> None:
        """Update contributor statistics.
        
        Args:
            commit_count: Number of commits
            lines_added: Number of lines added
            lines_deleted: Number of lines deleted
            files_changed: Number of files changed
            languages: Dictionary of languages and their counts
            issues: Number of issues created
            pull_requests: Number of pull requests created
        """
        self.stats.commit_count += commit_count
        self.stats.lines_added += lines_added
        self.stats.lines_deleted += lines_deleted
        self.stats.files_changed += files_changed
        self.stats.issues += issues
        self.stats.pull_requests += pull_requests
        
        if languages:
            for lang, count in languages.items():
                self.stats.languages[lang] = self.stats.languages.get(lang, 0) + count
    
    def to_dict(self) -> Dict:
        """Convert contributor stats to dictionary."""
        return {
            'name': self.stats.name,
            'email': self.stats.email,
            'commit_count': self.stats.commit_count,
            'lines_added': self.stats.lines_added,
            'lines_deleted': self.stats.lines_deleted,
            'files_changed': self.stats.files_changed,
            'total_changes': self.stats.total_changes,
            'percentage': self.stats.percentage,
            'languages': self.stats.languages,
            'issues': self.stats.issues,
            'pull_requests': self.stats.pull_requests
        } 