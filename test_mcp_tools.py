#!/usr/bin/env python3
"""Test MCP server tools list."""

import asyncio
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.server import app, register_all_handlers

async def test_mcp_tools():
    """Test MCP server tools listing."""
    try:
        # Register handlers
        register_all_handlers()

        # Test list_tools
        tools = await app.list_tools()

        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        return tools
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    tools = asyncio.run(test_mcp_tools())