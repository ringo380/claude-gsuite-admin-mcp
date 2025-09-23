#!/usr/bin/env python3
"""Test Google Workspace Reports and Auditing tools with correct parameters."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.reports import GetCustomerUsageReportsHandler, GetAuditActivitiesHandler

def test_customer_usage_reports():
    """Test the customer usage reports functionality."""
    try:
        handler = GetCustomerUsageReportsHandler()

        # Test arguments - use a date from 3 days ago to avoid data lag
        from datetime import datetime, timedelta
        date_3_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        args = {
            "user_id": "ryan@robworks.info",
            "date": date_3_days_ago,
            "customer_id": "my_customer"
        }

        print("Testing GetCustomerUsageReportsHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Customer usage reports successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Customer usage reports failed: {e}")
        import traceback
        traceback.print_exc()

def test_audit_activities():
    """Test the audit activities functionality."""
    try:
        handler = GetAuditActivitiesHandler()

        # Test arguments with proper date format
        from datetime import datetime, timedelta
        start_time = (datetime.now() - timedelta(days=7)).isoformat() + "Z"

        args = {
            "user_id": "ryan@robworks.info",
            "start_time": start_time,
            "application_name": "login",  # Changed to login for better data
            "max_results": 5
        }

        print("\nTesting GetAuditActivitiesHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Audit activities successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Audit activities failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_customer_usage_reports()
    test_audit_activities()