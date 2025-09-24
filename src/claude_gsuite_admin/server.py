"""Main MCP server for Claude GSuite Admin."""

import logging
import sys
import traceback
from typing import Any, Dict, List, Sequence
from collections.abc import Sequence as AbstractSequence

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .auth.oauth_manager import OAuthManager, get_account_info
from .core.tool_handler import AdminToolHandler, USER_ID_ARG
from .core.exceptions import AdminMCPError, AuthenticationError, ConfigurationError

# Import all tool handlers
from .tools.users import USER_HANDLERS
from .tools.groups import GROUP_HANDLERS
from .tools.org_units import ORG_UNIT_HANDLERS
from .tools.devices import DEVICE_HANDLERS
from .tools.reports import REPORT_HANDLERS
from .tools.security import SECURITY_HANDLERS
from .tools.domains import DOMAIN_HANDLERS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("claude-gsuite-admin-mcp")

# Global tool handlers registry
tool_handlers: Dict[str, AdminToolHandler] = {}


def add_tool_handler(handler: AdminToolHandler) -> None:
    """Add a tool handler to the registry."""
    global tool_handlers
    tool_handlers[handler.name] = handler
    logger.info(f"Registered tool handler: {handler.name}")


def get_tool_handler(name: str) -> AdminToolHandler | None:
    """Get a tool handler by name."""
    return tool_handlers.get(name)


# Initialize handlers immediately at module level
def _initialize_handlers():
    """Initialize all tool handlers at module import time."""
    logger.info("Initializing tool handlers at module level...")

    # Register user management handlers
    for handler in USER_HANDLERS:
        add_tool_handler(handler)

    # Register group management handlers
    for handler in GROUP_HANDLERS:
        add_tool_handler(handler)

    # Register organizational unit handlers
    for handler in ORG_UNIT_HANDLERS:
        add_tool_handler(handler)

    # Register device management handlers
    for handler in DEVICE_HANDLERS:
        add_tool_handler(handler)

    # Register reporting handlers
    for handler in REPORT_HANDLERS:
        add_tool_handler(handler)

    # Register security handlers
    for handler in SECURITY_HANDLERS:
        add_tool_handler(handler)

    for handler in DOMAIN_HANDLERS:
        add_tool_handler(handler)

    logger.info(f"Initialized {len(tool_handlers)} tool handlers")


# Call initialization immediately
_initialize_handlers()




def setup_oauth2(user_id: str) -> None:
    """Setup OAuth2 authentication for a user."""
    try:
        oauth_manager = OAuthManager()
        credentials = oauth_manager.get_stored_credentials(user_id)

        if not credentials:
            logger.warning(f"No stored OAuth2 credentials for user: {user_id}")
            raise AuthenticationError(
                f"No OAuth2 credentials found for user {user_id}. "
                "Please complete the OAuth flow first."
            )

        logger.info(f"OAuth2 credentials loaded for user: {user_id}")
    except Exception as e:
        logger.error(f"OAuth2 setup failed for {user_id}: {e}")
        raise AuthenticationError(f"Failed to authenticate user {user_id}")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools."""
    logger.info("Listing available tools...")

    tools = []
    for handler in tool_handlers.values():
        try:
            tool = handler.get_tool_description()
            tools.append(tool)
        except Exception as e:
            logger.error(f"Error getting tool description for {handler.name}: {e}")

    logger.info(f"Listed {len(tools)} available tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Execute a tool with the given arguments."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        # Validate arguments
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a dictionary")

        # Check if user_id is provided
        if USER_ID_ARG not in arguments:
            raise ValueError(f"Missing required argument: {USER_ID_ARG}")

        user_id = arguments[USER_ID_ARG]
        logger.info(f"Tool called by user: {user_id}")

        # Setup OAuth2 authentication
        setup_oauth2(user_id)

        # Get tool handler
        handler = get_tool_handler(name)
        if not handler:
            available_tools = list(tool_handlers.keys())
            raise ValueError(f"Unknown tool: {name}. Available tools: {', '.join(available_tools)}")

        # Execute the tool
        logger.info(f"Executing tool {name} with handler {handler.__class__.__name__}")
        result = handler.run_tool(arguments)

        logger.info(f"Tool {name} executed successfully")
        return result

    except AdminMCPError as e:
        # Handle our custom exceptions
        logger.error(f"Admin MCP error in tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error ({e.error_code}): {e.message}"
        )]

    except AuthenticationError as e:
        logger.error(f"Authentication error in tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"🔐 Authentication Error: {e.message}\n\n"
                 f"Please ensure you have completed the OAuth2 setup and have valid credentials."
        )]

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in tool {name}: {e}")
        logger.error(traceback.format_exc())

        error_msg = f"❌ Unexpected error in {name}: {str(e)}"
        if logger.isEnabledFor(logging.DEBUG):
            error_msg += f"\n\nDebug info:\n{traceback.format_exc()}"

        return [TextContent(type="text", text=error_msg)]


@app.list_resources()
async def list_resources():
    """List available resources (not used in this implementation)."""
    return []


@app.read_resource()
async def read_resource(uri: str):
    """Read a resource (not used in this implementation)."""
    raise NotImplementedError("Resource reading not supported")


async def main():
    """Main entry point for the MCP server."""
    # Tool handlers are already registered at module level
    logger.info(f"Starting MCP server with {len(tool_handlers)} registered tools")

    # Start the MCP server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())