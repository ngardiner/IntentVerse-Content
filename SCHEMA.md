# Content Pack Schema Documentation

This document describes the JSON schema for IntentVerse content packs.

## Overview

Content packs are JSON files that contain structured data for loading into IntentVerse. They consist of six main sections: metadata, database, prompts (deprecated), content_prompts, usage_prompts, variables, and state.

**Current Version**: v1.1.0 (supports variable system and enhanced prompt categorization)

## Schema Structure

### Root Object (v1.1.0)

```json
{
  "metadata": { ... },         // Required
  "database": [ ... ],         // Optional
  "prompts": [ ... ],          // Optional (DEPRECATED - use content_prompts/usage_prompts)
  "content_prompts": [ ... ],  // Optional - Prompts for dynamic content creation
  "usage_prompts": [ ... ],    // Optional - Suggested prompts for users
  "variables": { ... },        // Optional - Variable definitions with defaults
  "state": { ... }             // Optional
}
```

### Legacy Root Object (v1.0.0)

```json
{
  "metadata": { ... },      // Required
  "database": [ ... ],      // Optional
  "prompts": [ ... ],       // Optional
  "state": { ... }          // Optional
}
```

**Note**: v1.0.0 content packs continue to work in v1.1.0 without modification.

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

## Prompts Section (Optional, DEPRECATED)

**DEPRECATED**: The `prompts` field is deprecated in v1.1.0. Use `content_prompts` and `usage_prompts` instead for better categorization.

Contains predefined prompts for AI interaction. This field is maintained for backward compatibility but new content packs should use the categorized prompt fields.

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

## Content Prompts Section (Optional)

**New in v1.1.0**: Contains prompts designed for dynamic content creation. These prompts are used by the AI to generate content, documents, emails, or other materials based on the loaded data and context.

### Format

Array of content prompt objects.

### Content Prompt Object Structure

- **name** (string): Unique identifier for the prompt
- **description** (string): Human-readable description of the prompt's purpose
- **content** (string): The actual prompt text (supports variable tokens)
- **category** (string, optional): Categorization for the prompt (e.g., "email", "report", "analysis")
- **output_format** (string, optional): Expected output format (e.g., "markdown", "html", "plain_text")

### Example

```json
{
  "content_prompts": [
    {
      "name": "generate_welcome_email",
      "description": "Generate a welcome email for new users",
      "content": "Create a professional welcome email for new users joining {{company_name}}. Include information about our company culture, next steps, and contact information. The email should be sent from {{support_email}}.",
      "category": "email",
      "output_format": "html"
    },
    {
      "name": "create_data_report",
      "description": "Generate a comprehensive data analysis report",
      "content": "Analyze the available data and create a comprehensive report. Include key findings, trends, and actionable recommendations for {{company_name}}. Focus on metrics relevant to {{business_domain}}.",
      "category": "report",
      "output_format": "markdown"
    }
  ]
}
```

## Usage Prompts Section (Optional)

**New in v1.1.0**: Contains suggested prompts for users to interact with the AI. These prompts guide users on how to effectively use the content pack and explore its capabilities.

### Format

Array of usage prompt objects.

### Usage Prompt Object Structure

- **name** (string): Unique identifier for the prompt
- **description** (string): Human-readable description of what the prompt does
- **content** (string): The actual prompt text (supports variable tokens)
- **difficulty** (string, optional): Difficulty level ("beginner", "intermediate", "advanced")
- **estimated_time** (string, optional): Estimated time to complete (e.g., "5 minutes", "30 minutes")

### Example

```json
{
  "usage_prompts": [
    {
      "name": "explore_company_data",
      "description": "Get an overview of the company data and structure",
      "content": "Please explore the available data for {{company_name}} and provide a summary of what information is available. What insights can you gather about the company structure and operations?",
      "difficulty": "beginner",
      "estimated_time": "10 minutes"
    },
    {
      "name": "analyze_customer_trends",
      "description": "Perform advanced customer behavior analysis",
      "content": "Analyze customer data for {{company_name}} and identify trends in behavior, preferences, and engagement. Create visualizations if possible and provide actionable recommendations for improving customer experience.",
      "difficulty": "advanced",
      "estimated_time": "45 minutes"
    }
  ]
}
```

## Variables Section (Optional)

**New in v1.1.0**: Defines variables with default values that can be used throughout the content pack. Variables enable customization and reusability of content packs across different contexts.

### Format

Object with variable names as keys and default values as values.

### Variable Naming Rules

- Must match pattern: `^[a-zA-Z_][a-zA-Z0-9_]*$`
- Case-sensitive
- Cannot start with numbers
- Use descriptive names (e.g., `company_name`, `email_domain`)

### Variable Token Syntax

Variables can be used in prompt content using double curly braces:
- **Simple variables**: `{{variable_name}}`
- **Case-sensitive**: `{{Company_Name}}` is different from `{{company_name}}`

### Variable Resolution Order

1. **User override**: Custom value set by the user (stored in database)
2. **Pack default**: Default value from the content pack JSON
3. **Error**: If variable is not found, an error is raised

### Example

```json
{
  "variables": {
    "company_name": "ACME Corporation",
    "email_domain": "acmecorp.com",
    "support_email": "support@acmecorp.com",
    "business_domain": "e-commerce",
    "ceo_name": "Jane Smith",
    "headquarters_location": "San Francisco, CA",
    "employee_count": "500",
    "founded_year": "2010"
  }
}
```

### Variable Usage in Prompts

```json
{
  "content_prompts": [
    {
      "name": "company_overview",
      "description": "Generate a company overview document",
      "content": "Create a comprehensive overview of {{company_name}}, founded in {{founded_year}} and headquartered in {{headquarters_location}}. The company operates in the {{business_domain}} sector with approximately {{employee_count}} employees under the leadership of CEO {{ceo_name}}. Include contact information: {{support_email}}."
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

### v1.1.0 Content Pack Example

```json
{
  "metadata": {
    "name": "E-commerce Demo Pack",
    "summary": "A comprehensive e-commerce business simulation",
    "detailed_description": "This content pack provides a realistic e-commerce business environment with customer data, product information, and business scenarios. Includes variable customization for different company contexts.",
    "date_exported": "2024-01-15T10:30:00Z",
    "author_name": "IntentVerse Team",
    "author_email": "team@intentverse.com",
    "version": "1.1.0",
    "tags": ["ecommerce", "business", "demo", "variables"],
    "category": "demonstration",
    "compatibility_conditions": [
      {
        "type": "version_range",
        "min_version": "1.1.0",
        "reason": "Requires v1.1.0+ for variable system and new prompt categories"
      }
    ]
  },
  "variables": {
    "company_name": "TechMart Inc",
    "email_domain": "techmart.com",
    "support_email": "support@techmart.com",
    "business_domain": "electronics retail",
    "ceo_name": "Sarah Johnson",
    "headquarters_location": "Austin, TX",
    "employee_count": "250",
    "founded_year": "2018"
  },
  "database": [
    "CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, join_date TEXT);",
    "INSERT OR IGNORE INTO customers (name, email, join_date) VALUES ('Alice Smith', 'alice@example.com', '2023-01-15'), ('Bob Johnson', 'bob@example.com', '2023-02-20');"
  ],
  "content_prompts": [
    {
      "name": "generate_welcome_email",
      "description": "Generate a welcome email for new customers",
      "content": "Create a professional welcome email for new customers joining {{company_name}}. Include information about our {{business_domain}} offerings, customer support contact ({{support_email}}), and next steps for getting started.",
      "category": "email",
      "output_format": "html"
    },
    {
      "name": "create_quarterly_report",
      "description": "Generate a quarterly business report",
      "content": "Analyze the available customer and sales data to create a comprehensive quarterly report for {{company_name}}. Include key metrics, trends, and recommendations for the {{business_domain}} sector. Address the report to CEO {{ceo_name}}.",
      "category": "report",
      "output_format": "markdown"
    }
  ],
  "usage_prompts": [
    {
      "name": "explore_customer_data",
      "description": "Get an overview of customer information",
      "content": "Please explore the customer data for {{company_name}} and provide insights about our customer base. What patterns do you notice in customer behavior and demographics?",
      "difficulty": "beginner",
      "estimated_time": "10 minutes"
    },
    {
      "name": "analyze_business_performance",
      "description": "Perform comprehensive business analysis",
      "content": "Conduct a thorough analysis of {{company_name}}'s performance in the {{business_domain}} market. Include customer acquisition trends, revenue patterns, and strategic recommendations for growth.",
      "difficulty": "advanced",
      "estimated_time": "30 minutes"
    }
  ],
  "state": {
    "filesystem": {
      "type": "directory",
      "name": "/",
      "children": [
        {
          "type": "file",
          "name": "company_overview.md",
          "content": "# {{company_name}} Overview\n\nFounded: {{founded_year}}\nHeadquarters: {{headquarters_location}}\nEmployees: {{employee_count}}\nIndustry: {{business_domain}}"
        }
      ]
    },
    "email": {
      "inbox": [
        {
          "id": 1,
          "from": "customer@example.com",
          "to": "{{support_email}}",
          "subject": "Question about your {{business_domain}} products",
          "body": "Hi {{company_name}} team, I have a question about your latest products...",
          "timestamp": "2024-01-15T10:30:00Z",
          "read": false
        }
      ],
      "sent": [],
      "drafts": []
    },
    "memory": {
      "short_term": {
        "current_quarter": "Q1 2024",
        "active_campaigns": "3"
      },
      "long_term": {
        "company_mission": "Providing quality {{business_domain}} solutions",
        "core_values": "Innovation, Quality, Customer Focus"
      },
      "context": {
        "user_role": "Business Analyst",
        "access_level": "full"
      }
    }
  }
}
```

### Legacy v1.0.0 Content Pack Example

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
    "category": "demonstration"
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
8. **Variable Names**: Must match pattern `^[a-zA-Z_][a-zA-Z0-9_]*$` (v1.1.0+)
9. **Variable Tokens**: Must use `{{variable_name}}` syntax in prompt content (v1.1.0+)
10. **Prompt Names**: Must be unique within each prompt category (v1.1.0+)

## Best Practices

1. **Descriptive Names**: Use clear, descriptive names for content packs
2. **Comprehensive Descriptions**: Provide detailed descriptions of use cases
3. **Meaningful Tags**: Use relevant tags for discoverability
4. **Realistic Data**: Include realistic but fictional data
5. **Mergeable Content**: Ensure state and database content can merge with existing data
6. **Testing**: Test content packs in IntentVerse before submission
7. **Documentation**: Include README files in filesystem state when helpful

### v1.1.0 Best Practices

8. **Variable Usage**: Use variables for customizable content (company names, domains, etc.)
9. **Prompt Categorization**: Use `content_prompts` for AI content generation, `usage_prompts` for user guidance
10. **Variable Naming**: Use descriptive, consistent variable names (e.g., `company_name`, not `name`)
11. **Token Consistency**: Ensure all variable tokens in prompts have corresponding variable definitions
12. **Backward Compatibility**: Consider including legacy `prompts` field for v1.0.0 compatibility if needed

## Migration Guide (v1.0.0 to v1.1.0)

### Automatic Migration

v1.0.0 content packs work without modification in v1.1.0. No immediate action required.

### Manual Migration (Recommended)

1. **Categorize Prompts**: Move prompts from `prompts` to `content_prompts` or `usage_prompts`
2. **Extract Variables**: Identify repeated values and create variables
3. **Add Variable Tokens**: Replace hardcoded values with `{{variable_name}}` tokens
4. **Update Metadata**: Increment version and add v1.1.0 compatibility requirement
5. **Test**: Verify variable resolution and prompt categorization work correctly

### Migration Example

**Before (v1.0.0):**
```json
{
  "prompts": [
    {
      "name": "welcome",
      "content": "Welcome to ACME Corp! Contact us at support@acme.com"
    }
  ]
}
```

**After (v1.1.0):**
```json
{
  "variables": {
    "company_name": "ACME Corp",
    "support_email": "support@acme.com"
  },
  "usage_prompts": [
    {
      "name": "welcome",
      "content": "Welcome to {{company_name}}! Contact us at {{support_email}}"
    }
  ]
}
```