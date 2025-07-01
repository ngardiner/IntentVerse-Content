# Content Pack Developer Tools

This directory contains command-line tools to help content pack authors create, validate, and test their content packs.

## Available Tools

### Core Tools

- **`cpdev.py`** - Main CLI tool with multiple commands
- **`validate.py`** - Standalone validation tool
- **`test-compatibility.py`** - Local compatibility testing
- **`generate-template.py`** - Content pack template generator

### Usage

```bash
# Main CLI tool
python tools/cpdev.py --help

# Individual tools
python tools/validate.py my-content-pack.json
python tools/test-compatibility.py my-content-pack.json --version 1.0.0
python tools/generate-template.py --name "My Pack" --output my-pack.json
```

## Installation

```bash
# Install dependencies
pip install -r tools/requirements.txt
```

## Quick Start

1. **Create a new content pack:**
   ```bash
   python tools/cpdev.py create --name "My Content Pack" --output my-pack.json
   ```

2. **Validate your content pack:**
   ```bash
   python tools/cpdev.py validate my-pack.json
   ```

3. **Test compatibility:**
   ```bash
   python tools/cpdev.py test my-pack.json --version 1.0.0
   ```

4. **Generate compatibility conditions:**
   ```bash
   python tools/cpdev.py suggest-compatibility my-pack.json
   ```

## Documentation

For detailed documentation, see:
- **[Developer Tools Guide](../docs/DEVELOPER-TOOLS.md)** - Complete guide to using the developer tools
- **[Compatibility Guide](../docs/COMPATIBILITY-GUIDE.md)** - Understanding compatibility conditions
- **[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute content packs

## Examples

### Create and Test a Content Pack

```bash
# 1. Create a new content pack
python tools/cpdev.py create --name "My Demo" --template database --author "Your Name"

# 2. Validate the content pack
python tools/cpdev.py validate my-demo.json --verbose

# 3. Test compatibility
python tools/cpdev.py test my-demo.json --version 1.0.0

# 4. Get compatibility suggestions
python tools/cpdev.py suggest-compatibility my-demo.json --interactive
```

### Batch Operations

```bash
# Validate all content packs in a directory
python tools/cpdev.py batch-validate content-packs/ --recursive --fix

# Check available IntentVerse versions
python tools/cpdev.py versions --format table
```

### Scripting and Automation

```bash
# Use standalone tools for scripting
python tools/validate.py my-pack.json --json > validation-results.json
python tools/test-compatibility.py my-pack.json --version 1.0.0 --quiet && echo "Compatible"
```