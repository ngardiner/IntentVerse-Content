#!/usr/bin/env python3
"""
Script to fetch available IntentVerse versions from GitHub releases.

This script queries the GitHub API to get all available releases of IntentVerse
and filters them based on the specified criteria.
"""

import argparse
import json
import sys
import requests
from packaging import version
from typing import List, Dict, Any


def fetch_github_releases(repo: str, token: str = None) -> List[Dict[str, Any]]:
    """
    Fetch all releases from a GitHub repository.
    
    Args:
        repo: Repository in format 'owner/repo'
        token: Optional GitHub token for authentication
    
    Returns:
        List of release data from GitHub API
    """
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching releases from {repo}: {e}", file=sys.stderr)
        return []


def parse_version_tag(tag: str) -> version.Version:
    """
    Parse a version tag into a Version object.
    
    Args:
        tag: Version tag (e.g., 'v1.0.0', '1.0.0')
    
    Returns:
        Parsed version object
    
    Raises:
        ValueError: If tag is not a valid semantic version
    """
    # Remove 'v' prefix if present
    clean_tag = tag.lstrip('v')
    return version.parse(clean_tag)


def filter_versions(
    releases: List[Dict[str, Any]], 
    min_version: str = None,
    specific_version: str = None,
    test_all: bool = False,
    include_prereleases: bool = False
) -> List[str]:
    """
    Filter releases based on criteria.
    
    Args:
        releases: List of GitHub release data
        min_version: Minimum version to include
        specific_version: If specified, only return this version
        test_all: If True, include all versions (ignores min_version)
        include_prereleases: Whether to include pre-release versions
    
    Returns:
        List of version tags to test
    """
    if specific_version:
        # Validate that the specific version exists
        for release in releases:
            if release['tag_name'] == specific_version or release['tag_name'] == f"v{specific_version}":
                return [release['tag_name']]
        print(f"⚠️  Specific version {specific_version} not found", file=sys.stderr)
        return []
    
    valid_versions = []
    min_ver = None
    
    if min_version and not test_all:
        try:
            min_ver = parse_version_tag(min_version)
        except ValueError as e:
            print(f"❌ Invalid min_version format: {e}", file=sys.stderr)
            return []
    
    for release in releases:
        # Skip drafts
        if release.get('draft', False):
            continue
        
        # Skip pre-releases unless explicitly included
        if release.get('prerelease', False) and not include_prereleases:
            continue
        
        tag = release['tag_name']
        
        try:
            rel_version = parse_version_tag(tag)
            
            # Apply minimum version filter
            if min_ver and rel_version < min_ver:
                continue
            
            valid_versions.append(tag)
            
        except ValueError:
            print(f"⚠️  Skipping invalid version tag: {tag}", file=sys.stderr)
            continue
    
    # Sort versions in descending order (newest first)
    valid_versions.sort(key=lambda x: parse_version_tag(x), reverse=True)
    
    # Limit to reasonable number for CI performance
    if test_all:
        return valid_versions
    else:
        # Return latest 5 versions for regular testing
        return valid_versions[:5]


def get_latest_stable_version(releases: List[Dict[str, Any]]) -> str:
    """Get the latest stable (non-prerelease) version."""
    for release in releases:
        if not release.get('draft', False) and not release.get('prerelease', False):
            return release['tag_name']
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Fetch IntentVerse versions for compatibility testing"
    )
    parser.add_argument(
        "--repo", 
        required=True,
        help="GitHub repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--min-version",
        help="Minimum version to include (e.g., 'v1.0.0')"
    )
    parser.add_argument(
        "--specific-version",
        help="Test only this specific version"
    )
    parser.add_argument(
        "--test-all",
        action="store_true",
        help="Test against all available versions"
    )
    parser.add_argument(
        "--include-prereleases",
        action="store_true",
        help="Include pre-release versions"
    )
    parser.add_argument(
        "--output",
        help="Output file for version list (JSON format)"
    )
    parser.add_argument(
        "--github-token",
        help="GitHub token for API authentication"
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Fetching releases from {args.repo}...")
    
    releases = fetch_github_releases(args.repo, args.github_token)
    if not releases:
        print("❌ No releases found or API error", file=sys.stderr)
        sys.exit(1)
    
    print(f"📦 Found {len(releases)} total releases")
    
    versions = filter_versions(
        releases,
        min_version=args.min_version,
        specific_version=args.specific_version,
        test_all=args.test_all,
        include_prereleases=args.include_prereleases
    )
    
    if not versions:
        print("❌ No versions match the specified criteria", file=sys.stderr)
        sys.exit(1)
    
    latest_stable = get_latest_stable_version(releases)
    
    result = {
        "versions": versions,
        "latest_stable": latest_stable,
        "total_releases": len(releases),
        "filtered_count": len(versions),
        "criteria": {
            "min_version": args.min_version,
            "specific_version": args.specific_version,
            "test_all": args.test_all,
            "include_prereleases": args.include_prereleases
        }
    }
    
    print(f"✅ Selected {len(versions)} versions for testing:")
    for ver in versions:
        marker = " (latest stable)" if ver == latest_stable else ""
        print(f"   📌 {ver}{marker}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Version list saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()