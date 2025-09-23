#!/usr/bin/env python3
"""Test a simple audit activity query."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.auth.oauth_manager import OAuthManager

def test_simple_audit():
    """Test simple audit activity query."""
    try:
        print("Testing simple admin audit activities...")

        # Get authenticated service
        oauth_manager = OAuthManager()
        service = oauth_manager.get_service("ryan@robworks.info", "admin", "reports_v1")

        # Get admin audit activities for the last 30 days
        from datetime import datetime, timedelta
        start_time = (datetime.now() - timedelta(days=30)).isoformat() + "Z"

        print(f"Querying admin activities since {start_time}")

        result = service.activities().list(
            customerId="my_customer",
            applicationName="admin",
            userKey="all",  # Add the required userKey parameter
            startTime=start_time,
            maxResults=5
        ).execute()

        activities = result.get("items", [])

        if not activities:
            print("No admin activities found")
        else:
            print(f"✅ Found {len(activities)} admin activities:")
            for i, activity in enumerate(activities, 1):
                actor = activity.get("actor", {})
                actor_email = actor.get("email", "Unknown")
                time = activity.get("id", {}).get("time", "Unknown")

                events = activity.get("events", [])
                if events:
                    event_name = events[0].get("name", "Unknown")
                    print(f"{i}. {actor_email} - {event_name} at {time}")

    except Exception as e:
        print(f"❌ Simple audit test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_audit()