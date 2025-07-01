# Content Pack Developer Tools Guide

This guide covers the developer tools available for creating, validating, and testing content packs for IntentVerse.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Main CLI Tool (cpdev)](#main-cli-tool-cpdev)
- [Standalone Tools](#standalone-tools)
- [Workflows](#workflows)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The developer tools provide a comprehensive suite for content pack development:

- **Template Generation**: Create new content packs from templates
- **Validation**: Check content pack format and compatibility
- **Compatibility Testing**: Test against specific IntentVerse versions
- **Batch Operations**: Process multiple content packs at once
- **Version Management**: Check available IntentVerse versions

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for fetching version information)

### Install Dependencies

```bash
cd IntentVerse-Content
pip install -r tools/requirements.txt
```

### Make Tools Executable

```bash
chmod +x tools/*.py
```

## Main CLI Tool (cpdev)

The `cpdev.py` tool is the main command-line interface for content pack development.

### Basic Usage

```bash
python tools/cpdev.py --help
```

### Commands

#### Create a New Content Pack

```bash
# Basic content pack
python tools/cpdev.py create --name "My Content Pack" --output my-pack.json

# With additional metadata
python tools/cpdev.py create \
  --name "E-commerce Demo" \
  --description "Demonstration of e-commerce functionality" \
  --author "Your Name" \
  --category "demonstration" \
  --tags "ecommerce,demo,tutorial" \
  --min-version "1.0.0" \
  --template "full"
```

**Template Types:**
- `basic`: Minimal content pack with metadata only
- `database`: Includes database schema and sample data
- `state`: Includes state management examples
- `timeline`: Includes timeline events (requires v1.2.0+)
- `full`: Comprehensive template with all features

#### Validate Content Packs

```bash
# Basic validation
python tools/cpdev.py validate my-pack.json

# Verbose output
python tools/cpdev.py validate my-pack.json --verbose

# Auto-fix common issues
python tools/cpdev.py validate my-pack.json --fix
```

#### Test Compatibility

```bash
# Test against specific version
python tools/cpdev.py test my-pack.json --version 1.0.0

# Test against latest version
python tools/cpdev.py test my-pack.json --latest

# Test against all available versions
python tools/cpdev.py test my-pack.json --all-versions

# Verbose test output
python tools/cpdev.py test my-pack.json --version 1.0.0 --verbose
```

#### Suggest Compatibility Conditions

```bash
# Analyze and suggest compatibility conditions
python tools/cpdev.py suggest-compatibility my-pack.json

# Interactive mode
python tools/cpdev.py suggest-compatibility my-pack.json --interactive

# Save to new file
python tools/cpdev.py suggest-compatibility my-pack.json --output my-pack-updated.json
```

#### List Available Versions

```bash
# Table format (default)
python tools/cpdev.py versions

# JSON format
python tools/cpdev.py versions --format json

# Simple list
python tools/cpdev.py versions --format list
```

#### Batch Validation

```bash
# Validate all content packs in directory
python tools/cpdev.py batch-validate content-packs/

# Recursive search
python tools/cpdev.py batch-validate content-packs/ --recursive

# Auto-fix issues
python tools/cpdev.py batch-validate content-packs/ --fix
```

## Standalone Tools

### validate.py

Standalone validation tool for simple validation tasks.

```bash
# Basic validation
python tools/validate.py my-pack.json

# Verbose output
python tools/validate.py my-pack.json --verbose

# JSON output
python tools/validate.py my-pack.json --json

# Quiet mode (errors only)
python tools/validate.py my-pack.json --quiet
```

### test-compatibility.py

Standalone compatibility testing tool.

```bash
# Test compatibility
python tools/test-compatibility.py my-pack.json --version 1.0.0

# JSON output
python tools/test-compatibility.py my-pack.json --version 1.0.0 --json

# Verbose output
python tools/test-compatibility.py my-pack.json --version 1.0.0 --verbose

# Quiet mode (status only)
python tools/test-compatibility.py my-pack.json --version 1.0.0 --quiet
```

### generate-template.py

Standalone template generator.

```bash
# Basic template
python tools/generate-template.py --name "My Pack" --output my-pack.json

# Database template
python tools/generate-template.py \
  --name "Database Demo" \
  --template database \
  --description "Database functionality demo" \
  --author "Your Name" \
  --category "demonstration"

# Full template with all options
python tools/generate-template.py \
  --name "Complete Example" \
  --template full \
  --description "Complete content pack example" \
  --author "Your Name" \
  --category "example" \
  --tags "example,tutorial,complete" \
  --min-version "1.2.0" \
  --license "MIT" \
  --homepage "https://example.com" \
  --overwrite
```

## Workflows

### Creating a New Content Pack

1. **Generate Template**
   ```bash
   python tools/cpdev.py create --name "My Pack" --template database
   ```

2. **Edit Content**
   - Open the generated JSON file
   - Customize metadata, database, state, etc.

3. **Validate**
   ```bash
   python tools/cpdev.py validate my-pack.json --verbose
   ```

4. **Test Compatibility**
   ```bash
   python tools/cpdev.py test my-pack.json --version 1.0.0
   ```

5. **Suggest Improvements**
   ```bash
   python tools/cpdev.py suggest-compatibility my-pack.json --interactive
   ```

### Updating Existing Content Packs

1. **Validate Current State**
   ```bash
   python tools/cpdev.py validate existing-pack.json
   ```

2. **Test Against New Versions**
   ```bash
   python tools/cpdev.py test existing-pack.json --all-versions
   ```

3. **Update Compatibility Conditions**
   ```bash
   python tools/cpdev.py suggest-compatibility existing-pack.json --interactive
   ```

4. **Re-validate**
   ```bash
   python tools/cpdev.py validate existing-pack.json
   ```

### Batch Processing

1. **Validate All Packs**
   ```bash
   python tools/cpdev.py batch-validate content-packs/ --recursive
   ```

2. **Fix Common Issues**
   ```bash
   python tools/cpdev.py batch-validate content-packs/ --fix
   ```

3. **Test All Packs**
   ```bash
   for pack in content-packs/*/*.json; do
     echo "Testing $pack"
     python tools/cpdev.py test "$pack" --latest
   done
   ```

## Best Practices

### Content Pack Development

1. **Start with Templates**
   - Use appropriate templates for your use case
   - Templates include proper structure and compatibility conditions

2. **Validate Early and Often**
   - Validate after each major change
   - Use `--verbose` to understand validation details

3. **Test Compatibility**
   - Test against minimum required version
   - Test against latest stable version
   - Use `--all-versions` for comprehensive testing

4. **Use Meaningful Names**
   - Choose descriptive content pack names
   - Use consistent naming conventions

5. **Document Compatibility**
   - Always include compatibility conditions
   - Provide clear reasons for version requirements

### Tool Usage

1. **Use the Right Tool**
   - Use `cpdev.py` for comprehensive workflows
   - Use standalone tools for simple tasks or scripting

2. **Leverage Automation**
   - Use batch operations for multiple content packs
   - Integrate tools into your development workflow

3. **Check Versions Regularly**
   - Use `cpdev versions` to stay updated
   - Test against new IntentVerse releases

### Error Handling

1. **Read Error Messages**
   - Validation errors provide specific guidance
   - Use `--verbose` for detailed information

2. **Use Auto-Fix Carefully**
   - Review changes made by `--fix`
   - Keep backups of original files

3. **Test After Changes**
   - Always validate after making changes
   - Test compatibility after updates

## Troubleshooting

### Common Issues

#### "Invalid JSON" Error

```bash
# Check JSON syntax
python -m json.tool my-pack.json
```

**Solution**: Fix JSON syntax errors (missing commas, quotes, etc.)

#### "Missing min_version" Error

```bash
# Add compatibility conditions
python tools/cpdev.py suggest-compatibility my-pack.json
```

**Solution**: Add proper compatibility conditions to metadata

#### "Content pack validation failed"

```bash
# Get detailed validation info
python tools/cpdev.py validate my-pack.json --verbose
```

**Solution**: Address specific validation errors shown

#### "Version X.Y.Z not found"

```bash
# Check available versions
python tools/cpdev.py versions
```

**Solution**: Use a valid version from the available list

### Tool-Specific Issues

#### cpdev.py Import Errors

**Problem**: Module import errors when running cpdev.py

**Solution**: 
```bash
# Ensure you're in the right directory
cd IntentVerse-Content

# Install dependencies
pip install -r tools/requirements.txt
```

#### Network Errors with Version Fetching

**Problem**: Cannot fetch IntentVerse versions

**Solution**:
```bash
# Check internet connection
# Use specific version instead of --all-versions
python tools/cpdev.py test my-pack.json --version 1.0.0
```

#### Permission Errors

**Problem**: Cannot write output files

**Solution**:
```bash
# Make tools executable
chmod +x tools/*.py

# Check file permissions
ls -la my-pack.json
```

### Getting Help

1. **Tool Help**
   ```bash
   python tools/cpdev.py --help
   python tools/cpdev.py COMMAND --help
   ```

2. **Validation Details**
   ```bash
   python tools/cpdev.py validate my-pack.json --verbose
   ```

3. **Compatibility Analysis**
   ```bash
   python tools/cpdev.py test my-pack.json --version 1.0.0 --verbose
   ```

4. **Community Support**
   - Check the [Compatibility Guide](COMPATIBILITY-GUIDE.md)
   - Review [Contributing Guidelines](../CONTRIBUTING.md)
   - Open an issue on GitHub

## Advanced Usage

### Scripting with Tools

```bash
#!/bin/bash
# Example script for content pack CI

for pack in content-packs/*/*.json; do
  echo "Processing $pack"
  
  # Validate
  if ! python tools/validate.py "$pack" --quiet; then
    echo "❌ Validation failed for $pack"
    exit 1
  fi
  
  # Test compatibility
  if ! python tools/test-compatibility.py "$pack" --version 1.0.0 --quiet; then
    echo "❌ Compatibility test failed for $pack"
    exit 1
  fi
  
  echo "✅ $pack passed all checks"
done
```

### Custom Templates

You can modify the template generators in `generate-template.py` to create custom templates for your specific use cases.

### Integration with IDEs

Most tools support JSON output for integration with IDEs and other tools:

```bash
# Get validation results as JSON
python tools/validate.py my-pack.json --json | jq '.errors[]'

# Get compatibility results as JSON
python tools/test-compatibility.py my-pack.json --version 1.0.0 --json | jq '.compatible'
```

---

For more information, see:
- [Compatibility Guide](COMPATIBILITY-GUIDE.md)
- [Content Pack Schema](../SCHEMA.md)
- [Contributing Guidelines](../CONTRIBUTING.md)