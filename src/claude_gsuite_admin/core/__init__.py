"""Core components for the Claude GSuite Admin MCP server."""

from .tool_handler import AdminToolHandler
from .exceptions import (
    AdminMCPError,
    AuthenticationError,
    AuthorizationError,
    GoogleAPIError,
    ValidationError
)

__all__ = [
    "AdminToolHandler",
    "AdminMCPError",
    "AuthenticationError",
    "AuthorizationError",
    "GoogleAPIError",
    "ValidationError"
]