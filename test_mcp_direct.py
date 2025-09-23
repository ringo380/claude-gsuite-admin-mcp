#!/usr/bin/env python3
"""Test MCP server directly without Claude CLI."""

import asyncio
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.server import app, register_all_handlers

async def test_mcp_server():
    """Test the MCP server directly."""
    print("🧪 Testing MCP server directly...")

    # Register handlers
    register_all_handlers()

    # Test list_tools
    print("\n📋 Testing list_tools...")
    tools = await app.list_tools()
    print(f"✅ Found {len(tools)} tools:")
    for i, tool in enumerate(tools[:5], 1):
        print(f"  {i}. {tool.name}: {tool.description}")

    if len(tools) > 5:
        print(f"  ... and {len(tools) - 5} more tools")

    # Test a simple tool call
    print("\n🔧 Testing a tool call...")
    try:
        # Test list users tool
        result = await app.call_tool(
            "mcp__gsuite_admin__list_users",
            {
                "user_id": "ryan@robworks.info",
                "max_results": 3
            }
        )
        print("✅ Tool call successful!")
        print(f"📊 Result: {len(result)} items returned")
        if result:
            print(f"📝 First result: {result[0].text[:100]}...")

    except Exception as e:
        print(f"❌ Tool call failed: {e}")

    print("\n🎯 MCP server test complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())