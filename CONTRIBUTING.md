# Contributing to Claude Google Workspace Admin MCP

Thank you for your interest in contributing to the Claude Google Workspace Admin MCP server! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Security Considerations](#security-considerations)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow. Please be respectful, inclusive, and constructive in all interactions.

### Our Standards

- Be welcoming and inclusive
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.10 or higher
- Git
- A Google Workspace domain for testing (recommended)
- Claude CLI installed
- Basic understanding of Google Workspace Admin APIs

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/claude-gsuite-admin-mcp.git
   cd claude-gsuite-admin-mcp
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ryanrobson/claude-gsuite-admin-mcp.git
   ```

## Development Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### 2. Configuration

Set up your development configuration:

```bash
# Copy example files
cp .gauth.json.example .gauth.json
cp .accounts.json.example .accounts.json

# Edit with your credentials (DO NOT COMMIT THESE)
# .gauth.json - your OAuth2 credentials
# .accounts.json - your test admin accounts
```

### 3. Authentication

Complete the OAuth flow for testing:

```bash
python complete_oauth.py
```

### 4. Verify Setup

```bash
# Run basic tests
python test_auth.py
python -c "import claude_gsuite_admin; print('Setup successful')"
```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug Fixes**: Fix existing issues or problems
- **Feature Enhancements**: Improve existing functionality
- **New Tools**: Add new Google Workspace admin tools
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code

### Before Contributing

1. **Check existing issues** to see if your idea/bug is already being worked on
2. **Create an issue** for new features or significant changes
3. **Discuss your approach** before implementing large changes

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

Follow the coding standards and guidelines outlined below.

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test files
python test_users.py
python test_groups.py

# Test your specific changes
python test_comprehensive.py
```

### 4. Commit Changes

Use conventional commit format:

```bash
git commit -m "feat: add new user bulk operations tool"
git commit -m "fix: resolve authentication token refresh issue"
git commit -m "docs: update API documentation for security tools"
git commit -m "test: add integration tests for device management"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Python Code Style

We use Black for code formatting and follow PEP 8:

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Type checking
mypy src/

# Linting (if available)
flake8 src/
```

### Code Structure

#### Adding New Tools

When adding new admin tools, follow this structure:

```python
# src/claude_gsuite_admin/tools/your_area.py

from typing import Any, Dict, Sequence
from mcp.types import Tool, TextContent
from ..core.tool_handler import AdminToolHandler

class YourToolHandler(AdminToolHandler):
    def __init__(self):
        super().__init__("mcp__gsuite_admin__your_tool_name")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.tool_name,
            description="Clear description of what this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Admin user email"
                    },
                    # Add your parameters here
                },
                "required": ["user_id"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        # 1. Validate required parameters
        user_id = args.get("user_id")
        if not user_id:
            raise ValueError("user_id is required")

        # 2. Get authenticated service
        service = self.get_directory_service(user_id)

        try:
            # 3. Perform Google API operations
            result = service.users().list().execute()

            # 4. Format and return response
            return [TextContent(
                type="text",
                text=f"Operation completed successfully: {result}"
            )]

        except Exception as e:
            # 5. Handle errors appropriately
            return [TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

# Add to the handlers list at the end of the file
HANDLERS = [
    YourToolHandler(),
    # ... other handlers
]
```

#### Tool Handler Guidelines

1. **Inherit from AdminToolHandler**: Use the base class for consistency
2. **Clear Descriptions**: Provide detailed tool descriptions
3. **Parameter Validation**: Always validate required parameters
4. **Error Handling**: Use try/catch and provide meaningful error messages
5. **Consistent Response Format**: Return structured TextContent responses
6. **Documentation**: Include docstrings and type hints

### Documentation Standards

- **Docstrings**: Use Google-style docstrings for all functions and classes
- **Type Hints**: Include type hints for all function parameters and returns
- **Comments**: Add comments for complex logic or non-obvious code
- **API Documentation**: Update docs/API.md when adding new tools

### Testing Standards

#### Test Structure

```python
# tests/test_your_feature.py

import pytest
from claude_gsuite_admin.tools.your_area import YourToolHandler

class TestYourTool:
    def test_tool_description(self):
        """Test that tool description is properly formatted."""
        handler = YourToolHandler()
        description = handler.get_tool_description()
        assert description.name == "mcp__gsuite_admin__your_tool_name"
        assert "user_id" in description.inputSchema["required"]

    def test_parameter_validation(self):
        """Test parameter validation."""
        handler = YourToolHandler()

        # Test missing required parameter
        with pytest.raises(ValueError):
            handler.run_tool({})

    def test_successful_operation(self):
        """Test successful tool execution."""
        # Add test for successful operation
        pass

    def test_error_handling(self):
        """Test error handling."""
        # Add test for error scenarios
        pass
```

#### Test Guidelines

1. **Comprehensive Coverage**: Test both success and failure scenarios
2. **Isolated Tests**: Each test should be independent
3. **Mock External APIs**: Use mocks for Google API calls in unit tests
4. **Integration Tests**: Include tests that verify end-to-end functionality
5. **Error Cases**: Test various error conditions and edge cases

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_gsuite_admin

# Run specific test files
pytest tests/test_users.py
pytest tests/test_groups.py

# Run tests for a specific function
pytest tests/test_users.py::TestUserManagement::test_create_user
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test tool handlers with real API calls
- **End-to-End Tests**: Test complete workflows through Claude CLI
- **Security Tests**: Test authentication and authorization

### Test Data

Use the provided test accounts and avoid using production data:

```python
# Use test accounts from .accounts.json
TEST_ADMIN = "test-admin@yourtestdomain.com"
TEST_USER = "test-user@yourtestdomain.com"
```

## Documentation

### Types of Documentation

1. **API Documentation** (`docs/API.md`): Tool descriptions and parameters
2. **Setup Guide** (`docs/SETUP.md`): Installation and configuration
3. **Usage Examples** (`docs/EXAMPLES.md`): Practical usage examples
4. **Code Documentation**: Inline comments and docstrings

### Documentation Updates

When making changes:

1. **Update API docs** for new or changed tools
2. **Add usage examples** for new functionality
3. **Update setup guide** if installation process changes
4. **Update README** for significant changes

## Security Considerations

### Sensitive Information

- **Never commit** OAuth credentials or tokens
- **Use test accounts** for development and testing
- **Validate all inputs** to prevent injection attacks
- **Follow least privilege** principle for admin accounts

### Security Best Practices

1. **Input Validation**: Validate all user inputs
2. **Error Handling**: Don't expose sensitive information in error messages
3. **Authentication**: Verify OAuth tokens before API calls
4. **Audit Logging**: Log important operations for security auditing
5. **Rate Limiting**: Respect Google API rate limits

### Security Review

All contributions will be reviewed for security implications. Please:

- Document any security considerations in your PR
- Follow OWASP guidelines for secure coding
- Use the provided authentication mechanisms
- Don't introduce new credential storage methods without discussion

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml` and `setup.py`
2. **Update CHANGELOG.md** with new version details
3. **Run full test suite** to ensure stability
4. **Create release branch** and test thoroughly
5. **Tag release** and update GitHub releases
6. **Update documentation** if needed

## Getting Help

### Communication Channels

- **GitHub Issues**: For bugs, feature requests, and questions
- **GitHub Discussions**: For general discussion and help
- **Pull Request Reviews**: For code-specific questions

### Resources

- [Google Workspace Admin SDK Documentation](https://developers.google.com/admin-sdk)
- [Claude CLI Documentation](https://claude.ai/code)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Python Google API Client](https://github.com/googleapis/google-api-python-client)

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors page
- Release notes for significant contributions

Thank you for contributing to the Claude Google Workspace Admin MCP server!