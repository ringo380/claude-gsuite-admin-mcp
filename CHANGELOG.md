# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release preparation
- Comprehensive documentation
- Setup validation scripts

## [0.1.0] - 2025-09-23

### Added
- Initial release of Claude Google Workspace Admin MCP Server
- 31 comprehensive Google Workspace administrative tools
- OAuth2 authentication system with automatic token refresh
- Support for 6 major functional areas:
  - **User Management (7 tools)**: Create, update, suspend, delete users; password resets; user search and filtering
  - **Group Management (5 tools)**: Create, delete groups; manage memberships; group search and listing
  - **Organizational Unit Management (5 tools)**: Create, update, delete OUs; manage OU hierarchy
  - **Device Management (5 tools)**: Mobile and Chrome OS device listing, management, and remote actions
  - **Reports & Auditing (4 tools)**: Usage reports, audit logs, customer insights, domain analytics
  - **Security Management (5 tools)**: Domain aliases, user security settings, token management, role assignments, data transfers

### Features
- **Comprehensive Authentication**: Full OAuth2 flow with scope management for all required Google Workspace APIs
- **Error Handling**: Robust error handling with detailed error messages and automatic retry logic
- **Rate Limiting**: Built-in handling of Google API rate limits with exponential backoff
- **Security**: Secure credential storage and management with proper file permissions
- **Validation**: Input validation and parameter checking for all operations
- **Logging**: Comprehensive logging for debugging and audit purposes
- **Testing**: Extensive test suite covering all major functionality

### Documentation
- Complete API documentation with examples for all 31 tools
- Detailed setup guide with step-by-step instructions
- Usage examples for common administrative tasks
- Troubleshooting guide for common issues
- Security best practices and recommendations

### Configuration
- Example configuration files for OAuth and account setup
- Proper .gitignore to protect sensitive credentials
- MCP server configuration for Claude CLI integration
- Support for multiple admin accounts with different privilege levels

### Development
- Modern Python packaging with pyproject.toml
- Type hints and mypy configuration
- Black code formatting configuration
- Pytest test configuration
- Development dependency management

### Security
- OAuth2 with comprehensive Google Workspace scopes
- Secure token storage and refresh mechanisms
- Protection of sensitive configuration files
- Admin privilege validation and enforcement
- Audit logging for all administrative actions

### Claude CLI Integration
- Native MCP protocol implementation
- Automatic tool registration with Claude CLI
- Seamless integration with Claude's natural language interface
- Support for complex multi-step administrative workflows

## Security Advisories

### OAuth Scopes Required
This MCP server requires extensive Google Workspace admin permissions including:
- Directory API (users, groups, organizational units, devices)
- Reports API (usage analytics and audit logs)
- Admin SDK (domain and security management)
- Gmail API (for email-related operations)
- Calendar API (for calendar-related operations)

### Important Security Notes
- Always protect your `.gauth.json` and `.oauth*.json` files
- Use least-privilege admin accounts when possible
- Regularly audit admin actions through the built-in reporting tools
- Monitor for unusual access patterns or unauthorized activities
- Keep OAuth tokens secure and rotate them periodically

## Migration Guide

### From Development to Production
1. Ensure all sensitive files are properly excluded from version control
2. Set up proper monitoring and alerting for admin activities
3. Configure backup and disaster recovery procedures
4. Implement proper access controls and admin role assignments
5. Establish regular audit and compliance checking procedures

## Support and Compatibility

### Requirements
- Python 3.10 or higher
- Google Workspace domain with admin access
- Claude CLI with MCP support
- Active internet connection for Google API access

### Tested Environments
- macOS (Darwin 24.6.0)
- Python 3.10, 3.11, 3.12
- Google Workspace Business and Enterprise editions
- Claude CLI latest versions

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.