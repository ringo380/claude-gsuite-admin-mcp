"""Unit tests for OAuth Manager."""

import os
import json
import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path

from claude_gsuite_admin.auth.oauth_manager import (
    OAuthManager,
    AccountInfo,
    get_gauth_file,
    get_accounts_file,
    get_account_info,
    ADMIN_SCOPES,
    REDIRECT_URI
)
from claude_gsuite_admin.core.exceptions import AuthenticationError


class TestOAuthManager:
    """Test OAuth Manager functionality."""

    def test_init(self):
        """Test OAuthManager initialization."""
        manager = OAuthManager()
        assert manager.gauth_file is not None
        assert manager.accounts_file is not None
        assert manager._cached_credentials == {}

    def test_init_with_custom_files(self):
        """Test OAuthManager initialization with custom files."""
        gauth_file = "/custom/gauth.json"
        accounts_file = "/custom/accounts.json"
        manager = OAuthManager(gauth_file, accounts_file)
        assert manager.gauth_file == gauth_file
        assert manager.accounts_file == accounts_file

    @patch('claude_gsuite_admin.auth.oauth_manager.flow_from_clientsecrets')
    @patch('os.path.exists')
    def test_get_oauth_flow_success(self, mock_exists, mock_flow):
        """Test successful OAuth flow creation."""
        mock_exists.return_value = True
        mock_flow_instance = Mock()
        mock_flow.return_value = mock_flow_instance

        manager = OAuthManager()
        result = manager.get_oauth_flow()

        assert result == mock_flow_instance
        mock_flow.assert_called_once_with(
            manager.gauth_file,
            scope=ADMIN_SCOPES,
            redirect_uri=REDIRECT_URI
        )

    @patch('os.path.exists')
    def test_get_oauth_flow_file_not_found(self, mock_exists):
        """Test OAuth flow creation with missing file."""
        mock_exists.return_value = False
        manager = OAuthManager()

        with pytest.raises(FileNotFoundError):
            manager.get_oauth_flow()

    @patch('builtins.open', new_callable=mock_open, read_data='{"access_token": "test"}')
    @patch('os.path.exists')
    @patch('claude_gsuite_admin.auth.oauth_manager.OAuth2Credentials')
    def test_get_stored_credentials_success(self, mock_oauth2_creds, mock_exists, mock_file):
        """Test successful credential retrieval."""
        mock_exists.return_value = True
        mock_creds = Mock()
        mock_creds.access_token_expired = False
        mock_oauth2_creds.from_json.return_value = mock_creds

        manager = OAuthManager()
        result = manager.get_stored_credentials("test@example.com")

        assert result == mock_creds
        assert manager._cached_credentials["test@example.com"] == mock_creds

    @patch('os.path.exists')
    def test_get_stored_credentials_file_not_found(self, mock_exists):
        """Test credential retrieval with missing file."""
        mock_exists.return_value = False
        manager = OAuthManager()

        result = manager.get_stored_credentials("test@example.com")
        assert result is None

    def test_get_stored_credentials_cached(self):
        """Test cached credential retrieval."""
        manager = OAuthManager()
        cached_creds = Mock()
        manager._cached_credentials["test@example.com"] = cached_creds

        result = manager.get_stored_credentials("test@example.com")
        assert result == cached_creds

    @patch('builtins.open', new_callable=mock_open)
    def test_save_credentials(self, mock_file):
        """Test credential saving."""
        manager = OAuthManager()
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"access_token": "test"}'

        manager.save_credentials("test@example.com", mock_creds)

        mock_file.assert_called_once()
        assert manager._cached_credentials["test@example.com"] == mock_creds

    @patch.object(OAuthManager, 'get_stored_credentials')
    @patch.object(OAuthManager, 'get_oauth_flow')
    @patch.object(OAuthManager, 'save_credentials')
    def test_get_credentials_with_auth_code(self, mock_save, mock_flow, mock_stored):
        """Test credential retrieval with authorization code."""
        mock_stored.return_value = None
        mock_flow_instance = Mock()
        mock_flow.return_value = mock_flow_instance
        mock_creds = Mock()
        mock_flow_instance.step2_exchange.return_value = mock_creds

        manager = OAuthManager()
        result = manager.get_credentials("test@example.com", "auth_code")

        assert result == mock_creds
        mock_save.assert_called_once_with("test@example.com", mock_creds)

    @patch.object(OAuthManager, 'get_stored_credentials')
    def test_get_credentials_existing(self, mock_stored):
        """Test credential retrieval with existing credentials."""
        existing_creds = Mock()
        mock_stored.return_value = existing_creds

        manager = OAuthManager()
        result = manager.get_credentials("test@example.com")

        assert result == existing_creds

    @patch.object(OAuthManager, 'get_stored_credentials')
    @patch('claude_gsuite_admin.auth.oauth_manager.build')
    def test_get_service_success(self, mock_build, mock_stored):
        """Test successful service creation."""
        mock_creds = Mock()
        mock_stored.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        manager = OAuthManager()
        result = manager.get_service("test@example.com", "admin", "directory_v1")

        assert result == mock_service
        mock_build.assert_called_once()

    @patch.object(OAuthManager, 'get_stored_credentials')
    def test_get_service_no_credentials(self, mock_stored):
        """Test service creation with no credentials."""
        mock_stored.return_value = None

        manager = OAuthManager()
        with pytest.raises(ValueError, match="No valid credentials found"):
            manager.get_service("test@example.com", "admin")

    @patch.object(OAuthManager, 'get_stored_credentials')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_revoke_credentials_success(self, mock_remove, mock_exists, mock_stored):
        """Test successful credential revocation."""
        mock_creds = Mock()
        mock_stored.return_value = mock_creds
        mock_exists.return_value = True

        manager = OAuthManager()
        manager._cached_credentials["test@example.com"] = mock_creds

        result = manager.revoke_credentials("test@example.com")

        assert result is True
        mock_creds.revoke.assert_called_once()
        assert "test@example.com" not in manager._cached_credentials
        mock_remove.assert_called_once()

    @patch.object(OAuthManager, 'get_stored_credentials')
    def test_revoke_credentials_no_credentials(self, mock_stored):
        """Test credential revocation with no credentials."""
        mock_stored.return_value = None

        manager = OAuthManager()
        result = manager.revoke_credentials("test@example.com")

        assert result is False


class TestAccountInfo:
    """Test AccountInfo class."""

    def test_init(self):
        """Test AccountInfo initialization."""
        account = AccountInfo("test@example.com", "admin", "Test account")
        assert account.email == "test@example.com"
        assert account.account_type == "admin"
        assert account.extra_info == "Test account"

    def test_init_minimal(self):
        """Test AccountInfo initialization with minimal data."""
        account = AccountInfo("test@example.com", "admin")
        assert account.email == "test@example.com"
        assert account.account_type == "admin"
        assert account.extra_info == ""

    def test_to_description(self):
        """Test AccountInfo description generation."""
        account = AccountInfo("test@example.com", "admin", "Test account")
        description = account.to_description()

        assert "test@example.com" in description
        assert "admin" in description
        assert "Test account" in description


class TestUtilityFunctions:
    """Test utility functions."""

    @patch('claude_gsuite_admin.auth.oauth_manager.argparse')
    def test_get_gauth_file(self, mock_argparse):
        """Test gauth file path retrieval."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.gauth_file = "/custom/gauth.json"
        mock_parser.parse_known_args.return_value = (mock_args, [])
        mock_argparse.ArgumentParser.return_value = mock_parser

        result = get_gauth_file()
        assert result == "/custom/gauth.json"

    @patch('claude_gsuite_admin.auth.oauth_manager.argparse')
    def test_get_accounts_file(self, mock_argparse):
        """Test accounts file path retrieval."""
        mock_parser = Mock()
        mock_args = Mock()
        mock_args.accounts_file = "/custom/accounts.json"
        mock_parser.parse_known_args.return_value = (mock_args, [])
        mock_argparse.ArgumentParser.return_value = mock_parser

        result = get_accounts_file()
        assert result == "/custom/accounts.json"

    @patch('builtins.open', new_callable=mock_open, read_data='{"accounts": [{"email": "test@example.com", "account_type": "admin", "extra_info": "Test"}]}')
    @patch('os.path.exists')
    @patch('claude_gsuite_admin.auth.oauth_manager.get_accounts_file')
    def test_get_account_info_success(self, mock_get_file, mock_exists, mock_file):
        """Test successful account info retrieval."""
        mock_get_file.return_value = "accounts.json"
        mock_exists.return_value = True

        accounts = get_account_info()

        assert len(accounts) == 1
        assert accounts[0].email == "test@example.com"
        assert accounts[0].account_type == "admin"
        assert accounts[0].extra_info == "Test"

    @patch('os.path.exists')
    @patch('claude_gsuite_admin.auth.oauth_manager.get_accounts_file')
    def test_get_account_info_file_not_found(self, mock_get_file, mock_exists):
        """Test account info retrieval with missing file."""
        mock_get_file.return_value = "accounts.json"
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            get_account_info()

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('os.path.exists')
    @patch('claude_gsuite_admin.auth.oauth_manager.get_accounts_file')
    def test_get_account_info_invalid_json(self, mock_get_file, mock_exists, mock_file):
        """Test account info retrieval with invalid JSON."""
        mock_get_file.return_value = "accounts.json"
        mock_exists.return_value = True

        accounts = get_account_info()
        assert accounts == []


class TestConstants:
    """Test module constants."""

    def test_admin_scopes(self):
        """Test that required admin scopes are present."""
        required_scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/admin.directory.user",
            "https://www.googleapis.com/auth/admin.directory.group",
            "https://www.googleapis.com/auth/admin.reports.audit.readonly"
        ]

        for scope in required_scopes:
            assert scope in ADMIN_SCOPES

    def test_redirect_uri(self):
        """Test redirect URI format."""
        assert REDIRECT_URI.startswith("http://")
        assert "localhost" in REDIRECT_URI