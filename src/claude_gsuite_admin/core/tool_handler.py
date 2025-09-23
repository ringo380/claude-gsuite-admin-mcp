"""Base tool handler class for Google Workspace Admin MCP tools."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Union
from collections.abc import Sequence as AbstractSequence

from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from ..auth.oauth_manager import OAuthManager, get_account_info
from .exceptions import (
    AdminMCPError,
    AuthenticationError,
    ValidationError,
    GoogleAPIError,
)

# User ID argument key - required in all tool calls
USER_ID_ARG = "user_id"

# Default maximum results for list operations
DEFAULT_MAX_RESULTS = 100


class AdminToolHandler(ABC):
    """Base class for all Google Workspace Admin tool handlers."""

    def __init__(self, tool_name: str):
        self.name = tool_name
        self.oauth_manager = OAuthManager()
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

    @abstractmethod
    def get_tool_description(self) -> Tool:
        """Return the MCP tool description for this handler.

        This method must be implemented by each tool handler to define:
        - Tool name and description
        - Input schema with required and optional parameters
        - Any constraints or validation rules
        """
        pass

    @abstractmethod
    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute the tool with the given arguments.

        This method must be implemented by each tool handler to:
        - Validate input arguments
        - Authenticate the user
        - Execute the Google API operations
        - Format and return results
        """
        pass

    def validate_required_args(self, args: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required arguments are present."""
        missing_fields = []
        for field in required_fields:
            if field not in args or args[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    def validate_user_id(self, args: Dict[str, Any]) -> str:
        """Validate and extract user_id from arguments."""
        if USER_ID_ARG not in args:
            raise ValidationError(f"Missing required field: {USER_ID_ARG}")

        user_id = args[USER_ID_ARG]
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValidationError("user_id must be a non-empty string")

        return user_id.strip()

    def get_authenticated_service(self, user_id: str, service_name: str, version: str = 'v1'):
        """Get an authenticated Google API service for the user."""
        try:
            service = self.oauth_manager.get_service(user_id, service_name, version)
            return service
        except Exception as e:
            self._logger.error(f"Failed to get authenticated service {service_name} for {user_id}: {e}")
            raise AuthenticationError(f"Failed to authenticate user {user_id} for {service_name}")

    def handle_google_api_error(self, error: Exception, operation: str = "API operation") -> None:
        """Handle and convert Google API errors to our custom exceptions."""
        error_str = str(error)
        self._logger.error(f"Google API error during {operation}: {error_str}")

        # Extract status code if available
        status_code = None
        if hasattr(error, 'resp') and hasattr(error.resp, 'status'):
            status_code = error.resp.status

        # Handle specific error types
        if "403" in error_str or "Insufficient Permission" in error_str:
            raise GoogleAPIError(
                f"Insufficient permissions for {operation}. Check admin privileges and API scopes.",
                status_code=403,
                api_error=error_str
            )
        elif "404" in error_str or "notFound" in error_str:
            raise GoogleAPIError(
                f"Resource not found during {operation}",
                status_code=404,
                api_error=error_str
            )
        elif "400" in error_str or "invalid" in error_str.lower():
            raise GoogleAPIError(
                f"Invalid request during {operation}: {error_str}",
                status_code=400,
                api_error=error_str
            )
        elif "429" in error_str or "quota" in error_str.lower():
            raise GoogleAPIError(
                f"Rate limit or quota exceeded during {operation}",
                status_code=429,
                api_error=error_str
            )
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            raise GoogleAPIError(
                f"Google API server error during {operation}. Please try again later.",
                status_code=500,
                api_error=error_str
            )
        else:
            raise GoogleAPIError(
                f"Google API error during {operation}: {error_str}",
                status_code=status_code,
                api_error=error_str
            )

    def format_success_response(self, message: str, data: Dict[str, Any] = None) -> Sequence[TextContent]:
        """Format a successful response."""
        response = {"status": "success", "message": message}
        if data:
            response["data"] = data

        return [TextContent(
            type="text",
            text=f"✅ {message}\n\n{self._format_data_as_text(data) if data else ''}"
        )]

    def format_error_response(self, error: AdminMCPError) -> Sequence[TextContent]:
        """Format an error response."""
        return [TextContent(
            type="text",
            text=f"❌ Error ({error.error_code}): {error.message}"
        )]

    def format_list_response(self, items: List[Dict[str, Any]], item_type: str, total_count: int = None) -> Sequence[TextContent]:
        """Format a response containing a list of items."""
        if not items:
            return [TextContent(
                type="text",
                text=f"No {item_type} found."
            )]

        response_text = f"Found {len(items)} {item_type}"
        if total_count and total_count > len(items):
            response_text += f" (showing {len(items)} of {total_count} total)"
        response_text += ":\n\n"

        for i, item in enumerate(items, 1):
            response_text += f"{i}. {self._format_item_summary(item)}\n"

        return [TextContent(type="text", text=response_text)]

    def _format_data_as_text(self, data: Dict[str, Any]) -> str:
        """Format data dictionary as readable text."""
        if not data:
            return ""

        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                lines.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def _format_item_summary(self, item: Dict[str, Any]) -> str:
        """Format a single item as a summary line."""
        # This is a default implementation - tools can override for custom formatting
        if 'primaryEmail' in item:
            return f"{item.get('name', {}).get('fullName', 'Unknown')} ({item['primaryEmail']})"
        elif 'email' in item:
            return f"{item.get('name', 'Unknown Group')} ({item['email']})"
        elif 'name' in item:
            if isinstance(item['name'], dict):
                return item['name'].get('fullName') or item['name'].get('givenName', 'Unknown')
            else:
                return str(item['name'])
        elif 'id' in item:
            return f"ID: {item['id']}"
        else:
            # Fallback - show first few key-value pairs
            summary_parts = []
            for key, value in list(item.items())[:3]:
                if isinstance(value, (str, int, float, bool)):
                    summary_parts.append(f"{key}: {value}")
            return " | ".join(summary_parts) if summary_parts else "Unknown item"

    def get_supported_accounts_info(self) -> str:
        """Get information about configured accounts."""
        try:
            accounts = get_account_info()
            if not accounts:
                return "No accounts configured. Please set up .accounts.json file."

            account_info = []
            for account in accounts:
                account_info.append(f"• {account.email} ({account.account_type})")
                if account.extra_info:
                    account_info.append(f"  {account.extra_info}")

            return "Configured accounts:\n" + "\n".join(account_info)
        except Exception as e:
            return f"Error loading account information: {e}"

    def paginate_results(self, request_func, page_token_key: str = "pageToken",
                        results_key: str = "items", max_results: int = DEFAULT_MAX_RESULTS):
        """Helper method to paginate through Google API results."""
        all_results = []
        page_token = None

        try:
            while len(all_results) < max_results:
                # Prepare request parameters
                request_params = {}
                if page_token:
                    request_params[page_token_key] = page_token

                # Calculate how many results we still need
                remaining = max_results - len(all_results)
                if remaining < 100:  # Google APIs typically default to 100 per page
                    request_params['maxResults'] = remaining

                # Execute the request
                response = request_func(**request_params)

                # Extract results
                page_results = response.get(results_key, [])
                all_results.extend(page_results)

                # Check for next page
                page_token = response.get('nextPageToken')
                if not page_token or not page_results:
                    break

        except Exception as e:
            self.handle_google_api_error(e, "paginated request")

        return all_results[:max_results]  # Ensure we don't exceed the limit