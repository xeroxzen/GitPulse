#!/usr/bin/env python3
"""
Test script to demonstrate contribution percentages feature.
"""

import os
import argparse
from gitpulse.core.repository import Repository

def test_remote_contributions(repo_url):
    """Test contribution percentages feature with a remote repository."""
    print(f"Analyzing remote repository: {repo_url}")
    repo = Repository(repo_url, is_remote=True)
    
    # Display contribution statistics
    print("\nContribution Statistics:")
    repo.display_contribution_stats()
    
    # Display language statistics
    print("\nLanguage Statistics:")
    repo.display_language_stats()

def test_local_contributions(repo_path):
    """Test contribution percentages feature with a local repository."""
    # Convert to absolute path if needed
    if not os.path.isabs(repo_path):
        repo_path = os.path.abspath(repo_path)
    
    print(f"Analyzing local repository: {repo_path}")
    repo = Repository(repo_path, is_remote=False)
    
    # Display contribution statistics
    print("\nContribution Statistics:")
    repo.display_contribution_stats()
    
    # Display language statistics
    print("\nLanguage Statistics:")
    repo.display_language_stats()

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Analyze repository contributions")
    parser.add_argument("--remote", "-r", help="GitHub repository URL to analyze")
    parser.add_argument("--local", "-l", help="Local repository path to analyze")
    
    args = parser.parse_args()
    
    if args.remote:
        test_remote_contributions(args.remote)
    elif args.local:
        test_local_contributions(args.local)
    else:
        # Default to analyzing the current directory as a local repository
        print("No repository specified, analyzing current directory...")
        test_local_contributions(".")

if __name__ == "__main__":
    main() 