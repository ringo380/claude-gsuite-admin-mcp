"""Google Workspace Gmail Administration Tools."""

import logging
from typing import Any, Dict, List, Optional, Sequence
from collections.abc import Sequence as AbstractSequence

from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import ValidationError, UserNotFoundError
from ..utils.validators import validate_email
from ..utils.logging import get_logger, log_tool_execution, log_api_call


logger = get_logger('tools.gmail')


class GetGmailSettingsHandler(AdminToolHandler):
    """Handler for retrieving Gmail settings for a user."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_gmail_settings")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get Gmail settings for a specific user.
            Returns forwarding, delegation, IMAP/POP settings, and storage information.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user whose Gmail settings to retrieve"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the Gmail settings retrieval operation."""
        user_id = args.get("user_id")
        target_user = args.get("target_user")

        if not user_id:
            raise ValidationError("user_id is required")
        if not target_user:
            raise ValidationError("target_user is required")

        validate_email(target_user)

        try:
            gmail_service = self.get_google_service(user_id, "gmail", "v1", target_user)

            # Get Gmail profile
            profile = gmail_service.users().getProfile(userId="me").execute()

            # Get Gmail settings
            settings = gmail_service.users().settings()

            # Get forwarding settings
            try:
                forwarding = settings.getForwarding(userId="me").execute()
            except Exception:
                forwarding = {"enabled": False}

            # Get delegates
            try:
                delegates_response = settings.delegates().list(userId="me").execute()
                delegates = delegates_response.get("delegates", [])
            except Exception:
                delegates = []

            # Get IMAP settings
            try:
                imap_settings = settings.getImap(userId="me").execute()
            except Exception:
                imap_settings = {"enabled": False}

            # Get POP settings
            try:
                pop_settings = settings.getPop(userId="me").execute()
            except Exception:
                pop_settings = {"enabled": False}

            response_text = f"## Gmail Settings for {target_user}\n\n"

            # Profile information
            response_text += "### Profile Information\n"
            response_text += f"**Email Address:** {profile.get('emailAddress', 'N/A')}\n"
            response_text += f"**Messages Total:** {profile.get('messagesTotal', 0):,}\n"
            response_text += f"**Threads Total:** {profile.get('threadsTotal', 0):,}\n"
            response_text += f"**History ID:** {profile.get('historyId', 'N/A')}\n\n"

            # Forwarding settings
            response_text += "### Email Forwarding\n"
            if forwarding.get("enabled"):
                response_text += f"**Status:** Enabled ✅\n"
                response_text += f"**Forward To:** {forwarding.get('forwardingEmail', 'N/A')}\n"
                response_text += f"**Disposition:** {forwarding.get('disposition', 'N/A')}\n"
            else:
                response_text += "**Status:** Disabled\n"
            response_text += "\n"

            # Delegation settings
            response_text += "### Email Delegation\n"
            if delegates:
                response_text += f"**Delegates ({len(delegates)}):**\n"
                for delegate in delegates:
                    response_text += f"• {delegate.get('delegateEmail', 'N/A')}\n"
                    response_text += f"  - Status: {delegate.get('verificationStatus', 'unknown')}\n"
            else:
                response_text += "**No delegates configured**\n"
            response_text += "\n"

            # IMAP settings
            response_text += "### IMAP Access\n"
            response_text += f"**Status:** {'Enabled' if imap_settings.get('enabled') else 'Disabled'}\n"
            if imap_settings.get('enabled'):
                response_text += f"**Auto Expunge:** {'Yes' if imap_settings.get('autoExpunge') else 'No'}\n"
                response_text += f"**Expunge Behavior:** {imap_settings.get('expungeBehavior', 'N/A')}\n"
                response_text += f"**Max Folder Size:** {imap_settings.get('maxFolderSize', 'N/A')}\n"
            response_text += "\n"

            # POP settings
            response_text += "### POP Access\n"
            response_text += f"**Status:** {'Enabled' if pop_settings.get('enabled') else 'Disabled'}\n"
            if pop_settings.get('enabled'):
                response_text += f"**Access Window:** {pop_settings.get('accessWindow', 'N/A')}\n"
                response_text += f"**Disposition:** {pop_settings.get('disposition', 'N/A')}\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"get Gmail settings for {target_user}")


class SetGmailForwardingHandler(AdminToolHandler):
    """Handler for setting up Gmail forwarding."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__set_gmail_forwarding")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Set up email forwarding for a user's Gmail account.
            Can enable, disable, or update forwarding settings.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user to configure forwarding for"
                    },
                    "forwarding_email": {
                        "type": "string",
                        "description": "Email address to forward to (required if enabling)"
                    },
                    "enabled": {
                        "type": "boolean",
                        "description": "Whether to enable forwarding"
                    },
                    "disposition": {
                        "type": "string",
                        "description": "What to do with forwarded emails",
                        "enum": ["leaveInInbox", "archive", "trash", "markRead"],
                        "default": "leaveInInbox"
                    }
                },
                "required": [USER_ID_ARG, "target_user", "enabled"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the Gmail forwarding configuration operation."""
        user_id = args.get("user_id")
        target_user = args.get("target_user")
        forwarding_email = args.get("forwarding_email")
        enabled = args.get("enabled")
        disposition = args.get("disposition", "leaveInInbox")

        if not user_id:
            raise ValidationError("user_id is required")
        if not target_user:
            raise ValidationError("target_user is required")
        if enabled and not forwarding_email:
            raise ValidationError("forwarding_email is required when enabling forwarding")

        validate_email(target_user)
        if forwarding_email:
            validate_email(forwarding_email)

        try:
            gmail_service = self.get_google_service(user_id, "gmail", "v1", target_user)
            settings = gmail_service.users().settings()

            if enabled:
                # Create forwarding address first
                forward_body = {
                    "forwardingEmail": forwarding_email
                }
                settings.forwardingAddresses().create(
                    userId="me",
                    body=forward_body
                ).execute()

                # Set forwarding settings
                forwarding_body = {
                    "enabled": True,
                    "forwardingEmail": forwarding_email,
                    "disposition": disposition
                }
                result = settings.updateForwarding(
                    userId="me",
                    body=forwarding_body
                ).execute()

                response_text = f"## Gmail Forwarding Enabled\n\n"
                response_text += f"**User:** {target_user}\n"
                response_text += f"**Forward To:** {forwarding_email}\n"
                response_text += f"**Disposition:** {disposition}\n\n"
                response_text += "**Important Notes:**\n"
                response_text += "• The forwarding address may require verification\n"
                response_text += "• Check the forwarding email for a verification message\n"
                response_text += "• Forwarding will not be active until verification is complete\n"

            else:
                # Disable forwarding
                forwarding_body = {
                    "enabled": False
                }
                result = settings.updateForwarding(
                    userId="me",
                    body=forwarding_body
                ).execute()

                response_text = f"## Gmail Forwarding Disabled\n\n"
                response_text += f"**User:** {target_user}\n"
                response_text += "**Status:** Forwarding has been disabled\n\n"
                response_text += "Existing forwarding addresses remain configured but inactive.\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"set Gmail forwarding for {target_user}")


class ManageGmailDelegationHandler(AdminToolHandler):
    """Handler for managing Gmail delegation."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_gmail_delegation")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Manage Gmail delegation for a user.
            Add or remove delegates who can access the user's Gmail account.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user to manage delegation for"
                    },
                    "delegate_email": {
                        "type": "string",
                        "description": "Email address of the delegate"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["add", "remove", "list"]
                    }
                },
                "required": [USER_ID_ARG, "target_user", "action"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the Gmail delegation management operation."""
        user_id = args.get("user_id")
        target_user = args.get("target_user")
        delegate_email = args.get("delegate_email")
        action = args.get("action")

        if not user_id:
            raise ValidationError("user_id is required")
        if not target_user:
            raise ValidationError("target_user is required")
        if action in ["add", "remove"] and not delegate_email:
            raise ValidationError("delegate_email is required for add/remove actions")

        validate_email(target_user)
        if delegate_email:
            validate_email(delegate_email)

        try:
            gmail_service = self.get_google_service(user_id, "gmail", "v1", target_user)
            delegates_api = gmail_service.users().settings().delegates()

            if action == "list":
                # List existing delegates
                result = delegates_api.list(userId="me").execute()
                delegates = result.get("delegates", [])

                response_text = f"## Gmail Delegates for {target_user}\n\n"
                if delegates:
                    response_text += f"**Total Delegates:** {len(delegates)}\n\n"
                    for delegate in delegates:
                        response_text += f"**{delegate.get('delegateEmail', 'N/A')}**\n"
                        response_text += f"• Status: {delegate.get('verificationStatus', 'unknown')}\n\n"
                else:
                    response_text += "**No delegates configured**\n"

            elif action == "add":
                # Add delegate
                delegate_body = {
                    "delegateEmail": delegate_email
                }
                result = delegates_api.create(
                    userId="me",
                    body=delegate_body
                ).execute()

                response_text = f"## Gmail Delegate Added\n\n"
                response_text += f"**User:** {target_user}\n"
                response_text += f"**Delegate:** {delegate_email}\n"
                response_text += f"**Status:** {result.get('verificationStatus', 'pending')}\n\n"
                response_text += "**Important Notes:**\n"
                response_text += "• The delegate will receive a verification email\n"
                response_text += "• Access is not granted until verification is complete\n"
                response_text += "• Delegates can read, send, and delete emails on behalf of the user\n"

            elif action == "remove":
                # Remove delegate
                delegates_api.delete(
                    userId="me",
                    delegateEmail=delegate_email
                ).execute()

                response_text = f"## Gmail Delegate Removed\n\n"
                response_text += f"**User:** {target_user}\n"
                response_text += f"**Removed Delegate:** {delegate_email}\n\n"
                response_text += "The delegate no longer has access to this Gmail account.\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"manage Gmail delegation for {target_user}")


class SetGmailAccessSettingsHandler(AdminToolHandler):
    """Handler for configuring Gmail IMAP/POP access settings."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__set_gmail_access")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Configure Gmail IMAP and POP access settings for a user.
            Enable or disable external email client access.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user to configure access for"
                    },
                    "imap_enabled": {
                        "type": "boolean",
                        "description": "Whether to enable IMAP access"
                    },
                    "pop_enabled": {
                        "type": "boolean",
                        "description": "Whether to enable POP access"
                    },
                    "pop_access_window": {
                        "type": "string",
                        "description": "POP access window",
                        "enum": ["disabled", "fromNowOn", "allMail"],
                        "default": "fromNowOn"
                    },
                    "pop_disposition": {
                        "type": "string",
                        "description": "What to do with emails after POP access",
                        "enum": ["leaveInInbox", "archive", "trash"],
                        "default": "leaveInInbox"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the Gmail access settings configuration operation."""
        user_id = args.get("user_id")
        target_user = args.get("target_user")
        imap_enabled = args.get("imap_enabled")
        pop_enabled = args.get("pop_enabled")
        pop_access_window = args.get("pop_access_window", "fromNowOn")
        pop_disposition = args.get("pop_disposition", "leaveInInbox")

        if not user_id:
            raise ValidationError("user_id is required")
        if not target_user:
            raise ValidationError("target_user is required")

        validate_email(target_user)

        try:
            gmail_service = self.get_google_service(user_id, "gmail", "v1", target_user)
            settings = gmail_service.users().settings()

            response_text = f"## Gmail Access Settings Updated\n\n"
            response_text += f"**User:** {target_user}\n\n"

            # Update IMAP settings if specified
            if imap_enabled is not None:
                imap_body = {
                    "enabled": imap_enabled,
                    "autoExpunge": True,
                    "expungeBehavior": "expungeImmediately",
                    "maxFolderSize": 0
                }
                settings.updateImap(userId="me", body=imap_body).execute()
                response_text += f"**IMAP Access:** {'Enabled' if imap_enabled else 'Disabled'}\n"

            # Update POP settings if specified
            if pop_enabled is not None:
                if pop_enabled:
                    pop_body = {
                        "enabled": True,
                        "accessWindow": pop_access_window,
                        "disposition": pop_disposition
                    }
                else:
                    pop_body = {
                        "enabled": False
                    }
                settings.updatePop(userId="me", body=pop_body).execute()
                response_text += f"**POP Access:** {'Enabled' if pop_enabled else 'Disabled'}\n"
                if pop_enabled:
                    response_text += f"  • Access Window: {pop_access_window}\n"
                    response_text += f"  • Disposition: {pop_disposition}\n"

            response_text += "\n**Important Notes:**\n"
            response_text += "• Changes may take a few minutes to take effect\n"
            response_text += "• Users may need to restart their email clients\n"
            response_text += "• App passwords may be required for some clients\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"set Gmail access settings for {target_user}")


class GetGmailStorageHandler(AdminToolHandler):
    """Handler for retrieving Gmail storage information."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_gmail_storage")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get Gmail storage usage and quota information for a user.
            Returns mailbox size, quota limits, and storage breakdown.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user to check storage for"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the Gmail storage retrieval operation."""
        user_id = args.get("user_id")
        target_user = args.get("target_user")

        if not user_id:
            raise ValidationError("user_id is required")
        if not target_user:
            raise ValidationError("target_user is required")

        validate_email(target_user)

        try:
            # Get user info from Directory API for storage quota
            directory_service = self.get_google_service(user_id, "admin", "directory_v1")
            user_info = directory_service.users().get(userKey=target_user).execute()

            # Get Gmail profile for message counts
            gmail_service = self.get_google_service(user_id, "gmail", "v1", target_user)
            profile = gmail_service.users().getProfile(userId="me").execute()

            # Get label information for storage breakdown
            labels_response = gmail_service.users().labels().list(userId="me").execute()
            labels = labels_response.get("labels", [])

            response_text = f"## Gmail Storage Information for {target_user}\n\n"

            # Basic profile stats
            response_text += "### Mailbox Statistics\n"
            response_text += f"**Total Messages:** {profile.get('messagesTotal', 0):,}\n"
            response_text += f"**Total Threads:** {profile.get('threadsTotal', 0):,}\n"
            response_text += f"**History ID:** {profile.get('historyId', 'N/A')}\n\n"

            # Storage quota (from user profile)
            if 'quotaBytesUsed' in user_info:
                quota_used = int(user_info['quotaBytesUsed'])
                quota_used_gb = quota_used / (1024**3)
                response_text += "### Storage Usage\n"
                response_text += f"**Used:** {quota_used_gb:.2f} GB ({quota_used:,} bytes)\n"

                if 'quotaBytesTotal' in user_info:
                    quota_total = int(user_info['quotaBytesTotal'])
                    if quota_total > 0:
                        quota_total_gb = quota_total / (1024**3)
                        usage_percent = (quota_used / quota_total) * 100
                        response_text += f"**Total Quota:** {quota_total_gb:.2f} GB\n"
                        response_text += f"**Usage:** {usage_percent:.1f}%\n"

                        # Usage indicator
                        if usage_percent > 90:
                            response_text += "**Status:** ⚠️ Critical - Storage nearly full\n"
                        elif usage_percent > 75:
                            response_text += "**Status:** ⚠️ Warning - High storage usage\n"
                        else:
                            response_text += "**Status:** ✅ Normal usage\n"
                    else:
                        response_text += "**Total Quota:** Unlimited\n"
                response_text += "\n"

            # Label breakdown
            system_labels = []
            user_labels = []

            for label in labels:
                if label.get('type') == 'system':
                    system_labels.append(label)
                else:
                    user_labels.append(label)

            if system_labels:
                response_text += "### System Labels\n"
                for label in system_labels[:10]:  # Show top 10
                    name = label.get('name', 'Unknown')
                    messages_total = label.get('messagesTotal', 0)
                    threads_total = label.get('threadsTotal', 0)
                    response_text += f"**{name}:** {messages_total:,} messages, {threads_total:,} threads\n"
                if len(system_labels) > 10:
                    response_text += f"*... and {len(system_labels) - 10} more system labels*\n"
                response_text += "\n"

            if user_labels:
                response_text += f"### Custom Labels ({len(user_labels)})\n"
                for label in user_labels[:5]:  # Show top 5
                    name = label.get('name', 'Unknown')
                    messages_total = label.get('messagesTotal', 0)
                    response_text += f"**{name}:** {messages_total:,} messages\n"
                if len(user_labels) > 5:
                    response_text += f"*... and {len(user_labels) - 5} more custom labels*\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"get Gmail storage for {target_user}")


# Export all handlers
GMAIL_HANDLERS = [
    GetGmailSettingsHandler(),
    SetGmailForwardingHandler(),
    ManageGmailDelegationHandler(),
    SetGmailAccessSettingsHandler(),
    GetGmailStorageHandler(),
]