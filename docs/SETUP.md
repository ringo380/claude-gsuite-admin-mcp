# Setup Guide

This guide will walk you through setting up the Claude Google Workspace Admin MCP server.

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher
- Google Workspace domain with admin access
- Claude CLI installed and configured
- Access to Google Cloud Console

## Step 1: Google Cloud Console Setup

### 1.1 Create a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 1.2 Enable APIs

Enable the following APIs in your project:
- Admin SDK API
- Gmail API
- Calendar API
- Reports API

```bash
# Using gcloud CLI (if available)
gcloud services enable admin.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable calendar-json.googleapis.com
gcloud services enable reports.googleapis.com
```

### 1.3 Create OAuth2 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth 2.0 Client IDs**
3. Choose **Desktop Application**
4. Name your client (e.g., "Claude GSuite Admin MCP")
5. Download the JSON file

## Step 2: Install the MCP Server

### 2.1 Clone and Install

```bash
git clone https://github.com/ryanrobson/claude-gsuite-admin-mcp.git
cd claude-gsuite-admin-mcp
pip install -e .
```

### 2.2 Install Development Dependencies (Optional)

```bash
pip install -e ".[dev]"
```

## Step 3: Configuration

### 3.1 OAuth Configuration

1. Rename the downloaded OAuth JSON file to `.gauth.json`
2. Place it in the project root directory

Example `.gauth.json`:
```json
{
    "installed": {
        "client_id": "your-client-id.apps.googleusercontent.com",
        "client_secret": "GOCSPX-your-client-secret",
        "redirect_uris": ["http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
    }
}
```

### 3.2 Account Configuration

Create `.accounts.json` with your admin accounts:

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

## Step 4: OAuth Authentication

### 4.1 Complete OAuth Flow

Run the OAuth setup script:

```bash
python complete_oauth.py
```

This will:
1. Open a browser window
2. Prompt you to sign in to Google
3. Request necessary permissions
4. Save authentication tokens

### 4.2 Verify Authentication

Test authentication:

```bash
python test_auth.py
```

## Step 5: Claude CLI Integration

### 5.1 Automatic Registration

The MCP server should automatically register with Claude CLI. Verify by checking:

```bash
# Check if the server is registered
cat ~/.claude/settings.json | grep gsuite
```

### 5.2 Manual Registration (if needed)

If automatic registration failed, manually add to `~/.claude/settings.json`:

```json
{
  "mcp_servers": {
    "claude-gsuite-admin": {
      "command": "python",
      "args": ["/path/to/claude-gsuite-admin-mcp/src/claude_gsuite_admin/server.py"],
      "cwd": "/path/to/claude-gsuite-admin-mcp"
    }
  }
}
```

## Step 6: Testing

### 6.1 Run Basic Tests

```bash
# Test all functionality
python test_comprehensive.py

# Test specific areas
python test_users.py
python test_groups.py
python test_devices.py
```

### 6.2 Test with Claude CLI

Start a Claude CLI session and try:

```
List all users in my Google Workspace domain
```

## Step 7: Verification

### 7.1 Check Tool Registration

Verify all 31 tools are available:

```bash
python -c "from claude_gsuite_admin.server import TOOL_HANDLERS; print(f'Registered {len(TOOL_HANDLERS)} tools')"
```

### 7.2 Test Core Functionality

Try these Claude CLI commands:
- "List all users in the Engineering OU"
- "Create a new group called test-group@yourdomain.com"
- "Show me device usage reports for last week"

## Troubleshooting

### Common Issues

#### Authentication Errors
- Verify `.gauth.json` contains valid OAuth credentials
- Check that your Google account has admin privileges
- Re-run `python complete_oauth.py` to refresh tokens

#### Permission Errors
- Ensure your admin account has sufficient privileges
- Check Google Workspace admin console for role assignments
- Verify APIs are enabled in Google Cloud Console

#### Import Errors
- Ensure all dependencies are installed: `pip install -e .`
- Check Python version compatibility (3.10+)
- Verify package structure with `python -c "import claude_gsuite_admin"`

#### Claude CLI Integration Issues
- Check `~/.claude/settings.json` for MCP server registration
- Verify Claude CLI is updated to latest version
- Restart Claude CLI after configuration changes

### Validation Script

Run the validation script to check your setup:

```bash
python scripts/validate_setup.py
```

This will verify:
- Python version compatibility
- Required dependencies
- OAuth configuration
- Authentication status
- Claude CLI integration

## Security Best Practices

1. **Protect Credentials**: Never commit `.gauth.json` or `.oauth*.json` files
2. **Limit Scope**: Use least-privilege admin accounts when possible
3. **Regular Audits**: Monitor admin actions through audit logs
4. **Token Rotation**: Periodically refresh OAuth tokens
5. **Access Control**: Restrict who can use the MCP server

## Next Steps

After successful setup:
1. Explore the [API Documentation](API.md)
2. Review [Usage Examples](EXAMPLES.md)
3. Set up monitoring and logging
4. Configure backup and disaster recovery

## Support

If you encounter issues:
1. Check the [troubleshooting section](#troubleshooting)
2. Review logs in `~/.claude/logs/`
3. Open an issue on [GitHub](https://github.com/ryanrobson/claude-gsuite-admin-mcp/issues)
4. Consult Google Workspace Admin documentation