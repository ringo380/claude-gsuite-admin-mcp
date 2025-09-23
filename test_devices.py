#!/usr/bin/env python3
"""Test Google Workspace Device Management tools."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.devices import ListMobileDevicesHandler, ListChromeDevicesHandler

def test_list_mobile_devices():
    """Test the list mobile devices functionality."""
    try:
        handler = ListMobileDevicesHandler()

        # Test arguments
        args = {
            "user_id": "ryan@robworks.info",
            "customer_id": "my_customer",
            "max_results": 10
        }

        print("Testing ListMobileDevicesHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Mobile device listing successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Mobile device listing failed: {e}")
        import traceback
        traceback.print_exc()

def test_list_chrome_devices():
    """Test the list Chrome devices functionality."""
    try:
        handler = ListChromeDevicesHandler()

        # Test arguments
        args = {
            "user_id": "ryan@robworks.info",
            "customer_id": "my_customer",
            "max_results": 10
        }

        print("\nTesting ListChromeDevicesHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Chrome device listing successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Chrome device listing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_mobile_devices()
    test_list_chrome_devices()