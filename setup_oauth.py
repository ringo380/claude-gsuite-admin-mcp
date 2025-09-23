#!/usr/bin/env python3
"""Script to set up initial OAuth2 authentication."""

import sys
from claude_gsuite_admin.auth.oauth_manager import OAuthManager

def setup_oauth():
    """Interactive OAuth setup."""
    print("Google Workspace Admin MCP - OAuth Setup")
    print("=" * 50)

    try:
        oauth_manager = OAuthManager()

        # Get OAuth flow
        flow = oauth_manager.get_oauth_flow()

        # Generate authorization URL
        auth_url = flow.step1_get_authorize_url()

        print("\n1. Please visit the following URL in your browser:")
        print(f"\n{auth_url}")
        print("\n2. Grant the requested permissions")
        print("3. You'll be redirected to a URL that starts with http://localhost:4100/code?")
        print("4. Copy the ENTIRE URL from your browser's address bar")

        redirect_url = input("\nPaste the redirect URL here: ").strip()

        # Extract authorization code from URL
        if 'code=' not in redirect_url:
            print("❌ Error: The URL doesn't contain an authorization code")
            return False

        # Parse the authorization code
        code_start = redirect_url.find('code=') + 5
        code_end = redirect_url.find('&', code_start)
        if code_end == -1:
            auth_code = redirect_url[code_start:]
        else:
            auth_code = redirect_url[code_start:code_end]

        print(f"\nExtracted authorization code: {auth_code[:20]}...")

        # Exchange code for credentials
        print("Exchanging authorization code for credentials...")

        user_email = "ryan@robworks.info"  # From our accounts config
        credentials = oauth_manager.get_credentials(user_email, auth_code)

        if credentials:
            print(f"✅ Successfully obtained credentials for {user_email}")
            print(f"✅ Credentials saved to ./.oauth2.{user_email}.json")

            # Test the credentials with a simple API call
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
        print(f"❌ OAuth setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_oauth()
    if success:
        print("\n🎉 OAuth setup completed successfully!")
        print("You can now use the MCP server and its tools.")
    else:
        print("\n💥 OAuth setup failed. Please try again.")

    sys.exit(0 if success else 1)