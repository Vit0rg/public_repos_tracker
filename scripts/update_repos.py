#!/usr/bin/env python3
"""Fetch public repositories from GitHub and update README.md"""

import os
import sys
import requests
from datetime import datetime, timezone

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USER = os.environ.get("GITHUB_USER")
README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")


def fetch_public_repos(username: str, token: str) -> list[dict]:
    """Fetch all public repositories for a GitHub user."""
    repos = []
    url = f"https://api.github.com/users/{username}/repos?type=owner&per_page=100&sort=updated"
    headers = {"Authorization": f"token {token}"} if token else {}

    page = 1
    while True:
        response = requests.get(url + f"&page={page}", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        repos.extend(data)
        if len(data) < 100:
            break
        page += 1

    return repos


def format_repo_row(repo: dict) -> str:
    """Format a single repository into a markdown table row."""
    name = repo["full_name"]
    repo_url = repo["html_url"]
    description = (repo.get("description") or "").replace("|", "\\|") or "-"
    stars = repo["stargazers_count"]
    forks = repo["forks_count"]
    language = repo.get("language") or "-"
    updated = datetime.fromisoformat(repo["pushed_at"].rstrip("Z")).strftime("%Y-%m-%d")

    return f"| [{name}]({repo_url}) | {description} | {stars} | {forks} | {language} | {updated} |"


def generate_readme(repos: list[dict]) -> str:
    """Generate the full README content."""
    header = """# MY PUBLIC REPOSITORIES

| Repository | Description | Stars | Forks | Language | Last Updated |
|------------|-------------|-------|-------|----------|--------------|"""

    # Sort by most recently updated
    repos_sorted = sorted(repos, key=lambda r: r["pushed_at"], reverse=True)

    rows = [format_repo_row(repo) for repo in repos_sorted]
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return "\n".join([header, "", "\n".join(rows), "", f"Last updated: {timestamp}\n"])


def main():
    if not GITHUB_USER:
        print("Error: GITHUB_USER environment variable is required", file=sys.stderr)
        sys.exit(1)

    token = GITHUB_TOKEN  # Optional, but helps with rate limits

    print(f"Fetching public repos for {GITHUB_USER}...")
    repos = fetch_public_repos(GITHUB_USER, token)
    print(f"Found {len(repos)} public repositories")

    readme_content = generate_readme(repos)

    with open(README_PATH, "w") as f:
        f.write(readme_content)

    print(f"README updated at {README_PATH}")


if __name__ == "__main__":
    main()
