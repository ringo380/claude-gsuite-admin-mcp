"""Custom exceptions for Claude GSuite Admin MCP Server."""


class AdminMCPError(Exception):
    """Base exception for Claude GSuite Admin MCP Server."""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(AdminMCPError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_FAILED")


class AuthorizationError(AdminMCPError):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions", required_scope: str = None):
        self.required_scope = required_scope
        if required_scope:
            message = f"{message}. Required scope: {required_scope}"
        super().__init__(message, "AUTH_INSUFFICIENT")


class GoogleAPIError(AdminMCPError):
    """Raised when Google API calls fail."""

    def __init__(self, message: str, status_code: int = None, api_error: str = None):
        self.status_code = status_code
        self.api_error = api_error
        error_code = f"GOOGLE_API_{status_code}" if status_code else "GOOGLE_API_ERROR"
        super().__init__(message, error_code)


class ValidationError(AdminMCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field_name: str = None):
        self.field_name = field_name
        if field_name:
            message = f"Validation failed for {field_name}: {message}"
        super().__init__(message, "VALIDATION_ERROR")


class UserNotFoundError(AdminMCPError):
    """Raised when a requested user is not found."""

    def __init__(self, user_id: str):
        message = f"User not found: {user_id}"
        super().__init__(message, "USER_NOT_FOUND")


class GroupNotFoundError(AdminMCPError):
    """Raised when a requested group is not found."""

    def __init__(self, group_id: str):
        message = f"Group not found: {group_id}"
        super().__init__(message, "GROUP_NOT_FOUND")


class OrganizationUnitNotFoundError(AdminMCPError):
    """Raised when a requested organizational unit is not found."""

    def __init__(self, org_unit_path: str):
        message = f"Organizational unit not found: {org_unit_path}"
        super().__init__(message, "ORG_UNIT_NOT_FOUND")


class DeviceNotFoundError(AdminMCPError):
    """Raised when a requested device is not found."""

    def __init__(self, device_id: str):
        message = f"Device not found: {device_id}"
        super().__init__(message, "DEVICE_NOT_FOUND")


class DomainNotFoundError(AdminMCPError):
    """Raised when a requested domain is not found."""

    def __init__(self, domain_name: str):
        message = f"Domain not found: {domain_name}"
        super().__init__(message, "DOMAIN_NOT_FOUND")


class QuotaExceededError(AdminMCPError):
    """Raised when API quota is exceeded."""

    def __init__(self, message: str = "API quota exceeded"):
        super().__init__(message, "QUOTA_EXCEEDED")


class RateLimitError(AdminMCPError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "API rate limit exceeded", retry_after: int = None):
        self.retry_after = retry_after
        if retry_after:
            message = f"{message}. Retry after {retry_after} seconds."
        super().__init__(message, "RATE_LIMIT")


class ConfigurationError(AdminMCPError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str):
        super().__init__(message, "CONFIG_ERROR")


class OperationNotAllowedError(AdminMCPError):
    """Raised when an operation is not allowed in the current context."""

    def __init__(self, message: str):
        super().__init__(message, "OPERATION_NOT_ALLOWED")


class DuplicateResourceError(AdminMCPError):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} already exists: {identifier}"
        super().__init__(message, "DUPLICATE_RESOURCE")


class DependencyError(AdminMCPError):
    """Raised when a resource has dependencies preventing an operation."""

    def __init__(self, resource_type: str, identifier: str, dependency: str):
        message = f"Cannot modify {resource_type} '{identifier}' due to dependency: {dependency}"
        super().__init__(message, "DEPENDENCY_ERROR")