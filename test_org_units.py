#!/usr/bin/env python3
"""Test Google Workspace Organizational Unit Management tools."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.org_units import ListOrgUnitsHandler

def test_list_org_units():
    """Test the list organizational units functionality."""
    try:
        handler = ListOrgUnitsHandler()

        # Test arguments
        args = {
            "user_id": "ryan@robworks.info",
            "customer_id": "my_customer"
        }

        print("Testing ListOrgUnitsHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Organizational unit listing successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Organizational unit listing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_org_units()