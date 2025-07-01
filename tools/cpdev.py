#!/usr/bin/env python3
"""
Content Pack Developer CLI Tool

A comprehensive command-line tool for content pack authors to create, validate,
test, and manage their content packs.
"""

import click
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from packaging import version
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.tree import Tree

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.validate_content_packs import validate_content_pack
from scripts.get-intentverse-versions import fetch_github_releases, filter_versions

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="cpdev")
def cli():
    """Content Pack Developer Tools
    
    A comprehensive CLI tool for creating, validating, and testing content packs
    for IntentVerse.
    """
    pass


@cli.command()
@click.option("--name", required=True, help="Name of the content pack")
@click.option("--description", help="Description of the content pack")
@click.option("--author", help="Author name")
@click.option("--category", default="custom", help="Content pack category")
@click.option("--tags", help="Comma-separated tags")
@click.option("--min-version", default="1.0.0", help="Minimum IntentVerse version")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--template", type=click.Choice(["basic", "database", "state", "full"]), 
              default="basic", help="Template type to use")
def create(name, description, author, category, tags, min_version, output, template):
    """Create a new content pack from template."""
    
    console.print(f"[bold green]Creating content pack: {name}[/bold green]")
    
    # Generate content pack structure
    content_pack = generate_content_pack_template(
        name=name,
        description=description,
        author=author,
        category=category,
        tags=tags.split(",") if tags else [],
        min_version=min_version,
        template=template
    )
    
    # Determine output path
    if not output:
        safe_name = name.lower().replace(" ", "-").replace("_", "-")
        output = f"{safe_name}.json"
    
    output_path = Path(output)
    
    # Write content pack
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content_pack, f, indent=2)
        
        console.print(f"[green]✓[/green] Content pack created: {output_path}")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"1. Edit {output_path} to add your content")
        console.print(f"2. Validate: [cyan]cpdev validate {output_path}[/cyan]")
        console.print(f"3. Test: [cyan]cpdev test {output_path}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating content pack: {e}")
        sys.exit(1)


@cli.command()
@click.argument("content_pack", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed validation results")
@click.option("--fix", is_flag=True, help="Attempt to fix common issues automatically")
def validate(content_pack, verbose, fix):
    """Validate a content pack."""
    
    content_pack_path = Path(content_pack)
    console.print(f"[bold]Validating content pack: {content_pack_path.name}[/bold]")
    
    try:
        # Load content pack
        with open(content_pack_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Validate using existing validation logic
        validation_result = validate_content_pack(content)
        
        if validation_result["is_valid"]:
            console.print(f"[green]✓[/green] Content pack is valid!")
            
            if verbose:
                show_validation_details(validation_result, content)
        else:
            console.print(f"[red]✗[/red] Content pack validation failed")
            
            # Show errors
            for error in validation_result.get("errors", []):
                console.print(f"  [red]•[/red] {error}")
            
            # Show warnings
            for warning in validation_result.get("warnings", []):
                console.print(f"  [yellow]•[/yellow] {warning}")
            
            if fix:
                console.print("\n[yellow]Attempting to fix issues...[/yellow]")
                fixed_content = attempt_fixes(content, validation_result)
                
                if fixed_content != content:
                    # Save fixed version
                    backup_path = content_pack_path.with_suffix('.json.backup')
                    content_pack_path.rename(backup_path)
                    
                    with open(content_pack_path, 'w', encoding='utf-8') as f:
                        json.dump(fixed_content, f, indent=2)
                    
                    console.print(f"[green]✓[/green] Fixed content pack saved")
                    console.print(f"[dim]Original backed up to: {backup_path}[/dim]")
                else:
                    console.print("[yellow]No automatic fixes available[/yellow]")
            
            sys.exit(1)
    
    except json.JSONDecodeError as e:
        console.print(f"[red]✗[/red] Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error validating content pack: {e}")
        sys.exit(1)


@cli.command()
@click.argument("content_pack", type=click.Path(exists=True))
@click.option("--version", help="Specific IntentVerse version to test against")
@click.option("--all-versions", is_flag=True, help="Test against all available versions")
@click.option("--latest", is_flag=True, help="Test against latest version only")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed test output")
def test(content_pack, version, all_versions, latest, verbose):
    """Test content pack compatibility."""
    
    content_pack_path = Path(content_pack)
    console.print(f"[bold]Testing content pack: {content_pack_path.name}[/bold]")
    
    try:
        # Load content pack
        with open(content_pack_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Determine versions to test
        if version:
            test_versions = [version]
        elif all_versions:
            test_versions = get_available_versions()
        elif latest:
            test_versions = [get_latest_version()]
        else:
            # Default: test against current and latest
            test_versions = get_default_test_versions()
        
        console.print(f"Testing against {len(test_versions)} version(s)")
        
        # Run compatibility tests
        results = run_compatibility_tests(content, test_versions, verbose)
        
        # Display results
        display_test_results(results, verbose)
        
        # Exit with appropriate code
        if any(not result["compatible"] for result in results.values()):
            sys.exit(1)
    
    except Exception as e:
        console.print(f"[red]✗[/red] Error testing content pack: {e}")
        sys.exit(1)


@cli.command()
@click.argument("content_pack", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file for updated content pack")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode for suggestions")
def suggest_compatibility(content_pack, output, interactive):
    """Suggest compatibility conditions for a content pack."""
    
    content_pack_path = Path(content_pack)
    console.print(f"[bold]Analyzing content pack: {content_pack_path.name}[/bold]")
    
    try:
        # Load content pack
        with open(content_pack_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Analyze content pack features
        suggestions = analyze_content_pack_features(content)
        
        console.print("\n[bold]Compatibility Analysis:[/bold]")
        
        for suggestion in suggestions:
            console.print(f"  [cyan]•[/cyan] {suggestion['reason']}")
            console.print(f"    Suggested: {suggestion['condition']}")
        
        if interactive:
            # Interactive mode to select suggestions
            selected_conditions = interactive_condition_selection(suggestions)
        else:
            # Use all suggestions
            selected_conditions = [s["condition"] for s in suggestions]
        
        if selected_conditions:
            # Update content pack
            metadata = content.get("metadata", {})
            metadata["compatibility_conditions"] = selected_conditions
            content["metadata"] = metadata
            
            # Save updated content pack
            output_path = Path(output) if output else content_pack_path
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
            
            console.print(f"\n[green]✓[/green] Updated content pack with {len(selected_conditions)} compatibility condition(s)")
        else:
            console.print("\n[yellow]No compatibility conditions suggested[/yellow]")
    
    except Exception as e:
        console.print(f"[red]✗[/red] Error analyzing content pack: {e}")
        sys.exit(1)


@cli.command()
@click.option("--repo", default="your-org/IntentVerse", help="IntentVerse repository")
@click.option("--format", type=click.Choice(["table", "json", "list"]), default="table", help="Output format")
def versions(repo, format):
    """List available IntentVerse versions."""
    
    console.print("[bold]Fetching IntentVerse versions...[/bold]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching releases...", total=None)
            
            releases = fetch_github_releases(repo)
            versions_list = filter_versions(releases, include_prereleases=False)
        
        if format == "table":
            display_versions_table(versions_list, releases)
        elif format == "json":
            console.print(json.dumps(versions_list, indent=2))
        elif format == "list":
            for ver in versions_list:
                console.print(ver)
    
    except Exception as e:
        console.print(f"[red]✗[/red] Error fetching versions: {e}")
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Search recursively")
@click.option("--fix", is_flag=True, help="Attempt to fix issues automatically")
def batch_validate(directory, recursive, fix):
    """Validate all content packs in a directory."""
    
    directory_path = Path(directory)
    console.print(f"[bold]Batch validating content packs in: {directory_path}[/bold]")
    
    # Find content pack files
    if recursive:
        pattern = "**/*.json"
    else:
        pattern = "*.json"
    
    content_packs = list(directory_path.glob(pattern))
    
    if not content_packs:
        console.print("[yellow]No content pack files found[/yellow]")
        return
    
    console.print(f"Found {len(content_packs)} content pack file(s)")
    
    results = []
    
    with Progress(console=console) as progress:
        task = progress.add_task("Validating...", total=len(content_packs))
        
        for pack_path in content_packs:
            try:
                with open(pack_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                validation_result = validate_content_pack(content)
                
                results.append({
                    "path": pack_path,
                    "valid": validation_result["is_valid"],
                    "errors": validation_result.get("errors", []),
                    "warnings": validation_result.get("warnings", [])
                })
                
                if fix and not validation_result["is_valid"]:
                    fixed_content = attempt_fixes(content, validation_result)
                    if fixed_content != content:
                        with open(pack_path, 'w', encoding='utf-8') as f:
                            json.dump(fixed_content, f, indent=2)
                        results[-1]["fixed"] = True
            
            except Exception as e:
                results.append({
                    "path": pack_path,
                    "valid": False,
                    "errors": [str(e)],
                    "warnings": []
                })
            
            progress.advance(task)
    
    # Display results
    display_batch_results(results)


def generate_content_pack_template(name: str, description: str = None, author: str = None,
                                 category: str = "custom", tags: List[str] = None,
                                 min_version: str = "1.0.0", template: str = "basic") -> Dict[str, Any]:
    """Generate a content pack template."""
    
    if tags is None:
        tags = []
    
    # Base metadata
    metadata = {
        "name": name,
        "version": "1.0.0",
        "date_exported": datetime.now().isoformat(),
        "category": category,
        "compatibility_conditions": [
            {
                "type": "version_range",
                "min_version": min_version,
                "reason": f"Requires IntentVerse {min_version}+ features"
            }
        ]
    }
    
    if description:
        metadata["description"] = description
    
    if author:
        metadata["author"] = author
    
    if tags:
        metadata["tags"] = tags
    
    # Base content pack structure
    content_pack = {
        "metadata": metadata
    }
    
    # Add template-specific content
    if template == "database":
        content_pack["database"] = [
            "CREATE TABLE IF NOT EXISTS example_table (id INTEGER PRIMARY KEY, name TEXT);",
            "INSERT OR IGNORE INTO example_table (name) VALUES ('Example Data');"
        ]
    
    elif template == "state":
        content_pack["state"] = {
            "example_module": {
                "example_data": "This is example state data",
                "settings": {
                    "enabled": True,
                    "value": 42
                }
            }
        }
    
    elif template == "full":
        content_pack["database"] = [
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT);",
            "INSERT OR IGNORE INTO users (username, email) VALUES ('admin', 'admin@example.com');"
        ]
        content_pack["state"] = {
            "user_management": {
                "default_role": "user",
                "settings": {
                    "registration_enabled": True,
                    "email_verification": False
                }
            },
            "timeline": {
                "events": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "type": "system",
                        "description": "Content pack installed"
                    }
                ]
            }
        }
        content_pack["prompts"] = {
            "welcome": "Welcome to the {name} content pack!",
            "help": "This content pack provides example functionality."
        }
    
    return content_pack


def show_validation_details(validation_result: Dict[str, Any], content: Dict[str, Any]):
    """Show detailed validation information."""
    
    # Create a summary table
    table = Table(title="Validation Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    # Check each component
    components = [
        ("Metadata", "metadata" in content),
        ("Database", "database" in content),
        ("State", "state" in content),
        ("Prompts", "prompts" in content),
        ("Compatibility", bool(content.get("metadata", {}).get("compatibility_conditions")))
    ]
    
    for component, present in components:
        status = "✓ Present" if present else "- Not present"
        table.add_row(component, status, "")
    
    console.print(table)


def attempt_fixes(content: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to automatically fix common content pack issues."""
    
    fixed_content = content.copy()
    
    # Ensure metadata exists
    if "metadata" not in fixed_content:
        fixed_content["metadata"] = {}
    
    metadata = fixed_content["metadata"]
    
    # Add missing required fields
    if "name" not in metadata:
        metadata["name"] = "Untitled Content Pack"
    
    if "version" not in metadata:
        metadata["version"] = "1.0.0"
    
    if "date_exported" not in metadata:
        metadata["date_exported"] = datetime.now().isoformat()
    
    # Add compatibility conditions if missing
    if "compatibility_conditions" not in metadata:
        metadata["compatibility_conditions"] = [
            {
                "type": "version_range",
                "min_version": "1.0.0",
                "reason": "Requires IntentVerse 1.0+ features"
            }
        ]
    
    return fixed_content


def get_available_versions() -> List[str]:
    """Get list of available IntentVerse versions."""
    try:
        releases = fetch_github_releases("your-org/IntentVerse")
        return filter_versions(releases, include_prereleases=False)
    except:
        return ["1.0.0"]  # Fallback


def get_latest_version() -> str:
    """Get the latest IntentVerse version."""
    versions = get_available_versions()
    return versions[0] if versions else "1.0.0"


def get_default_test_versions() -> List[str]:
    """Get default versions for testing."""
    try:
        all_versions = get_available_versions()
        # Return latest and a few recent versions
        return all_versions[:3]
    except:
        return ["1.0.0"]


def run_compatibility_tests(content: Dict[str, Any], test_versions: List[str], verbose: bool) -> Dict[str, Dict[str, Any]]:
    """Run compatibility tests against specified versions."""
    
    results = {}
    compatibility_conditions = content.get("metadata", {}).get("compatibility_conditions", [])
    
    for test_version in test_versions:
        # Simulate compatibility checking
        is_compatible, reasons = check_compatibility_conditions(test_version, compatibility_conditions)
        
        results[test_version] = {
            "compatible": is_compatible,
            "reasons": reasons,
            "conditions": compatibility_conditions
        }
    
    return results


def check_compatibility_conditions(app_version: str, conditions: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    """Check if app version meets compatibility conditions."""
    
    if not conditions:
        return True, []
    
    reasons = []
    
    for condition in conditions:
        if condition.get("type") == "version_range":
            min_ver = condition.get("min_version")
            max_ver = condition.get("max_version")
            reason = condition.get("reason", "Version compatibility requirement")
            
            try:
                app_ver = version.parse(app_version)
                
                if min_ver:
                    min_version_obj = version.parse(min_ver)
                    if app_ver < min_version_obj:
                        if max_ver:
                            reasons.append(f"{reason}: requires {min_ver} <= version <= {max_ver}, got {app_version}")
                        else:
                            reasons.append(f"{reason}: requires version >= {min_ver}, got {app_version}")
                        continue
                
                if max_ver:
                    max_version_obj = version.parse(max_ver)
                    if app_ver > max_version_obj:
                        reasons.append(f"{reason}: requires {min_ver} <= version <= {max_ver}, got {app_version}")
                        continue
                
            except Exception as e:
                reasons.append(f"Invalid version in compatibility condition: {e}")
    
    return len(reasons) == 0, reasons


def display_test_results(results: Dict[str, Dict[str, Any]], verbose: bool):
    """Display compatibility test results."""
    
    table = Table(title="Compatibility Test Results")
    table.add_column("Version", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Issues")
    
    for test_version, result in results.items():
        if result["compatible"]:
            status = "✓ Compatible"
            issues = "-"
        else:
            status = "✗ Incompatible"
            issues = "; ".join(result["reasons"])
        
        table.add_row(test_version, status, issues)
    
    console.print(table)
    
    if verbose:
        for test_version, result in results.items():
            if result["conditions"]:
                console.print(f"\n[bold]Conditions for {test_version}:[/bold]")
                for condition in result["conditions"]:
                    console.print(f"  • {condition}")


def analyze_content_pack_features(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze content pack features and suggest compatibility conditions."""
    
    suggestions = []
    
    # Check for database content
    if "database" in content:
        suggestions.append({
            "reason": "Content pack uses database features",
            "condition": {
                "type": "version_range",
                "min_version": "1.0.0",
                "reason": "Requires database module support"
            }
        })
    
    # Check for state content
    if "state" in content:
        state_modules = list(content["state"].keys())
        
        # Check for specific modules that might have version requirements
        if "timeline" in state_modules:
            suggestions.append({
                "reason": "Content pack uses timeline module",
                "condition": {
                    "type": "version_range",
                    "min_version": "1.2.0",
                    "reason": "Requires timeline module features"
                }
            })
        
        if "email" in state_modules:
            suggestions.append({
                "reason": "Content pack uses email module",
                "condition": {
                    "type": "version_range",
                    "min_version": "1.1.0",
                    "reason": "Requires email module support"
                }
            })
    
    # Default suggestion if no specific features detected
    if not suggestions:
        suggestions.append({
            "reason": "General IntentVerse compatibility",
            "condition": {
                "type": "version_range",
                "min_version": "1.0.0",
                "reason": "Requires IntentVerse 1.0+ core features"
            }
        })
    
    return suggestions


def interactive_condition_selection(suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Interactive selection of compatibility conditions."""
    
    selected = []
    
    console.print("\n[bold]Select compatibility conditions to add:[/bold]")
    
    for i, suggestion in enumerate(suggestions):
        choice = click.confirm(f"Add: {suggestion['reason']}")
        if choice:
            selected.append(suggestion["condition"])
    
    return selected


def display_versions_table(versions_list: List[str], releases: List[Dict[str, Any]]):
    """Display versions in a table format."""
    
    table = Table(title="Available IntentVerse Versions")
    table.add_column("Version", style="cyan")
    table.add_column("Release Date")
    table.add_column("Type")
    
    # Create lookup for release info
    release_info = {r["tag_name"]: r for r in releases}
    
    for ver in versions_list:
        release = release_info.get(ver, {})
        release_date = release.get("published_at", "Unknown")
        if release_date != "Unknown":
            release_date = release_date.split("T")[0]  # Just the date part
        
        release_type = "Pre-release" if release.get("prerelease") else "Stable"
        
        table.add_row(ver, release_date, release_type)
    
    console.print(table)


def display_batch_results(results: List[Dict[str, Any]]):
    """Display batch validation results."""
    
    table = Table(title="Batch Validation Results")
    table.add_column("File", style="cyan")
    table.add_column("Status")
    table.add_column("Issues")
    table.add_column("Fixed")
    
    valid_count = 0
    
    for result in results:
        path = result["path"]
        valid = result["valid"]
        errors = result["errors"]
        fixed = result.get("fixed", False)
        
        if valid:
            status = "[green]✓ Valid[/green]"
            issues = "-"
            valid_count += 1
        else:
            status = "[red]✗ Invalid[/red]"
            issues = f"{len(errors)} error(s)"
        
        fixed_text = "✓" if fixed else "-"
        
        table.add_row(str(path.name), status, issues, fixed_text)
    
    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {valid_count}/{len(results)} content packs are valid")


if __name__ == "__main__":
    cli()