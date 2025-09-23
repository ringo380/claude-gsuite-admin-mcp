"""Google Workspace Security Management Tools."""

import logging
from typing import Any, Dict, List, Sequence
from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import AdminMCPError, ValidationError
from ..auth.oauth_manager import OAuthManager

logger = logging.getLogger(__name__)


class ListDomainAliasesHandler(AdminToolHandler):
    """Handler for listing domain aliases."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_domain_aliases")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List all domain aliases for the Google Workspace domain",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (use 'my_customer' for your domain)",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")

            logger.info(f"Listing domain aliases for customer {customer_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # List domain aliases
            result = service.domainAliases().list(
                customer=customer_id
            ).execute()

            domain_aliases = result.get("domainAliases", [])

            if not domain_aliases:
                return [TextContent(
                    type="text",
                    text="No domain aliases found for this domain."
                )]

            # Format response
            response = f"Domain Aliases ({len(domain_aliases)} found):\n\n"

            for i, alias in enumerate(domain_aliases, 1):
                domain_alias_name = alias.get("domainAliasName", "Unknown")
                parent_domain_name = alias.get("parentDomainName", "Unknown")
                verified = alias.get("verified", False)
                creation_time = alias.get("creationTime", "Unknown")

                response += f"{i}. {domain_alias_name}\n"
                response += f"   🏠 Parent Domain: {parent_domain_name}\n"
                response += f"   ✅ Verified: {'Yes' if verified else 'No'}\n"
                response += f"   📅 Created: {creation_time}\n\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing domain aliases: {e}")
            raise AdminMCPError(f"Failed to list domain aliases: {str(e)}")


class ManageUserSecurityHandler(AdminToolHandler):
    """Handler for managing user security settings."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_user_security")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Manage user security settings including 2SV status, admin status, and password changes",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user to manage"
                    },
                    "action": {
                        "type": "string",
                        "description": "Security action to perform",
                        "enum": ["get_security_info", "require_2sv", "disable_2sv", "make_admin", "remove_admin", "reset_signin_cookies", "generate_app_password"]
                    },
                    "admin_role": {
                        "type": "string",
                        "description": "Admin role to assign (when action is 'make_admin')",
                        "enum": ["super_admin", "user_management_admin", "groups_admin", "org_unit_admin"]
                    }
                },
                "required": [USER_ID_ARG, "target_user", "action"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            target_user = arguments["target_user"]
            action = arguments["action"]
            admin_role = arguments.get("admin_role")

            logger.info(f"Managing security for user {target_user}: {action}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            if action == "get_security_info":
                # Get user info including security details
                user_info = service.users().get(
                    userKey=target_user,
                    projection="full"
                ).execute()

                # Security-related fields
                is_admin = user_info.get("isAdmin", False)
                is_delegated_admin = user_info.get("isDelegatedAdmin", False)
                suspended = user_info.get("suspended", False)
                change_password_at_next_login = user_info.get("changePasswordAtNextLogin", False)

                # 2SV enrollment
                is_enrolled_in_2sv = user_info.get("isEnrolledIn2Sv", False)
                is_enforced_in_2sv = user_info.get("isEnforcedIn2Sv", False)

                response = f"Security Information for {target_user}:\n\n"
                response += f"👑 Admin Status: {'Super Admin' if is_admin else 'Delegated Admin' if is_delegated_admin else 'Regular User'}\n"
                response += f"🔒 Account Status: {'Suspended' if suspended else 'Active'}\n"
                response += f"🛡️ 2SV Enrolled: {'Yes' if is_enrolled_in_2sv else 'No'}\n"
                response += f"🛡️ 2SV Enforced: {'Yes' if is_enforced_in_2sv else 'No'}\n"
                response += f"🔑 Password Change Required: {'Yes' if change_password_at_next_login else 'No'}\n"

                return [TextContent(type="text", text=response)]

            elif action == "require_2sv":
                # Update user to require 2SV
                user_body = {
                    "isEnforcedIn2Sv": True
                }

                service.users().update(
                    userKey=target_user,
                    body=user_body
                ).execute()

                return [TextContent(
                    type="text",
                    text=f"✅ Successfully enabled 2SV requirement for {target_user}"
                )]

            elif action == "disable_2sv":
                # Remove 2SV requirement
                user_body = {
                    "isEnforcedIn2Sv": False
                }

                service.users().update(
                    userKey=target_user,
                    body=user_body
                ).execute()

                return [TextContent(
                    type="text",
                    text=f"✅ Successfully disabled 2SV requirement for {target_user}"
                )]

            elif action == "reset_signin_cookies":
                # Sign out user from all sessions
                service.users().signOut(userKey=target_user).execute()

                return [TextContent(
                    type="text",
                    text=f"✅ Successfully signed out {target_user} from all sessions"
                )]

            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Action '{action}' is not implemented yet"
                )]

        except Exception as e:
            logger.error(f"Error managing user security: {e}")
            raise AdminMCPError(f"Failed to manage user security: {str(e)}")


class ListTokensHandler(AdminToolHandler):
    """Handler for listing user tokens and app passwords."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_tokens")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List OAuth tokens and app-specific passwords for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user whose tokens to list"
                    },
                    "token_type": {
                        "type": "string",
                        "description": "Type of tokens to list",
                        "enum": ["all", "oauth", "app_passwords"],
                        "default": "all"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            target_user = arguments["target_user"]
            token_type = arguments.get("token_type", "all")

            logger.info(f"Listing {token_type} tokens for user {target_user}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            response = f"Tokens for {target_user}:\n\n"

            if token_type in ["all", "oauth"]:
                try:
                    # List OAuth tokens
                    oauth_result = service.tokens().list(userKey=target_user).execute()
                    tokens = oauth_result.get("items", [])

                    if tokens:
                        response += f"🔑 OAuth Tokens ({len(tokens)} found):\n"
                        for i, token in enumerate(tokens, 1):
                            client_id = token.get("clientId", "Unknown")
                            display_text = token.get("displayText", "Unknown App")
                            scopes = token.get("scopes", [])
                            anonymous = token.get("anonymous", False)

                            response += f"{i}. {display_text}\n"
                            response += f"   📱 Client ID: {client_id}\n"
                            response += f"   🕵️ Anonymous: {'Yes' if anonymous else 'No'}\n"
                            if scopes:
                                response += f"   🔓 Scopes: {len(scopes)} permissions\n"
                            response += "\n"
                    else:
                        response += "🔑 OAuth Tokens: None found\n\n"

                except Exception as e:
                    response += f"❌ Could not retrieve OAuth tokens: {str(e)}\n\n"

            if token_type in ["all", "app_passwords"]:
                try:
                    # List app-specific passwords (ASPs)
                    asp_result = service.asps().list(userKey=target_user).execute()
                    asps = asp_result.get("items", [])

                    if asps:
                        response += f"🔐 App Passwords ({len(asps)} found):\n"
                        for i, asp in enumerate(asps, 1):
                            code_id = asp.get("codeId", "Unknown")
                            name = asp.get("name", "Unknown")
                            creation_time = asp.get("creationTime", "Unknown")
                            last_time_used = asp.get("lastTimeUsed", "Never")

                            response += f"{i}. {name}\n"
                            response += f"   🆔 Code ID: {code_id}\n"
                            response += f"   📅 Created: {creation_time}\n"
                            response += f"   ⏰ Last Used: {last_time_used}\n\n"
                    else:
                        response += "🔐 App Passwords: None found\n"

                except Exception as e:
                    response += f"❌ Could not retrieve app passwords: {str(e)}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing tokens: {e}")
            raise AdminMCPError(f"Failed to list tokens: {str(e)}")


class ManageRoleAssignmentsHandler(AdminToolHandler):
    """Handler for managing admin role assignments."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_role_assignments")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Manage admin role assignments for users",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["list_roles", "list_assignments", "assign_role", "remove_role"]
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of user (required for assign_role, remove_role)"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "Role ID to assign/remove (required for assign_role, remove_role)"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (use 'my_customer' for your domain)",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG, "action"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            action = arguments["action"]
            target_user = arguments.get("target_user")
            role_id = arguments.get("role_id")
            customer_id = arguments.get("customer_id", "my_customer")

            logger.info(f"Managing role assignments: {action}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            if action == "list_roles":
                # List all available admin roles
                result = service.roles().list(customer=customer_id).execute()
                roles = result.get("items", [])

                if not roles:
                    return [TextContent(
                        type="text",
                        text="No admin roles found."
                    )]

                response = f"Available Admin Roles ({len(roles)} found):\n\n"

                for i, role in enumerate(roles, 1):
                    role_id = role.get("roleId", "Unknown")
                    role_name = role.get("roleName", "Unknown")
                    role_description = role.get("roleDescription", "No description")
                    is_system_role = role.get("isSystemRole", False)

                    response += f"{i}. {role_name}\n"
                    response += f"   🆔 ID: {role_id}\n"
                    response += f"   📝 Description: {role_description}\n"
                    response += f"   🏛️ System Role: {'Yes' if is_system_role else 'No'}\n\n"

                return [TextContent(type="text", text=response)]

            elif action == "list_assignments":
                # List all role assignments
                result = service.roleAssignments().list(customer=customer_id).execute()
                assignments = result.get("items", [])

                if not assignments:
                    return [TextContent(
                        type="text",
                        text="No role assignments found."
                    )]

                response = f"Current Role Assignments ({len(assignments)} found):\n\n"

                for i, assignment in enumerate(assignments, 1):
                    assigned_to = assignment.get("assignedTo", "Unknown")
                    role_id = assignment.get("roleId", "Unknown")
                    scope_type = assignment.get("scopeType", "Unknown")

                    response += f"{i}. User: {assigned_to}\n"
                    response += f"   🎭 Role ID: {role_id}\n"
                    response += f"   🌐 Scope: {scope_type}\n\n"

                return [TextContent(type="text", text=response)]

            elif action in ["assign_role", "remove_role"]:
                if not target_user or not role_id:
                    raise ValidationError("target_user and role_id are required for role assignment operations")

                if action == "assign_role":
                    # Assign role to user
                    assignment_body = {
                        "assignedTo": target_user,
                        "roleId": role_id,
                        "scopeType": "CUSTOMER"
                    }

                    service.roleAssignments().insert(
                        customer=customer_id,
                        body=assignment_body
                    ).execute()

                    return [TextContent(
                        type="text",
                        text=f"✅ Successfully assigned role {role_id} to {target_user}"
                    )]

                else:  # remove_role
                    # First find the assignment to get its ID
                    result = service.roleAssignments().list(
                        customer=customer_id,
                        userKey=target_user
                    ).execute()

                    assignments = result.get("items", [])
                    assignment_to_delete = None

                    for assignment in assignments:
                        if assignment.get("roleId") == role_id:
                            assignment_to_delete = assignment.get("roleAssignmentId")
                            break

                    if not assignment_to_delete:
                        return [TextContent(
                            type="text",
                            text=f"❌ Role assignment not found for {target_user} with role {role_id}"
                        )]

                    # Delete the assignment
                    service.roleAssignments().delete(
                        customer=customer_id,
                        roleAssignmentId=assignment_to_delete
                    ).execute()

                    return [TextContent(
                        type="text",
                        text=f"✅ Successfully removed role {role_id} from {target_user}"
                    )]

            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Unknown action: {action}"
                )]

        except Exception as e:
            logger.error(f"Error managing role assignments: {e}")
            raise AdminMCPError(f"Failed to manage role assignments: {str(e)}")


class ManageDataTransferHandler(AdminToolHandler):
    """Handler for managing data transfer requests."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_data_transfer")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Manage data transfer requests for users leaving the organization",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["list_transfers", "create_transfer", "get_transfer_status"]
                    },
                    "old_owner_id": {
                        "type": "string",
                        "description": "Email of user whose data to transfer (for create_transfer)"
                    },
                    "new_owner_id": {
                        "type": "string",
                        "description": "Email of user to receive the data (for create_transfer)"
                    },
                    "transfer_id": {
                        "type": "string",
                        "description": "Transfer ID to check status (for get_transfer_status)"
                    }
                },
                "required": [USER_ID_ARG, "action"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            action = arguments["action"]
            old_owner_id = arguments.get("old_owner_id")
            new_owner_id = arguments.get("new_owner_id")
            transfer_id = arguments.get("transfer_id")

            logger.info(f"Managing data transfer: {action}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "datatransfer_v1")

            if action == "list_transfers":
                # List all data transfers
                result = service.transfers().list().execute()
                transfers = result.get("dataTransfers", [])

                if not transfers:
                    return [TextContent(
                        type="text",
                        text="No data transfers found."
                    )]

                response = f"Data Transfers ({len(transfers)} found):\n\n"

                for i, transfer in enumerate(transfers, 1):
                    transfer_id = transfer.get("id", "Unknown")
                    old_owner_id = transfer.get("oldOwnerUserId", "Unknown")
                    new_owner_id = transfer.get("newOwnerUserId", "Unknown")
                    overall_transfer_status = transfer.get("overallTransferStatusCode", "Unknown")
                    request_time = transfer.get("requestTime", "Unknown")

                    response += f"{i}. Transfer ID: {transfer_id}\n"
                    response += f"   👤 From: {old_owner_id}\n"
                    response += f"   👤 To: {new_owner_id}\n"
                    response += f"   📊 Status: {overall_transfer_status}\n"
                    response += f"   📅 Requested: {request_time}\n\n"

                return [TextContent(type="text", text=response)]

            elif action == "get_transfer_status":
                if not transfer_id:
                    raise ValidationError("transfer_id is required for checking transfer status")

                # Get transfer details
                transfer = service.transfers().get(dataTransferId=transfer_id).execute()

                transfer_id = transfer.get("id", "Unknown")
                old_owner_id = transfer.get("oldOwnerUserId", "Unknown")
                new_owner_id = transfer.get("newOwnerUserId", "Unknown")
                overall_status = transfer.get("overallTransferStatusCode", "Unknown")
                request_time = transfer.get("requestTime", "Unknown")

                response = f"Data Transfer Status - ID: {transfer_id}\n\n"
                response += f"👤 From: {old_owner_id}\n"
                response += f"👤 To: {new_owner_id}\n"
                response += f"📊 Overall Status: {overall_status}\n"
                response += f"📅 Request Time: {request_time}\n\n"

                # Show application-specific transfer details
                app_data_transfers = transfer.get("applicationDataTransfers", [])
                if app_data_transfers:
                    response += f"Application Transfer Details:\n"
                    for app_transfer in app_data_transfers:
                        app_id = app_transfer.get("applicationId", "Unknown")
                        transfer_params = app_transfer.get("applicationTransferParams", [])

                        response += f"  📱 Application: {app_id}\n"
                        if transfer_params:
                            for param in transfer_params:
                                key = param.get("key", "Unknown")
                                value = param.get("value", [])
                                response += f"    • {key}: {', '.join(value) if isinstance(value, list) else value}\n"

                return [TextContent(type="text", text=response)]

            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Action '{action}' is not fully implemented yet. Data transfer creation requires careful application configuration."
                )]

        except Exception as e:
            logger.error(f"Error managing data transfer: {e}")
            raise AdminMCPError(f"Failed to manage data transfer: {str(e)}")


# Export all security handlers
SECURITY_HANDLERS: List[AdminToolHandler] = [
    ListDomainAliasesHandler(),
    ManageUserSecurityHandler(),
    ListTokensHandler(),
    ManageRoleAssignmentsHandler(),
    ManageDataTransferHandler()
]