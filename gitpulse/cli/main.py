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
@click.option('--lines', is_flag=True, help='Show lines of code statistics instead of file counts')
def languages(path: str, remote: bool, token: str, lines: bool):
    """Show language distribution in the repository."""
    try:
        # Set GitHub token if provided
        if token:
            os.environ['GITHUB_TOKEN'] = token
            
        repo = Repository(path, is_remote=remote)
        
        if remote:
            # For remote repos, use GitHub API
            languages = repo.github_client._make_request(f'/repos/{repo.owner}/{repo.repo_name}/languages')
            
            if lines:
                # Show note that LOC stats not available for remote repos
                console.print("[yellow]Note: Lines of code statistics are not available for remote repositories via GitHub API.[/yellow]")
                console.print("[yellow]GitHub only provides language statistics in bytes.[/yellow]")
            
            table = Table(title="Language Distribution (by bytes)")
            table.add_column("Language", style="green")
            table.add_column("Bytes", justify="right")
            table.add_column("Percentage", justify="right")
            
            total_bytes = sum(languages.values())
            for lang, bytes_count in languages.items():
                percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                table.add_row(lang, str(bytes_count), f"{percentage:.1f}%")
        else:
            # For local repos, use Repository class methods
            if lines:
                # Show lines of code statistics
                loc_stats = repo.get_lines_of_code_stats()
                
                # Display total LOC summary
                summary_table = Table(title="Lines of Code Summary")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", justify="right")
                summary_table.add_row("Total Lines of Code", f"{loc_stats['total_lines']:,}")
                summary_table.add_row("Code Files", f"{loc_stats['code_files']:,}")
                summary_table.add_row("Non-Code Files", f"{loc_stats['non_code_files']:,}")
                console.print(summary_table)
                
                # Display LOC by language
                table = Table(title="Lines of Code by Language")
                table.add_column("Language", style="green")
                table.add_column("Lines of Code", justify="right")
                table.add_column("Percentage", justify="right")
                
                for lang, line_count in loc_stats["by_language"].items():
                    percentage = (line_count / loc_stats["total_lines"]) * 100 if loc_stats["total_lines"] > 0 else 0
                    table.add_row(lang, f"{line_count:,}", f"{percentage:.1f}%")
            else:
                # Show file count statistics (original behavior)
                languages = repo.codebase.get_language_stats()
                
                table = Table(title="Language Distribution (by file count)")
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

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--remote', is_flag=True, help='Analyze a remote GitHub repository')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub personal access token')
def loc(path: str, remote: bool, token: str):
    """Show detailed lines of code statistics for the repository."""
    try:
        # Set GitHub token if provided
        if token:
            os.environ['GITHUB_TOKEN'] = token
            
        repo = Repository(path, is_remote=remote)
        
        if remote:
            # For remote repos, LOC stats not available
            console.print("[yellow]Lines of code statistics are not available for remote repositories.[/yellow]")
            console.print("[yellow]GitHub API only provides language statistics in bytes.[/yellow]")
            console.print("[yellow]Use 'gitpulse languages --remote' to see language distribution by bytes.[/yellow]")
        else:
            # For local repos, show comprehensive LOC stats
            loc_stats = repo.get_lines_of_code_stats()
            
            # Display total LOC summary
            summary_table = Table(title="Lines of Code Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", justify="right")
            summary_table.add_row("Total Lines of Code", f"{loc_stats['total_lines']:,}")
            summary_table.add_row("Code Files", f"{loc_stats['code_files']:,}")
            summary_table.add_row("Non-Code Files", f"{loc_stats['non_code_files']:,}")
            console.print(summary_table)
            
            # Display LOC by language
            if loc_stats['by_language']:
                lang_table = Table(title="Lines of Code by Language")
                lang_table.add_column("Language", style="green")
                lang_table.add_column("Lines of Code", justify="right")
                lang_table.add_column("Percentage", justify="right")
                
                for lang, line_count in loc_stats["by_language"].items():
                    percentage = (line_count / loc_stats["total_lines"]) * 100 if loc_stats["total_lines"] > 0 else 0
                    lang_table.add_row(lang, f"{line_count:,}", f"{percentage:.1f}%")
                console.print(lang_table)
            else:
                console.print("[yellow]No code files found in the repository.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        raise click.Abort()

if __name__ == '__main__':
    cli() 