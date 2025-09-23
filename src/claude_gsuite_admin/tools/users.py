"""Google Workspace User Management Tools."""

import logging
import secrets
import string
from typing import Any, Dict, List, Optional, Sequence, Union
from collections.abc import Sequence as AbstractSequence

from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import ValidationError, UserNotFoundError, DuplicateResourceError
from ..utils.validators import validate_email


class ListUsersHandler(AdminToolHandler):
    """Handler for listing Google Workspace users."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_users")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""List Google Workspace users with optional filtering.
            Can search by domain, organizational unit, or query string.
            Returns user details including name, email, status, and last login.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain to list users from (optional)"
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Organizational unit path to filter by (optional)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (name, email, etc.) (optional)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 100, max: 500)",
                        "minimum": 1,
                        "maximum": 500
                    },
                    "order_by": {
                        "type": "string",
                        "description": "Sort field (email, givenName, familyName)",
                        "enum": ["email", "givenName", "familyName"]
                    },
                    "show_suspended": {
                        "type": "boolean",
                        "description": "Include suspended users (default: true)"
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Build request parameters
            request_params = {}

            if 'domain' in args:
                request_params['domain'] = args['domain']
            else:
                request_params['customer'] = 'my_customer'

            if 'org_unit_path' in args:
                request_params['orgUnitPath'] = args['org_unit_path']

            if 'query' in args and args['query']:
                request_params['query'] = args['query']

            if 'order_by' in args:
                request_params['orderBy'] = args['order_by']

            # Set max results
            max_results = min(args.get('max_results', 100), 500)
            request_params['maxResults'] = max_results

            # Handle show suspended
            if 'show_suspended' in args and not args['show_suspended']:
                # Add to query to exclude suspended users
                existing_query = request_params.get('query', '')
                suspend_query = 'isSuspended=false'
                if existing_query:
                    request_params['query'] = f"{existing_query} {suspend_query}"
                else:
                    request_params['query'] = suspend_query

            # Execute request
            result = service.users().list(**request_params).execute()
            users = result.get('users', [])

            if not users:
                return [TextContent(type="text", text="No users found matching the criteria.")]

            # Format response
            response_text = f"Found {len(users)} user(s):\n\n"

            for i, user in enumerate(users, 1):
                name = user.get('name', {})
                full_name = name.get('fullName', 'Unknown')
                email = user.get('primaryEmail', 'No email')
                suspended = user.get('suspended', False)
                org_unit = user.get('orgUnitPath', '/')
                last_login = user.get('lastLoginTime', 'Never')

                status_indicator = "🔴 SUSPENDED" if suspended else "🟢 ACTIVE"

                response_text += f"{i}. {full_name}\n"
                response_text += f"   📧 Email: {email}\n"
                response_text += f"   {status_indicator}\n"
                response_text += f"   🏢 Org Unit: {org_unit}\n"
                response_text += f"   🕐 Last Login: {last_login}\n\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "list users")


class GetUserHandler(AdminToolHandler):
    """Handler for getting detailed information about a specific user."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_user")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get detailed information about a specific Google Workspace user.
            Returns comprehensive user details including profile, settings, and organizational info.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email or user ID of the user to retrieve"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)
            self.validate_required_args(args, ["target_user"])

            target_user = args["target_user"]
            validate_email(target_user)

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Get user details
            user = service.users().get(userKey=target_user).execute()

            # Format detailed response
            name = user.get('name', {})
            response_text = f"User Details: {name.get('fullName', 'Unknown')}\n"
            response_text += "=" * 50 + "\n\n"

            # Basic Info
            response_text += "📋 Basic Information:\n"
            response_text += f"   Full Name: {name.get('fullName', 'N/A')}\n"
            response_text += f"   First Name: {name.get('givenName', 'N/A')}\n"
            response_text += f"   Last Name: {name.get('familyName', 'N/A')}\n"
            response_text += f"   Primary Email: {user.get('primaryEmail', 'N/A')}\n"
            response_text += f"   User ID: {user.get('id', 'N/A')}\n\n"

            # Status
            suspended = user.get('suspended', False)
            status_text = "🔴 SUSPENDED" if suspended else "🟢 ACTIVE"
            response_text += f"📊 Status: {status_text}\n"
            if suspended:
                response_text += f"   Suspension Reason: {user.get('suspensionReason', 'N/A')}\n"
            response_text += f"   Account Created: {user.get('creationTime', 'N/A')}\n"
            response_text += f"   Last Login: {user.get('lastLoginTime', 'Never')}\n\n"

            # Organization
            response_text += "🏢 Organization:\n"
            response_text += f"   Org Unit: {user.get('orgUnitPath', '/')}\n"
            response_text += f"   Admin: {'Yes' if user.get('isAdmin', False) else 'No'}\n"
            response_text += f"   Delegated Admin: {'Yes' if user.get('isDelegatedAdmin', False) else 'No'}\n\n"

            # Email aliases
            aliases = user.get('aliases', [])
            response_text += f"📧 Email Aliases ({len(aliases)}):\n"
            if aliases:
                for alias in aliases:
                    response_text += f"   • {alias}\n"
            else:
                response_text += "   No aliases\n"
            response_text += "\n"

            # Additional info
            if user.get('recoveryEmail'):
                response_text += f"🔄 Recovery Email: {user.get('recoveryEmail')}\n"
            if user.get('recoveryPhone'):
                response_text += f"📱 Recovery Phone: {user.get('recoveryPhone')}\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "get user details")


class CreateUserHandler(AdminToolHandler):
    """Handler for creating new Google Workspace users."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__create_user")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Create a new Google Workspace user account.
            Requires email, first name, last name, and optionally a password.
            If no password is provided, a secure random password is generated.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "email": {
                        "type": "string",
                        "description": "Primary email address for the new user"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "First name"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "Last name"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password (optional, will generate if not provided)"
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Organizational unit path (default: /)"
                    },
                    "change_password_next_login": {
                        "type": "boolean",
                        "description": "Force password change on next login (default: true)"
                    },
                    "suspended": {
                        "type": "boolean",
                        "description": "Create account as suspended (default: false)"
                    }
                },
                "required": [USER_ID_ARG, "email", "first_name", "last_name"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)
            self.validate_required_args(args, ["email", "first_name", "last_name"])

            email = args["email"]
            validate_email(email)

            first_name = args["first_name"].strip()
            last_name = args["last_name"].strip()

            if not first_name or not last_name:
                raise ValidationError("First name and last name cannot be empty")

            # Generate password if not provided
            password = args.get("password")
            generated_password = False
            if not password:
                password = self._generate_secure_password()
                generated_password = True

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Prepare user data
            user_data = {
                'primaryEmail': email,
                'name': {
                    'givenName': first_name,
                    'familyName': last_name
                },
                'password': password,
                'changePasswordAtNextLogin': args.get('change_password_next_login', True),
                'suspended': args.get('suspended', False),
                'orgUnitPath': args.get('org_unit_path', '/')
            }

            # Create user
            result = service.users().insert(body=user_data).execute()

            # Format success response
            response_text = f"✅ Successfully created user: {email}\n\n"
            response_text += f"👤 Name: {first_name} {last_name}\n"
            response_text += f"📧 Email: {email}\n"
            response_text += f"🏢 Org Unit: {user_data['orgUnitPath']}\n"
            response_text += f"🔐 Change Password Next Login: {'Yes' if user_data['changePasswordAtNextLogin'] else 'No'}\n"

            if generated_password:
                response_text += f"\n🔑 Generated Password: {password}\n"
                response_text += "⚠️  Please provide this password to the user securely.\n"

            response_text += f"\n📋 User ID: {result.get('id', 'N/A')}"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "create user")

    def _generate_secure_password(self, length: int = 12) -> str:
        """Generate a secure random password."""
        # Ensure password contains at least one of each character type
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*"

        # Start with one character from each type
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special_chars)
        ]

        # Fill remaining length with random choices from all characters
        all_chars = lowercase + uppercase + digits + special_chars
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)


class UpdateUserHandler(AdminToolHandler):
    """Handler for updating Google Workspace user properties."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__update_user")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Update properties of an existing Google Workspace user.
            Can update name, organizational unit, suspension status, and other user properties.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email or user ID of the user to update"
                    },
                    "first_name": {
                        "type": "string",
                        "description": "New first name (optional)"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "New last name (optional)"
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "New organizational unit path (optional)"
                    },
                    "suspended": {
                        "type": "boolean",
                        "description": "Suspend or unsuspend user (optional)"
                    },
                    "suspension_reason": {
                        "type": "string",
                        "description": "Reason for suspension (required if suspending)"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)
            self.validate_required_args(args, ["target_user"])

            target_user = args["target_user"]
            validate_email(target_user)

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Build update data
            update_data = {}
            changes = []

            # Name updates
            if args.get("first_name") or args.get("last_name"):
                name_data = {}
                if args.get("first_name"):
                    name_data["givenName"] = args["first_name"].strip()
                    changes.append(f"First name: {name_data['givenName']}")
                if args.get("last_name"):
                    name_data["familyName"] = args["last_name"].strip()
                    changes.append(f"Last name: {name_data['familyName']}")
                update_data["name"] = name_data

            # Organizational unit
            if "org_unit_path" in args:
                update_data["orgUnitPath"] = args["org_unit_path"]
                changes.append(f"Org Unit: {args['org_unit_path']}")

            # Suspension status
            if "suspended" in args:
                suspended = args["suspended"]
                update_data["suspended"] = suspended

                if suspended:
                    suspension_reason = args.get("suspension_reason", "Administrative action")
                    update_data["suspensionReason"] = suspension_reason
                    changes.append(f"Suspended: {suspension_reason}")
                else:
                    changes.append("Unsuspended")

            if not update_data:
                raise ValidationError("No update fields provided")

            # Execute update
            service.users().update(userKey=target_user, body=update_data).execute()

            # Format response
            response_text = f"✅ Successfully updated user: {target_user}\n\n"
            response_text += "Changes made:\n"
            for change in changes:
                response_text += f"  • {change}\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "update user")


class SuspendUserHandler(AdminToolHandler):
    """Handler for suspending/unsuspending Google Workspace users."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__suspend_user")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Suspend or unsuspend a Google Workspace user account.
            Suspended users cannot sign in to Google Workspace services.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email or user ID of the user to suspend/unsuspend"
                    },
                    "suspend": {
                        "type": "boolean",
                        "description": "True to suspend, False to unsuspend"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for suspension (required when suspending)"
                    }
                },
                "required": [USER_ID_ARG, "target_user", "suspend"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)
            self.validate_required_args(args, ["target_user", "suspend"])

            target_user = args["target_user"]
            validate_email(target_user)
            suspend = args["suspend"]

            if suspend and not args.get("reason"):
                raise ValidationError("Reason is required when suspending a user")

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Prepare update data
            update_data = {"suspended": suspend}
            if suspend and args.get("reason"):
                update_data["suspensionReason"] = args["reason"]

            # Execute update
            service.users().update(userKey=target_user, body=update_data).execute()

            # Format response
            action = "suspended" if suspend else "unsuspended"
            response_text = f"✅ Successfully {action} user: {target_user}\n"

            if suspend:
                response_text += f"\n🔴 Reason: {args.get('reason', 'Administrative action')}\n"
                response_text += "\n⚠️  User will not be able to sign in to Google Workspace services."
            else:
                response_text += "\n🟢 User can now sign in to Google Workspace services."

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"{'suspend' if args.get('suspend') else 'unsuspend'} user")


class ResetPasswordHandler(AdminToolHandler):
    """Handler for resetting Google Workspace user passwords."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__reset_password")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Reset a Google Workspace user's password.
            Can generate a secure random password or use a provided password.
            User will be required to change password on next login.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email or user ID of the user whose password to reset"
                    },
                    "new_password": {
                        "type": "string",
                        "description": "New password (optional, will generate if not provided)"
                    },
                    "force_change_next_login": {
                        "type": "boolean",
                        "description": "Force password change on next login (default: true)"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)
            self.validate_required_args(args, ["target_user"])

            target_user = args["target_user"]
            validate_email(target_user)

            # Generate password if not provided
            new_password = args.get("new_password")
            generated_password = False
            if not new_password:
                new_password = self._generate_secure_password()
                generated_password = True

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Prepare update data
            update_data = {
                "password": new_password,
                "changePasswordAtNextLogin": args.get("force_change_next_login", True)
            }

            # Execute update
            service.users().update(userKey=target_user, body=update_data).execute()

            # Format response
            response_text = f"✅ Successfully reset password for user: {target_user}\n\n"

            if generated_password:
                response_text += f"🔑 New Password: {new_password}\n"
                response_text += "⚠️  Please provide this password to the user securely.\n\n"

            if update_data["changePasswordAtNextLogin"]:
                response_text += "🔐 User will be required to change password on next login."
            else:
                response_text += "🔓 User can use this password immediately."

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "reset password")

    def _generate_secure_password(self, length: int = 12) -> str:
        """Generate a secure random password."""
        # Same implementation as CreateUserHandler
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*"

        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special_chars)
        ]

        all_chars = lowercase + uppercase + digits + special_chars
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        secrets.SystemRandom().shuffle(password)
        return ''.join(password)


class DeleteUserHandler(AdminToolHandler):
    """Handler for deleting Google Workspace users."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__delete_user")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Delete a Google Workspace user account.
            WARNING: This action is irreversible and will permanently delete the user and all associated data.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email or user ID of the user to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation that you want to permanently delete this user"
                    }
                },
                "required": [USER_ID_ARG, "target_user", "confirm"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = self.validate_user_id(args)
            self.validate_required_args(args, ["target_user", "confirm"])

            target_user = args["target_user"]
            validate_email(target_user)

            if not args["confirm"]:
                raise ValidationError("User deletion requires explicit confirmation (confirm: true)")

            # Get authenticated service
            service = self.get_authenticated_service(user_id, 'admin', 'directory_v1')

            # Execute deletion
            service.users().delete(userKey=target_user).execute()

            # Format response
            response_text = f"✅ Successfully deleted user: {target_user}\n\n"
            response_text += "⚠️  WARNING: This action is permanent and cannot be undone.\n"
            response_text += "   • All user data has been permanently deleted\n"
            response_text += "   • Email messages and files are no longer accessible\n"
            response_text += "   • The user cannot sign in to Google Workspace services"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "delete user")


# Export all handlers
USER_HANDLERS = [
    ListUsersHandler(),
    GetUserHandler(),
    CreateUserHandler(),
    UpdateUserHandler(),
    SuspendUserHandler(),
    ResetPasswordHandler(),
    DeleteUserHandler(),
]