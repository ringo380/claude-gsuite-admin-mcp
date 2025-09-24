#!/usr/bin/env python3
"""Test Google Workspace Security Management tools."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_gsuite_admin.tools.security import (
    ListDomainAliasesHandler,
    ManageUserSecurityHandler,
    ListTokensHandler,
    ManageRoleAssignmentsHandler,
    ManageDataTransferHandler
)

def test_domain_aliases():
    """Test listing domain aliases."""
    try:
        handler = ListDomainAliasesHandler()

        args = {
            "user_id": "ryan@robworks.info"
        }

        print("Testing ListDomainAliasesHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Domain aliases successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Domain aliases failed: {e}")

def test_user_security():
    """Test user security management."""
    try:
        handler = ManageUserSecurityHandler()

        args = {
            "user_id": "ryan@robworks.info",
            "target_user": "ryan@robworks.info",
            "action": "get_security_info"
        }

        print("\nTesting ManageUserSecurityHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ User security successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ User security failed: {e}")

def test_list_tokens():
    """Test listing user tokens."""
    try:
        handler = ListTokensHandler()

        args = {
            "user_id": "ryan@robworks.info",
            "target_user": "ryan@robworks.info",
            "token_type": "all"
        }

        print("\nTesting ListTokensHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ List tokens successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ List tokens failed: {e}")

def test_role_assignments():
    """Test role assignment management."""
    try:
        handler = ManageRoleAssignmentsHandler()

        args = {
            "user_id": "ryan@robworks.info",
            "action": "list_roles"
        }

        print("\nTesting ManageRoleAssignmentsHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Role assignments successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text[:500]}...")

    except Exception as e:
        print(f"❌ Role assignments failed: {e}")

def test_data_transfer():
    """Test data transfer management."""
    try:
        handler = ManageDataTransferHandler()

        args = {
            "user_id": "ryan@robworks.info",
            "action": "list_transfers"
        }

        print("\nTesting ManageDataTransferHandler...")
        print(f"Arguments: {args}")

        result = handler.run_tool(args)

        print("✅ Data transfer successful!")
        print("Result:")
        for item in result:
            print(f"  {item.text}")

    except Exception as e:
        print(f"❌ Data transfer failed: {e}")

if __name__ == "__main__":
    test_domain_aliases()
    test_user_security()
    test_list_tokens()
    test_role_assignments()
    test_data_transfer()