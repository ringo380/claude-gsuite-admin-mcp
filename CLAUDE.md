# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides Claude with comprehensive Google Workspace administrative capabilities. The server implements 31 administrative tools across 6 major functional areas: user management, group management, organizational units, device management, reports & auditing, and security management.

## Key Commands

### Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run specific test files
python test_auth.py
python test_users.py
python test_groups.py
python test_org_units.py
python test_devices.py
python test_reports.py
python test_security.py

# Run comprehensive test
python test_comprehensive.py
```

### Code Quality
```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Linting (if flake8 is installed)
flake8 src/
```

### OAuth Setup
```bash
# Complete OAuth flow
python complete_oauth.py
python setup_oauth.py
```

### Running the MCP Server
```bash
# Run the server directly
python -m claude_gsuite_admin.server

# Or using the installed script
claude-gsuite-admin-mcp
```

## Architecture

### Core Components

1. **Server Entry Point** (`src/claude_gsuite_admin/server.py`):
   - Main MCP server that registers and handles all tools
   - Global tool handlers registry
   - Error handling and authentication flow

2. **Tool Handler Base** (`src/claude_gsuite_admin/core/tool_handler.py`):
   - Abstract base class `AdminToolHandler` for all Google Workspace tools
   - Common authentication, validation, and error handling
   - Standardized response formatting

3. **OAuth Management** (`src/claude_gsuite_admin/auth/oauth_manager.py`):
   - Handles OAuth2 flow with comprehensive Google Workspace scopes
   - Credential storage, refresh, and validation
   - Account information management

### Tool Organization

Tools are organized by functional area in separate modules:

- **User Management** (`tools/users.py`): 7 tools for user CRUD operations, suspension, password resets
- **Group Management** (`tools/groups.py`): 5 tools for group management and membership
- **Organizational Units** (`tools/org_units.py`): 5 tools for OU hierarchy management
- **Device Management** (`tools/devices.py`): 5 tools for mobile and Chrome device management
- **Reports & Auditing** (`tools/reports.py`): 4 tools for usage analytics and audit logs
- **Security Management** (`tools/security.py`): 5 tools for domain security and role management

### Authentication Flow

1. Each tool call requires a `user_id` parameter (admin email)
2. Server validates OAuth2 credentials for the user
3. If credentials are expired, they are automatically refreshed
4. Google API services are instantiated with authenticated credentials
5. Tool-specific operations are executed with proper error handling

### Configuration Files

- **`.gauth.json`**: OAuth2 client credentials from Google Cloud Console
- **`.accounts.json`**: Account configuration for admin users
- **`.oauth2.{user_id}.json`**: Stored OAuth2 tokens per user
- **`.mcp.json`**: MCP server configuration for Claude CLI

### Error Handling

The system uses a hierarchical exception system:
- `AdminMCPError`: Base exception with error codes
- `AuthenticationError`: OAuth and permission issues
- `ValidationError`: Input validation failures
- `GoogleAPIError`: Google API-specific errors with status codes

### Google API Scopes

The OAuth manager requests comprehensive admin scopes including:
- Directory API (users, groups, OUs, devices)
- Reports API (usage and audit data)
- Admin SDK (domain and security management)
- Legacy Gmail and Calendar APIs for compatibility

## Development Guidelines

### Adding New Tools

1. Create a new handler class extending `AdminToolHandler`
2. Implement `get_tool_description()` with proper MCP Tool schema
3. Implement `run_tool()` with validation, API calls, and response formatting
4. Add the handler to the appropriate module's handler list
5. The server will automatically register it at startup

### Tool Handler Pattern

Each tool follows this pattern:
```python
class ToolHandler(AdminToolHandler):
    def __init__(self):
        super().__init__("mcp__gsuite_admin__tool_name")

    def get_tool_description(self) -> Tool:
        # Return MCP tool schema

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        # 1. Validate user_id and required args
        # 2. Get authenticated Google API service
        # 3. Execute API operations with error handling
        # 4. Format and return response
```

### Testing Strategy

- Unit tests for individual tools in `test_*.py` files
- OAuth testing in `test_auth.py`
- Comprehensive integration testing in `test_comprehensive.py`
- MCP protocol testing in `test_mcp_direct.py` and `test_mcp_tools.py`

### Common Pitfalls

- All tools require `user_id` parameter for authentication
- Google API rate limits may require retry logic
- OAuth tokens expire and need refresh handling
- Some admin operations require specific role permissions
- Domain-level operations may have different permission requirements than user-level operations