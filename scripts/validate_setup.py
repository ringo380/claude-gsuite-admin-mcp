#!/usr/bin/env python3
"""
Setup validation script for Claude Google Workspace Admin MCP Server.

This script validates that the MCP server is properly configured and ready for use.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message: str, status: str, details: str = ""):
    """Print status message with color coding."""
    color = GREEN if status == "OK" else RED if status == "ERROR" else YELLOW
    print(f"{message:<50} [{color}{status}{RESET}]")
    if details:
        print(f"  {details}")

def check_python_version() -> Tuple[bool, str]:
    """Check Python version compatibility."""
    version = sys.version_info
    if version >= (3, 10):
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)"

def check_file_exists(filepath: str, description: str) -> Tuple[bool, str]:
    """Check if a file exists."""
    if os.path.exists(filepath):
        return True, f"Found {filepath}"
    else:
        return False, f"Missing {filepath}"

def check_package_installed(package: str) -> Tuple[bool, str]:
    """Check if a Python package is installed."""
    try:
        result = subprocess.run([sys.executable, "-c", f"import {package}"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"{package} is installed"
        else:
            return False, f"{package} not found"
    except Exception as e:
        return False, f"Error checking {package}: {str(e)}"

def check_oauth_config() -> Tuple[bool, str]:
    """Check OAuth configuration file."""
    if not os.path.exists('.gauth.json'):
        return False, "OAuth config not found (.gauth.json missing)"

    try:
        with open('.gauth.json', 'r') as f:
            config = json.load(f)

        if 'installed' not in config:
            return False, "Invalid OAuth config (missing 'installed' section)"

        required_fields = ['client_id', 'client_secret', 'redirect_uris', 'auth_uri', 'token_uri']
        missing_fields = [field for field in required_fields if field not in config['installed']]

        if missing_fields:
            return False, f"OAuth config missing fields: {', '.join(missing_fields)}"

        return True, "OAuth configuration is valid"
    except json.JSONDecodeError:
        return False, "OAuth config is not valid JSON"
    except Exception as e:
        return False, f"Error reading OAuth config: {str(e)}"

def check_accounts_config() -> Tuple[bool, str]:
    """Check accounts configuration file."""
    if not os.path.exists('.accounts.json'):
        return False, "Accounts config not found (.accounts.json missing)"

    try:
        with open('.accounts.json', 'r') as f:
            config = json.load(f)

        if 'accounts' not in config:
            return False, "Invalid accounts config (missing 'accounts' section)"

        if not config['accounts']:
            return False, "No accounts configured"

        admin_accounts = [acc for acc in config['accounts'] if acc.get('account_type') == 'admin']
        if not admin_accounts:
            return False, "No admin accounts configured"

        return True, f"Found {len(config['accounts'])} accounts, {len(admin_accounts)} admin"
    except json.JSONDecodeError:
        return False, "Accounts config is not valid JSON"
    except Exception as e:
        return False, f"Error reading accounts config: {str(e)}"

def check_authentication() -> Tuple[bool, str]:
    """Check if OAuth authentication is completed."""
    # Look for OAuth token files
    oauth_files = [f for f in os.listdir('.') if f.startswith('.oauth2.') and f.endswith('.json')]

    if not oauth_files:
        return False, "No OAuth tokens found (run complete_oauth.py)"

    try:
        # Try to import and get account info
        from claude_gsuite_admin.auth.oauth_manager import get_account_info

        # Check if we can load accounts
        accounts = get_account_info()
        if not accounts:
            return False, "No authenticated accounts found"

        return True, f"Authentication configured for {len(accounts)} accounts"
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def check_package_import() -> Tuple[bool, str]:
    """Check if the package can be imported successfully."""
    try:
        import claude_gsuite_admin
        from claude_gsuite_admin.server import tool_handlers
        return True, f"Package imports successfully, {len(tool_handlers)} tools registered"
    except Exception as e:
        return False, f"Import error: {str(e)}"

def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Check all required dependencies."""
    dependencies = [
        'mcp',
        'google.auth',
        'googleapiclient',
        'oauth2client',
        'requests',
        'httplib2'
    ]

    results = []
    for dep in dependencies:
        success, message = check_package_installed(dep)
        results.append((dep, success, message))

    return results

def check_claude_cli() -> Tuple[bool, str]:
    """Check if Claude CLI is available and configured."""
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"Claude CLI available: {result.stdout.strip()}"
        else:
            return False, "Claude CLI not found or not working"
    except FileNotFoundError:
        return False, "Claude CLI not installed"
    except Exception as e:
        return False, f"Error checking Claude CLI: {str(e)}"

def check_mcp_config() -> Tuple[bool, str]:
    """Check MCP configuration for Claude CLI."""
    if os.path.exists('.mcp.json'):
        return True, "MCP configuration found"
    else:
        return False, "MCP configuration not found (.mcp.json missing)"

def run_tests() -> Tuple[bool, str]:
    """Run basic tests to verify functionality."""
    try:
        # Test authentication
        result = subprocess.run([sys.executable, 'test_auth.py'],
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, "Basic authentication test passed"
        else:
            return False, f"Authentication test failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Authentication test timed out"
    except FileNotFoundError:
        return False, "test_auth.py not found"
    except Exception as e:
        return False, f"Error running tests: {str(e)}"

def main():
    """Main validation function."""
    print(f"{BLUE}Claude Google Workspace Admin MCP Server - Setup Validation{RESET}")
    print("=" * 70)

    all_checks_passed = True

    # Basic system checks
    print(f"\n{BLUE}System Requirements{RESET}")
    success, details = check_python_version()
    print_status("Python Version", "OK" if success else "ERROR", details)
    if not success:
        all_checks_passed = False

    # File existence checks
    print(f"\n{BLUE}Configuration Files{RESET}")
    files_to_check = [
        ('.gauth.json', 'OAuth credentials'),
        ('.accounts.json', 'Account configuration'),
        ('.mcp.json', 'MCP configuration'),
        ('requirements.txt', 'Dependencies list'),
        ('README.md', 'Documentation'),
        ('src/claude_gsuite_admin/server.py', 'Main server module')
    ]

    for filepath, description in files_to_check:
        success, details = check_file_exists(filepath, description)
        print_status(f"{description}", "OK" if success else "ERROR", details)
        if not success and filepath in ['.gauth.json', '.accounts.json']:
            all_checks_passed = False

    # OAuth configuration validation
    print(f"\n{BLUE}OAuth Configuration{RESET}")
    success, details = check_oauth_config()
    print_status("OAuth Config Validation", "OK" if success else "ERROR", details)
    if not success:
        all_checks_passed = False

    # Accounts configuration validation
    success, details = check_accounts_config()
    print_status("Accounts Config Validation", "OK" if success else "ERROR", details)
    if not success:
        all_checks_passed = False

    # Dependency checks
    print(f"\n{BLUE}Dependencies{RESET}")
    deps = check_dependencies()
    for dep, success, details in deps:
        print_status(f"{dep} package", "OK" if success else "ERROR", details)
        if not success:
            all_checks_passed = False

    # Package import check
    print(f"\n{BLUE}Package Status{RESET}")
    success, details = check_package_import()
    print_status("Package Import", "OK" if success else "ERROR", details)
    if not success:
        all_checks_passed = False

    # Authentication check
    success, details = check_authentication()
    print_status("OAuth Authentication", "OK" if success else "WARN", details)
    if not success:
        print(f"  {YELLOW}Run 'python complete_oauth.py' to complete authentication{RESET}")

    # Claude CLI integration
    print(f"\n{BLUE}Claude CLI Integration{RESET}")
    success, details = check_claude_cli()
    print_status("Claude CLI", "OK" if success else "WARN", details)

    success, details = check_mcp_config()
    print_status("MCP Configuration", "OK" if success else "WARN", details)

    # Basic functionality tests
    print(f"\n{BLUE}Functionality Tests{RESET}")
    success, details = run_tests()
    print_status("Basic Tests", "OK" if success else "WARN", details)

    # Summary
    print(f"\n{BLUE}Summary{RESET}")
    if all_checks_passed:
        print(f"{GREEN}✓ All critical checks passed! The MCP server should be ready for use.{RESET}")
        print(f"\nNext steps:")
        print(f"1. Complete OAuth authentication: python complete_oauth.py")
        print(f"2. Test with Claude CLI: Start Claude and try 'List all users'")
        print(f"3. Review the documentation in docs/ for usage examples")
    else:
        print(f"{RED}✗ Some critical checks failed. Please address the errors above.{RESET}")
        print(f"\nCommon solutions:")
        print(f"1. Install dependencies: pip install -e .")
        print(f"2. Set up OAuth: Copy your Google OAuth credentials to .gauth.json")
        print(f"3. Configure accounts: Copy .accounts.json.example to .accounts.json and edit")
        print(f"4. Complete authentication: python complete_oauth.py")

    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())