"""Pytest configuration and fixtures for Claude GSuite Admin MCP tests."""

import os
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from claude_gsuite_admin.auth.oauth_manager import OAuthManager
from claude_gsuite_admin.core.tool_handler import AdminToolHandler


@pytest.fixture
def mock_oauth_credentials():
    """Mock OAuth2 credentials for testing."""
    mock_creds = Mock()
    mock_creds.access_token = "mock_access_token"
    mock_creds.refresh_token = "mock_refresh_token"
    mock_creds.access_token_expired = False
    mock_creds.to_json.return_value = '{"access_token": "mock_access_token"}'
    return mock_creds


@pytest.fixture
def mock_oauth_manager(mock_oauth_credentials):
    """Mock OAuth manager for testing."""
    with patch('claude_gsuite_admin.auth.oauth_manager.OAuthManager') as mock_manager:
        manager_instance = Mock()
        manager_instance.get_stored_credentials.return_value = mock_oauth_credentials
        manager_instance.get_service.return_value = Mock()
        mock_manager.return_value = manager_instance
        yield manager_instance


@pytest.fixture
def mock_google_service():
    """Mock Google API service for testing."""
    service = Mock()

    # Mock common API responses
    service.users().list().execute.return_value = {
        "users": [
            {
                "id": "123456789",
                "primaryEmail": "test@example.com",
                "name": {"givenName": "Test", "familyName": "User"},
                "suspended": False,
                "orgUnitPath": "/",
                "lastLoginTime": "2024-01-01T10:00:00.000Z"
            }
        ]
    }

    service.groups().list().execute.return_value = {
        "groups": [
            {
                "id": "group123",
                "email": "test-group@example.com",
                "name": "Test Group",
                "description": "Test group for testing"
            }
        ]
    }

    service.orgunits().list().execute.return_value = {
        "organizationUnits": [
            {
                "name": "Engineering",
                "orgUnitPath": "/Engineering",
                "description": "Engineering department"
            }
        ]
    }

    return service


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "user_id": "admin@example.com",
        "email": "newuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "org_unit_path": "/",
        "suspended": False
    }


@pytest.fixture
def sample_group_data():
    """Sample group data for testing."""
    return {
        "user_id": "admin@example.com",
        "group_email": "testgroup@example.com",
        "group_name": "Test Group",
        "description": "Test group for unit testing"
    }


@pytest.fixture
def mock_tool_handler():
    """Mock tool handler for testing."""
    class MockToolHandler(AdminToolHandler):
        def __init__(self, name="test_handler"):
            super().__init__(name)

        def get_tool_description(self):
            return Mock()

        def run_tool(self, args: Dict[str, Any]):
            return [Mock()]

    return MockToolHandler()


@pytest.fixture
def test_config():
    """Test configuration data."""
    return {
        "gauth_file": ".gauth.json.example",
        "accounts_file": ".accounts.json.example",
        "test_user": "admin@example.com",
        "test_domain": "example.com"
    }


@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables."""
    original_env = os.environ.copy()

    # Set test environment
    os.environ["GSUITE_GAUTH_FILE"] = ".gauth.json.example"
    os.environ["GSUITE_ACCOUNTS_FILE"] = ".accounts.json.example"
    os.environ["GSUITE_OAUTH_DIR"] = "/tmp/test_oauth"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_logging():
    """Mock logging to prevent log pollution during tests."""
    with patch('claude_gsuite_admin.core.tool_handler.logging'):
        yield


# Skip integration tests by default
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless specifically requested."""
    if config.getoption("--run-integration"):
        return

    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )