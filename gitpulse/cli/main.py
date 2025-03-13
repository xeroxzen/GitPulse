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
@click.argument('path')
@click.option('--remote', is_flag=True, help='Analyze a remote GitHub repository')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub personal access token')
def analyze(path: str, remote: bool, token: str):
    """Analyze a Git repository and display contribution statistics."""
    try:
        # Set GitHub token if provided
        if token:
            os.environ['GITHUB_TOKEN'] = token
        
        # For remote repositories, we don't need to check if path exists
        if not remote:
            if not os.path.exists(path):
                raise click.BadParameter(f"Path '{path}' does not exist")
        
        repo = Repository(path, is_remote=remote)
        
        # Perform complete analysis
        repo.analyze()
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('path')
@click.option('--remote', is_flag=True, help='Analyze a remote GitHub repository')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub personal access token')
def codebase(path: str, remote: bool, token: str):
    """Analyze the codebase/repository structure."""
    try:
        # Set GitHub token if provided
        if token:
            os.environ['GITHUB_TOKEN'] = token
            
        # For remote repositories, we don't need to check if path exists
        if not remote:
            if not os.path.exists(path):
                raise click.BadParameter(f"Path '{path}' does not exist")
        
        repo = Repository(path, is_remote=remote)
        
        # Analyze only the codebase
        repo.analyze_codebase()
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise click.Abort()

@cli.command()
@click.argument('path')
@click.option('--remote', is_flag=True, help='Analyze a remote GitHub repository')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub personal access token')
def contributors(path: str, remote: bool, token: str):
    """Analyze contributors to the repository."""
    try:
        # Set GitHub token if provided
        if token:
            os.environ['GITHUB_TOKEN'] = token
            
        # For remote repositories, we don't need to check if path exists
        if not remote:
            if not os.path.exists(path):
                raise click.BadParameter(f"Path '{path}' does not exist")
        
        repo = Repository(path, is_remote=remote)
        
        # Analyze only the contributors
        repo.analyze_contributors()
        
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
        
        if remote:
            # For remote repos, use GitHub API
            languages = repo.github_client._make_request(f'/repos/{repo.owner}/{repo.repo_name}/languages')
            
            table = Table(title="Language Distribution")
            table.add_column("Language", style="green")
            table.add_column("Bytes", justify="right")
            table.add_column("Percentage", justify="right")
            
            total_bytes = sum(languages.values())
            for lang, bytes_count in languages.items():
                percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                table.add_row(lang, str(bytes_count), f"{percentage:.1f}%")
        else:
            # For local repos, use Codebase class
            languages = repo.codebase.get_language_stats()
            
            table = Table(title="Language Distribution")
            table.add_column("Language", style="green")
            table.add_column("Files", justify="right")
            table.add_column("Percentage", justify="right")
            
            total_files = sum(languages.values())
            for lang, count in languages.items():
                percentage = (count / total_files) * 100 if total_files > 0 else 0
                table.add_row(lang, str(count), f"{percentage:.1f}%")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    cli() 