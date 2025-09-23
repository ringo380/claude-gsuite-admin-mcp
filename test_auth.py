#!/usr/bin/env python3
"""Test script to verify OAuth authentication works."""

import asyncio
import sys
from pathlib import Path
from claude_gsuite_admin.auth.oauth_manager import OAuthManager

async def test_authentication():
    """Test OAuth authentication flow."""
    try:
        # Initialize OAuth manager
        oauth_manager = OAuthManager()

        # Test getting service with account
        print("Testing authentication for ryan@robworks.info...")

        service = oauth_manager.get_service("ryan@robworks.info", "admin", "directory_v1")

        if service:
            print("✅ OAuth authentication successful!")
            print("✅ Google Admin API service created")

            # Try a simple API call to list users (first 5)
            print("Testing API call - listing first 5 users...")
            users_result = service.users().list(domain='robworks.info', maxResults=5).execute()
            users = users_result.get('users', [])

            if users:
                print(f"✅ Successfully retrieved {len(users)} users:")
                for user in users:
                    print(f"  - {user['primaryEmail']} ({user.get('name', {}).get('fullName', 'No name')})")
            else:
                print("⚠️ No users found in domain")

            return True

        else:
            print("❌ Failed to create service")
            return False

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_authentication())
    sys.exit(0 if success else 1)