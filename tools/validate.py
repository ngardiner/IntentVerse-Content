#!/usr/bin/env python3
"""
Standalone Content Pack Validation Tool

A simple tool to validate content pack JSON files against the schema
and compatibility requirements.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.validate_content_packs import validate_content_pack


def main():
    parser = argparse.ArgumentParser(
        description="Validate content pack JSON files"
    )
    parser.add_argument(
        "content_pack",
        type=Path,
        help="Path to content pack JSON file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation information"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show errors (no success messages)"
    )
    
    args = parser.parse_args()
    
    if not args.content_pack.exists():
        print(f"Error: File not found: {args.content_pack}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load content pack
        with open(args.content_pack, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Validate
        result = validate_content_pack(content)
        
        if args.json:
            # JSON output
            output = {
                "file": str(args.content_pack),
                "valid": result["is_valid"],
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", []),
                "summary": result.get("summary", {})
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            if result["is_valid"]:
                if not args.quiet:
                    print(f"✓ {args.content_pack.name} is valid")
                
                if args.verbose:
                    summary = result.get("summary", {})
                    print(f"  Metadata: {'✓' if 'metadata' in content else '✗'}")
                    print(f"  Database: {'✓' if 'database' in content else '-'}")
                    print(f"  State: {'✓' if 'state' in content else '-'}")
                    print(f"  Prompts: {'✓' if 'prompts' in content else '-'}")
                    
                    compatibility = content.get("metadata", {}).get("compatibility_conditions", [])
                    print(f"  Compatibility conditions: {len(compatibility)}")
            else:
                print(f"✗ {args.content_pack.name} validation failed")
                
                # Show errors
                for error in result.get("errors", []):
                    print(f"  Error: {error}")
                
                # Show warnings
                for warning in result.get("warnings", []):
                    print(f"  Warning: {warning}")
                
                sys.exit(1)
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.content_pack}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()