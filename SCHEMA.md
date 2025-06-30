# Content Pack Schema Documentation

This document describes the JSON schema for IntentVerse content packs.

## Overview

Content packs are JSON files that contain structured data for loading into IntentVerse. They consist of four main sections: metadata, database, prompts, and state.

## Schema Structure

### Root Object

```json
{
  "metadata": { ... },      // Required
  "database": [ ... ],      // Optional
  "prompts": [ ... ],       // Optional
  "state": { ... }          // Optional
}
```

## Metadata Section (Required)

The metadata section contains information about the content pack itself.

### Required Fields

- **name** (string): Unique name for the content pack
- **summary** (string): Brief description (recommended max 100 characters)
- **detailed_description** (string): Comprehensive description of the pack's purpose and contents
- **date_exported** (string): ISO 8601 timestamp (format: YYYY-MM-DDTHH:MM:SSZ)
- **author_name** (string): Name of the content pack author
- **author_email** (string): Valid email address of the author
- **version** (string): Semantic version number (format: X.Y.Z)

### Optional Fields

- **tags** (array of strings): Categorization tags
- **category** (string): Primary category (defaults to "uncategorized")
- **compatibility_conditions** (array of objects): Defines IntentVerse version compatibility requirements (defaults to empty array = universal compatibility)

### Example

```json
{
  "metadata": {
    "name": "My Content Pack",
    "summary": "A sample content pack for demonstration",
    "detailed_description": "This content pack provides sample data and scenarios for testing AI agent interactions with various tools and data sources.",
    "date_exported": "2024-01-15T10:30:00Z",
    "author_name": "John Doe",
    "author_email": "john.doe@example.com",
    "version": "1.0.0",
    "tags": ["demo", "testing", "sample"],
    "category": "demonstration"
  }
}
```

## Compatibility Conditions Section (Optional)

The compatibility_conditions array defines which versions of IntentVerse this content pack is compatible with. If empty or omitted, the content pack is considered compatible with all versions.

### Compatibility Condition Object Structure

- **type** (string): Type of compatibility check. Currently supported: "version_range"
- **min_version** (string): Minimum compatible IntentVerse version (semantic version format)
- **max_version** (string, optional): Maximum compatible IntentVerse version (semantic version format)
- **reason** (string, optional): Human-readable explanation for the compatibility requirement

### Example

```json
{
  "metadata": {
    "name": "Advanced Features Pack",
    "version": "2.1.0",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.0.0",
        "max_version": "2.0.0",
        "reason": "Uses filesystem API that changed in v2.1"
      }
    ]
  }
}
```

### Compatibility Rules

1. **Empty Array**: Content pack works with all IntentVerse versions
2. **Version Range**: Content pack only works within specified version range
3. **Multiple Conditions**: All conditions must be satisfied for compatibility
4. **Semantic Versioning**: All versions must follow semver format (X.Y.Z)

## Database Section (Optional)

Contains SQL statements to populate the SQLite database.

### Format

Array of SQL statement strings.

### Guidelines

- Use `CREATE TABLE IF NOT EXISTS` for table creation
- Use `INSERT OR IGNORE` or `INSERT OR REPLACE` for data insertion
- Statements are executed in order
- Foreign key constraints are supported

### Example

```json
{
  "database": [
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT);",
    "INSERT OR IGNORE INTO users (name, email) VALUES ('Alice', 'alice@example.com');",
    "INSERT OR IGNORE INTO users (name, email) VALUES ('Bob', 'bob@example.com');"
  ]
}
```

## Prompts Section (Optional)

Contains predefined prompts for AI interaction.

### Format

Array of prompt objects.

### Prompt Object Structure

- **name** (string): Unique identifier for the prompt
- **description** (string): Human-readable description of the prompt's purpose
- **content** (string): The actual prompt text

### Example

```json
{
  "prompts": [
    {
      "name": "explore_data",
      "description": "Initial data exploration prompt",
      "content": "Please explore the available data and provide a summary of what you find."
    },
    {
      "name": "analyze_trends",
      "description": "Data analysis prompt",
      "content": "Analyze the data for trends and patterns. Provide insights and recommendations."
    }
  ]
}
```

## State Section (Optional)

Contains the initial state for various IntentVerse modules.

### Supported Modules

- **filesystem**: Virtual file system structure
- **email**: Email inbox, sent, and drafts
- **memory**: Short-term, long-term, and context memory
- **web_search**: Web search history and results (if applicable)

### Filesystem Structure

Represents a hierarchical file system.

#### Directory Object
```json
{
  "type": "directory",
  "name": "directory_name",
  "children": [ ... ]
}
```

#### File Object
```json
{
  "type": "file",
  "name": "filename.txt",
  "content": "File content as a string"
}
```

### Email Structure

```json
{
  "email": {
    "inbox": [
      {
        "id": 1,
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "subject": "Email subject",
        "body": "Email body content",
        "timestamp": "2024-01-15T10:30:00Z",
        "read": false
      }
    ],
    "sent": [ ... ],
    "drafts": [ ... ]
  }
}
```

### Memory Structure

```json
{
  "memory": {
    "short_term": {
      "key": "value"
    },
    "long_term": {
      "key": "value"
    },
    "context": {
      "key": "value"
    }
  }
}
```

## Complete Example

```json
{
  "metadata": {
    "name": "Sample Content Pack",
    "summary": "A basic example content pack",
    "detailed_description": "This content pack demonstrates the basic structure and capabilities of IntentVerse content packs.",
    "date_exported": "2024-01-15T10:30:00Z",
    "author_name": "IntentVerse Team",
    "author_email": "team@intentverse.com",
    "version": "1.0.0",
    "tags": ["example", "demo"],
    "category": "demonstration",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.0.0",
        "reason": "Requires v1.0+ features for proper functionality"
      }
    ]
  },
  "database": [
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT);",
    "INSERT OR IGNORE INTO users (name) VALUES ('Alice'), ('Bob');"
  ],
  "prompts": [
    {
      "name": "explore",
      "description": "Explore the environment",
      "content": "Please explore the available tools and data."
    }
  ],
  "state": {
    "filesystem": {
      "type": "directory",
      "name": "/",
      "children": [
        {
          "type": "file",
          "name": "welcome.txt",
          "content": "Welcome to IntentVerse!"
        }
      ]
    },
    "email": {
      "inbox": [],
      "sent": [],
      "drafts": []
    },
    "memory": {
      "short_term": {},
      "long_term": {},
      "context": {}
    }
  }
}
```

## Validation Rules

1. **JSON Syntax**: Must be valid JSON
2. **Required Fields**: All required metadata fields must be present and non-empty
3. **Email Format**: author_email must be a valid email address
4. **Date Format**: date_exported must be ISO 8601 format
5. **Version Format**: version must follow semantic versioning (X.Y.Z)
6. **Unique Names**: Content pack names must be unique within the repository
7. **File Size**: Recommended maximum size is 1MB per content pack

## Best Practices

1. **Descriptive Names**: Use clear, descriptive names for content packs
2. **Comprehensive Descriptions**: Provide detailed descriptions of use cases
3. **Meaningful Tags**: Use relevant tags for discoverability
4. **Realistic Data**: Include realistic but fictional data
5. **Mergeable Content**: Ensure state and database content can merge with existing data
6. **Testing**: Test content packs in IntentVerse before submission
7. **Documentation**: Include README files in filesystem state when helpful