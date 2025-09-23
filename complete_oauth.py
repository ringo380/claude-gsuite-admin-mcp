#!/usr/bin/env python3
"""Complete OAuth setup with authorization code."""

import sys
from claude_gsuite_admin.auth.oauth_manager import OAuthManager

def complete_oauth():
    """Complete OAuth with authorization code."""
    print("Google Workspace Admin MCP - Complete OAuth")
    print("=" * 50)

    print("From the localhost URL you received, copy just the authorization code.")
    print("The URL looks like: http://localhost:4100/code?code=AUTHORIZATION_CODE&scope=...")
    print("Copy everything after 'code=' and before '&scope' (or end of URL if no &scope)")
    print()

    auth_code = input("Paste the authorization code here: ").strip()

    if not auth_code:
        print("❌ No authorization code provided")
        return False

    # Clean up the code (remove any extra parameters if user pasted more)
    if '&' in auth_code:
        auth_code = auth_code.split('&')[0]

    print(f"Using authorization code: {auth_code[:20]}...")

    try:
        oauth_manager = OAuthManager()
        user_email = "ryan@robworks.info"

        print("Exchanging authorization code for credentials...")
        credentials = oauth_manager.get_credentials(user_email, auth_code)

        if credentials:
            print(f"✅ Successfully obtained credentials for {user_email}")
            print(f"✅ Credentials saved to ./.oauth2.{user_email}.json")

            # Test the credentials
            print("\nTesting credentials with API call...")
            service = oauth_manager.get_service(user_email, "admin", "directory_v1")

            users_result = service.users().list(domain='robworks.info', maxResults=1).execute()
            users = users_result.get('users', [])

            if users:
                print(f"✅ Successfully tested API - found user: {users[0]['primaryEmail']}")
            else:
                print("⚠️ API test successful but no users found")

            return True
        else:
            print("❌ Failed to exchange authorization code for credentials")
            return False

    except Exception as e:
        print(f"❌ OAuth completion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = complete_oauth()
    if success:
        print("\n🎉 OAuth setup completed successfully!")
        print("The MCP server is now ready to use.")
    else:
        print("\n💥 OAuth setup failed. Please try again.")

    sys.exit(0 if success else 1)