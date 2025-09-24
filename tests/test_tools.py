#!/usr/bin/env python3
"""Test the Google Workspace Admin tools directly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.users import ListUsersHandler

def test_list_users():
    """Test the list users functionality directly."""
    try:
        handler = ListUsersHandler()

        # Test arguments
        args = {
            "user_id": "ryan@robworks.info",
            "domain": "robworks.info",
            "max_results": 5
        }

        print("Testing ListUsersHandler directly...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Tool execution successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_users()