"""OAuth2 authentication manager for Google Workspace Admin APIs."""

import logging
import os
import json
import argparse
from typing import Dict, List, Optional, Any
from oauth2client.client import (
    flow_from_clientsecrets,
    FlowExchangeError,
    OAuth2Credentials,
    Credentials,
)
from googleapiclient.discovery import build
import httplib2
from google.auth.transport.requests import Request
import pydantic


# Comprehensive Google Workspace Admin API scopes
ADMIN_SCOPES = [
    # Basic authentication
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",

    # User Management
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.user.alias",
    "https://www.googleapis.com/auth/admin.directory.user.security",

    # Group Management
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member",
    "https://www.googleapis.com/auth/apps.groups.settings",

    # Organizational Units
    "https://www.googleapis.com/auth/admin.directory.orgunit",

    # Device Management
    "https://www.googleapis.com/auth/admin.directory.device.mobile",
    "https://www.googleapis.com/auth/admin.directory.device.chromeos",

    # Domain Management
    "https://www.googleapis.com/auth/admin.directory.domain",

    # Reports & Auditing
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
    "https://www.googleapis.com/auth/admin.reports.usage.readonly",

    # Customer Management
    "https://www.googleapis.com/auth/admin.directory.customer",

    # Role Management
    "https://www.googleapis.com/auth/admin.directory.rolemanagement",

    # Gmail & Calendar (compatibility with existing tools)
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",

    # Additional admin scopes
    "https://www.googleapis.com/auth/admin.directory.resource.calendar",
    "https://www.googleapis.com/auth/admin.directory.notifications",
]

# OAuth redirect URI for desktop applications
REDIRECT_URI = 'http://localhost:4100/code'

# Default paths for configuration files
# Default paths - use environment variables or fall back to project directory
# This file is at: src/claude_gsuite_admin/auth/oauth_manager.py
# Project root is: ../../../ from here
_project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_GAUTH_FILE = os.environ.get("GSUITE_GAUTH_FILE", os.path.join(_project_dir, ".gauth.json"))
DEFAULT_ACCOUNTS_FILE = os.environ.get("GSUITE_ACCOUNTS_FILE", os.path.join(_project_dir, ".accounts.json"))



class AccountInfo(pydantic.BaseModel):
    """Information about a Google Workspace account."""

    email: str
    account_type: str
    extra_info: str = ""

    def __init__(self, email: str, account_type: str, extra_info: str = ""):
        super().__init__(email=email, account_type=account_type, extra_info=extra_info)

    def to_description(self) -> str:
        """Return a human-readable description of the account."""
        return f"Account for email: {self.email} of type: {self.account_type}. Extra info: {self.extra_info}"


class OAuthManager:
    """Manages OAuth2 authentication for Google Workspace Admin APIs."""

    def __init__(self, gauth_file: str = None, accounts_file: str = None):
        self.gauth_file = gauth_file or DEFAULT_GAUTH_FILE
        self.accounts_file = accounts_file or DEFAULT_ACCOUNTS_FILE
        self._cached_credentials: Dict[str, OAuth2Credentials] = {}

    def get_oauth_flow(self) -> Any:
        """Create and return an OAuth2 flow object."""
        if not os.path.exists(self.gauth_file):
            raise FileNotFoundError(f"OAuth configuration file not found: {self.gauth_file}")

        flow = flow_from_clientsecrets(
            self.gauth_file,
            scope=ADMIN_SCOPES,
            redirect_uri=REDIRECT_URI
        )
        return flow

    def get_stored_credentials(self, user_id: str) -> Optional[OAuth2Credentials]:
        """Retrieve stored credentials for a user."""
        if user_id in self._cached_credentials:
            logging.info(f"Found cached credentials for {user_id}")
            return self._cached_credentials[user_id]

        oauth_dir = os.environ.get("GSUITE_OAUTH_DIR", _project_dir)
        creds_file = os.path.join(oauth_dir, f".oauth2.{user_id}.json")
        logging.info(f"Looking for credentials at: {creds_file}")
        if not os.path.exists(creds_file):
            logging.warning(f"No stored OAuth2 credentials at path: {creds_file}")
            return None

        try:
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)

            credentials = OAuth2Credentials.from_json(json.dumps(creds_data))

            # Check if credentials are valid and refresh if needed
            if credentials.access_token_expired:
                http = httplib2.Http()
                try:
                    credentials.refresh(http)
                    self.save_credentials(user_id, credentials)
                    logging.info(f"Refreshed credentials for {user_id}")
                except Exception as e:
                    logging.error(f"Failed to refresh credentials for {user_id}: {e}")
                    return None

            self._cached_credentials[user_id] = credentials
            return credentials

        except Exception as e:
            logging.error(f"Error loading credentials for {user_id}: {e}")
            return None

    def save_credentials(self, user_id: str, credentials: OAuth2Credentials) -> None:
        """Save credentials to file."""
        oauth_dir = os.environ.get("GSUITE_OAUTH_DIR", _project_dir)
        creds_file = os.path.join(oauth_dir, f".oauth2.{user_id}.json")
        try:
            with open(creds_file, 'w') as f:
                f.write(credentials.to_json())
            logging.info(f"Saved credentials for {user_id}")
            self._cached_credentials[user_id] = credentials
        except Exception as e:
            logging.error(f"Failed to save credentials for {user_id}: {e}")

    def get_credentials(self, user_id: str, authorization_code: str = None) -> Optional[OAuth2Credentials]:
        """Get credentials for a user, either from storage or by exchanging auth code."""
        # Try to get stored credentials first
        credentials = self.get_stored_credentials(user_id)
        if credentials:
            return credentials

        # If no stored credentials and no auth code, return None
        if not authorization_code:
            return None

        # Exchange authorization code for credentials
        try:
            flow = self.get_oauth_flow()
            credentials = flow.step2_exchange(authorization_code)
            self.save_credentials(user_id, credentials)
            return credentials
        except FlowExchangeError as e:
            logging.error(f"OAuth flow exchange failed: {e}")
            return None

    def get_service(self, user_id: str, service_name: str, version: str = 'v1'):
        """Get a Google API service client for a user."""
        credentials = self.get_stored_credentials(user_id)
        if not credentials:
            raise ValueError(f"No valid credentials found for user: {user_id}")

        http = credentials.authorize(httplib2.Http())
        return build(service_name, version, http=http)

    def revoke_credentials(self, user_id: str) -> bool:
        """Revoke stored credentials for a user."""
        credentials = self.get_stored_credentials(user_id)
        if not credentials:
            return False

        try:
            credentials.revoke(httplib2.Http())
            # Remove from cache and delete file
            if user_id in self._cached_credentials:
                del self._cached_credentials[user_id]

            oauth_dir = os.environ.get("GSUITE_OAUTH_DIR", _project_dir)
            creds_file = os.path.join(oauth_dir, f".oauth2.{user_id}.json")
            if os.path.exists(creds_file):
                os.remove(creds_file)

            logging.info(f"Revoked credentials for {user_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to revoke credentials for {user_id}: {e}")
            return False


def get_gauth_file() -> str:
    """Get the path to the OAuth configuration file from command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gauth-file",
        type=str,
        default=DEFAULT_GAUTH_FILE,
        help="Path to client secrets file",
    )
    args, _ = parser.parse_known_args()
    return args.gauth_file


def get_accounts_file() -> str:
    """Get the path to the accounts configuration file from command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--accounts-file",
        type=str,
        default=DEFAULT_ACCOUNTS_FILE,
        help="Path to accounts configuration file"
    )
    args, _ = parser.parse_known_args()
    return args.accounts_file


def get_credentials_dir() -> str:
    """Get the directory for storing credentials from command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--credentials-dir",
        type=str,
        default="./",
        help="Directory to store OAuth credentials"
    )
    args, _ = parser.parse_known_args()
    return args.credentials_dir


def get_account_info() -> List[AccountInfo]:
    """Load account information from configuration file."""
    accounts_file = get_accounts_file()
    if not os.path.exists(accounts_file):
        raise FileNotFoundError(f"Accounts configuration file not found: {accounts_file}")

    try:
        with open(accounts_file, 'r') as f:
            data = json.load(f)

        accounts = []
        for account_data in data.get('accounts', []):
            account = AccountInfo(
                email=account_data['email'],
                account_type=account_data['account_type'],
                extra_info=account_data.get('extra_info', '')
            )
            accounts.append(account)

        return accounts
    except Exception as e:
        logging.error(f"Error loading account information: {e}")
        return []


def get_stored_credentials(user_id: str) -> Optional[OAuth2Credentials]:
    """Get stored credentials for a user (convenience function)."""
    oauth_manager = OAuthManager()
    return oauth_manager.get_stored_credentials(user_id)


def get_credentials(user_id: str, authorization_code: str = None) -> Optional[OAuth2Credentials]:
    """Get credentials for a user (convenience function)."""
    oauth_manager = OAuthManager()
    return oauth_manager.get_credentials(user_id, authorization_code)