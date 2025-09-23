"""Claude GSuite Admin MCP Server.

A comprehensive Google Workspace Admin MCP server specifically designed for Claude CLI
that provides full administrative capabilities for Google Workspace management.
"""

from . import server
import asyncio

__version__ = "0.1.0"
__author__ = "Ryan Robson"
__email__ = "ryan@robworks.info"

def main():
    """Main entry point for the package."""
    asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server', '__version__']