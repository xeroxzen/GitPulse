#!/usr/bin/env python3
"""
Test script to verify GitHub API authentication and functionality.
"""

from gitpulse.core.repository import Repository
from gitpulse.core.github import GitHubClient

def test_github_auth():
    """Test GitHub API authentication."""
    client = GitHubClient()
    print(f"Authenticated: {client.token is not None}")
    
    # Test with a popular repository
    repo_owner = "microsoft"
    repo_name = "vscode"
    
    print(f"\nTesting with repository: {repo_owner}/{repo_name}")
    
    # Get languages
    try:
        languages = client.get_repository_languages(repo_owner, repo_name)
        print("\nRepository Languages:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {lang}: {count}")
        print("  ...")
    except Exception as e:
        print(f"Error getting languages: {e}")
    
    # Get contributors
    try:
        print("\nTop Contributors:")
        contributors = client.get_contributor_stats(repo_owner, repo_name)
        for contributor in contributors[:5]:
            print(f"  {contributor.name}: {contributor.commit_count} commits")
        print("  ...")
    except Exception as e:
        print(f"Error getting contributors: {e}")

if __name__ == "__main__":
    test_github_auth() 