#!/usr/bin/env python3
"""
Script to update compatibility documentation based on test results.

This script processes compatibility test results and updates documentation
files with current compatibility information.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_compatibility_matrix_doc(matrix_data: Dict[str, Any]) -> str:
    """
    Generate a compatibility matrix documentation file.
    
    Args:
        matrix_data: JSON compatibility matrix data
    
    Returns:
        Markdown content for compatibility matrix documentation
    """
    doc = []
    
    # Header
    doc.append("# Content Pack Compatibility Matrix")
    doc.append("")
    doc.append("This document shows the compatibility status of all content packs across different IntentVerse versions.")
    doc.append("")
    doc.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    doc.append(f"**Generated From**: Automated compatibility testing")
    doc.append("")
    
    # Summary
    summary = matrix_data.get("summary", {})
    doc.append("## Summary")
    doc.append("")
    doc.append(f"- **Total Tests**: {summary.get('total_tests', 0)}")
    doc.append(f"- **Content Packs**: {summary.get('total_content_packs', 0)}")
    doc.append(f"- **IntentVerse Versions**: {summary.get('total_versions', 0)}")
    doc.append("")
    
    if summary.get('total_tests', 0) > 0:
        passed = summary.get('passed', 0)
        total = summary.get('total_tests', 0)
        success_rate = (passed / total) * 100
        doc.append(f"**Overall Success Rate**: {success_rate:.1f}%")
        doc.append("")
    
    # Legend
    doc.append("## Legend")
    doc.append("")
    doc.append("- ✅ **Compatible**: Content pack works correctly with this IntentVerse version")
    doc.append("- ❌ **Incompatible**: Content pack fails compatibility tests")
    doc.append("- 💥 **Error**: Testing encountered errors (may indicate bugs)")
    doc.append("- ❓ **Unknown**: Compatibility status unknown")
    doc.append("- - **Not Tested**: This combination was not tested")
    doc.append("")
    
    # Compatibility Matrix Table
    doc.append("## Compatibility Matrix")
    doc.append("")
    
    versions = matrix_data.get("versions", [])
    compatibility_matrix = matrix_data.get("compatibility_matrix", {})
    
    if versions and compatibility_matrix:
        # Create table header
        header = "| Content Pack | " + " | ".join(f"**{v}**" for v in versions) + " |"
        separator = "|" + "|".join([" :---: "] * (len(versions) + 1)) + "|"
        
        doc.append(header)
        doc.append(separator)
        
        # Create table rows
        for pack_name in sorted(compatibility_matrix.keys()):
            pack_results = compatibility_matrix[pack_name]
            row = f"| **{pack_name}** |"
            
            for version in versions:
                status = pack_results.get(version, "not_tested")
                
                if status == "passed":
                    cell = " ✅ |"
                elif status == "failed":
                    cell = " ❌ |"
                elif status == "error":
                    cell = " 💥 |"
                elif status == "not_tested":
                    cell = " - |"
                else:
                    cell = " ❓ |"
                
                row += cell
            
            doc.append(row)
    
    doc.append("")
    
    # Detailed Information
    doc.append("## Content Pack Details")
    doc.append("")
    
    detailed_results = matrix_data.get("detailed_results", {})
    
    for pack_name in sorted(detailed_results.keys()):
        pack_data = detailed_results[pack_name]
        
        doc.append(f"### {pack_name}")
        doc.append("")
        
        # Basic info
        doc.append(f"- **Version**: {pack_data.get('pack_version', 'unknown')}")
        
        # Compatibility conditions
        conditions = pack_data.get("compatibility_conditions", [])
        if conditions:
            doc.append("- **Compatibility Requirements**:")
            for condition in conditions:
                if condition.get("type") == "version_range":
                    min_ver = condition.get("min_version", "")
                    max_ver = condition.get("max_version", "")
                    reason = condition.get("reason", "")
                    
                    req_str = f"  - Minimum IntentVerse version: {min_ver}"
                    if max_ver:
                        req_str += f", Maximum: {max_ver}"
                    if reason:
                        req_str += f" ({reason})"
                    
                    doc.append(req_str)
        else:
            doc.append("- **Compatibility Requirements**: None specified (universal compatibility)")
        
        # Test summary
        pack_summary = pack_data.get("summary", {})
        total_tests = pack_summary.get("total_tests", 0)
        passed = pack_summary.get("passed", 0)
        failed = pack_summary.get("failed", 0)
        errors = pack_summary.get("errors", 0)
        
        if total_tests > 0:
            success_rate = (passed / total_tests) * 100
            doc.append(f"- **Test Results**: {passed}/{total_tests} passed ({success_rate:.1f}% success rate)")
            
            if failed > 0 or errors > 0:
                issues = []
                if failed > 0:
                    issues.append(f"{failed} failed")
                if errors > 0:
                    issues.append(f"{errors} errors")
                doc.append(f"- **Issues**: {', '.join(issues)}")
        
        doc.append("")
    
    # Usage Instructions
    doc.append("## How to Use This Information")
    doc.append("")
    doc.append("### For Content Pack Users")
    doc.append("")
    doc.append("1. **Check Compatibility**: Before installing a content pack, check its compatibility with your IntentVerse version")
    doc.append("2. **Understand Symbols**: Use the legend above to understand the compatibility status")
    doc.append("3. **Report Issues**: If you encounter problems with a content pack marked as compatible, please report it")
    doc.append("")
    doc.append("### For Content Pack Authors")
    doc.append("")
    doc.append("1. **Review Results**: Check your content pack's compatibility across versions")
    doc.append("2. **Update Requirements**: Add or update compatibility conditions based on test results")
    doc.append("3. **Fix Issues**: Address any failed tests or errors")
    doc.append("4. **Test Locally**: Use the compatibility testing tools to verify fixes")
    doc.append("")
    doc.append("### For Maintainers")
    doc.append("")
    doc.append("1. **Monitor Trends**: Watch for patterns in compatibility issues")
    doc.append("2. **Update Documentation**: Keep compatibility guides up to date")
    doc.append("3. **Coordinate Fixes**: Help content pack authors resolve compatibility issues")
    doc.append("")
    
    # Automated Testing Info
    doc.append("## Automated Testing")
    doc.append("")
    doc.append("This compatibility matrix is generated automatically by our CI/CD pipeline:")
    doc.append("")
    doc.append("- **Frequency**: Tests run weekly and on content pack changes")
    doc.append("- **Coverage**: All content packs are tested against supported IntentVerse versions")
    doc.append("- **Test Types**: Validation, loading, database operations, state management")
    doc.append("- **Results**: Detailed test results are available in the CI artifacts")
    doc.append("")
    doc.append("For more information about compatibility testing, see:")
    doc.append("- [Compatibility Guide](COMPATIBILITY-GUIDE.md)")
    doc.append("- [Contributing Guidelines](../CONTRIBUTING.md)")
    doc.append("")
    
    # Footer
    doc.append("---")
    doc.append("")
    doc.append("*This document is automatically generated. Do not edit manually.*")
    doc.append("")
    
    return "\n".join(doc)


def update_readme_compatibility_section(readme_path: Path, matrix_data: Dict[str, Any]) -> bool:
    """
    Update the compatibility section in README.md.
    
    Args:
        readme_path: Path to README.md file
        matrix_data: Compatibility matrix data
    
    Returns:
        True if updated successfully, False otherwise
    """
    if not readme_path.exists():
        print(f"⚠️  README.md not found at {readme_path}")
        return False
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate compatibility summary
        summary = matrix_data.get("summary", {})
        total_packs = summary.get("total_content_packs", 0)
        total_versions = summary.get("total_versions", 0)
        
        if summary.get('total_tests', 0) > 0:
            passed = summary.get('passed', 0)
            total = summary.get('total_tests', 0)
            success_rate = (passed / total) * 100
            
            compatibility_section = f"""
## Compatibility Status

- **Content Packs**: {total_packs}
- **Tested Versions**: {total_versions}
- **Overall Success Rate**: {success_rate:.1f}%

For detailed compatibility information, see the [Compatibility Matrix](docs/COMPATIBILITY-MATRIX.md).

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        else:
            compatibility_section = f"""
## Compatibility Status

- **Content Packs**: {total_packs}
- **Tested Versions**: {total_versions}

For detailed compatibility information, see the [Compatibility Matrix](docs/COMPATIBILITY-MATRIX.md).

*Last updated: {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        # Try to replace existing compatibility section
        import re
        
        # Look for existing compatibility section
        pattern = r'## Compatibility Status.*?(?=##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Replace existing section
            new_content = content[:match.start()] + compatibility_section.strip() + content[match.end():]
        else:
            # Add new section before "Documentation" section if it exists
            doc_pattern = r'## Documentation'
            doc_match = re.search(doc_pattern, content)
            
            if doc_match:
                new_content = content[:doc_match.start()] + compatibility_section + "\n" + content[doc_match.start():]
            else:
                # Add at the end
                new_content = content + "\n" + compatibility_section
        
        # Write updated content
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating README.md: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Update compatibility documentation from test results"
    )
    parser.add_argument(
        "--matrix",
        type=Path,
        required=True,
        help="JSON compatibility matrix file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for compatibility matrix documentation"
    )
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Update README.md with compatibility summary"
    )
    parser.add_argument(
        "--readme-path",
        type=Path,
        default=Path("README.md"),
        help="Path to README.md file"
    )
    
    args = parser.parse_args()
    
    # Load compatibility matrix
    try:
        with open(args.matrix, 'r', encoding='utf-8') as f:
            matrix_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading compatibility matrix: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📊 Loaded compatibility matrix with {matrix_data.get('summary', {}).get('total_tests', 0)} test results")
    
    # Generate compatibility matrix documentation
    if args.output:
        print(f"📝 Generating compatibility matrix documentation...")
        
        doc_content = generate_compatibility_matrix_doc(matrix_data)
        
        # Ensure output directory exists
        args.output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"✅ Compatibility matrix documentation saved to {args.output}")
    
    # Update README.md
    if args.update_readme:
        print(f"📝 Updating README.md compatibility section...")
        
        if update_readme_compatibility_section(args.readme_path, matrix_data):
            print(f"✅ README.md updated successfully")
        else:
            print(f"❌ Failed to update README.md")
            sys.exit(1)
    
    print("✅ Documentation update complete")


if __name__ == "__main__":
    main()