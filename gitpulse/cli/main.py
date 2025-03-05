import click
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from pathlib import Path
from ..core.repository import Repository

console = Console()

@click.group()
def cli():
    """GitPulse - Git Repository Analytics Tool"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--remote', is_flag=True, help='Analyze a remote GitHub repository')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub personal access token')
def analyze(path: str, remote: bool, token: str):
    """Analyze a Git repository and display contribution statistics."""
    try:
        with Progress() as progress:
            task = progress.add_task("[cyan]Analyzing repository...", total=None)
            
            # Set GitHub token if provided
            if token:
                os.environ['GITHUB_TOKEN'] = token
            
            repo = Repository(path, is_remote=remote)
            
            # Get contributor statistics
            stats = repo.get_contributor_stats()
            
            # Create and display contributor table
            table = Table(title="Contributor Statistics")
            table.add_column("Name", style="cyan")
            table.add_column("Commits", justify="right")
            table.add_column("Files Changed", justify="right")
            table.add_column("Lines Added", justify="right")
            table.add_column("Lines Deleted", justify="right")
            
            for stat in stats:
                table.add_row(
                    stat.name,
                    str(stat.commit_count),
                    str(stat.files_changed),
                    str(stat.lines_added),
                    str(stat.lines_deleted)
                )
            
            console.print(table)
            
            # Display top languages
            languages = repo.get_top_languages()
            lang_table = Table(title="Top Languages")
            lang_table.add_column("Language", style="green")
            lang_table.add_column("Files", justify="right")
            
            for lang, count in languages.items():
                lang_table.add_row(lang, str(count))
            
            console.print(lang_table)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--remote', is_flag=True, help='Analyze a remote GitHub repository')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub personal access token')
def languages(path: str, remote: bool, token: str):
    """Show language distribution in the repository."""
    try:
        # Set GitHub token if provided
        if token:
            os.environ['GITHUB_TOKEN'] = token
            
        repo = Repository(path, is_remote=remote)
        languages = repo.get_top_languages()
        
        table = Table(title="Language Distribution")
        table.add_column("Language", style="green")
        table.add_column("Files", justify="right")
        
        for lang, count in languages.items():
            table.add_row(lang, str(count))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    cli() 