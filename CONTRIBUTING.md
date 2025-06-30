# Contributing to IntentVerse-Content

Thank you for your interest in contributing to IntentVerse-Content! This document provides detailed guidelines for contributing content packs to the repository.

## Table of Contents

- [Getting Started](#getting-started)
- [Content Pack Creation](#content-pack-creation)
- [Submission Process](#submission-process)
- [Review Process](#review-process)
- [Content Guidelines](#content-guidelines)
- [Technical Requirements](#technical-requirements)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A working IntentVerse installation (for creating and testing content packs)

### Repository Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/IntentVerse-Content.git
   cd IntentVerse-Content
   ```
3. Install validation dependencies:
   ```bash
   pip install jsonschema
   ```

## Content Pack Creation

### Using IntentVerse UI

The recommended way to create content packs is through the IntentVerse web interface:

1. Set up your desired state in IntentVerse (database content, files, emails, etc.)
2. Use the Content Pack Manager in the web UI
3. Fill out all required metadata fields
4. Export the content pack as a JSON file

### Manual Creation

You can also create content packs manually by following the JSON schema. See the [README.md](README.md) for the complete format specification.

### Required Metadata

When creating a content pack for submission, ensure these fields are completed:

```json
{
  "metadata": {
    "name": "Unique Content Pack Name",
    "summary": "Brief description under 100 characters",
    "detailed_description": "Comprehensive description of the content pack's purpose, use cases, and what it contains. Explain how users should interact with it.",
    "date_exported": "2024-01-01T12:00:00Z",
    "author_name": "Your Full Name",
    "author_email": "your.email@example.com",
    "version": "1.0.0",
    "tags": ["relevant", "tags", "here"],
    "category": "appropriate-category"
  }
}
```

## Submission Process

### 1. Prepare Your Content Pack

- Place your JSON file in the appropriate `content-packs/` subdirectory
- Use a descriptive filename (e.g., `ecommerce-demo-v1.json`)
- Ensure the file is valid JSON

### 2. Validate Locally

Run the validation script to check your content pack:

```bash
python scripts/validate_content_packs.py
```

Fix any validation errors before proceeding.

### 3. Test Manifest Generation

Optionally test that your content pack will be properly indexed:

```bash
python scripts/generate_manifest.py
```

### 4. Create a Pull Request

1. Commit your changes:
   ```bash
   git add content-packs/your-category/your-content-pack.json
   git commit -m "Add: Your Content Pack Name"
   ```

2. Push to your fork:
   ```bash
   git push origin main
   ```

3. Create a Pull Request on GitHub with:
   - Descriptive title
   - Summary of what the content pack provides
   - Any special instructions for reviewers

## Review Process

### Automated Checks

When you submit a PR, the CI pipeline will:

1. Validate JSON syntax and schema compliance
2. Check for required metadata fields
3. Verify no duplicate content pack names exist
4. Generate an updated manifest

### Manual Review

Maintainers will review your submission for:

- **Content Quality**: Is the content useful and well-structured?
- **Documentation**: Are descriptions clear and helpful?
- **Appropriateness**: Does the content align with IntentVerse's purpose?
- **Technical Correctness**: Does the content work as intended?

### Approval Process

- ✅ **Approved**: Your content pack will be merged and become available
- 🔄 **Changes Requested**: Address feedback and update your PR
- ❌ **Rejected**: Rare, but may happen for inappropriate or low-quality content

## Content Guidelines

### Compatibility Requirements

**Important**: All content packs must specify compatibility conditions to ensure they work correctly across different IntentVerse versions.

See the **[Compatibility Guide](docs/COMPATIBILITY-GUIDE.md)** for complete documentation on:
- How to specify version requirements
- Best practices for compatibility conditions
- Testing across multiple versions
- Troubleshooting compatibility issues

**Minimum requirement**: All content packs must include at least one compatibility condition:

```json
{
  "metadata": {
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

### Quality Standards

#### Database Content
- Use `CREATE TABLE IF NOT EXISTS` to avoid conflicts
- Use `INSERT OR IGNORE` or `INSERT OR REPLACE` for data
- Include meaningful, realistic sample data
- Document any special database requirements

#### File System State
- Create logical directory structures
- Include relevant file types for your scenario
- Keep file content concise but realistic
- Avoid including sensitive or proprietary information

#### Email Content
- Use realistic but fictional email addresses
- Create believable email threads and conversations
- Include various email types (notifications, conversations, etc.)
- Respect privacy - no real email addresses

#### Prompts
- Write clear, actionable prompts
- Include context about what the AI should explore
- Provide multiple prompts for different interaction styles
- Test prompts with actual AI agents when possible

### Content Categories

Choose the most appropriate category:

- **`demonstration`**: Basic demos showing IntentVerse features
- **`testing`**: Specific testing scenarios and edge cases
- **`education`**: Educational content and tutorials
- **`business`**: Business process simulations
- **`development`**: Software development scenarios
- **`security`**: Security testing and red team scenarios
- **`research`**: Academic or research-focused content
- **`entertainment`**: Fun, creative, or game-like scenarios

### Tagging Best Practices

Use relevant tags to help users discover your content:

- **Functional tags**: `database`, `filesystem`, `email`, `memory`
- **Domain tags**: `ecommerce`, `healthcare`, `finance`, `education`
- **Complexity tags**: `beginner`, `intermediate`, `advanced`
- **Purpose tags**: `demo`, `tutorial`, `testing`, `simulation`

## Technical Requirements

### File Size Limits

- **Recommended**: Under 500KB per content pack
- **Maximum**: 1MB per content pack
- For larger content, consider splitting into multiple packs

### JSON Format

- Use UTF-8 encoding
- Indent with 2 spaces for readability
- Ensure valid JSON syntax
- Follow the exact schema structure

### Naming Conventions

#### File Names
- Use lowercase with hyphens: `my-content-pack.json`
- Include version if multiple versions exist: `demo-v2.json`
- Be descriptive but concise

#### Content Pack Names
- Use title case: "My Content Pack"
- Be unique across the entire repository
- Clearly indicate the content's purpose

### Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Increment versions for significant changes
- Consider creating new files for major version changes

## Getting Help

### Resources

- **Documentation**: [IntentVerse README](https://github.com/your-org/IntentVerse)
- **Examples**: Browse existing content packs in this repository
- **Schema**: See validation script for detailed schema requirements

### Support Channels

- **GitHub Issues**: For bugs or feature requests
- **GitHub Discussions**: For questions and community help
- **Pull Request Comments**: For specific feedback on your submission

### Common Issues

#### Validation Failures
- Check JSON syntax with a JSON validator
- Ensure all required metadata fields are present
- Verify email format in `author_email`
- Check date format is ISO 8601

#### Merge Conflicts
- Keep your fork updated with the main repository
- Resolve conflicts in `manifest.json` by regenerating it

#### Content Not Loading
- Test your content pack in a local IntentVerse instance
- Check for SQL syntax errors in database statements
- Verify state structure matches expected format

## Code of Conduct

By contributing to this repository, you agree to:

- Be respectful and inclusive in all interactions
- Provide constructive feedback and accept it gracefully
- Focus on what's best for the community
- Show empathy towards other community members

Thank you for contributing to IntentVerse-Content! Your contributions help make AI agent testing more accessible and effective for everyone.