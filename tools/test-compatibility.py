#!/usr/bin/env python3
"""
Standalone Content Pack Compatibility Testing Tool

Test content pack compatibility against specific IntentVerse versions
without requiring full IntentVerse installation.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from packaging import version

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_version(version_str: str) -> version.Version:
    """Parse a semantic version string."""
    try:
        # Remove 'v' prefix if present
        clean_version = version_str.lstrip('v')
        
        # Validate format (must be X.Y.Z)
        parts = clean_version.split('.')
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise ValueError(f"Invalid semantic version format: {version_str}")
        
        return version.parse(clean_version)
    except Exception as e:
        raise ValueError(f"Invalid semantic version format: {version_str}") from e


def check_compatibility_conditions(app_version: str, conditions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Check if app version meets compatibility conditions.
    
    Args:
        app_version: IntentVerse version to check
        conditions: List of compatibility condition objects
    
    Returns:
        Tuple of (is_compatible, list_of_failure_reasons)
    """
    if not conditions:
        return True, []
    
    reasons = []
    
    for condition in conditions:
        condition_type = condition.get("type")
        
        if condition_type == "version_range":
            min_ver = condition.get("min_version")
            max_ver = condition.get("max_version")
            reason = condition.get("reason", "Version compatibility requirement")
            
            if not min_ver:
                reasons.append(f"{reason}: missing min_version in compatibility condition")
                continue
            
            try:
                app_ver = parse_version(app_version)
                min_version_obj = parse_version(min_ver)
                
                # Check minimum version
                if app_ver < min_version_obj:
                    if max_ver:
                        reasons.append(f"{reason}: requires {min_ver} <= version <= {max_ver}, got {app_version}")
                    else:
                        reasons.append(f"{reason}: requires version >= {min_ver}, got {app_version}")
                    continue
                
                # Check maximum version if specified
                if max_ver:
                    max_version_obj = parse_version(max_ver)
                    if app_ver > max_version_obj:
                        reasons.append(f"{reason}: requires {min_ver} <= version <= {max_ver}, got {app_version}")
                        continue
                
            except ValueError as e:
                reasons.append(f"Invalid version in compatibility condition: {e}")
                continue
        
        else:
            reasons.append(f"Unknown compatibility condition type: {condition_type}")
    
    return len(reasons) == 0, reasons


def test_content_pack_compatibility(content: Dict[str, Any], test_version: str) -> Dict[str, Any]:
    """
    Test content pack compatibility against a specific version.
    
    Args:
        content: Content pack data
        test_version: IntentVerse version to test against
    
    Returns:
        Test result dictionary
    """
    metadata = content.get("metadata", {})
    pack_name = metadata.get("name", "Unknown")
    compatibility_conditions = metadata.get("compatibility_conditions", [])
    
    # Check compatibility
    is_compatible, reasons = check_compatibility_conditions(test_version, compatibility_conditions)
    
    result = {
        "content_pack": pack_name,
        "test_version": test_version,
        "compatible": is_compatible,
        "reasons": reasons,
        "conditions": compatibility_conditions,
        "has_conditions": len(compatibility_conditions) > 0
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Test content pack compatibility against IntentVerse versions"
    )
    parser.add_argument(
        "content_pack",
        type=Path,
        help="Path to content pack JSON file"
    )
    parser.add_argument(
        "--version", "-v",
        required=True,
        help="IntentVerse version to test against (e.g., '1.0.0', 'v1.2.0')"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed compatibility information"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show compatibility status (no details)"
    )
    
    args = parser.parse_args()
    
    if not args.content_pack.exists():
        print(f"Error: File not found: {args.content_pack}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Validate test version format
        parse_version(args.version)
        
        # Load content pack
        with open(args.content_pack, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Test compatibility
        result = test_content_pack_compatibility(content, args.version)
        
        if args.json:
            # JSON output
            print(json.dumps(result, indent=2))
        else:
            # Human-readable output
            pack_name = result["content_pack"]
            test_version = result["test_version"]
            compatible = result["compatible"]
            
            if compatible:
                if not args.quiet:
                    print(f"✓ {pack_name} is compatible with IntentVerse {test_version}")
            else:
                print(f"✗ {pack_name} is NOT compatible with IntentVerse {test_version}")
                
                if not args.quiet:
                    for reason in result["reasons"]:
                        print(f"  • {reason}")
            
            if args.verbose and not args.quiet:
                print(f"\nCompatibility Analysis:")
                print(f"  Content Pack: {pack_name}")
                print(f"  Test Version: {test_version}")
                print(f"  Has Conditions: {'Yes' if result['has_conditions'] else 'No'}")
                print(f"  Conditions Count: {len(result['conditions'])}")
                
                if result["conditions"]:
                    print(f"  Conditions:")
                    for i, condition in enumerate(result["conditions"], 1):
                        print(f"    {i}. Type: {condition.get('type', 'unknown')}")
                        if condition.get("min_version"):
                            print(f"       Min Version: {condition['min_version']}")
                        if condition.get("max_version"):
                            print(f"       Max Version: {condition['max_version']}")
                        if condition.get("reason"):
                            print(f"       Reason: {condition['reason']}")
        
        # Exit with appropriate code
        sys.exit(0 if result["compatible"] else 1)
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.content_pack}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()