#!/usr/bin/env python3
"""
Script to install specific versions of IntentVerse for compatibility testing.

This script downloads and sets up specific versions of IntentVerse in isolated
environments for testing content pack compatibility.
"""

import argparse
import json
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional
import requests
import zipfile
import os


def download_release(repo: str, version: str, cache_dir: Path) -> Optional[Path]:
    """
    Download a specific release of IntentVerse.
    
    Args:
        repo: GitHub repository in format 'owner/repo'
        version: Version tag to download
        cache_dir: Directory to cache downloads
    
    Returns:
        Path to downloaded and extracted release, or None if failed
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already cached
    cached_path = cache_dir / f"intentverse-{version}"
    if cached_path.exists():
        print(f"📦 Using cached IntentVerse {version} from {cached_path}")
        return cached_path
    
    # Download release
    download_url = f"https://github.com/{repo}/archive/refs/tags/{version}.zip"
    zip_path = cache_dir / f"intentverse-{version}.zip"
    
    print(f"⬇️  Downloading IntentVerse {version} from GitHub...")
    
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"📦 Downloaded {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
        
    except requests.RequestException as e:
        print(f"❌ Error downloading release: {e}", file=sys.stderr)
        return None
    
    # Extract release
    print(f"📂 Extracting release...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(cache_dir)
        
        # Find extracted directory (GitHub creates a directory with repo name and version)
        extracted_dirs = [d for d in cache_dir.iterdir() if d.is_dir() and version.lstrip('v') in d.name]
        
        if not extracted_dirs:
            print(f"❌ Could not find extracted directory", file=sys.stderr)
            return None
        
        extracted_dir = extracted_dirs[0]
        
        # Rename to consistent name
        if extracted_dir != cached_path:
            extracted_dir.rename(cached_path)
        
        # Clean up zip file
        zip_path.unlink()
        
        print(f"✅ Extracted to {cached_path}")
        return cached_path
        
    except Exception as e:
        print(f"❌ Error extracting release: {e}", file=sys.stderr)
        return None


def setup_python_environment(intentverse_path: Path, python_version: str = "3.11") -> bool:
    """
    Set up Python virtual environment for IntentVerse.
    
    Args:
        intentverse_path: Path to IntentVerse installation
        python_version: Python version to use
    
    Returns:
        True if setup successful, False otherwise
    """
    venv_path = intentverse_path / "test_venv"
    
    if venv_path.exists():
        print(f"🐍 Using existing virtual environment at {venv_path}")
        return True
    
    print(f"🐍 Creating Python virtual environment...")
    
    try:
        # Create virtual environment
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True, capture_output=True)
        
        # Get pip path
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
            python_path = venv_path / "Scripts" / "python"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        # Upgrade pip
        subprocess.run([
            str(python_path), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True, capture_output=True)
        
        # Install requirements if they exist
        requirements_files = [
            intentverse_path / "requirements.txt",
            intentverse_path / "core" / "requirements.txt",
            intentverse_path / "mcp" / "requirements.txt"
        ]
        
        for req_file in requirements_files:
            if req_file.exists():
                print(f"📦 Installing requirements from {req_file.name}...")
                subprocess.run([
                    str(pip_path), "install", "-r", str(req_file)
                ], check=True, capture_output=True)
        
        # Install IntentVerse in development mode if setup.py exists
        setup_py = intentverse_path / "setup.py"
        pyproject_toml = intentverse_path / "pyproject.toml"
        
        if setup_py.exists() or pyproject_toml.exists():
            print(f"📦 Installing IntentVerse in development mode...")
            subprocess.run([
                str(pip_path), "install", "-e", str(intentverse_path)
            ], check=True, capture_output=True)
        
        print(f"✅ Python environment ready at {venv_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up Python environment: {e}", file=sys.stderr)
        if e.stdout:
            print(f"stdout: {e.stdout.decode()}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr.decode()}", file=sys.stderr)
        return False


def verify_installation(intentverse_path: Path) -> bool:
    """
    Verify that IntentVerse is properly installed and can be imported.
    
    Args:
        intentverse_path: Path to IntentVerse installation
    
    Returns:
        True if verification successful, False otherwise
    """
    venv_path = intentverse_path / "test_venv"
    
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python"
    else:
        python_path = venv_path / "bin" / "python"
    
    print(f"🔍 Verifying IntentVerse installation...")
    
    # Test basic import
    test_script = """
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from app.content_pack_manager import ContentPackManager
    from app.version_utils import get_app_version
    
    version = get_app_version()
    print(f"IntentVerse version: {version}")
    print("✅ Basic imports successful")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
"""
    
    try:
        # Write test script
        test_file = intentverse_path / "test_import.py"
        test_file.write_text(test_script)
        
        # Run test
        result = subprocess.run([
            str(python_path), str(test_file)
        ], capture_output=True, text=True, cwd=intentverse_path)
        
        # Clean up test file
        test_file.unlink()
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Verification failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Install specific IntentVerse version for compatibility testing"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="IntentVerse version to install (e.g., 'v1.0.0')"
    )
    parser.add_argument(
        "--repo",
        default="your-org/IntentVerse",
        help="GitHub repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path.home() / ".cache" / "intentverse-testing",
        help="Directory to cache downloads"
    )
    parser.add_argument(
        "--python-version",
        default="3.11",
        help="Python version to use"
    )
    parser.add_argument(
        "--force-reinstall",
        action="store_true",
        help="Force reinstallation even if cached version exists"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        default=True,
        help="Verify installation after setup"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Installing IntentVerse {args.version}...")
    
    # Force reinstall if requested
    if args.force_reinstall:
        cached_path = args.cache_dir / f"intentverse-{args.version}"
        if cached_path.exists():
            print(f"🗑️  Removing existing installation...")
            shutil.rmtree(cached_path)
    
    # Download and extract release
    intentverse_path = download_release(args.repo, args.version, args.cache_dir)
    if not intentverse_path:
        sys.exit(1)
    
    # Set up Python environment
    if not setup_python_environment(intentverse_path, args.python_version):
        sys.exit(1)
    
    # Verify installation
    if args.verify:
        if not verify_installation(intentverse_path):
            sys.exit(1)
    
    print(f"✅ IntentVerse {args.version} is ready at {intentverse_path}")
    
    # Output installation info for CI
    install_info = {
        "version": args.version,
        "path": str(intentverse_path),
        "venv_path": str(intentverse_path / "test_venv"),
        "python_path": str(intentverse_path / "test_venv" / ("Scripts" if sys.platform == "win32" else "bin") / "python")
    }
    
    print(f"📋 Installation info:")
    print(json.dumps(install_info, indent=2))


if __name__ == "__main__":
    main()