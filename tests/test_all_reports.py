#!/usr/bin/env python3
"""Test all Google Workspace Reports and Auditing tools."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.reports import (
    GetUsageReportsHandler,
    GetAuditActivitiesHandler,
    GetCustomerUsageReportsHandler,
    GetDomainInsightsHandler
)

def test_usage_reports():
    """Test user usage reports."""
    try:
        handler = GetUsageReportsHandler()

        from datetime import datetime, timedelta
        date_3_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        args = {
            "user_id": "ryan@robworks.info",
            "user_key": "ryan@robworks.info",  # Test specific user
            "date": date_3_days_ago,
            "parameters": "gmail:num_emails_sent,gmail:num_emails_received",
            "max_results": 3
        }

        print("Testing GetUsageReportsHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Usage reports successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text[:200]}...")

    except Exception as e:
        print(f"❌ Usage reports failed: {e}")

def test_domain_insights():
    """Test domain insights."""
    try:
        handler = GetDomainInsightsHandler()

        from datetime import datetime, timedelta
        date_3_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        args = {
            "user_id": "ryan@robworks.info",
            "date": date_3_days_ago,
            "insight_type": "security"
        }

        print("\nTesting GetDomainInsightsHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Domain insights successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text[:500]}...")

    except Exception as e:
        print(f"❌ Domain insights failed: {e}")

if __name__ == "__main__":
    test_usage_reports()
    test_domain_insights()