# API Documentation

This document provides detailed information about all 31 Google Workspace Admin tools available in the Claude GSuite Admin MCP server.

## Authentication

All tools require a `user_id` parameter containing the email address of an authenticated Google Workspace admin user. The server handles OAuth2 authentication automatically.

## Tool Categories

### 👤 User Management (7 tools)

#### `mcp__gsuite_admin__list_users`

List and filter users across the domain.

**Parameters:**
- `user_id` (required): Admin user email
- `domain` (optional): Filter by domain
- `org_unit_path` (optional): Filter by organizational unit
- `query` (optional): Search query
- `max_results` (optional): Maximum results (default: 100, max: 500)
- `order_by` (optional): Sort field (email, givenName, familyName)
- `show_suspended` (optional): Include suspended users (default: true)

**Example:**
```python
{
    "user_id": "admin@company.com",
    "org_unit_path": "/Engineering",
    "max_results": 50
}
```

#### `mcp__gsuite_admin__get_user`

Get detailed information about a specific user.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): Email or user ID to retrieve

#### `mcp__gsuite_admin__create_user`

Create a new user account.

**Parameters:**
- `user_id` (required): Admin user email
- `email` (required): Primary email for new user
- `first_name` (required): First name
- `last_name` (required): Last name
- `password` (optional): Password (auto-generated if not provided)
- `org_unit_path` (optional): Organizational unit (default: /)
- `suspended` (optional): Create as suspended (default: false)
- `change_password_next_login` (optional): Force password change (default: true)

#### `mcp__gsuite_admin__update_user`

Update user properties.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): Email or user ID to update
- `first_name` (optional): New first name
- `last_name` (optional): New last name
- `org_unit_path` (optional): New organizational unit
- `suspended` (optional): Suspend/unsuspend user

#### `mcp__gsuite_admin__suspend_user`

Suspend or unsuspend a user account.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): Email or user ID
- `suspend` (required): true to suspend, false to unsuspend
- `reason` (optional): Reason for suspension

#### `mcp__gsuite_admin__reset_password`

Reset a user's password.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): Email or user ID
- `new_password` (optional): New password (auto-generated if not provided)
- `force_change_next_login` (optional): Force change on next login (default: true)

#### `mcp__gsuite_admin__delete_user`

Permanently delete a user account.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): Email or user ID to delete
- `confirm` (required): Must be true to confirm deletion

### 👥 Group Management (5 tools)

#### `mcp__gsuite_admin__list_groups`

List groups in the domain.

**Parameters:**
- `user_id` (required): Admin user email
- `domain` (required): Domain to list groups from
- `query` (optional): Search query
- `max_results` (optional): Maximum results (default: 100, max: 500)

#### `mcp__gsuite_admin__get_group`

Get detailed group information.

**Parameters:**
- `user_id` (required): Admin user email
- `group_email` (required): Group email address

#### `mcp__gsuite_admin__create_group`

Create a new group.

**Parameters:**
- `user_id` (required): Admin user email
- `group_email` (required): Group email address
- `group_name` (required): Display name
- `description` (optional): Group description

#### `mcp__gsuite_admin__delete_group`

Delete a group.

**Parameters:**
- `user_id` (required): Admin user email
- `group_email` (required): Group email to delete
- `confirm` (required): Must be true to confirm deletion

#### `mcp__gsuite_admin__list_group_members`

List members of a group.

**Parameters:**
- `user_id` (required): Admin user email
- `group_email` (required): Group email address
- `max_results` (optional): Maximum results (default: 100, max: 500)

### 🏢 Organizational Unit Management (5 tools)

#### `mcp__gsuite_admin__list_org_units`

List organizational units.

**Parameters:**
- `user_id` (required): Admin user email
- `customer_id` (optional): Customer ID (default: "my_customer")
- `org_unit_path` (optional): Starting path (default: "/")
- `type` (optional): Type to list (all, children, all_including_parent)

#### `mcp__gsuite_admin__get_org_unit`

Get detailed organizational unit information.

**Parameters:**
- `user_id` (required): Admin user email
- `org_unit_path` (required): OU path to retrieve
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__create_org_unit`

Create a new organizational unit.

**Parameters:**
- `user_id` (required): Admin user email
- `name` (required): OU name
- `parent_org_unit_path` (optional): Parent path (default: "/")
- `description` (optional): OU description
- `block_inheritance` (optional): Block inheritance (default: false)
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__update_org_unit`

Update an organizational unit.

**Parameters:**
- `user_id` (required): Admin user email
- `org_unit_path` (required): Current OU path
- `name` (optional): New name
- `parent_org_unit_path` (optional): New parent path
- `description` (optional): New description
- `block_inheritance` (optional): Block inheritance setting
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__delete_org_unit`

Delete an organizational unit.

**Parameters:**
- `user_id` (required): Admin user email
- `org_unit_path` (required): OU path to delete
- `confirm` (required): Must be true to confirm deletion
- `customer_id` (optional): Customer ID (default: "my_customer")

### 📱 Device Management (5 tools)

#### `mcp__gsuite_admin__list_mobile_devices`

List mobile devices in the domain.

**Parameters:**
- `user_id` (required): Admin user email
- `customer_id` (optional): Customer ID (default: "my_customer")
- `query` (optional): Search query
- `max_results` (optional): Maximum results (default: 100, max: 500)
- `order_by` (optional): Sort field (deviceId, email, lastSync, model, name, os, status, type)

#### `mcp__gsuite_admin__get_mobile_device`

Get detailed mobile device information.

**Parameters:**
- `user_id` (required): Admin user email
- `device_id` (required): Device resource ID
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__manage_mobile_device`

Perform management actions on mobile devices.

**Parameters:**
- `user_id` (required): Admin user email
- `device_id` (required): Device resource ID
- `action` (required): Action to perform (approve, block, cancel_remote_wipe_then_activate, cancel_remote_wipe_then_block, remote_wipe, delete)
- `confirm` (optional): Confirmation for destructive actions (default: false)
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__list_chrome_devices`

List Chrome OS devices.

**Parameters:**
- `user_id` (required): Admin user email
- `customer_id` (optional): Customer ID (default: "my_customer")
- `org_unit_path` (optional): Filter by OU
- `query` (optional): Search query
- `max_results` (optional): Maximum results (default: 100, max: 500)
- `order_by` (optional): Sort field (annotatedLocation, annotatedUser, lastSync, notes, serialNumber, status, supportEndDate)

#### `mcp__gsuite_admin__get_chrome_device`

Get detailed Chrome OS device information.

**Parameters:**
- `user_id` (required): Admin user email
- `device_id` (required): Device ID
- `customer_id` (optional): Customer ID (default: "my_customer")

### 📊 Reports & Auditing (4 tools)

#### `mcp__gsuite_admin__get_usage_reports`

Get usage reports for applications and services.

**Parameters:**
- `user_id` (required): Admin user email
- `date` (required): Report date (YYYY-MM-DD or "today")
- `user_key` (optional): User email or "all" (default: "all")
- `parameters` (optional): Comma-separated parameters (default: "accounts:num_users,accounts:used_quota_in_mb")
- `max_results` (optional): Maximum results (default: 1000, max: 1000)

#### `mcp__gsuite_admin__get_audit_activities`

Get audit activity logs.

**Parameters:**
- `user_id` (required): Admin user email
- `start_time` (required): Start time (ISO format or "today", "1d", "7d", "30d")
- `application_name` (optional): Application (admin, calendar, chat, drive, gcp, gplus, groups, groups_enterprise, jamboard, login, meet, mobile, rules, saml, token, user_accounts)
- `actor_email` (optional): Filter by user email
- `event_name` (optional): Filter by event name
- `end_time` (optional): End time (ISO format)
- `max_results` (optional): Maximum results (default: 1000, max: 1000)
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__get_customer_usage_reports`

Get customer-level usage reports.

**Parameters:**
- `user_id` (required): Admin user email
- `date` (required): Report date (YYYY-MM-DD or "today")
- `parameters` (optional): Comma-separated parameters (default: "accounts:total_quota_in_mb,accounts:used_quota_in_mb,accounts:num_users")
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__get_domain_insights`

Get domain insights including security and activity data.

**Parameters:**
- `user_id` (required): Admin user email
- `date` (required): Insights date (YYYY-MM-DD or "today")
- `insight_type` (optional): Type of insights (security, usage, activity, apps) (default: "security")

### 🔐 Security Management (5 tools)

#### `mcp__gsuite_admin__list_domain_aliases`

List domain aliases.

**Parameters:**
- `user_id` (required): Admin user email
- `customer_id` (optional): Customer ID (default: "my_customer")

#### `mcp__gsuite_admin__manage_user_security`

Manage user security settings.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): User to manage
- `action` (required): Action (get_security_info, require_2sv, disable_2sv, make_admin, remove_admin, reset_signin_cookies, generate_app_password)
- `admin_role` (optional): Admin role when making admin (super_admin, user_management_admin, groups_admin, org_unit_admin)

#### `mcp__gsuite_admin__list_tokens`

List OAuth tokens and app passwords.

**Parameters:**
- `user_id` (required): Admin user email
- `target_user` (required): User whose tokens to list
- `token_type` (optional): Token type (all, oauth, app_passwords) (default: "all")

#### `mcp__gsuite_admin__manage_role_assignments`

Manage admin role assignments.

**Parameters:**
- `user_id` (required): Admin user email
- `action` (required): Action (list_roles, list_assignments, assign_role, remove_role)
- `customer_id` (optional): Customer ID (default: "my_customer")
- `role_id` (optional): Role ID (for assign_role, remove_role)
- `target_user` (optional): User email (for assign_role, remove_role)

#### `mcp__gsuite_admin__manage_data_transfer`

Manage data transfer requests.

**Parameters:**
- `user_id` (required): Admin user email
- `action` (required): Action (list_transfers, create_transfer, get_transfer_status)
- `old_owner_id` (optional): User whose data to transfer (for create_transfer)
- `new_owner_id` (optional): User to receive data (for create_transfer)
- `transfer_id` (optional): Transfer ID (for get_transfer_status)

## Error Handling

All tools return structured error responses for:
- Authentication failures
- Permission errors
- Invalid parameters
- Google API errors

## Rate Limiting

Tools automatically handle Google API rate limits with exponential backoff retry logic.