#!/usr/bin/env python3
"""
Script to generate compatibility reports from test results.

This script processes test results from compatibility testing and generates
human-readable reports and machine-readable compatibility matrices.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import re


def load_test_results(results_dir: Path) -> List[Dict[str, Any]]:
    """
    Load all test result files from the results directory.
    
    Args:
        results_dir: Directory containing test result JSON files
    
    Returns:
        List of test result dictionaries
    """
    results = []
    
    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}", file=sys.stderr)
        return results
    
    # Find all JSON files in the results directory
    for json_file in results_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            # Add file metadata
            result["_metadata"] = {
                "file_path": str(json_file),
                "file_name": json_file.name
            }
            
            results.append(result)
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Skipping invalid JSON file {json_file}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Error loading {json_file}: {e}", file=sys.stderr)
    
    return results


def organize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Organize test results by content pack and version.
    
    Args:
        results: List of test result dictionaries
    
    Returns:
        Organized results structure
    """
    organized = {
        "content_packs": {},
        "versions": set(),
        "summary": {
            "total_tests": len(results),
            "total_content_packs": 0,
            "total_versions": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0
        }
    }
    
    for result in results:
        # Extract content pack info
        content_pack = result.get("content_pack", {})
        pack_name = content_pack.get("name", "Unknown")
        version = result.get("version", "unknown")
        status = result.get("status", "unknown")
        
        # Track versions
        organized["versions"].add(version)
        
        # Initialize content pack entry
        if pack_name not in organized["content_packs"]:
            organized["content_packs"][pack_name] = {
                "name": pack_name,
                "pack_version": content_pack.get("version", "unknown"),
                "compatibility_conditions": content_pack.get("compatibility_conditions", []),
                "test_results": {},
                "summary": {
                    "total_tests": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0
                }
            }
        
        # Add test result
        organized["content_packs"][pack_name]["test_results"][version] = result
        organized["content_packs"][pack_name]["summary"]["total_tests"] += 1
        
        # Update counters
        if status == "passed":
            organized["content_packs"][pack_name]["summary"]["passed"] += 1
            organized["summary"]["passed"] += 1
        elif status == "failed":
            organized["content_packs"][pack_name]["summary"]["failed"] += 1
            organized["summary"]["failed"] += 1
        elif status == "error":
            organized["content_packs"][pack_name]["summary"]["errors"] += 1
            organized["summary"]["errors"] += 1
    
    # Convert versions set to sorted list
    organized["versions"] = sorted(list(organized["versions"]))
    organized["summary"]["total_content_packs"] = len(organized["content_packs"])
    organized["summary"]["total_versions"] = len(organized["versions"])
    
    return organized


def generate_markdown_report(organized_results: Dict[str, Any]) -> str:
    """
    Generate a markdown compatibility report.
    
    Args:
        organized_results: Organized test results
    
    Returns:
        Markdown report string
    """
    report = []
    
    # Header
    report.append("# Content Pack Compatibility Report")
    report.append("")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")
    
    # Summary
    summary = organized_results["summary"]
    report.append("## Summary")
    report.append("")
    report.append(f"- **Total Tests**: {summary['total_tests']}")
    report.append(f"- **Content Packs**: {summary['total_content_packs']}")
    report.append(f"- **IntentVerse Versions**: {summary['total_versions']}")
    report.append(f"- **Passed**: {summary['passed']} ✅")
    report.append(f"- **Failed**: {summary['failed']} ❌")
    report.append(f"- **Errors**: {summary['errors']} 💥")
    report.append("")
    
    # Success rate
    if summary['total_tests'] > 0:
        success_rate = (summary['passed'] / summary['total_tests']) * 100
        report.append(f"**Overall Success Rate**: {success_rate:.1f}%")
        report.append("")
    
    # Compatibility Matrix
    report.append("## Compatibility Matrix")
    report.append("")
    
    versions = organized_results["versions"]
    content_packs = organized_results["content_packs"]
    
    if versions and content_packs:
        # Create table header
        header = "| Content Pack | " + " | ".join(versions) + " |"
        separator = "|" + "|".join([" --- "] * (len(versions) + 1)) + "|"
        
        report.append(header)
        report.append(separator)
        
        # Create table rows
        for pack_name, pack_data in content_packs.items():
            row = f"| **{pack_name}** |"
            
            for version in versions:
                result = pack_data["test_results"].get(version)
                if result:
                    status = result.get("status", "unknown")
                    if status == "passed":
                        cell = " ✅ |"
                    elif status == "failed":
                        cell = " ❌ |"
                    elif status == "error":
                        cell = " 💥 |"
                    else:
                        cell = " ❓ |"
                else:
                    cell = " - |"
                
                row += cell
            
            report.append(row)
    
    report.append("")
    
    # Detailed Results
    report.append("## Detailed Results")
    report.append("")
    
    for pack_name, pack_data in content_packs.items():
        report.append(f"### {pack_name}")
        report.append("")
        
        # Pack info
        report.append(f"- **Version**: {pack_data['pack_version']}")
        
        # Compatibility conditions
        conditions = pack_data.get("compatibility_conditions", [])
        if conditions:
            report.append("- **Compatibility Conditions**:")
            for condition in conditions:
                if condition.get("type") == "version_range":
                    min_ver = condition.get("min_version", "")
                    max_ver = condition.get("max_version", "")
                    reason = condition.get("reason", "")
                    
                    range_str = f"  - Min: {min_ver}"
                    if max_ver:
                        range_str += f", Max: {max_ver}"
                    if reason:
                        range_str += f" ({reason})"
                    
                    report.append(range_str)
        else:
            report.append("- **Compatibility Conditions**: None specified")
        
        report.append("")
        
        # Test results
        pack_summary = pack_data["summary"]
        report.append(f"**Test Summary**: {pack_summary['passed']} passed, {pack_summary['failed']} failed, {pack_summary['errors']} errors")
        report.append("")
        
        # Version-specific results
        for version in versions:
            result = pack_data["test_results"].get(version)
            if result:
                status = result.get("status", "unknown")
                status_icon = {"passed": "✅", "failed": "❌", "error": "💥"}.get(status, "❓")
                
                report.append(f"#### {version} {status_icon}")
                
                # Test details
                tests = result.get("tests", {})
                if tests:
                    for test_name, test_result in tests.items():
                        test_status = test_result.get("status", "unknown")
                        test_icon = {"passed": "✅", "failed": "❌", "error": "💥"}.get(test_status, "❓")
                        duration = test_result.get("duration", 0)
                        
                        report.append(f"- **{test_name}**: {test_icon} ({duration:.2f}s)")
                        
                        # Show error details
                        if test_status in ["failed", "error"] and test_result.get("error"):
                            report.append(f"  - Error: `{test_result['error']}`")
                
                report.append("")
        
        report.append("---")
        report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    report.append("")
    
    # Find content packs with issues
    problematic_packs = []
    for pack_name, pack_data in content_packs.items():
        if pack_data["summary"]["failed"] > 0 or pack_data["summary"]["errors"] > 0:
            problematic_packs.append(pack_name)
    
    if problematic_packs:
        report.append("### Content Packs Needing Attention")
        report.append("")
        for pack_name in problematic_packs:
            pack_data = content_packs[pack_name]
            report.append(f"- **{pack_name}**: {pack_data['summary']['failed']} failures, {pack_data['summary']['errors']} errors")
            
            # Suggest fixes
            conditions = pack_data.get("compatibility_conditions", [])
            if not conditions:
                report.append("  - Consider adding compatibility conditions")
            
            # Check for version-specific patterns
            failed_versions = []
            for version, result in pack_data["test_results"].items():
                if result.get("status") in ["failed", "error"]:
                    failed_versions.append(version)
            
            if failed_versions:
                report.append(f"  - Fails on versions: {', '.join(failed_versions)}")
        
        report.append("")
    
    # General recommendations
    report.append("### General Recommendations")
    report.append("")
    report.append("1. **Add Compatibility Conditions**: All content packs should specify minimum version requirements")
    report.append("2. **Test Regularly**: Run compatibility tests when new IntentVerse versions are released")
    report.append("3. **Update Documentation**: Keep compatibility information up to date")
    report.append("4. **Monitor Failures**: Address compatibility issues promptly")
    report.append("")
    
    return "\n".join(report)


def generate_json_matrix(organized_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a JSON compatibility matrix.
    
    Args:
        organized_results: Organized test results
    
    Returns:
        JSON-serializable compatibility matrix
    """
    matrix = {
        "generated_at": datetime.now().isoformat(),
        "summary": organized_results["summary"],
        "versions": organized_results["versions"],
        "compatibility_matrix": {},
        "detailed_results": {}
    }
    
    # Create compatibility matrix
    for pack_name, pack_data in organized_results["content_packs"].items():
        matrix["compatibility_matrix"][pack_name] = {}
        matrix["detailed_results"][pack_name] = {
            "pack_version": pack_data["pack_version"],
            "compatibility_conditions": pack_data["compatibility_conditions"],
            "summary": pack_data["summary"]
        }
        
        for version in organized_results["versions"]:
            result = pack_data["test_results"].get(version)
            if result:
                matrix["compatibility_matrix"][pack_name][version] = result.get("status", "unknown")
            else:
                matrix["compatibility_matrix"][pack_name][version] = "not_tested"
    
    return matrix


def main():
    parser = argparse.ArgumentParser(
        description="Generate compatibility reports from test results"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
        help="Directory containing test result JSON files"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for markdown report"
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Output file for JSON compatibility matrix"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed processing information"
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Loading test results from {args.results_dir}...")
    
    # Load test results
    results = load_test_results(args.results_dir)
    
    if not results:
        print("❌ No test results found", file=sys.stderr)
        sys.exit(1)
    
    print(f"📊 Found {len(results)} test results")
    
    # Organize results
    if args.verbose:
        print("🔄 Organizing results...")
    
    organized = organize_results(results)
    
    print(f"📋 Processed {organized['summary']['total_content_packs']} content packs across {organized['summary']['total_versions']} versions")
    
    # Generate markdown report
    if args.output:
        if args.verbose:
            print("📝 Generating markdown report...")
        
        markdown_report = generate_markdown_report(organized)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        print(f"✅ Markdown report saved to {args.output}")
    
    # Generate JSON matrix
    if args.output_json:
        if args.verbose:
            print("📊 Generating JSON compatibility matrix...")
        
        json_matrix = generate_json_matrix(organized)
        
        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(json_matrix, f, indent=2)
        
        print(f"✅ JSON matrix saved to {args.output_json}")
    
    # Print summary
    summary = organized["summary"]
    print(f"\n📊 Test Summary:")
    print(f"   ✅ Passed: {summary['passed']}")
    print(f"   ❌ Failed: {summary['failed']}")
    print(f"   💥 Errors: {summary['errors']}")
    
    if summary['total_tests'] > 0:
        success_rate = (summary['passed'] / summary['total_tests']) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Exit with appropriate code
    if summary['failed'] > 0 or summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()