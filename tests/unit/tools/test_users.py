"""Unit tests for user management tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp.types import TextContent

from claude_gsuite_admin.tools.users import (
    ListUsersHandler,
    GetUserHandler,
    CreateUserHandler,
    UpdateUserHandler,
    SuspendUserHandler,
    ResetPasswordHandler,
    DeleteUserHandler,
    USER_HANDLERS
)
from claude_gsuite_admin.core.exceptions import (
    ValidationError,
    UserNotFoundError,
    DuplicateResourceError
)


class TestListUsersHandler:
    """Test ListUsersHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ListUsersHandler()

    def test_init(self):
        """Test handler initialization."""
        assert self.handler.name == "mcp__gsuite_admin__list_users"

    def test_get_tool_description(self):
        """Test tool description generation."""
        description = self.handler.get_tool_description()
        assert description.name == "mcp__gsuite_admin__list_users"
        assert "List Google Workspace users" in description.description
        assert "user_id" in description.inputSchema["properties"]

    @patch.object(ListUsersHandler, 'get_google_service')
    def test_run_tool_success(self, mock_get_service):
        """Test successful user listing."""
        # Mock Google service
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_list_request = Mock()
        mock_users_resource.list.return_value = mock_list_request

        mock_list_request.execute.return_value = {
            "users": [
                {
                    "id": "123456789",
                    "primaryEmail": "test@example.com",
                    "name": {"givenName": "Test", "familyName": "User"},
                    "suspended": False,
                    "orgUnitPath": "/",
                    "lastLoginTime": "2024-01-01T10:00:00.000Z",
                    "creationTime": "2023-01-01T10:00:00.000Z"
                }
            ]
        }

        mock_get_service.return_value = mock_service

        # Test execution
        args = {"user_id": "admin@example.com"}
        result = self.handler.run_tool(args)

        # Verify results
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "test@example.com" in result[0].text
        assert "Test User" in result[0].text

    @patch.object(ListUsersHandler, 'get_google_service')
    def test_run_tool_with_filters(self, mock_get_service):
        """Test user listing with filters."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_list_request = Mock()
        mock_users_resource.list.return_value = mock_list_request

        mock_list_request.execute.return_value = {"users": []}
        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "domain": "example.com",
            "org_unit_path": "/Engineering",
            "query": "john",
            "max_results": 50,
            "show_suspended": False
        }

        self.handler.run_tool(args)

        # Verify API call parameters
        mock_users_resource.list.assert_called_once_with(
            customer="my_customer",
            domain="example.com",
            orgUnitPath="/Engineering",
            query="john",
            maxResults=50,
            showDeleted="false"
        )

    def test_run_tool_missing_user_id(self):
        """Test error handling for missing user_id."""
        args = {}

        with pytest.raises(ValidationError, match="user_id is required"):
            self.handler.run_tool(args)

    @patch.object(ListUsersHandler, 'get_google_service')
    def test_run_tool_api_error(self, mock_get_service):
        """Test API error handling."""
        mock_get_service.side_effect = Exception("API Error")

        args = {"user_id": "admin@example.com"}

        with pytest.raises(Exception):
            self.handler.run_tool(args)


class TestGetUserHandler:
    """Test GetUserHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = GetUserHandler()

    @patch.object(GetUserHandler, 'get_google_service')
    def test_run_tool_success(self, mock_get_service):
        """Test successful user retrieval."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_get_request = Mock()
        mock_users_resource.get.return_value = mock_get_request

        mock_get_request.execute.return_value = {
            "id": "123456789",
            "primaryEmail": "test@example.com",
            "name": {"givenName": "Test", "familyName": "User"},
            "suspended": False,
            "orgUnitPath": "/Engineering",
            "lastLoginTime": "2024-01-01T10:00:00.000Z"
        }

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "target_user": "test@example.com"
        }

        result = self.handler.run_tool(args)

        assert len(result) == 1
        assert "test@example.com" in result[0].text
        assert "Test User" in result[0].text

    def test_run_tool_missing_target_user(self):
        """Test error handling for missing target_user."""
        args = {"user_id": "admin@example.com"}

        with pytest.raises(ValidationError, match="target_user is required"):
            self.handler.run_tool(args)


class TestCreateUserHandler:
    """Test CreateUserHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = CreateUserHandler()

    @patch.object(CreateUserHandler, 'get_google_service')
    def test_run_tool_success(self, mock_get_service):
        """Test successful user creation."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_insert_request = Mock()
        mock_users_resource.insert.return_value = mock_insert_request

        mock_insert_request.execute.return_value = {
            "id": "123456789",
            "primaryEmail": "newuser@example.com",
            "name": {"givenName": "New", "familyName": "User"}
        }

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User"
        }

        result = self.handler.run_tool(args)

        assert len(result) == 1
        assert "successfully created" in result[0].text.lower()
        assert "newuser@example.com" in result[0].text

    @patch.object(CreateUserHandler, 'get_google_service')
    def test_run_tool_with_password(self, mock_get_service):
        """Test user creation with custom password."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_insert_request = Mock()
        mock_users_resource.insert.return_value = mock_insert_request

        mock_insert_request.execute.return_value = {
            "id": "123456789",
            "primaryEmail": "newuser@example.com",
            "name": {"givenName": "New", "familyName": "User"}
        }

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "customPassword123!"
        }

        self.handler.run_tool(args)

        # Verify password was used
        call_args = mock_users_resource.insert.call_args[1]["body"]
        assert call_args["password"] == "customPassword123!"

    def test_run_tool_missing_required_fields(self):
        """Test error handling for missing required fields."""
        args = {"user_id": "admin@example.com"}

        with pytest.raises(ValidationError):
            self.handler.run_tool(args)

    def test_run_tool_invalid_email(self):
        """Test error handling for invalid email."""
        args = {
            "user_id": "admin@example.com",
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User"
        }

        with pytest.raises(ValidationError, match="Invalid email format"):
            self.handler.run_tool(args)


class TestSuspendUserHandler:
    """Test SuspendUserHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = SuspendUserHandler()

    @patch.object(SuspendUserHandler, 'get_google_service')
    def test_run_tool_suspend_success(self, mock_get_service):
        """Test successful user suspension."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_patch_request = Mock()
        mock_users_resource.patch.return_value = mock_patch_request

        mock_patch_request.execute.return_value = {
            "primaryEmail": "test@example.com",
            "suspended": True
        }

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "target_user": "test@example.com",
            "suspend": True,
            "reason": "Security violation"
        }

        result = self.handler.run_tool(args)

        assert len(result) == 1
        assert "suspended" in result[0].text.lower()
        assert "test@example.com" in result[0].text

    @patch.object(SuspendUserHandler, 'get_google_service')
    def test_run_tool_unsuspend_success(self, mock_get_service):
        """Test successful user unsuspension."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_patch_request = Mock()
        mock_users_resource.patch.return_value = mock_patch_request

        mock_patch_request.execute.return_value = {
            "primaryEmail": "test@example.com",
            "suspended": False
        }

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "target_user": "test@example.com",
            "suspend": False
        }

        result = self.handler.run_tool(args)

        assert len(result) == 1
        assert "reactivated" in result[0].text.lower()


class TestResetPasswordHandler:
    """Test ResetPasswordHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ResetPasswordHandler()

    @patch.object(ResetPasswordHandler, 'get_google_service')
    def test_run_tool_success(self, mock_get_service):
        """Test successful password reset."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_patch_request = Mock()
        mock_users_resource.patch.return_value = mock_patch_request

        mock_patch_request.execute.return_value = {
            "primaryEmail": "test@example.com"
        }

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "target_user": "test@example.com"
        }

        result = self.handler.run_tool(args)

        assert len(result) == 1
        assert "password reset" in result[0].text.lower()
        assert "temporary password" in result[0].text.lower()


class TestDeleteUserHandler:
    """Test DeleteUserHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = DeleteUserHandler()

    @patch.object(DeleteUserHandler, 'get_google_service')
    def test_run_tool_success(self, mock_get_service):
        """Test successful user deletion."""
        mock_service = Mock()
        mock_users_resource = Mock()
        mock_service.users.return_value = mock_users_resource
        mock_delete_request = Mock()
        mock_users_resource.delete.return_value = mock_delete_request

        mock_delete_request.execute.return_value = {}

        mock_get_service.return_value = mock_service

        args = {
            "user_id": "admin@example.com",
            "target_user": "test@example.com",
            "confirm": True
        }

        result = self.handler.run_tool(args)

        assert len(result) == 1
        assert "permanently deleted" in result[0].text.lower()

    def test_run_tool_missing_confirmation(self):
        """Test error handling for missing confirmation."""
        args = {
            "user_id": "admin@example.com",
            "target_user": "test@example.com"
        }

        with pytest.raises(ValidationError, match="confirm must be true"):
            self.handler.run_tool(args)


class TestUserHandlers:
    """Test user handlers collection."""

    def test_user_handlers_count(self):
        """Test that all user handlers are included."""
        assert len(USER_HANDLERS) == 7

    def test_user_handlers_types(self):
        """Test that all handlers are correct types."""
        expected_types = [
            ListUsersHandler,
            GetUserHandler,
            CreateUserHandler,
            UpdateUserHandler,
            SuspendUserHandler,
            ResetPasswordHandler,
            DeleteUserHandler
        ]

        for i, handler in enumerate(USER_HANDLERS):
            assert isinstance(handler, expected_types[i])

    def test_user_handlers_unique_names(self):
        """Test that all handlers have unique names."""
        names = [handler.name for handler in USER_HANDLERS]
        assert len(names) == len(set(names))  # All names are unique