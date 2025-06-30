#!/usr/bin/env python3
"""
Script to create a test matrix for GitHub Actions compatibility testing.

This script takes the list of IntentVerse versions and content packs and creates
a matrix configuration for GitHub Actions to run tests in parallel.
"""

import argparse
import json
import sys
from typing import List, Dict, Any
from packaging import version


def parse_compatibility_conditions(conditions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Parse compatibility conditions to extract version requirements.
    
    Args:
        conditions: List of compatibility condition objects
    
    Returns:
        Dictionary with parsed requirements
    """
    requirements = {
        "min_version": None,
        "max_version": None,
        "reasons": []
    }
    
    for condition in conditions:
        if condition.get("type") == "version_range":
            min_ver = condition.get("min_version")
            max_ver = condition.get("max_version")
            reason = condition.get("reason", "Version compatibility requirement")
            
            if min_ver:
                if not requirements["min_version"] or version.parse(min_ver) > version.parse(requirements["min_version"]):
                    requirements["min_version"] = min_ver
            
            if max_ver:
                if not requirements["max_version"] or version.parse(max_ver) < version.parse(requirements["max_version"]):
                    requirements["max_version"] = max_ver
            
            requirements["reasons"].append(reason)
    
    return requirements


def is_version_compatible(test_version: str, requirements: Dict[str, Any]) -> tuple[bool, str]:
    """
    Check if a test version is compatible with the requirements.
    
    Args:
        test_version: Version to test (e.g., "v1.0.0")
        requirements: Parsed compatibility requirements
    
    Returns:
        Tuple of (is_compatible, reason)
    """
    # Clean version string (remove 'v' prefix)
    clean_version = test_version.lstrip('v')
    
    try:
        test_ver = version.parse(clean_version)
    except Exception as e:
        return False, f"Invalid version format: {e}"
    
    # Check minimum version
    if requirements["min_version"]:
        min_ver = version.parse(requirements["min_version"])
        if test_ver < min_ver:
            return False, f"Version {test_version} is below minimum required {requirements['min_version']}"
    
    # Check maximum version
    if requirements["max_version"]:
        max_ver = version.parse(requirements["max_version"])
        if test_ver > max_ver:
            return False, f"Version {test_version} is above maximum supported {requirements['max_version']}"
    
    return True, "Compatible"


def create_test_matrix(versions: List[str], content_packs: List[Dict[str, Any]], max_jobs: int = 50) -> Dict[str, Any]:
    """
    Create a test matrix for GitHub Actions.
    
    Args:
        versions: List of IntentVerse versions to test
        content_packs: List of content pack information
        max_jobs: Maximum number of parallel jobs
    
    Returns:
        GitHub Actions matrix configuration
    """
    matrix_include = []
    skipped_combinations = []
    
    for pack in content_packs:
        pack_name = pack["name"]
        pack_file = pack["relative_path"]
        compatibility_conditions = pack.get("compatibility_conditions", [])
        
        # Parse compatibility requirements
        requirements = parse_compatibility_conditions(compatibility_conditions)
        
        for ver in versions:
            # Check if this version is compatible with the content pack
            is_compatible, reason = is_version_compatible(ver, requirements)
            
            if is_compatible:
                # Create a safe job name (GitHub Actions requirement)
                safe_pack_name = pack_name.replace(" ", "-").replace("_", "-").lower()
                safe_version = ver.replace(".", "-").replace("v", "")
                
                matrix_include.append({
                    "version": ver,
                    "content_pack": pack_file,
                    "content_pack_name": safe_pack_name,
                    "content_pack_display_name": pack_name,
                    "job_name": f"{safe_pack_name}-{safe_version}",
                    "requirements": requirements,
                    "expected_result": "pass"
                })
            else:
                skipped_combinations.append({
                    "version": ver,
                    "content_pack": pack_name,
                    "reason": reason,
                    "requirements": requirements
                })
    
    # Limit the number of jobs to avoid overwhelming CI
    if len(matrix_include) > max_jobs:
        print(f"⚠️  Matrix has {len(matrix_include)} jobs, limiting to {max_jobs} for CI performance", file=sys.stderr)
        
        # Prioritize: latest versions first, then by content pack importance
        def job_priority(job):
            ver = job["version"]
            # Remove 'v' prefix and parse version
            clean_ver = ver.lstrip('v')
            try:
                parsed_ver = version.parse(clean_ver)
                # Higher version = higher priority
                version_priority = parsed_ver.major * 1000 + parsed_ver.minor * 100 + parsed_ver.micro
            except:
                version_priority = 0
            
            # Prioritize certain content packs (demo, education)
            pack_priority = 0
            if "demo" in job["content_pack_name"] or "demonstration" in job["content_pack_name"]:
                pack_priority = 100
            elif "education" in job["content_pack_name"]:
                pack_priority = 50
            
            return version_priority + pack_priority
        
        matrix_include.sort(key=job_priority, reverse=True)
        matrix_include = matrix_include[:max_jobs]
    
    matrix = {
        "include": matrix_include
    }
    
    summary = {
        "total_combinations": len(matrix_include) + len(skipped_combinations),
        "test_jobs": len(matrix_include),
        "skipped_combinations": len(skipped_combinations),
        "versions_tested": len(versions),
        "content_packs_tested": len(content_packs),
        "matrix": matrix,
        "skipped": skipped_combinations
    }
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Create test matrix for compatibility testing"
    )
    parser.add_argument(
        "--versions",
        required=True,
        help="JSON file with IntentVerse versions"
    )
    parser.add_argument(
        "--content-packs",
        required=True,
        help="JSON file with content pack information"
    )
    parser.add_argument(
        "--output",
        help="Output file for test matrix (JSON format)"
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=50,
        help="Maximum number of parallel test jobs"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    
    args = parser.parse_args()
    
    # Load versions
    try:
        with open(args.versions, 'r') as f:
            version_data = json.load(f)
        versions = version_data.get("versions", [])
    except Exception as e:
        print(f"❌ Error loading versions file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load content packs
    try:
        with open(args.content_packs, 'r') as f:
            content_pack_data = json.load(f)
        
        # Handle both direct list and wrapped format
        if isinstance(content_pack_data, list):
            content_packs = content_pack_data
        else:
            content_packs = content_pack_data.get("content_packs", [])
    except Exception as e:
        print(f"❌ Error loading content packs file: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not versions:
        print("❌ No versions found", file=sys.stderr)
        sys.exit(1)
    
    if not content_packs:
        print("❌ No content packs found", file=sys.stderr)
        sys.exit(1)
    
    print(f"🔍 Creating test matrix for {len(versions)} versions and {len(content_packs)} content packs...")
    
    # Create the test matrix
    result = create_test_matrix(versions, content_packs, args.max_jobs)
    
    print(f"✅ Created test matrix:")
    print(f"   📊 {result['test_jobs']} test jobs")
    print(f"   ⏭️  {result['skipped_combinations']} skipped combinations")
    print(f"   📦 {result['content_packs_tested']} content packs")
    print(f"   🏷️  {result['versions_tested']} versions")
    
    if args.verbose and result['skipped']:
        print("\n⏭️  Skipped combinations:")
        for skip in result['skipped'][:10]:  # Show first 10
            print(f"   • {skip['content_pack']} + {skip['version']}: {skip['reason']}")
        if len(result['skipped']) > 10:
            print(f"   ... and {len(result['skipped']) - 10} more")
    
    if args.verbose and result['matrix']['include']:
        print("\n🧪 Test jobs:")
        for job in result['matrix']['include'][:10]:  # Show first 10
            print(f"   • {job['content_pack_display_name']} + {job['version']}")
        if len(result['matrix']['include']) > 10:
            print(f"   ... and {len(result['matrix']['include']) - 10} more")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Test matrix saved to {args.output}")
    else:
        # Output just the matrix for GitHub Actions
        print(json.dumps(result['matrix'], indent=2))


if __name__ == "__main__":
    main()