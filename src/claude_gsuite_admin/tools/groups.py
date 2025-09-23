"""Google Workspace Group Management Tools."""

import logging
from typing import Any, Dict, List, Sequence
from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import AdminMCPError, ValidationError
from ..auth.oauth_manager import OAuthManager

logger = logging.getLogger(__name__)


class ListGroupsHandler(AdminToolHandler):
    """Handler for listing Google Workspace groups."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_groups")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List groups in a Google Workspace domain",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain to list groups from"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of groups to return",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 500
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query to filter groups (optional)"
                    }
                },
                "required": [USER_ID_ARG, "domain"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            domain = arguments["domain"]
            max_results = arguments.get("max_results", 100)
            query = arguments.get("query")

            logger.info(f"Listing groups for domain: {domain}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Build request parameters
            request_params = {
                "domain": domain,
                "maxResults": max_results
            }

            if query:
                request_params["query"] = query

            # Make API call
            result = service.groups().list(**request_params).execute()
            groups = result.get("groups", [])

            if not groups:
                return [TextContent(
                    type="text",
                    text=f"No groups found in domain '{domain}'"
                )]

            # Format response
            response = f"Found {len(groups)} group(s) in '{domain}':\n\n"

            for i, group in enumerate(groups, 1):
                name = group.get("name", "Unknown")
                email = group.get("email", "No email")
                description = group.get("description", "No description")
                member_count = group.get("directMembersCount", "Unknown")

                response += f"{i}. {name}\n"
                response += f"   📧 Email: {email}\n"
                response += f"   📝 Description: {description}\n"
                response += f"   👥 Members: {member_count}\n"
                response += f"   🆔 ID: {group.get('id', 'Unknown')}\n\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing groups: {e}")
            raise AdminMCPError(f"Failed to list groups: {str(e)}")


class GetGroupHandler(AdminToolHandler):
    """Handler for getting details about a specific group."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_group")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get detailed information about a specific Google Workspace group",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "group_email": {
                        "type": "string",
                        "description": "Email address of the group to retrieve"
                    }
                },
                "required": [USER_ID_ARG, "group_email"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            group_email = arguments["group_email"]

            logger.info(f"Getting group details for: {group_email}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Get group details
            group = service.groups().get(groupKey=group_email).execute()

            # Format response
            response = f"Group Details for '{group_email}':\n\n"
            response += f"📛 Name: {group.get('name', 'Unknown')}\n"
            response += f"📧 Email: {group.get('email', 'Unknown')}\n"
            response += f"📝 Description: {group.get('description', 'No description')}\n"
            response += f"👥 Direct Members: {group.get('directMembersCount', 'Unknown')}\n"
            response += f"🆔 Group ID: {group.get('id', 'Unknown')}\n"
            response += f"🏷️ Admin Created: {group.get('adminCreated', 'Unknown')}\n"

            # Get group settings if available
            try:
                settings = service.groups().get(groupKey=group_email).execute()
                if settings:
                    response += f"\n📋 Group Settings:\n"
                    response += f"   - Non-editable: {group.get('nonEditableAliases', [])}\n"
                    response += f"   - Aliases: {group.get('aliases', [])}\n"
            except Exception as e:
                logger.warning(f"Could not get group settings: {e}")

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting group details: {e}")
            raise AdminMCPError(f"Failed to get group details: {str(e)}")


class CreateGroupHandler(AdminToolHandler):
    """Handler for creating a new Google Workspace group."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__create_group")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Create a new Google Workspace group",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "group_email": {
                        "type": "string",
                        "description": "Email address for the new group"
                    },
                    "group_name": {
                        "type": "string",
                        "description": "Display name for the new group"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the group (optional)"
                    }
                },
                "required": [USER_ID_ARG, "group_email", "group_name"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            group_email = arguments["group_email"]
            group_name = arguments["group_name"]
            description = arguments.get("description", "")

            logger.info(f"Creating group: {group_email}")

            # Validate email format
            if "@" not in group_email:
                raise ValidationError("Group email must be a valid email address")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Create group
            group_data = {
                "email": group_email,
                "name": group_name,
                "description": description
            }

            created_group = service.groups().insert(body=group_data).execute()

            response = f"✅ Successfully created group:\n\n"
            response += f"📛 Name: {created_group.get('name')}\n"
            response += f"📧 Email: {created_group.get('email')}\n"
            response += f"📝 Description: {created_group.get('description', 'No description')}\n"
            response += f"🆔 Group ID: {created_group.get('id')}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error creating group: {e}")
            raise AdminMCPError(f"Failed to create group: {str(e)}")


class DeleteGroupHandler(AdminToolHandler):
    """Handler for deleting a Google Workspace group."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__delete_group")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Delete a Google Workspace group",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "group_email": {
                        "type": "string",
                        "description": "Email address of the group to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation that you want to delete the group",
                        "default": False
                    }
                },
                "required": [USER_ID_ARG, "group_email", "confirm"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            group_email = arguments["group_email"]
            confirm = arguments.get("confirm", False)

            if not confirm:
                return [TextContent(
                    type="text",
                    text="❌ Group deletion requires explicit confirmation. Set 'confirm' to true to proceed."
                )]

            logger.info(f"Deleting group: {group_email}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Delete group
            service.groups().delete(groupKey=group_email).execute()

            response = f"✅ Successfully deleted group: {group_email}"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error deleting group: {e}")
            raise AdminMCPError(f"Failed to delete group: {str(e)}")


class ListGroupMembersHandler(AdminToolHandler):
    """Handler for listing members of a Google Workspace group."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_group_members")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List members of a Google Workspace group",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "group_email": {
                        "type": "string",
                        "description": "Email address of the group"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of members to return",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 500
                    }
                },
                "required": [USER_ID_ARG, "group_email"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            group_email = arguments["group_email"]
            max_results = arguments.get("max_results", 100)

            logger.info(f"Listing members for group: {group_email}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # List group members
            result = service.members().list(
                groupKey=group_email,
                maxResults=max_results
            ).execute()

            members = result.get("members", [])

            if not members:
                return [TextContent(
                    type="text",
                    text=f"No members found in group '{group_email}'"
                )]

            # Format response
            response = f"Found {len(members)} member(s) in group '{group_email}':\n\n"

            for i, member in enumerate(members, 1):
                email = member.get("email", "Unknown")
                role = member.get("role", "MEMBER")
                member_type = member.get("type", "USER")
                status = member.get("status", "ACTIVE")

                response += f"{i}. {email}\n"
                response += f"   🎭 Role: {role}\n"
                response += f"   👤 Type: {member_type}\n"
                response += f"   🟢 Status: {status}\n\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing group members: {e}")
            raise AdminMCPError(f"Failed to list group members: {str(e)}")


# Export all group handlers
GROUP_HANDLERS: List[AdminToolHandler] = [
    ListGroupsHandler(),
    GetGroupHandler(),
    CreateGroupHandler(),
    DeleteGroupHandler(),
    ListGroupMembersHandler()
]