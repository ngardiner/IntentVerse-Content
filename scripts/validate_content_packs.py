#!/usr/bin/env python3
"""
Content Pack Validation Script

This script validates all JSON content packs in the content-packs directory
against the expected schema and checks for required metadata fields.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import jsonschema

# Content Pack JSON Schema
CONTENT_PACK_SCHEMA = {
    "type": "object",
    "required": ["metadata"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["name", "summary", "detailed_description", "date_exported", "author_name", "author_email", "version"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "summary": {"type": "string", "minLength": 1},
                "detailed_description": {"type": "string", "minLength": 1},
                "date_exported": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"},
                "author_name": {"type": "string", "minLength": 1},
                "author_email": {"type": "string", "format": "email"},
                "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "category": {"type": "string"}
            }
        },
        "database": {
            "type": "array",
            "items": {"type": "string"}
        },
        "prompts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "content"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        },
        "state": {
            "type": "object",
            "properties": {
                "filesystem": {"type": "object"},
                "email": {"type": "object"},
                "memory": {"type": "object"},
                "web_search": {"type": "object"}
            }
        }
    }
}

def validate_content_pack(file_path: Path) -> Dict[str, Any]:
    """
    Validate a single content pack file.
    
    Returns:
        Dict with validation results including success status and any errors
    """
    result = {
        "file": str(file_path),
        "valid": False,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Load and parse JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Validate against schema
        jsonschema.validate(content, CONTENT_PACK_SCHEMA)
        
        # Additional validation checks
        metadata = content.get("metadata", {})
        
        # Check for duplicate names (will be checked across all files later)
        # Check version format
        version = metadata.get("version", "")
        if version and not version.count('.') == 2:
            result["warnings"].append("Version should follow semantic versioning (x.y.z)")
        
        # Check if required sections are present but empty
        if "database" in content and len(content["database"]) == 0:
            result["warnings"].append("Database section is present but empty")
        
        if "prompts" in content and len(content["prompts"]) == 0:
            result["warnings"].append("Prompts section is present but empty")
        
        if "state" in content and len(content["state"]) == 0:
            result["warnings"].append("State section is present but empty")
        
        result["valid"] = True
        
    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {str(e)}")
    except jsonschema.ValidationError as e:
        result["errors"].append(f"Schema validation failed: {e.message}")
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
    
    return result

def check_duplicate_names(validation_results: List[Dict[str, Any]]) -> List[str]:
    """Check for duplicate content pack names across all valid files."""
    names = {}
    duplicates = []
    
    for result in validation_results:
        if result["valid"]:
            try:
                with open(result["file"], 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    name = content["metadata"]["name"]
                    if name in names:
                        duplicates.append(f"Duplicate name '{name}' found in {result['file']} and {names[name]}")
                    else:
                        names[name] = result["file"]
            except Exception:
                pass  # Already handled in individual validation
    
    return duplicates

def main():
    """Main validation function."""
    content_packs_dir = Path("content-packs")
    
    if not content_packs_dir.exists():
        print("❌ content-packs directory not found")
        sys.exit(1)
    
    # Find all JSON files
    json_files = list(content_packs_dir.rglob("*.json"))
    
    if not json_files:
        print("ℹ️  No content pack files found")
        return
    
    print(f"🔍 Validating {len(json_files)} content pack(s)...")
    
    validation_results = []
    total_errors = 0
    total_warnings = 0
    
    # Validate each file
    for json_file in json_files:
        result = validate_content_pack(json_file)
        validation_results.append(result)
        
        if result["valid"]:
            status = "✅"
        else:
            status = "❌"
            total_errors += len(result["errors"])
        
        total_warnings += len(result["warnings"])
        
        print(f"{status} {json_file}")
        
        for error in result["errors"]:
            print(f"   ❌ {error}")
        
        for warning in result["warnings"]:
            print(f"   ⚠️  {warning}")
    
    # Check for duplicate names
    duplicate_errors = check_duplicate_names(validation_results)
    for error in duplicate_errors:
        print(f"❌ {error}")
        total_errors += 1
    
    # Summary
    valid_count = sum(1 for r in validation_results if r["valid"])
    print(f"\n📊 Summary:")
    print(f"   Valid: {valid_count}/{len(validation_results)}")
    print(f"   Errors: {total_errors}")
    print(f"   Warnings: {total_warnings}")
    
    if total_errors > 0:
        print("\n❌ Validation failed")
        sys.exit(1)
    else:
        print("\n✅ All content packs are valid")

if __name__ == "__main__":
    main()