#!/usr/bin/env python3
"""
Script to discover and list content packs for compatibility testing.

This script scans the content-packs directory and returns a list of content packs
that match the specified filter criteria.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import fnmatch


def discover_content_packs(content_dir: Path) -> List[Dict[str, Any]]:
    """
    Discover all content pack JSON files in the content directory.
    
    Args:
        content_dir: Path to the content-packs directory
    
    Returns:
        List of content pack information
    """
    if not content_dir.exists():
        print(f"❌ Content directory not found: {content_dir}", file=sys.stderr)
        return []
    
    content_packs = []
    
    # Find all JSON files recursively
    for json_file in content_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            metadata = content.get("metadata", {})
            
            # Calculate relative path from content-packs directory
            relative_path = json_file.relative_to(content_dir)
            
            pack_info = {
                "filename": json_file.name,
                "relative_path": str(relative_path),
                "full_path": str(json_file),
                "name": metadata.get("name", json_file.stem),
                "version": metadata.get("version", "unknown"),
                "category": metadata.get("category", "uncategorized"),
                "tags": metadata.get("tags", []),
                "compatibility_conditions": metadata.get("compatibility_conditions", []),
                "has_database": bool(content.get("database")),
                "has_state": bool(content.get("state")),
                "has_prompts": bool(content.get("prompts")),
                "file_size": json_file.stat().st_size
            }
            
            content_packs.append(pack_info)
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Skipping invalid JSON file {json_file}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Error processing {json_file}: {e}", file=sys.stderr)
    
    return content_packs


def apply_filters(content_packs: List[Dict[str, Any]], filter_pattern: str) -> List[Dict[str, Any]]:
    """
    Apply filter patterns to content packs.
    
    Args:
        content_packs: List of content pack information
        filter_pattern: Filter pattern (supports wildcards)
    
    Returns:
        Filtered list of content packs
    """
    if not filter_pattern or filter_pattern == "*":
        return content_packs
    
    filtered = []
    
    for pack in content_packs:
        # Check multiple fields for matches
        match_fields = [
            pack["filename"],
            pack["relative_path"],
            pack["name"],
            pack["category"]
        ]
        
        # Also check tags
        match_fields.extend(pack["tags"])
        
        # Check if any field matches the pattern
        for field in match_fields:
            if fnmatch.fnmatch(field.lower(), filter_pattern.lower()):
                filtered.append(pack)
                break
    
    return filtered


def validate_content_packs(content_packs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate content packs and return validation summary.
    
    Args:
        content_packs: List of content pack information
    
    Returns:
        Validation summary
    """
    validation = {
        "total_packs": len(content_packs),
        "valid_packs": 0,
        "packs_with_compatibility": 0,
        "packs_without_compatibility": 0,
        "categories": set(),
        "issues": []
    }
    
    for pack in content_packs:
        validation["categories"].add(pack["category"])
        
        # Check if pack has compatibility conditions
        if pack["compatibility_conditions"]:
            validation["packs_with_compatibility"] += 1
        else:
            validation["packs_without_compatibility"] += 1
            validation["issues"].append({
                "pack": pack["name"],
                "issue": "No compatibility conditions specified",
                "severity": "warning"
            })
        
        # Check for required metadata
        if not pack["name"] or pack["name"] == pack["filename"].replace(".json", ""):
            validation["issues"].append({
                "pack": pack["filename"],
                "issue": "Missing or default name in metadata",
                "severity": "warning"
            })
        
        if pack["version"] == "unknown":
            validation["issues"].append({
                "pack": pack["name"],
                "issue": "Missing version in metadata",
                "severity": "warning"
            })
        
        # Count as valid if it has basic structure
        if pack["name"] and (pack["has_database"] or pack["has_state"] or pack["has_prompts"]):
            validation["valid_packs"] += 1
    
    validation["categories"] = sorted(list(validation["categories"]))
    
    return validation


def main():
    parser = argparse.ArgumentParser(
        description="Discover content packs for compatibility testing"
    )
    parser.add_argument(
        "--content-dir",
        type=Path,
        default=Path("content-packs"),
        help="Path to content-packs directory"
    )
    parser.add_argument(
        "--filter",
        default="*",
        help="Filter pattern for content packs (supports wildcards)"
    )
    parser.add_argument(
        "--output",
        help="Output file for content pack list (JSON format)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Perform validation checks on content packs"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information"
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Discovering content packs in {args.content_dir}...")
    
    content_packs = discover_content_packs(args.content_dir)
    
    if not content_packs:
        print("❌ No content packs found", file=sys.stderr)
        sys.exit(1)
    
    print(f"📦 Found {len(content_packs)} content packs")
    
    # Apply filters
    if args.filter and args.filter != "*":
        print(f"🔍 Applying filter: {args.filter}")
        content_packs = apply_filters(content_packs, args.filter)
        print(f"📦 {len(content_packs)} content packs match filter")
    
    # Validate if requested
    validation = None
    if args.validate:
        print("🔍 Validating content packs...")
        validation = validate_content_packs(content_packs)
        
        print(f"✅ {validation['valid_packs']}/{validation['total_packs']} content packs are valid")
        print(f"📋 {validation['packs_with_compatibility']} have compatibility conditions")
        print(f"⚠️  {validation['packs_without_compatibility']} missing compatibility conditions")
        
        if validation["issues"]:
            print(f"⚠️  Found {len(validation['issues'])} validation issues:")
            for issue in validation["issues"]:
                severity_icon = "❌" if issue["severity"] == "error" else "⚠️ "
                print(f"   {severity_icon} {issue['pack']}: {issue['issue']}")
    
    # Show content pack list
    if args.verbose:
        print("\n📋 Content Packs:")
        for pack in content_packs:
            compat_info = f" ({len(pack['compatibility_conditions'])} conditions)" if pack['compatibility_conditions'] else " (no conditions)"
            print(f"   📄 {pack['name']} v{pack['version']}{compat_info}")
            print(f"      📁 {pack['relative_path']}")
            if pack['tags']:
                print(f"      🏷️  {', '.join(pack['tags'])}")
    
    # Prepare output
    result = {
        "content_packs": content_packs,
        "filter_applied": args.filter,
        "total_found": len(content_packs),
        "validation": validation
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Content pack list saved to {args.output}")
    else:
        # Output just the content packs for pipeline use
        print(json.dumps(content_packs, indent=2))


if __name__ == "__main__":
    main()