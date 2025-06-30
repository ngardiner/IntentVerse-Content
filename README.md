# IntentVerse-Content

Community Content Packs for the IntentVerse AI Observability Platform

## Overview

This repository contains community-contributed content packs for [IntentVerse](https://github.com/your-org/IntentVerse), an AI observability platform that provides mock tools and environments for testing AI agents.

Content packs are JSON files that contain pre-configured data, prompts, and state that can be loaded into IntentVerse to create specific testing scenarios or demonstrations.

## Repository Structure

```
IntentVerse-Content/
├── content-packs/           # Directory containing all content pack JSON files
│   ├── category1/          # Optional: organize by category
│   └── category2/
├── scripts/                # Automation scripts
│   ├── validate_content_packs.py
│   └── generate_manifest.py
├── .github/workflows/      # CI/CD automation
│   └── content-pack-ci.yml
├── manifest.json           # Auto-generated index of all content packs
└── README.md              # This file
```

## Content Pack Format

Content packs are JSON files with the following structure:

```json
{
  "metadata": {
    "name": "My Content Pack",
    "summary": "Brief description of what this pack provides",
    "detailed_description": "Longer description with use cases and details",
    "date_exported": "2024-01-01T12:00:00Z",
    "author_name": "Your Name",
    "author_email": "your.email@example.com",
    "version": "1.0.0",
    "tags": ["demo", "testing", "database"],
    "category": "demonstration"
  },
  "database": [
    "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
    "INSERT INTO users (name) VALUES ('Alice'), ('Bob');"
  ],
  "prompts": [
    {
      "name": "explore_data",
      "description": "Prompt to explore the loaded data",
      "content": "Please explore the database and tell me what you find."
    }
  ],
  "state": {
    "filesystem": {
      "type": "directory",
      "name": "/",
      "children": []
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

## Contributing

### Prerequisites

- Python 3.11+
- Git

### Submission Process

1. **Fork this repository**

2. **Create your content pack**
   - Export a content pack from your IntentVerse instance
   - Ensure all required metadata fields are filled out
   - Place the JSON file in the appropriate `content-packs/` subdirectory

3. **Validate your content pack**
   ```bash
   python scripts/validate_content_packs.py
   ```

4. **Test locally** (optional)
   ```bash
   python scripts/generate_manifest.py
   ```

5. **Submit a Pull Request**
   - Create a descriptive PR title and description
   - The CI pipeline will automatically validate your content pack
   - If validation passes, the manifest will be updated automatically

### Content Pack Guidelines

#### Required Metadata Fields
- `name`: Unique, descriptive name for your content pack
- `summary`: Brief one-line description (max 100 characters)
- `detailed_description`: Comprehensive description of use cases and contents
- `author_name`: Your name or organization
- `author_email`: Contact email address
- `version`: Semantic version (e.g., "1.0.0")
- `date_exported`: ISO 8601 timestamp of when the pack was created

#### Optional Metadata Fields
- `tags`: Array of relevant tags for categorization
- `category`: Category for organization (defaults to "uncategorized")
- `compatibility_conditions`: Array of compatibility requirements (see [Compatibility Guide](docs/COMPATIBILITY-GUIDE.md))

#### Content Guidelines
- **Database**: SQL statements should use `CREATE TABLE IF NOT EXISTS` and `INSERT OR IGNORE` to avoid conflicts
- **State**: Should be mergeable with existing state (additive, not replacement)
- **Prompts**: Should be clear, actionable, and relevant to the included content
- **File Size**: Keep content packs under 1MB when possible

#### Categories
Suggested categories include:
- `demonstration` - Basic demos and examples
- `testing` - Content for testing specific scenarios
- `education` - Educational content and tutorials
- `business` - Business scenario simulations
- `development` - Development and coding scenarios
- `security` - Security testing scenarios

## Automated Processing

### CI Pipeline
When you submit a PR or push to main:

1. **Validation**: All content packs are validated against the schema
2. **Manifest Generation**: The `manifest.json` file is automatically updated
3. **Duplicate Check**: Ensures no duplicate content pack names exist

### Manifest File
The `manifest.json` file is automatically generated and contains:
- Metadata for all valid content packs
- Statistics about the repository
- File information and categorization
- Search and filtering metadata

This manifest is consumed by IntentVerse to display available content packs in the UI.

## Local Development

### Setup
```bash
git clone https://github.com/your-org/IntentVerse-Content.git
cd IntentVerse-Content
pip install jsonschema
```

### Validation
```bash
# Validate all content packs
python scripts/validate_content_packs.py

# Generate manifest
python scripts/generate_manifest.py
```

## Documentation

- **[Compatibility Guide](docs/COMPATIBILITY-GUIDE.md)**: Complete guide to content pack compatibility conditions
- **[Schema Documentation](SCHEMA.md)**: Detailed content pack format specification
- **[Contributing Guidelines](CONTRIBUTING.md)**: How to contribute content packs

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and community interaction
- **Documentation**: See the main [IntentVerse documentation](https://github.com/your-org/IntentVerse)

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Individual content packs may have their own licensing terms as specified in their metadata.