#!/usr/bin/env python3
"""
Script to test content pack compatibility with specific IntentVerse versions.

This script loads a content pack into a specific version of IntentVerse and
performs various tests to ensure compatibility.
"""

import argparse
import json
import sys
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback


class CompatibilityTester:
    """Main class for running compatibility tests."""
    
    def __init__(self, intentverse_version: str, cache_dir: Path):
        self.intentverse_version = intentverse_version
        self.cache_dir = cache_dir
        self.intentverse_path = cache_dir / f"intentverse-{intentverse_version}"
        self.test_results = {
            "version": intentverse_version,
            "timestamp": time.time(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
    
    def get_python_path(self) -> Path:
        """Get path to Python executable in the virtual environment."""
        venv_path = self.intentverse_path / "test_venv"
        if sys.platform == "win32":
            return venv_path / "Scripts" / "python"
        else:
            return venv_path / "bin" / "python"
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """
        Run a single test and record results.
        
        Args:
            test_name: Name of the test
            test_func: Function to run
            *args, **kwargs: Arguments for test function
        
        Returns:
            True if test passed, False otherwise
        """
        print(f"🧪 Running test: {test_name}")
        
        test_result = {
            "name": test_name,
            "status": "unknown",
            "duration": 0,
            "error": None,
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            test_result["status"] = "passed" if result else "failed"
            test_result["details"] = result if isinstance(result, dict) else {"result": result}
            
            if result:
                print(f"   ✅ {test_name} passed")
                self.test_results["summary"]["passed"] += 1
            else:
                print(f"   ❌ {test_name} failed")
                self.test_results["summary"]["failed"] += 1
                
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
            test_result["traceback"] = traceback.format_exc()
            print(f"   💥 {test_name} error: {e}")
            self.test_results["summary"]["errors"] += 1
        
        test_result["duration"] = time.time() - start_time
        self.test_results["tests"][test_name] = test_result
        self.test_results["summary"]["total_tests"] += 1
        
        return test_result["status"] == "passed"
    
    def test_basic_import(self) -> bool:
        """Test that IntentVerse can be imported without errors."""
        test_script = """
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.version_utils import get_app_version
    from app.state_manager import StateManager
    from app.module_loader import ModuleLoader
    
    print("✅ All imports successful")
    print(f"Version: {get_app_version()}")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
"""
        
        return self._run_python_script(test_script, "basic_import")
    
    def test_content_pack_validation(self, content_pack_path: Path) -> bool:
        """Test that the content pack passes validation."""
        if not content_pack_path.exists():
            return False
        
        test_script = f"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.state_manager import StateManager
    from app.module_loader import ModuleLoader
    
    # Create mock dependencies
    state_manager = StateManager()
    module_loader = ModuleLoader(state_manager)
    
    # Create content pack manager
    cpm = ContentPackManager(state_manager, module_loader)
    
    # Load and validate content pack
    with open(r"{content_pack_path}", 'r', encoding='utf-8') as f:
        content_pack = json.load(f)
    
    # Validate content pack
    validation_result = cpm.validate_content_pack_detailed(content_pack)
    
    if validation_result["is_valid"]:
        print("✅ Content pack validation passed")
        print(f"Summary: {{validation_result['summary']}}")
    else:
        print("❌ Content pack validation failed")
        print(f"Errors: {{validation_result['errors']}}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Validation test failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        return self._run_python_script(test_script, "content_pack_validation")
    
    def test_compatibility_checking(self, content_pack_path: Path) -> bool:
        """Test that compatibility checking works correctly."""
        test_script = f"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.state_manager import StateManager
    from app.module_loader import ModuleLoader
    from app.version_utils import get_app_version
    
    # Create mock dependencies
    state_manager = StateManager()
    module_loader = ModuleLoader(state_manager)
    
    # Create content pack manager
    cpm = ContentPackManager(state_manager, module_loader)
    
    # Load content pack
    with open(r"{content_pack_path}", 'r', encoding='utf-8') as f:
        content_pack = json.load(f)
    
    # Test compatibility checking
    is_compatible = cpm._is_pack_compatible(content_pack)
    app_version = get_app_version()
    
    print(f"App version: {{app_version}}")
    print(f"Content pack compatibility: {{is_compatible}}")
    
    if is_compatible:
        print("✅ Content pack is compatible")
    else:
        reason = cpm._get_incompatibility_reason(content_pack)
        print(f"❌ Content pack is incompatible: {{reason}}")
        # This is expected for some tests, so don't fail
    
except Exception as e:
    print(f"❌ Compatibility test failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        return self._run_python_script(test_script, "compatibility_checking")
    
    def test_content_pack_loading(self, content_pack_path: Path) -> bool:
        """Test that the content pack can be loaded without errors."""
        test_script = f"""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.state_manager import StateManager
    from app.module_loader import ModuleLoader
    
    # Create mock dependencies
    state_manager = StateManager()
    module_loader = ModuleLoader(state_manager)
    
    # Create content pack manager
    cpm = ContentPackManager(state_manager, module_loader)
    
    # Try to load the content pack
    success = cpm.load_content_pack(Path(r"{content_pack_path}"))
    
    if success:
        print("✅ Content pack loaded successfully")
        loaded_packs = cpm.get_loaded_packs_info()
        print(f"Loaded packs: {{len(loaded_packs)}}")
    else:
        print("❌ Content pack failed to load")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Loading test failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        return self._run_python_script(test_script, "content_pack_loading")
    
    def test_database_operations(self, content_pack_path: Path) -> bool:
        """Test database operations if the content pack has database content."""
        test_script = f"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.state_manager import StateManager
    from app.module_loader import ModuleLoader
    
    # Load content pack to check if it has database content
    with open(r"{content_pack_path}", 'r', encoding='utf-8') as f:
        content_pack = json.load(f)
    
    if not content_pack.get("database"):
        print("ℹ️  No database content to test")
        sys.exit(0)
    
    # Create mock dependencies
    state_manager = StateManager()
    module_loader = ModuleLoader(state_manager)
    
    # Create content pack manager
    cpm = ContentPackManager(state_manager, module_loader)
    
    # Test database operations
    database_statements = content_pack["database"]
    print(f"Testing {{len(database_statements)}} database statements")
    
    # Basic syntax check for SQL statements
    for i, stmt in enumerate(database_statements):
        if not isinstance(stmt, str) or not stmt.strip():
            print(f"❌ Invalid statement {{i+1}}: empty or not string")
            sys.exit(1)
        
        # Check for basic SQL keywords
        stmt_upper = stmt.strip().upper()
        if not any(stmt_upper.startswith(kw) for kw in ['CREATE', 'INSERT', 'UPDATE', 'DELETE', 'ALTER', 'DROP']):
            print(f"⚠️  Statement {{i+1}} doesn't start with recognized SQL keyword")
    
    print("✅ Database statements appear valid")
    
except Exception as e:
    print(f"❌ Database test failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        return self._run_python_script(test_script, "database_operations")
    
    def test_state_operations(self, content_pack_path: Path) -> bool:
        """Test state operations if the content pack has state content."""
        test_script = f"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.state_manager import StateManager
    from app.module_loader import ModuleLoader
    
    # Load content pack to check if it has state content
    with open(r"{content_pack_path}", 'r', encoding='utf-8') as f:
        content_pack = json.load(f)
    
    if not content_pack.get("state"):
        print("ℹ️  No state content to test")
        sys.exit(0)
    
    # Create mock dependencies
    state_manager = StateManager()
    module_loader = ModuleLoader(state_manager)
    
    # Create content pack manager
    cpm = ContentPackManager(state_manager, module_loader)
    
    # Test state operations
    state_content = content_pack["state"]
    print(f"Testing state modules: {{list(state_content.keys())}}")
    
    # Test state merging
    cpm._merge_state_content(state_content)
    
    # Verify state was set
    for module_name in state_content.keys():
        if module_name != "database":  # Database is handled separately
            module_state = state_manager.get(module_name)
            if module_state is None:
                print(f"❌ State for module {{module_name}} was not set")
                sys.exit(1)
    
    print("✅ State operations successful")
    
except Exception as e:
    print(f"❌ State test failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        
        return self._run_python_script(test_script, "state_operations")
    
    def _run_python_script(self, script: str, test_name: str) -> bool:
        """
        Run a Python script in the IntentVerse environment.
        
        Args:
            script: Python script to run
            test_name: Name of the test for logging
        
        Returns:
            True if script ran successfully, False otherwise
        """
        python_path = self.get_python_path()
        
        if not python_path.exists():
            print(f"❌ Python executable not found: {python_path}")
            return False
        
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Run script
            result = subprocess.run([
                str(python_path), script_path
            ], capture_output=True, text=True, cwd=self.intentverse_path, timeout=60)
            
            # Store output in test results
            self.test_results["tests"][test_name] = {
                **self.test_results["tests"].get(test_name, {}),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
            if result.returncode == 0:
                return True
            else:
                print(f"❌ Script failed with return code {result.returncode}")
                if result.stderr:
                    print(f"stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Script timed out after 60 seconds")
            return False
        except Exception as e:
            print(f"❌ Error running script: {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                Path(script_path).unlink()
            except:
                pass
    
    def run_all_tests(self, content_pack_path: Path) -> Dict[str, Any]:
        """
        Run all compatibility tests for a content pack.
        
        Args:
            content_pack_path: Path to content pack JSON file
        
        Returns:
            Test results dictionary
        """
        print(f"🚀 Starting compatibility tests for {content_pack_path.name}")
        print(f"📦 IntentVerse version: {self.intentverse_version}")
        
        # Load content pack metadata
        try:
            with open(content_pack_path, 'r', encoding='utf-8') as f:
                content_pack = json.load(f)
            
            metadata = content_pack.get("metadata", {})
            self.test_results["content_pack"] = {
                "name": metadata.get("name", content_pack_path.stem),
                "version": metadata.get("version", "unknown"),
                "path": str(content_pack_path),
                "compatibility_conditions": metadata.get("compatibility_conditions", [])
            }
            
        except Exception as e:
            print(f"❌ Error loading content pack: {e}")
            self.test_results["content_pack"] = {
                "name": content_pack_path.stem,
                "error": str(e)
            }
            return self.test_results
        
        # Run tests
        self.run_test("basic_import", self.test_basic_import)
        self.run_test("content_pack_validation", self.test_content_pack_validation, content_pack_path)
        self.run_test("compatibility_checking", self.test_compatibility_checking, content_pack_path)
        self.run_test("content_pack_loading", self.test_content_pack_loading, content_pack_path)
        self.run_test("database_operations", self.test_database_operations, content_pack_path)
        self.run_test("state_operations", self.test_state_operations, content_pack_path)
        
        # Calculate final status
        if self.test_results["summary"]["errors"] > 0:
            self.test_results["status"] = "error"
        elif self.test_results["summary"]["failed"] > 0:
            self.test_results["status"] = "failed"
        else:
            self.test_results["status"] = "passed"
        
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Passed: {self.test_results['summary']['passed']}")
        print(f"   ❌ Failed: {self.test_results['summary']['failed']}")
        print(f"   💥 Errors: {self.test_results['summary']['errors']}")
        print(f"   📋 Status: {self.test_results['status']}")
        
        return self.test_results


def main():
    parser = argparse.ArgumentParser(
        description="Test content pack compatibility with IntentVerse"
    )
    parser.add_argument(
        "--content-pack",
        type=Path,
        required=True,
        help="Path to content pack JSON file"
    )
    parser.add_argument(
        "--intentverse-version",
        required=True,
        help="IntentVerse version to test against"
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path.home() / ".cache" / "intentverse-testing",
        help="Directory with cached IntentVerse installations"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save test results"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.content_pack.exists():
        print(f"❌ Content pack not found: {args.content_pack}", file=sys.stderr)
        sys.exit(1)
    
    intentverse_path = args.cache_dir / f"intentverse-{args.intentverse_version}"
    if not intentverse_path.exists():
        print(f"❌ IntentVerse {args.intentverse_version} not found at {intentverse_path}", file=sys.stderr)
        print("Run install-intentverse.py first", file=sys.stderr)
        sys.exit(1)
    
    # Create tester and run tests
    tester = CompatibilityTester(args.intentverse_version, args.cache_dir)
    results = tester.run_all_tests(args.content_pack)
    
    # Save results
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename
        content_pack_name = results["content_pack"]["name"].replace(" ", "-").replace("/", "-")
        results_file = args.output_dir / f"{content_pack_name}-{args.intentverse_version}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to {results_file}")
    
    # Output results for CI
    if args.verbose:
        print(f"\n📋 Full Results:")
        print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    if results["status"] == "passed":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()