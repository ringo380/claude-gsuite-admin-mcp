#!/usr/bin/env python3
"""Test Google Workspace Group Management tools."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.groups import ListGroupsHandler

def test_list_groups():
    """Test the list groups functionality."""
    try:
        handler = ListGroupsHandler()

        # Test arguments
        args = {
            "user_id": "ryan@robworks.info",
            "domain": "robworks.info",
            "max_results": 10
        }

        print("Testing ListGroupsHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Group listing successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Group listing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_groups()