#!/usr/bin/env python3
"""
Manifest Generation Script

This script scans all valid content packs and generates a manifest.json file
that can be consumed by the IntentVerse application to display available
content packs.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

def extract_metadata(content_pack_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from a content pack file.
    
    Returns:
        Dictionary containing the metadata and file information
    """
    try:
        with open(content_pack_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        metadata = content.get("metadata", {})
        
        # Calculate file size
        file_size = content_pack_path.stat().st_size
        
        # Count sections
        sections = {
            "has_database": bool(content.get("database")),
            "has_prompts": bool(content.get("prompts")),
            "has_state": bool(content.get("state")),
            "database_statements": len(content.get("database", [])),
            "prompt_count": len(content.get("prompts", [])),
            "state_modules": list(content.get("state", {}).keys()) if content.get("state") else []
        }
        
        return {
            "filename": content_pack_path.name,
            "relative_path": str(content_pack_path.relative_to(Path("content-packs"))),
            "file_size_bytes": file_size,
            "name": metadata.get("name", ""),
            "summary": metadata.get("summary", ""),
            "detailed_description": metadata.get("detailed_description", ""),
            "version": metadata.get("version", ""),
            "author_name": metadata.get("author_name", ""),
            "author_email": metadata.get("author_email", ""),
            "date_exported": metadata.get("date_exported", ""),
            "tags": metadata.get("tags", []),
            "category": metadata.get("category", "uncategorized"),
            "sections": sections
        }
        
    except Exception as e:
        print(f"⚠️  Error processing {content_pack_path}: {e}")
        return None

def generate_manifest() -> Dict[str, Any]:
    """
    Generate the complete manifest from all content packs.
    
    Returns:
        Dictionary containing the manifest data
    """
    content_packs_dir = Path("content-packs")
    
    if not content_packs_dir.exists():
        print("❌ content-packs directory not found")
        return None
    
    # Find all JSON files
    json_files = list(content_packs_dir.rglob("*.json"))
    
    content_packs = []
    categories = set()
    authors = set()
    
    print(f"📦 Processing {len(json_files)} content pack(s)...")
    
    for json_file in json_files:
        metadata = extract_metadata(json_file)
        if metadata:
            content_packs.append(metadata)
            categories.add(metadata["category"])
            if metadata["author_name"]:
                authors.add(metadata["author_name"])
            print(f"   ✅ {json_file.name}")
        else:
            print(f"   ❌ {json_file.name}")
    
    # Sort content packs by name
    content_packs.sort(key=lambda x: x["name"].lower())
    
    # Generate statistics
    stats = {
        "total_packs": len(content_packs),
        "categories": sorted(list(categories)),
        "authors": sorted(list(authors)),
        "total_size_bytes": sum(pack["file_size_bytes"] for pack in content_packs),
        "packs_with_database": sum(1 for pack in content_packs if pack["sections"]["has_database"]),
        "packs_with_prompts": sum(1 for pack in content_packs if pack["sections"]["has_prompts"]),
        "packs_with_state": sum(1 for pack in content_packs if pack["sections"]["has_state"])
    }
    
    manifest = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repository_url": "https://github.com/your-org/IntentVerse-Content",
        "statistics": stats,
        "content_packs": content_packs
    }
    
    return manifest

def main():
    """Main function to generate and save the manifest."""
    manifest = generate_manifest()
    
    if not manifest:
        sys.exit(1)
    
    # Write manifest to file
    manifest_path = Path("manifest.json")
    
    try:
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Manifest generated successfully: {manifest_path}")
        print(f"   📊 {manifest['statistics']['total_packs']} content packs indexed")
        print(f"   📁 {len(manifest['statistics']['categories'])} categories")
        print(f"   👥 {len(manifest['statistics']['authors'])} authors")
        
    except Exception as e:
        print(f"❌ Error writing manifest: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()