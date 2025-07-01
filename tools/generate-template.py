#!/usr/bin/env python3
"""
Content Pack Template Generator

Generate content pack templates with proper structure and compatibility conditions.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def generate_basic_template(name: str, **kwargs) -> Dict[str, Any]:
    """Generate a basic content pack template."""
    return {
        "metadata": {
            "name": name,
            "version": "1.0.0",
            "date_exported": datetime.now().isoformat(),
            "category": kwargs.get("category", "custom"),
            "compatibility_conditions": [
                {
                    "type": "version_range",
                    "min_version": kwargs.get("min_version", "1.0.0"),
                    "reason": f"Requires IntentVerse {kwargs.get('min_version', '1.0.0')}+ features"
                }
            ]
        }
    }


def generate_database_template(name: str, **kwargs) -> Dict[str, Any]:
    """Generate a content pack template with database content."""
    template = generate_basic_template(name, **kwargs)
    
    # Add database content
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    table_name = f"{safe_name}_data"
    
    template["database"] = [
        f"CREATE TABLE IF NOT EXISTS {table_name} (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    name TEXT NOT NULL,",
        "    value TEXT,",
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        ");",
        f"INSERT OR IGNORE INTO {table_name} (name, value) VALUES",
        "    ('example_item_1', 'Example value 1'),",
        "    ('example_item_2', 'Example value 2');"
    ]
    
    return template


def generate_state_template(name: str, **kwargs) -> Dict[str, Any]:
    """Generate a content pack template with state content."""
    template = generate_basic_template(name, **kwargs)
    
    # Add state content
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    
    template["state"] = {
        safe_name: {
            "settings": {
                "enabled": True,
                "debug_mode": False,
                "max_items": 100
            },
            "data": {
                "example_key": "example_value",
                "items": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"}
                ]
            }
        }
    }
    
    return template


def generate_timeline_template(name: str, **kwargs) -> Dict[str, Any]:
    """Generate a content pack template with timeline content."""
    template = generate_basic_template(name, **kwargs)
    
    # Update compatibility for timeline features
    template["metadata"]["compatibility_conditions"] = [
        {
            "type": "version_range",
            "min_version": "1.2.0",
            "reason": "Requires timeline module introduced in v1.2.0"
        }
    ]
    
    # Add timeline state
    template["state"] = {
        "timeline": {
            "events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "system",
                    "description": f"{name} content pack installed",
                    "metadata": {
                        "source": "content_pack",
                        "pack_name": name
                    }
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "user_action",
                    "description": "Example user action event",
                    "metadata": {
                        "action": "example_action",
                        "result": "success"
                    }
                }
            ]
        }
    }
    
    return template


def generate_full_template(name: str, **kwargs) -> Dict[str, Any]:
    """Generate a comprehensive content pack template with all features."""
    template = generate_basic_template(name, **kwargs)
    
    # Update compatibility for all features
    template["metadata"]["compatibility_conditions"] = [
        {
            "type": "version_range",
            "min_version": "1.0.0",
            "reason": "Requires database and state management features"
        },
        {
            "type": "version_range",
            "min_version": "1.2.0",
            "reason": "Requires timeline module for event tracking"
        }
    ]
    
    # Add comprehensive content
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    
    # Database content
    template["database"] = [
        f"CREATE TABLE IF NOT EXISTS {safe_name}_users (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    username TEXT UNIQUE NOT NULL,",
        "    email TEXT,",
        "    role TEXT DEFAULT 'user',",
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        ");",
        f"CREATE TABLE IF NOT EXISTS {safe_name}_settings (",
        "    key TEXT PRIMARY KEY,",
        "    value TEXT,",
        "    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        ");",
        f"INSERT OR IGNORE INTO {safe_name}_users (username, email, role) VALUES",
        "    ('admin', 'admin@example.com', 'admin'),",
        "    ('user1', 'user1@example.com', 'user');",
        f"INSERT OR IGNORE INTO {safe_name}_settings (key, value) VALUES",
        "    ('theme', 'default'),",
        "    ('notifications', 'enabled'),",
        "    ('max_items_per_page', '25');"
    ]
    
    # State content
    template["state"] = {
        safe_name: {
            "settings": {
                "enabled": True,
                "debug_mode": False,
                "auto_save": True,
                "theme": "default"
            },
            "user_preferences": {
                "default_view": "list",
                "items_per_page": 25,
                "show_timestamps": True
            },
            "cache": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        },
        "timeline": {
            "events": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "system",
                    "description": f"{name} content pack installed",
                    "metadata": {
                        "source": "content_pack",
                        "pack_name": name,
                        "version": "1.0.0"
                    }
                }
            ]
        }
    }
    
    # Prompts content
    template["prompts"] = {
        "welcome": f"Welcome to {name}!",
        "help": f"This is the {name} content pack. Use the available features to get started.",
        "error_generic": "An error occurred. Please try again.",
        "success_save": "Data saved successfully.",
        "confirm_delete": "Are you sure you want to delete this item?"
    }
    
    return template


def add_optional_metadata(template: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Add optional metadata fields to the template."""
    metadata = template["metadata"]
    
    if kwargs.get("description"):
        metadata["description"] = kwargs["description"]
    
    if kwargs.get("author"):
        metadata["author"] = kwargs["author"]
    
    if kwargs.get("tags"):
        metadata["tags"] = kwargs["tags"]
    
    if kwargs.get("license"):
        metadata["license"] = kwargs["license"]
    
    if kwargs.get("homepage"):
        metadata["homepage"] = kwargs["homepage"]
    
    return template


def main():
    parser = argparse.ArgumentParser(
        description="Generate content pack templates"
    )
    parser.add_argument(
        "--name", "-n",
        required=True,
        help="Name of the content pack"
    )
    parser.add_argument(
        "--template", "-t",
        choices=["basic", "database", "state", "timeline", "full"],
        default="basic",
        help="Template type to generate"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path (default: based on name)"
    )
    parser.add_argument(
        "--description", "-d",
        help="Content pack description"
    )
    parser.add_argument(
        "--author", "-a",
        help="Author name"
    )
    parser.add_argument(
        "--category", "-c",
        default="custom",
        help="Content pack category"
    )
    parser.add_argument(
        "--tags",
        help="Comma-separated tags"
    )
    parser.add_argument(
        "--min-version",
        default="1.0.0",
        help="Minimum IntentVerse version requirement"
    )
    parser.add_argument(
        "--license",
        help="License for the content pack"
    )
    parser.add_argument(
        "--homepage",
        help="Homepage URL for the content pack"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing file"
    )
    
    args = parser.parse_args()
    
    # Prepare kwargs
    kwargs = {
        "category": args.category,
        "min_version": args.min_version,
        "description": args.description,
        "author": args.author,
        "license": args.license,
        "homepage": args.homepage
    }
    
    if args.tags:
        kwargs["tags"] = [tag.strip() for tag in args.tags.split(",")]
    
    # Generate template based on type
    template_generators = {
        "basic": generate_basic_template,
        "database": generate_database_template,
        "state": generate_state_template,
        "timeline": generate_timeline_template,
        "full": generate_full_template
    }
    
    generator = template_generators[args.template]
    template = generator(args.name, **kwargs)
    
    # Add optional metadata
    template = add_optional_metadata(template, **kwargs)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        safe_name = args.name.lower().replace(" ", "-").replace("_", "-")
        output_path = Path(f"{safe_name}.json")
    
    # Check if file exists
    if output_path.exists() and not args.overwrite:
        print(f"Error: File {output_path} already exists. Use --overwrite to replace it.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Write template
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"✓ Generated {args.template} template: {output_path}")
        
        # Show next steps
        print(f"\nNext steps:")
        print(f"1. Edit {output_path} to customize your content")
        print(f"2. Validate: python tools/validate.py {output_path}")
        print(f"3. Test compatibility: python tools/test-compatibility.py {output_path} --version 1.0.0")
        
        # Show template-specific guidance
        if args.template == "database":
            print(f"\nDatabase template guidance:")
            print(f"• Modify the SQL statements in the 'database' array")
            print(f"• Ensure table names are unique to avoid conflicts")
            print(f"• Use IF NOT EXISTS and OR IGNORE for safe installation")
        
        elif args.template == "state":
            print(f"\nState template guidance:")
            print(f"• Customize the state data in the 'state' object")
            print(f"• Use module names that match IntentVerse modules")
            print(f"• Avoid overwriting existing state data")
        
        elif args.template == "timeline":
            print(f"\nTimeline template guidance:")
            print(f"• Add events to the timeline.events array")
            print(f"• Use ISO format timestamps")
            print(f"• Include meaningful metadata for events")
        
        elif args.template == "full":
            print(f"\nFull template guidance:")
            print(f"• This template includes database, state, timeline, and prompts")
            print(f"• Customize each section according to your needs")
            print(f"• Remove sections you don't need")
    
    except Exception as e:
        print(f"Error: Failed to write template: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()