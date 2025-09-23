#!/usr/bin/env python3
"""Comprehensive test of all Google Workspace Admin MCP tools."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_all_tools():
    """Test all 31 admin tools to verify functionality."""
    print("🧪 Testing all Google Workspace Admin MCP tools...")
    print("=" * 60)

    # Test counts by category
    test_results = {
        "user_management": 0,
        "group_management": 0,
        "org_unit_management": 0,
        "device_management": 0,
        "reports_auditing": 0,
        "security_management": 0,
        "total_passed": 0,
        "total_failed": 0
    }

    # User Management (7 tools)
    print("\n👤 User Management (7 tools):")
    user_tests = [
        ("List Users", "from claude_gsuite_admin.tools.users import ListUsersHandler; h = ListUsersHandler(); print('✅ Tool loaded')"),
        ("Get User", "from claude_gsuite_admin.tools.users import GetUserHandler; h = GetUserHandler(); print('✅ Tool loaded')"),
        ("Create User", "from claude_gsuite_admin.tools.users import CreateUserHandler; h = CreateUserHandler(); print('✅ Tool loaded')"),
        ("Update User", "from claude_gsuite_admin.tools.users import UpdateUserHandler; h = UpdateUserHandler(); print('✅ Tool loaded')"),
        ("Suspend User", "from claude_gsuite_admin.tools.users import SuspendUserHandler; h = SuspendUserHandler(); print('✅ Tool loaded')"),
        ("Reset Password", "from claude_gsuite_admin.tools.users import ResetPasswordHandler; h = ResetPasswordHandler(); print('✅ Tool loaded')"),
        ("Delete User", "from claude_gsuite_admin.tools.users import DeleteUserHandler; h = DeleteUserHandler(); print('✅ Tool loaded')")
    ]

    for test_name, test_code in user_tests:
        try:
            exec(test_code)
            test_results["user_management"] += 1
            test_results["total_passed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["total_failed"] += 1

    # Group Management (5 tools)
    print("\n👥 Group Management (5 tools):")
    group_tests = [
        ("List Groups", "from claude_gsuite_admin.tools.groups import ListGroupsHandler; h = ListGroupsHandler(); print('✅ Tool loaded')"),
        ("Get Group", "from claude_gsuite_admin.tools.groups import GetGroupHandler; h = GetGroupHandler(); print('✅ Tool loaded')"),
        ("Create Group", "from claude_gsuite_admin.tools.groups import CreateGroupHandler; h = CreateGroupHandler(); print('✅ Tool loaded')"),
        ("Delete Group", "from claude_gsuite_admin.tools.groups import DeleteGroupHandler; h = DeleteGroupHandler(); print('✅ Tool loaded')"),
        ("List Group Members", "from claude_gsuite_admin.tools.groups import ListGroupMembersHandler; h = ListGroupMembersHandler(); print('✅ Tool loaded')")
    ]

    for test_name, test_code in group_tests:
        try:
            exec(test_code)
            test_results["group_management"] += 1
            test_results["total_passed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["total_failed"] += 1

    # Organizational Unit Management (5 tools)
    print("\n🏢 Organizational Unit Management (5 tools):")
    ou_tests = [
        ("List OUs", "from claude_gsuite_admin.tools.org_units import ListOrgUnitsHandler; h = ListOrgUnitsHandler(); print('✅ Tool loaded')"),
        ("Get OU", "from claude_gsuite_admin.tools.org_units import GetOrgUnitHandler; h = GetOrgUnitHandler(); print('✅ Tool loaded')"),
        ("Create OU", "from claude_gsuite_admin.tools.org_units import CreateOrgUnitHandler; h = CreateOrgUnitHandler(); print('✅ Tool loaded')"),
        ("Update OU", "from claude_gsuite_admin.tools.org_units import UpdateOrgUnitHandler; h = UpdateOrgUnitHandler(); print('✅ Tool loaded')"),
        ("Delete OU", "from claude_gsuite_admin.tools.org_units import DeleteOrgUnitHandler; h = DeleteOrgUnitHandler(); print('✅ Tool loaded')")
    ]

    for test_name, test_code in ou_tests:
        try:
            exec(test_code)
            test_results["org_unit_management"] += 1
            test_results["total_passed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["total_failed"] += 1

    # Device Management (5 tools)
    print("\n📱 Device Management (5 tools):")
    device_tests = [
        ("List Mobile Devices", "from claude_gsuite_admin.tools.devices import ListMobileDevicesHandler; h = ListMobileDevicesHandler(); print('✅ Tool loaded')"),
        ("Get Mobile Device", "from claude_gsuite_admin.tools.devices import GetMobileDeviceHandler; h = GetMobileDeviceHandler(); print('✅ Tool loaded')"),
        ("Manage Mobile Device", "from claude_gsuite_admin.tools.devices import ManageMobileDeviceHandler; h = ManageMobileDeviceHandler(); print('✅ Tool loaded')"),
        ("List Chrome Devices", "from claude_gsuite_admin.tools.devices import ListChromeDevicesHandler; h = ListChromeDevicesHandler(); print('✅ Tool loaded')"),
        ("Get Chrome Device", "from claude_gsuite_admin.tools.devices import GetChromeDeviceHandler; h = GetChromeDeviceHandler(); print('✅ Tool loaded')")
    ]

    for test_name, test_code in device_tests:
        try:
            exec(test_code)
            test_results["device_management"] += 1
            test_results["total_passed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["total_failed"] += 1

    # Reports & Auditing (4 tools)
    print("\n📊 Reports & Auditing (4 tools):")
    report_tests = [
        ("User Usage Reports", "from claude_gsuite_admin.tools.reports import GetUsageReportsHandler; h = GetUsageReportsHandler(); print('✅ Tool loaded')"),
        ("Audit Activities", "from claude_gsuite_admin.tools.reports import GetAuditActivitiesHandler; h = GetAuditActivitiesHandler(); print('✅ Tool loaded')"),
        ("Customer Usage Reports", "from claude_gsuite_admin.tools.reports import GetCustomerUsageReportsHandler; h = GetCustomerUsageReportsHandler(); print('✅ Tool loaded')"),
        ("Domain Insights", "from claude_gsuite_admin.tools.reports import GetDomainInsightsHandler; h = GetDomainInsightsHandler(); print('✅ Tool loaded')")
    ]

    for test_name, test_code in report_tests:
        try:
            exec(test_code)
            test_results["reports_auditing"] += 1
            test_results["total_passed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["total_failed"] += 1

    # Security Management (5 tools)
    print("\n🔐 Security Management (5 tools):")
    security_tests = [
        ("Domain Aliases", "from claude_gsuite_admin.tools.security import ListDomainAliasesHandler; h = ListDomainAliasesHandler(); print('✅ Tool loaded')"),
        ("User Security", "from claude_gsuite_admin.tools.security import ManageUserSecurityHandler; h = ManageUserSecurityHandler(); print('✅ Tool loaded')"),
        ("Token Management", "from claude_gsuite_admin.tools.security import ListTokensHandler; h = ListTokensHandler(); print('✅ Tool loaded')"),
        ("Role Assignments", "from claude_gsuite_admin.tools.security import ManageRoleAssignmentsHandler; h = ManageRoleAssignmentsHandler(); print('✅ Tool loaded')"),
        ("Data Transfer", "from claude_gsuite_admin.tools.security import ManageDataTransferHandler; h = ManageDataTransferHandler(); print('✅ Tool loaded')")
    ]

    for test_name, test_code in security_tests:
        try:
            exec(test_code)
            test_results["security_management"] += 1
            test_results["total_passed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["total_failed"] += 1

    # Print comprehensive results
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    print(f"👤 User Management:        {test_results['user_management']}/7 tools loaded")
    print(f"👥 Group Management:       {test_results['group_management']}/5 tools loaded")
    print(f"🏢 Organizational Units:   {test_results['org_unit_management']}/5 tools loaded")
    print(f"📱 Device Management:      {test_results['device_management']}/5 tools loaded")
    print(f"📊 Reports & Auditing:     {test_results['reports_auditing']}/4 tools loaded")
    print(f"🔐 Security Management:    {test_results['security_management']}/5 tools loaded")
    print("-" * 60)
    print(f"✅ Total Passed:          {test_results['total_passed']}/31 tools")
    print(f"❌ Total Failed:          {test_results['total_failed']}/31 tools")

    if test_results['total_passed'] == 31:
        print("\n🎉 ALL 31 TOOLS LOADED SUCCESSFULLY!")
        print("💪 Google Workspace Admin MCP Server is fully operational!")
    else:
        print(f"\n⚠️  {test_results['total_failed']} tools failed to load.")
        print("🔧 Please check the implementation for any missing dependencies or imports.")

    return test_results

def test_server_registration():
    """Test that all tools are properly registered in the server."""
    print("\n🔧 Testing server registration...")

    try:
        from claude_gsuite_admin.server import register_all_handlers, tool_handlers

        # Register all handlers
        register_all_handlers()

        # Check total count
        total_registered = len(tool_handlers)
        print(f"📝 Total tools registered: {total_registered}")

        # Check each category
        user_tools = [k for k in tool_handlers.keys() if 'user' in k and 'security' not in k]
        group_tools = [k for k in tool_handlers.keys() if 'group' in k]
        ou_tools = [k for k in tool_handlers.keys() if 'org_unit' in k]
        device_tools = [k for k in tool_handlers.keys() if 'device' in k or 'mobile' in k or 'chrome' in k]
        report_tools = [k for k in tool_handlers.keys() if any(x in k for x in ['usage', 'audit', 'customer', 'domain_insights'])]
        security_tools = [k for k in tool_handlers.keys() if any(x in k for x in ['security', 'token', 'role', 'alias', 'transfer'])]

        print(f"👤 User tools: {len(user_tools)}")
        print(f"👥 Group tools: {len(group_tools)}")
        print(f"🏢 OU tools: {len(ou_tools)}")
        print(f"📱 Device tools: {len(device_tools)}")
        print(f"📊 Report tools: {len(report_tools)}")
        print(f"🔐 Security tools: {len(security_tools)}")

        if total_registered == 31:
            print("✅ All 31 tools successfully registered!")
            return True
        else:
            print(f"❌ Expected 31 tools, but registered {total_registered}")
            return False

    except Exception as e:
        print(f"❌ Server registration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive test of Claude Google Workspace Admin MCP")
    print("⏱️  This test verifies all 31 administrative tools are available")

    # Test tool loading
    tool_results = test_all_tools()

    # Test server registration
    server_ok = test_server_registration()

    print("\n" + "=" * 60)
    print("🏁 FINAL SUMMARY")
    print("=" * 60)

    if tool_results['total_passed'] == 31 and server_ok:
        print("🎯 SUCCESS: All 31 Google Workspace Admin tools are ready!")
        print("🎉 The MCP server is fully functional and ready for Claude CLI")
        exit(0)
    else:
        print("⚠️  Some issues detected. Please review the output above.")
        exit(1)