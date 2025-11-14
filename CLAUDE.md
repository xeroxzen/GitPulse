# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitPulse is a Git repository analysis tool that provides insights into contributor statistics, language usage, lines of code, and contribution metrics. It supports both local Git repositories and remote GitHub repositories via the GitHub API.

The project has two main interfaces:
- **CLI**: Command-line interface built with Click
- **Web App**: FastAPI-based REST API with a static frontend

## Development Commands

### Setup and Installation

```bash
# Install dependencies using uv (preferred)
uv sync

# Or using pip
pip install -e .

# Set up GitHub token for remote repository analysis
echo "GITHUB_TOKEN=your_github_token" > .env
```

### Running the CLI

```bash
# Analyze a local repository
gitpulse analyze /path/to/repo

# Analyze current directory
gitpulse analyze .

# Analyze a remote GitHub repository
gitpulse analyze https://github.com/owner/repo --remote --token YOUR_TOKEN

# Show codebase statistics
gitpulse codebase /path/to/repo

# Show contributor statistics
gitpulse contributors /path/to/repo

# Show language distribution (by file count)
gitpulse languages /path/to/repo

# Show lines of code statistics
gitpulse loc /path/to/repo
gitpulse languages /path/to/repo --lines
```

### Running the Web App

```bash
# Start the FastAPI server
python -m gitpulse.web.run

# Or using uvicorn directly
uvicorn gitpulse.web.app:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/unit/test_codebase.py

# Run with verbose output
python -m pytest -v tests/

# Run specific test class or method
python -m pytest tests/unit/test_codebase.py::TestCodebase::test_get_basic_info
```

## Architecture

### Core Components

**`gitpulse/core/`** - Core analysis logic

- **`repository.py`**: Main entry point for repository analysis
  - `Repository` class: Orchestrates analysis for both local and remote repositories
  - `ContributorStats` dataclass: Stores contributor statistics
  - Handles switching between local (GitPython) and remote (GitHub API) analysis modes

- **`codebase.py`**: Local repository analysis
  - `Codebase` class: Analyzes local Git repositories using GitPython
  - Provides: basic info, language stats, LOC stats, commit activity, file stats
  - Uses `_map_extension_to_language()` for file extension → language mapping

- **`contributor.py`**: Contributor data model
  - `Contributor` class: Represents a single contributor
  - `ContributorStats` dataclass: Stores contribution metrics

- **`contributor_analyzer.py`**: Local contributor analysis
  - `ContributorAnalyzer` class: Analyzes contributors in local repositories
  - Processes commits, calculates stats, and generates contribution percentages

- **`github.py`**: GitHub API integration
  - `GitHubClient` class: Interacts with GitHub API v3
  - `GitHubContributor` dataclass: GitHub-specific contributor data
  - Implements retry logic for 202 responses (data being computed)
  - Rate limiting considerations: Uses token authentication when available

### CLI Layer

**`gitpulse/cli/main.py`** - Click-based CLI implementation

- Commands: `analyze`, `codebase`, `contributors`, `languages`, `loc`
- All commands support `--remote` flag for GitHub repositories
- Uses Rich library for formatted table output
- Environment variable support for `GITHUB_TOKEN`

### Web Layer

**`gitpulse/web/`** - FastAPI web application

- **`app.py`**: FastAPI application with REST endpoints
  - POST `/analyze`: Analyze repository and return contributor stats
  - POST `/languages`: Get language distribution
  - GET `/health`: Health check
  - GET `/`: Redirect to static frontend

- **`run.py`**: Uvicorn server entry point
- **`static/`**: Frontend HTML/CSS/JS files

### Utilities

**`gitpulse/utils/`** - Shared utilities

- **`language.py`**: Language detection utilities
- **`exclusions.py`**: File exclusion patterns (e.g., `package-lock.json`, `yarn.lock`)

## Key Design Patterns

### Dual-Mode Analysis

The `Repository` class acts as a facade that switches between two analysis strategies:

1. **Local Mode** (`is_remote=False`):
   - Uses GitPython (`git.Repo`) for direct repository access
   - Delegates to `Codebase` for codebase analysis
   - Delegates to `ContributorAnalyzer` for contributor analysis
   - Provides detailed LOC statistics by counting lines in files

2. **Remote Mode** (`is_remote=True`):
   - Uses `GitHubClient` for API-based analysis
   - Limited to data available via GitHub API
   - Cannot provide detailed LOC stats (only bytes by language)
   - Includes additional metrics: issues, PRs, stars, forks

### File Exclusion Strategy

Both local analyzers exclude specific files from metrics:
- `package-lock.json` and `yarn.lock` by default
- Implemented via `_should_exclude_file()` method
- Prevents these large, auto-generated files from skewing statistics

### Language Detection

Three implementations of language detection:
1. `Codebase._map_extension_to_language()` - For local file analysis
2. `ContributorAnalyzer._detect_language()` - For contributor analysis
3. `GitHubClient._detect_language()` - For GitHub API responses

All use similar extension mapping dictionaries. Consider consolidating these into `gitpulse/utils/language.py`.

## Important Implementation Details

### GitHub API Considerations

- **Rate Limiting**: GitHub API has rate limits (60 requests/hour unauthenticated, 5000/hour with token)
- **202 Responses**: Some endpoints (like `/repos/{owner}/{repo}/stats/contributors`) return 202 while computing data
  - `GitHubClient._make_request_with_retry()` implements retry logic with delays
- **Missing Data**: Not all data is available via API (e.g., detailed LOC statistics)

### Lines of Code Calculation

- **Local repos**: Counts actual lines in files using Python's file reading
- **Remote repos**: GitHub only provides bytes per language, not line counts
- Code vs. non-code files are distinguished by extension whitelist in `Codebase.get_lines_of_code_stats()`

### Contributor Percentage Calculation

- Based on total changes (lines added + lines deleted)
- Calculated after all commits are processed
- Formula: `(contributor_changes / total_changes) * 100`

## Testing Strategy

Tests are located in `tests/unit/`:
- `test_codebase.py`: Tests `Codebase` class using temporary Git repositories
- `test_contributor.py`: Tests `Contributor` and related classes

Tests use:
- `tempfile.TemporaryDirectory()` for isolated test repositories
- `git.Repo.init()` to create test Git repos
- Standard Python `unittest` framework

## Common Development Patterns

### Adding a New CLI Command

1. Add command function to `gitpulse/cli/main.py` using `@cli.command()` decorator
2. Use `@click.argument()` and `@click.option()` for parameters
3. Support `--remote` flag for GitHub repositories
4. Use Rich tables for formatted output
5. Handle exceptions with `console.print()` error messages

### Adding a New Web Endpoint

1. Add endpoint to `gitpulse/web/app.py` using FastAPI decorators
2. Define request/response models with Pydantic
3. Instantiate `Repository` with appropriate mode
4. Return JSON-serializable data

### Extending Analysis Metrics

1. Add field to `ContributorStats` dataclass in `repository.py`
2. Update `_get_local_contributor_stats()` for local repos
3. Update `GitHubClient.get_contributor_stats()` for remote repos
4. Update display tables in both CLI and web outputs

## Dependencies

- **GitPython**: Local Git repository interaction
- **Click**: CLI framework
- **Rich**: Terminal formatting and tables
- **FastAPI**: Web framework
- **Requests**: HTTP client for GitHub API
- **Python-dotenv**: Environment variable management
- **Pygments**: Syntax highlighting (for language detection)

## Project Structure

```
gitpulse/
├── cli/           # Command-line interface
├── core/          # Core analysis logic
├── utils/         # Shared utilities
└── web/           # Web application
    ├── app.py
    ├── run.py
    └── static/    # Frontend files
tests/
└── unit/          # Unit tests
```
