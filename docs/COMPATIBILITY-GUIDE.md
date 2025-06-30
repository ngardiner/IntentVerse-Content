# Content Pack Compatibility Guide

This guide explains how to use compatibility conditions in your content packs to ensure they work correctly across different versions of IntentVerse.

## Table of Contents

- [Overview](#overview)
- [Why Compatibility Matters](#why-compatibility-matters)
- [Compatibility Conditions](#compatibility-conditions)
- [Version Specification](#version-specification)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Testing Compatibility](#testing-compatibility)
- [Troubleshooting](#troubleshooting)

## Overview

Starting with IntentVerse v1.0.0, content packs can specify compatibility requirements using the `compatibility_conditions` array in their metadata. This ensures that:

- Content packs only load on compatible IntentVerse versions
- Users see clear error messages for incompatible content
- The ecosystem remains stable as new features are added

## Why Compatibility Matters

As IntentVerse evolves, new features are added and APIs may change. Content packs that rely on specific features or APIs need to declare their requirements to prevent:

- **Runtime crashes** when loading incompatible content
- **Silent failures** where content doesn't work as expected
- **Poor user experience** with unclear error messages
- **Data corruption** from incompatible database schemas

## Compatibility Conditions

### Basic Structure

Add a `compatibility_conditions` array to your content pack metadata:

```json
{
  "metadata": {
    "name": "My Content Pack",
    "version": "1.0.0",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.0.0",
        "reason": "Requires v1.0+ database and state management features"
      }
    ]
  }
}
```

### Compatibility Condition Types

#### 1. Version Range (`version_range`)

The most common type, specifying minimum and/or maximum IntentVerse versions:

```json
{
  "type": "version_range",
  "min_version": "1.0.0",
  "max_version": "2.0.0",
  "reason": "Uses filesystem API that changed in v2.1"
}
```

**Fields:**
- `type`: Must be `"version_range"`
- `min_version`: Minimum required IntentVerse version (inclusive)
- `max_version`: Maximum supported IntentVerse version (inclusive, optional)
- `reason`: Human-readable explanation of why this restriction exists

#### 2. Future Extension Points

The compatibility system is designed to support additional condition types in the future, such as:
- Feature-based requirements
- Module-specific version requirements
- Platform-specific conditions

## Version Specification

### Semantic Versioning

IntentVerse follows [Semantic Versioning](https://semver.org/) (semver):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **MAJOR**: Breaking changes that may affect content packs
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Comparison Rules

- `min_version` is **inclusive**: `"min_version": "1.0.0"` allows 1.0.0 and higher
- `max_version` is **inclusive**: `"max_version": "2.0.0"` allows up to and including 2.0.0
- Versions are compared using semantic versioning rules

### Common Version Patterns

```json
// Requires exactly v1.0.0 or higher (no upper limit)
{
  "type": "version_range",
  "min_version": "1.0.0",
  "reason": "Requires v1.0+ core features"
}

// Compatible with v1.x only (before v2.0 breaking changes)
{
  "type": "version_range",
  "min_version": "1.0.0",
  "max_version": "1.999.999",
  "reason": "Uses v1.x API that changed in v2.0"
}

// Requires specific feature introduced in v1.2.0
{
  "type": "version_range",
  "min_version": "1.2.0",
  "reason": "Requires timeline module introduced in v1.2.0"
}
```

## Best Practices

### 1. Always Specify Minimum Version

**DO:**
```json
"compatibility_conditions": [
  {
    "type": "version_range",
    "min_version": "1.0.0",
    "reason": "Requires v1.0+ database features"
  }
]
```

**DON'T:**
```json
"compatibility_conditions": []  // Empty = works with all versions (risky)
```

### 2. Be Conservative with Maximum Versions

Only specify `max_version` if you know the content pack will break:

```json
// Good: Known breaking change
{
  "type": "version_range",
  "min_version": "1.0.0",
  "max_version": "1.999.999",
  "reason": "Database schema API changed in v2.0"
}

// Avoid: Unnecessary restriction
{
  "type": "version_range",
  "min_version": "1.0.0",
  "max_version": "1.5.0",
  "reason": "Only tested up to v1.5"
}
```

### 3. Provide Clear Reasons

**Good reasons:**
- "Requires timeline module introduced in v1.2.0"
- "Uses filesystem API that changed in v2.0"
- "Depends on email module bug fix from v1.1.5"

**Poor reasons:**
- "Version requirement"
- "Compatibility"
- "Needs newer version"

### 4. Test Across Versions

Before publishing, test your content pack with:
- The minimum version you specify
- The latest stable version
- Any maximum version you specify

### 5. Update Compatibility When Needed

When IntentVerse releases new versions:
- Review release notes for breaking changes
- Test your content pack with new versions
- Update compatibility conditions if needed
- Release new versions of your content pack as necessary

## Examples

### Example 1: Basic Database Content Pack

```json
{
  "metadata": {
    "name": "Customer Database Demo",
    "version": "1.0.0",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.0.0",
        "reason": "Requires v1.0+ database module with SQL support"
      }
    ]
  },
  "database": [
    "CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT);",
    "INSERT OR IGNORE INTO customers (name) VALUES ('Alice'), ('Bob');"
  ]
}
```

### Example 2: Advanced Features Content Pack

```json
{
  "metadata": {
    "name": "Timeline Analysis Pack",
    "version": "2.0.0",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.2.0",
        "reason": "Requires timeline module with event filtering (introduced in v1.2.0)"
      }
    ]
  },
  "state": {
    "timeline": {
      "events": [
        {"timestamp": "2024-01-01T10:00:00Z", "type": "user_action", "data": "login"}
      ]
    }
  }
}
```

### Example 3: Version-Constrained Content Pack

```json
{
  "metadata": {
    "name": "Legacy API Demo",
    "version": "1.5.0",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.0.0",
        "max_version": "1.999.999",
        "reason": "Uses v1.x filesystem API that was redesigned in v2.0"
      }
    ]
  }
}
```

### Example 4: Multiple Conditions

```json
{
  "metadata": {
    "name": "Complex Integration Pack",
    "version": "1.0.0",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.1.0",
        "reason": "Requires email module bug fixes from v1.1.0"
      },
      {
        "type": "version_range",
        "min_version": "1.2.0",
        "max_version": "2.999.999",
        "reason": "Uses timeline features from v1.2.0, compatible through v2.x"
      }
    ]
  }
}
```

## Testing Compatibility

### Local Testing

1. **Install target IntentVerse version:**
   ```bash
   # Test with specific version
   pip install intentverse==1.0.0
   ```

2. **Validate your content pack:**
   ```bash
   python scripts/validate_content_packs.py
   ```

3. **Test loading in IntentVerse:**
   ```bash
   # Load your content pack and verify it works
   intentverse load-content-pack your-pack.json
   ```

### CI/CD Validation

The repository's CI pipeline automatically:
- Validates compatibility condition format
- Checks semantic version strings
- Ensures no conflicting version ranges
- Tests basic loading scenarios

### Version Matrix Testing

For comprehensive testing, the repository provides automated testing across multiple IntentVerse versions (see Phase 3 implementation).

## Troubleshooting

### Common Issues

#### 1. Content Pack Not Loading

**Error:** "Content pack 'My Pack' is incompatible with IntentVerse 1.0.0"

**Solution:** Check your compatibility conditions:
```json
// If you see this error, your min_version might be too high
{
  "type": "version_range",
  "min_version": "1.1.0",  // This excludes v1.0.0
  "reason": "..."
}

// Fix: Lower the minimum version if appropriate
{
  "type": "version_range",
  "min_version": "1.0.0",  // Now includes v1.0.0
  "reason": "..."
}
```

#### 2. Validation Errors

**Error:** "Invalid compatibility condition: missing min_version"

**Solution:** Ensure all required fields are present:
```json
{
  "type": "version_range",
  "min_version": "1.0.0",  // Required
  "reason": "..."          // Recommended
}
```

#### 3. Version Format Errors

**Error:** "Invalid semantic version format: 1.0"

**Solution:** Use proper semantic versioning:
```json
// Wrong
"min_version": "1.0"

// Correct
"min_version": "1.0.0"
```

### Getting Help

If you encounter issues:

1. **Check the validation output:** Run `python scripts/validate_content_packs.py`
2. **Review the schema:** See [SCHEMA.md](../SCHEMA.md) for complete format specification
3. **Check examples:** Look at existing content packs in the repository
4. **Ask for help:** Open an issue or discussion on GitHub

## Migration Guide

### From Pre-v1.0 Content Packs

If you have content packs created before compatibility conditions were introduced:

1. **Add compatibility conditions:**
   ```json
   {
     "metadata": {
       // ... existing metadata ...
       "compatibility_conditions": [
         {
           "type": "version_range",
           "min_version": "1.0.0",
           "reason": "Requires v1.0+ core features"
         }
       ]
     }
   }
   ```

2. **Test with current IntentVerse version**
3. **Update version and date_exported**
4. **Submit updated content pack**

### Updating Existing Content Packs

When updating content packs for new IntentVerse versions:

1. **Review IntentVerse release notes** for breaking changes
2. **Test your content pack** with the new version
3. **Update compatibility conditions** if needed:
   ```json
   // Before: Only supported v1.x
   {
     "type": "version_range",
     "min_version": "1.0.0",
     "max_version": "1.999.999",
     "reason": "Uses v1.x API"
   }
   
   // After: Updated for v2.x compatibility
   {
     "type": "version_range",
     "min_version": "1.0.0",
     "max_version": "2.999.999",
     "reason": "Compatible with v1.x and v2.x APIs"
   }
   ```
4. **Increment your content pack version**
5. **Submit the update**

## Future Enhancements

The compatibility system is designed for future expansion:

- **Feature-based conditions:** Specify required modules or features
- **Platform conditions:** Different requirements for different platforms
- **Performance conditions:** Minimum system requirements
- **API-level conditions:** Specific API version requirements

Stay tuned for updates to this guide as new condition types are added!

---

For more information, see:
- [Content Pack Schema Documentation](../SCHEMA.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [IntentVerse Documentation](https://github.com/your-org/IntentVerse)