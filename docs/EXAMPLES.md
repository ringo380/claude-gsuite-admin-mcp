# Usage Examples

This document provides practical examples of using the Claude Google Workspace Admin MCP server.

## User Management Examples

### Creating Users

```
# Create a single user
"Create a new user john.doe@company.com with first name John and last name Doe"

# Create user with specific OU
"Create a new user jane.smith@company.com in the Engineering organizational unit"

# Create multiple users
"Create new users for the marketing team:
- alice.marketing@company.com (Alice Johnson)
- bob.marketing@company.com (Bob Wilson)
- carol.marketing@company.com (Carol Davis)"
```

### Managing User Accounts

```
# List users
"Show me all users in the Engineering organizational unit"

# Search for specific users
"Find all users with 'admin' in their name"

# Suspend a user
"Suspend the user account for former.employee@company.com due to termination"

# Reset passwords
"Reset the password for john.doe@company.com and require them to change it on next login"

# Move users between OUs
"Move jane.smith@company.com from Engineering to Management organizational unit"
```

### User Information and Reporting

```
# Get detailed user info
"Show me detailed information for the user admin@company.com"

# List suspended users
"Show me all suspended user accounts"

# User activity reports
"Generate a user activity report for the last 30 days"
```

## Group Management Examples

### Creating and Managing Groups

```
# Create a group
"Create a new group called 'engineering-team@company.com' with the name 'Engineering Team'"

# Add members to a group
"Add john.doe@company.com and jane.smith@company.com to the engineering-team group"

# List group members
"Show me all members of the executives@company.com group"

# Remove a group
"Delete the old-project-team@company.com group after confirming it's no longer needed"
```

### Group Information

```
# List all groups
"Show me all groups in the company.com domain"

# Search for specific groups
"Find all groups that contain 'marketing' in their name"

# Group details
"Show me detailed information about the hr-team@company.com group"
```

## Organizational Unit Management

### OU Structure Management

```
# Create organizational units
"Create a new organizational unit called 'Sales' under the root"

# Create nested OUs
"Create a 'West Coast' organizational unit under the Sales OU"

# Move OUs
"Move the Marketing OU to be under the Sales OU"

# List OU structure
"Show me the complete organizational unit structure"
```

### OU User Management

```
# List users in OU
"Show me all users in the /Engineering/Frontend organizational unit"

# Move users between OUs
"Move all users from the /Contractors OU to /Engineering/External"
```

## Device Management Examples

### Mobile Device Management

```
# List mobile devices
"Show me all mobile devices registered to user john.doe@company.com"

# Device actions
"Remotely wipe the mobile device with ID 'ABC123' due to security concerns"

# Device reports
"Generate a report of all Android devices that haven't synced in the last 30 days"

# Approve/block devices
"Block the mobile device with ID 'XYZ789' from accessing company data"
```

### Chrome OS Device Management

```
# List Chrome devices
"Show me all Chrome OS devices in the /Students organizational unit"

# Device information
"Get detailed information about the Chrome device with serial number 'CH123456'"

# Device location tracking
"Show me all Chrome devices that are currently marked as 'Lost' or 'Stolen'"
```

## Reports and Auditing Examples

### Usage Reports

```
# Domain usage reports
"Generate a usage report for the entire domain for last month"

# Application-specific usage
"Show me Gmail usage statistics for the last week"

# Storage usage
"Create a report showing which organizational units are using the most storage"

# User activity
"Show me the most active users based on email and calendar usage"
```

### Audit Logs

```
# Admin activity audit
"Show me all admin actions performed in the last 7 days"

# User login audit
"Generate an audit report of all failed login attempts in the last 24 hours"

# Group changes audit
"Show me all group membership changes in the last month"

# Security events
"Create an audit report of all 2-step verification changes"
```

### Security Reports

```
# Security overview
"Generate a security overview report for today"

# Suspicious activity
"Show me any suspicious login attempts from unusual locations"

# 2SV compliance
"Create a report showing which users don't have 2-step verification enabled"
```

## Security Management Examples

### User Security Settings

```
# 2SV enforcement
"Require 2-step verification for the user risky.user@company.com"

# Admin role management
"Make jane.doe@company.com a user management admin"

# Security tokens
"Show me all OAuth tokens for the user john.doe@company.com"

# Session management
"Reset all sign-in cookies for compromised.user@company.com"
```

### Domain Security

```
# Domain aliases
"Show me all domain aliases configured for our workspace"

# Role assignments
"List all users with super admin privileges"

# Data transfer
"Create a data transfer request from departing.employee@company.com to manager@company.com"
```

## Advanced Workflows

### New Employee Onboarding

```
"I need to onboard a new employee Sarah Johnson (sarah.johnson@company.com) to the Marketing team:
1. Create her user account in the /Marketing OU
2. Add her to the marketing-team@company.com group
3. Add her to the all-employees@company.com group
4. Generate a temporary password and require password change on first login"
```

### Employee Offboarding

```
"I need to offboard John Smith (john.smith@company.com) who is leaving the company:
1. Suspend his user account
2. Remove him from all groups except archived-employees@company.com
3. Transfer his data to his manager (mary.manager@company.com)
4. Generate an audit report of his recent activities
5. Wipe any registered mobile devices"
```

### Security Incident Response

```
"We have a security incident with user compromised@company.com:
1. Immediately suspend the account
2. Reset all sign-in cookies
3. Show me all recent login activities
4. List all devices registered to this user
5. Remote wipe all mobile devices
6. Generate an audit report of all actions by this user in the last 48 hours"
```

### Organizational Restructuring

```
"We're restructuring our Engineering department:
1. Create new OUs: /Engineering/Backend, /Engineering/Frontend, /Engineering/DevOps
2. Move users from /Engineering to appropriate sub-OUs based on their roles
3. Create new groups: backend-team@company.com, frontend-team@company.com, devops-team@company.com
4. Update group memberships accordingly
5. Generate a report showing the new structure"
```

### Compliance Auditing

```
"I need to prepare for a compliance audit:
1. Generate a report of all admin actions in the last 6 months
2. Show all users who don't have 2SV enabled
3. List all external sharing activities
4. Create a device inventory report
5. Show all data export activities
6. Generate a user access review report"
```

## Bulk Operations

### Bulk User Operations

```
"I have a CSV file with 50 new employees. For each person, create their account in the appropriate OU based on their department column, and add them to department-specific groups"

"Suspend all users in the /Contractors OU who haven't logged in for the last 90 days"

"Reset passwords for all users in the /Interns OU and require password change on next login"
```

### Bulk Group Operations

```
"Create department-specific groups for all organizational units under /Departments"

"Add all users from the /Engineering OU to the engineering-all@company.com group"

"Remove all suspended users from active project groups"
```

## Monitoring and Alerting

### Regular Health Checks

```
"Create a weekly report showing:
1. New user accounts created
2. Users who haven't logged in for 30+ days
3. Devices that haven't synced recently
4. Any security violations or alerts
5. Storage usage by department"
```

### Security Monitoring

```
"Set up monitoring for:
1. Failed login attempts from new locations
2. Users accessing data outside business hours
3. Bulk download activities
4. Admin privilege changes
5. New device registrations"
```

## Tips for Effective Usage

1. **Be Specific**: Include exact email addresses and organizational unit paths
2. **Use Confirmation**: For destructive operations, always include confirmation
3. **Batch Operations**: Group related actions together for efficiency
4. **Regular Auditing**: Schedule regular reports and audits
5. **Test First**: Use test accounts for learning and validation

## Error Handling Examples

When operations fail, Claude will provide detailed error information:

```
# If user creation fails
"Error creating user: Email address already exists"

# If permission denied
"Error: Insufficient permissions to perform this action. Ensure your admin account has the required privileges."

# If quota exceeded
"Error: Domain user limit reached. Contact Google Workspace support to increase quota."
```

## Best Practices

1. **Always verify** critical operations before execution
2. **Use organizational units** for logical user grouping
3. **Implement consistent naming** conventions for groups and OUs
4. **Regular backups** of important configurations
5. **Monitor audit logs** for unusual activities
6. **Test procedures** in a development environment first