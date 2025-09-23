"""Google Workspace Organizational Unit Management Tools."""

import logging
from typing import Any, Dict, List, Sequence
from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import AdminMCPError, ValidationError
from ..auth.oauth_manager import OAuthManager

logger = logging.getLogger(__name__)


class ListOrgUnitsHandler(AdminToolHandler):
    """Handler for listing Google Workspace organizational units."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_org_units")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List organizational units in a Google Workspace domain",
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
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Organization unit path to search within (optional)",
                        "default": "/"
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of organizational units to list",
                        "enum": ["all", "children", "all_including_parent"],
                        "default": "all"
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            org_unit_path = arguments.get("org_unit_path", "/")
            org_type = arguments.get("type", "all")

            logger.info(f"Listing organizational units for customer: {customer_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Make API call
            result = service.orgunits().list(
                customerId=customer_id,
                orgUnitPath=org_unit_path,
                type=org_type
            ).execute()

            org_units = result.get("organizationUnits", [])

            if not org_units:
                return [TextContent(
                    type="text",
                    text=f"No organizational units found under '{org_unit_path}'"
                )]

            # Format response
            response = f"Found {len(org_units)} organizational unit(s):\n\n"

            for i, ou in enumerate(org_units, 1):
                name = ou.get("name", "Unknown")
                path = ou.get("orgUnitPath", "Unknown")
                description = ou.get("description", "No description")
                parent_path = ou.get("parentOrgUnitPath", "No parent")
                block_inheritance = ou.get("blockInheritance", False)

                response += f"{i}. {name}\n"
                response += f"   📁 Path: {path}\n"
                response += f"   📝 Description: {description}\n"
                response += f"   📂 Parent: {parent_path}\n"
                response += f"   🚫 Block Inheritance: {block_inheritance}\n"
                response += f"   🆔 ID: {ou.get('orgUnitId', 'Unknown')}\n\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing organizational units: {e}")
            raise AdminMCPError(f"Failed to list organizational units: {str(e)}")


class GetOrgUnitHandler(AdminToolHandler):
    """Handler for getting details about a specific organizational unit."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_org_unit")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get detailed information about a specific organizational unit",
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
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Organization unit path to retrieve"
                    }
                },
                "required": [USER_ID_ARG, "org_unit_path"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            org_unit_path = arguments["org_unit_path"]

            logger.info(f"Getting organizational unit details for: {org_unit_path}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Get organizational unit details
            ou = service.orgunits().get(
                customerId=customer_id,
                orgUnitPath=org_unit_path
            ).execute()

            # Format response
            response = f"Organizational Unit Details for '{org_unit_path}':\n\n"
            response += f"📛 Name: {ou.get('name', 'Unknown')}\n"
            response += f"📁 Path: {ou.get('orgUnitPath', 'Unknown')}\n"
            response += f"📝 Description: {ou.get('description', 'No description')}\n"
            response += f"📂 Parent Path: {ou.get('parentOrgUnitPath', 'No parent')}\n"
            response += f"🆔 Organization Unit ID: {ou.get('orgUnitId', 'Unknown')}\n"
            response += f"🚫 Block Inheritance: {ou.get('blockInheritance', False)}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting organizational unit details: {e}")
            raise AdminMCPError(f"Failed to get organizational unit details: {str(e)}")


class CreateOrgUnitHandler(AdminToolHandler):
    """Handler for creating a new organizational unit."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__create_org_unit")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Create a new organizational unit",
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
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the new organizational unit"
                    },
                    "parent_org_unit_path": {
                        "type": "string",
                        "description": "Parent organizational unit path",
                        "default": "/"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the organizational unit (optional)"
                    },
                    "block_inheritance": {
                        "type": "boolean",
                        "description": "Whether to block inheritance from parent OU",
                        "default": False
                    }
                },
                "required": [USER_ID_ARG, "name"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            name = arguments["name"]
            parent_path = arguments.get("parent_org_unit_path", "/")
            description = arguments.get("description", "")
            block_inheritance = arguments.get("block_inheritance", False)

            logger.info(f"Creating organizational unit: {name}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Create organizational unit
            ou_data = {
                "name": name,
                "parentOrgUnitPath": parent_path,
                "description": description,
                "blockInheritance": block_inheritance
            }

            created_ou = service.orgunits().insert(
                customerId=customer_id,
                body=ou_data
            ).execute()

            response = f"✅ Successfully created organizational unit:\n\n"
            response += f"📛 Name: {created_ou.get('name')}\n"
            response += f"📁 Path: {created_ou.get('orgUnitPath')}\n"
            response += f"📝 Description: {created_ou.get('description', 'No description')}\n"
            response += f"📂 Parent Path: {created_ou.get('parentOrgUnitPath')}\n"
            response += f"🆔 Organization Unit ID: {created_ou.get('orgUnitId')}\n"
            response += f"🚫 Block Inheritance: {created_ou.get('blockInheritance', False)}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error creating organizational unit: {e}")
            raise AdminMCPError(f"Failed to create organizational unit: {str(e)}")


class UpdateOrgUnitHandler(AdminToolHandler):
    """Handler for updating an organizational unit."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__update_org_unit")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Update an existing organizational unit",
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
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Current path of the organizational unit to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "New name for the organizational unit (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the organizational unit (optional)"
                    },
                    "parent_org_unit_path": {
                        "type": "string",
                        "description": "New parent path (for moving the OU) (optional)"
                    },
                    "block_inheritance": {
                        "type": "boolean",
                        "description": "Whether to block inheritance from parent OU (optional)"
                    }
                },
                "required": [USER_ID_ARG, "org_unit_path"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            org_unit_path = arguments["org_unit_path"]

            logger.info(f"Updating organizational unit: {org_unit_path}")

            # Build update data (only include fields that were provided)
            update_data = {}
            if "name" in arguments:
                update_data["name"] = arguments["name"]
            if "description" in arguments:
                update_data["description"] = arguments["description"]
            if "parent_org_unit_path" in arguments:
                update_data["parentOrgUnitPath"] = arguments["parent_org_unit_path"]
            if "block_inheritance" in arguments:
                update_data["blockInheritance"] = arguments["block_inheritance"]

            if not update_data:
                return [TextContent(
                    type="text",
                    text="❌ No update fields provided. Please specify at least one field to update."
                )]

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Update organizational unit
            updated_ou = service.orgunits().update(
                customerId=customer_id,
                orgUnitPath=org_unit_path,
                body=update_data
            ).execute()

            response = f"✅ Successfully updated organizational unit:\n\n"
            response += f"📛 Name: {updated_ou.get('name')}\n"
            response += f"📁 Path: {updated_ou.get('orgUnitPath')}\n"
            response += f"📝 Description: {updated_ou.get('description', 'No description')}\n"
            response += f"📂 Parent Path: {updated_ou.get('parentOrgUnitPath')}\n"
            response += f"🆔 Organization Unit ID: {updated_ou.get('orgUnitId')}\n"
            response += f"🚫 Block Inheritance: {updated_ou.get('blockInheritance', False)}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error updating organizational unit: {e}")
            raise AdminMCPError(f"Failed to update organizational unit: {str(e)}")


class DeleteOrgUnitHandler(AdminToolHandler):
    """Handler for deleting an organizational unit."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__delete_org_unit")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Delete an organizational unit",
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
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Path of the organizational unit to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation that you want to delete the organizational unit",
                        "default": False
                    }
                },
                "required": [USER_ID_ARG, "org_unit_path", "confirm"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            org_unit_path = arguments["org_unit_path"]
            confirm = arguments.get("confirm", False)

            if not confirm:
                return [TextContent(
                    type="text",
                    text="❌ Organizational unit deletion requires explicit confirmation. Set 'confirm' to true to proceed."
                )]

            logger.info(f"Deleting organizational unit: {org_unit_path}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Delete organizational unit
            service.orgunits().delete(
                customerId=customer_id,
                orgUnitPath=org_unit_path
            ).execute()

            response = f"✅ Successfully deleted organizational unit: {org_unit_path}"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error deleting organizational unit: {e}")
            raise AdminMCPError(f"Failed to delete organizational unit: {str(e)}")


# Export all organizational unit handlers
ORG_UNIT_HANDLERS: List[AdminToolHandler] = [
    ListOrgUnitsHandler(),
    GetOrgUnitHandler(),
    CreateOrgUnitHandler(),
    UpdateOrgUnitHandler(),
    DeleteOrgUnitHandler()
]