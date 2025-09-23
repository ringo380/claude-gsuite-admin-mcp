# Claude Google Workspace Admin MCP Server

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Google Workspace](https://img.shields.io/badge/Google%20Workspace-Admin%20SDK-red.svg)](https://developers.google.com/admin-sdk)

A comprehensive Model Context Protocol (MCP) server that provides Claude with powerful Google Workspace administrative capabilities. This server enables Claude to manage users, groups, organizational units, devices, security settings, and generate detailed reports for Google Workspace domains.

**🎯 Total Tools Available: 31 Administrative Functions**

## Features

### 👤 User Management (7 tools)
- **List Users**: Search and filter users across the domain
- **Get User Details**: Retrieve comprehensive user information
- **Create Users**: Add new user accounts with full configuration
- **Update Users**: Modify user properties and settings
- **Suspend/Unsuspend**: Manage user account status
- **Reset Passwords**: Force password resets and temporary passwords
- **Delete Users**: Remove user accounts (with confirmation)

### 👥 Group Management (5 tools)
- **List Groups**: Browse and search all domain groups
- **Get Group Details**: Detailed group information and settings
- **Create Groups**: Establish new groups with custom settings
- **Delete Groups**: Remove groups (with member verification)
- **Manage Members**: Add/remove users from groups

### 🏢 Organizational Unit Management (5 tools)
- **List OUs**: Browse organizational structure
- **Get OU Details**: Detailed organizational unit information
- **Create OUs**: Establish new organizational units
- **Update OUs**: Modify OU properties and parent relationships
- **Delete OUs**: Remove organizational units (with user checks)

### 📱 Device Management (5 tools)
- **List Mobile Devices**: View all mobile devices by user/domain
- **Get Mobile Device**: Detailed mobile device information
- **Manage Mobile Devices**: Remote wipe, approve, block actions
- **List Chrome Devices**: View all Chrome OS devices
- **Get Chrome Device**: Detailed Chrome device information

### 📊 Reports & Auditing (4 tools)
- **User Usage Reports**: Detailed application usage with custom parameters
- **Audit Activities**: Comprehensive activity logs across all applications
- **Customer Usage Reports**: Domain-level usage analytics and quotas
- **Domain Insights**: Security and activity insights with trend analysis

### 🔐 Security Management (5 tools)
- **Domain Aliases**: List and manage domain aliases
- **User Security**: 2SV enforcement, admin status, session management
- **Token Management**: OAuth tokens and app password visibility
- **Role Assignments**: Admin role management and delegation
- **Data Transfer**: User data transfer for departing employees

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/ryanrobson/claude-gsuite-admin-mcp.git
cd claude-gsuite-admin-mcp
pip install -e .

# 2. Setup OAuth credentials (see detailed setup guide)
cp .gauth.json.example .gauth.json
cp .accounts.json.example .accounts.json
# Edit with your Google Cloud Console OAuth credentials

# 3. Complete authentication
python complete_oauth.py

# 4. Validate setup
python scripts/validate_setup.py

# 5. Start using with Claude CLI
# "List all users in my Google Workspace domain"
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Google Workspace Admin account
- Claude CLI installed and configured
- Google Cloud Console project with Admin SDK APIs enabled

### Detailed Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ryanrobson/claude-gsuite-admin-mcp.git
   cd claude-gsuite-admin-mcp
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download and save as `.gauth.json`
   - Configure your admin account in `.accounts.json`

4. **Add to Claude CLI:**
   - The server will automatically register with Claude CLI
   - Permissions will be added to your settings

## Configuration

### OAuth Configuration (`.gauth.json`)
```json
{
    "installed": {
        "client_id": "your-client-id.apps.googleusercontent.com",
        "client_secret": "your-client-secret",
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
}
```

### Account Configuration (`.accounts.json`)
```json
{
    "accounts": [
        {
            "email": "admin@yourdomain.com",
            "account_type": "admin",
            "extra_info": "Primary Google Workspace admin account"
        }
    ]
}
```

## Usage

Once configured, you can use Claude CLI to perform Google Workspace admin tasks:

```bash
# User management examples
"Create a new user john.doe@company.com with temporary password"
"List all users in the Engineering OU"
"Suspend the user account for jane.smith@company.com"

# Group management examples
"Create a new group called 'marketing-team@company.com'"
"Add john.doe@company.com to the sales-team group"
"List all members of the executives group"

# Device management examples
"List all mobile devices for user john.doe@company.com"
"Wipe the mobile device with ID abc123"
"Generate a device usage report for the last 30 days"

# Reporting examples
"Show me the user activity report for last week"
"Generate an audit log for admin actions in the past month"
"Get security alerts for suspicious login attempts"
```

## Available Tools

### User Management
- `mcp__gsuite_admin__create_user` - Create new users
- `mcp__gsuite_admin__update_user` - Update user properties
- `mcp__gsuite_admin__delete_user` - Delete users
- `mcp__gsuite_admin__suspend_user` - Suspend/unsuspend users
- `mcp__gsuite_admin__reset_password` - Reset user passwords
- `mcp__gsuite_admin__list_users` - List/search users
- `mcp__gsuite_admin__get_user` - Get user details
- `mcp__gsuite_admin__manage_aliases` - Manage user aliases

### Group Management
- `mcp__gsuite_admin__create_group` - Create groups
- `mcp__gsuite_admin__update_group` - Update group settings
- `mcp__gsuite_admin__delete_group` - Delete groups
- `mcp__gsuite_admin__list_groups` - List/search groups
- `mcp__gsuite_admin__manage_members` - Add/remove members
- `mcp__gsuite_admin__list_members` - List group members

### Organizational Units
- `mcp__gsuite_admin__create_org_unit` - Create OUs
- `mcp__gsuite_admin__update_org_unit` - Update OUs
- `mcp__gsuite_admin__delete_org_unit` - Delete OUs
- `mcp__gsuite_admin__list_org_units` - List OUs
- `mcp__gsuite_admin__move_users` - Move users between OUs

### Device Management
- `mcp__gsuite_admin__list_mobile_devices` - List mobile devices
- `mcp__gsuite_admin__manage_mobile_device` - Wipe/block devices
- `mcp__gsuite_admin__list_chrome_devices` - List Chrome devices
- `mcp__gsuite_admin__manage_chrome_device` - Manage Chrome devices

### Reports & Auditing
- `mcp__gsuite_admin__get_usage_reports` - Usage statistics
- `mcp__gsuite_admin__get_audit_logs` - Audit log retrieval
- `mcp__gsuite_admin__get_security_reports` - Security events
- `mcp__gsuite_admin__get_device_reports` - Device reports

## Security

This MCP server requires extensive Google Workspace admin permissions. Please ensure:

- OAuth credentials are kept secure and not committed to version control
- The `.gauth.json` and `.accounts.json` files are added to `.gitignore`
- Regular audit of admin actions performed through the MCP
- Principle of least privilege when assigning Google Workspace admin roles

## Development

### Setting up development environment

1. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run tests:**
   ```bash
   pytest
   ```

3. **Format code:**
   ```bash
   black src/ tests/
   ```

4. **Type checking:**
   ```bash
   mypy src/
   ```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

- 📖 **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration guide
- 🔧 **[API Documentation](docs/API.md)** - Detailed documentation for all 31 tools
- 💡 **[Usage Examples](docs/EXAMPLES.md)** - Practical examples and workflows
- 🤝 **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ryanrobson/claude-gsuite-admin-mcp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ryanrobson/claude-gsuite-admin-mcp/discussions)
- 📚 **Google Workspace Docs**: [Admin SDK Documentation](https://developers.google.com/admin-sdk)

## Key Features

✅ **Production Ready** - Comprehensive error handling, rate limiting, and retry logic
✅ **Secure Authentication** - OAuth2 with automatic token refresh and secure credential storage
✅ **31 Admin Tools** - Complete coverage of Google Workspace administrative functions
✅ **Natural Language Interface** - Use plain English commands through Claude CLI
✅ **Extensive Documentation** - Complete setup guides, API docs, and usage examples
✅ **Type Safety** - Full type hints and mypy compatibility
✅ **Testing** - Comprehensive test suite with validation scripts

## Changelog

### v0.1.0 (Initial Release)
- Core Google Workspace admin functionality
- User, group, and organizational unit management
- Device management and reporting
- Security and domain administration
- Claude CLI integration

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.