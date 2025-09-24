"""Google Workspace Device Management Tools."""

import logging
from typing import Any, Dict, List, Sequence
from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import AdminMCPError, ValidationError
from ..auth.oauth_manager import OAuthManager

logger = logging.getLogger(__name__)


class ListMobileDevicesHandler(AdminToolHandler):
    """Handler for listing Google Workspace mobile devices."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_mobile_devices")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List mobile devices in a Google Workspace domain",
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
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of devices to return",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 500
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query to filter devices (optional)"
                    },
                    "order_by": {
                        "type": "string",
                        "description": "Sort order for results",
                        "enum": ["deviceId", "email", "lastSync", "model", "name", "os", "status", "type"],
                        "default": "email"
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            max_results = arguments.get("max_results", 100)
            query = arguments.get("query")
            order_by = arguments.get("order_by", "email")

            logger.info(f"Listing mobile devices for customer: {customer_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Build request parameters
            request_params = {
                "customerId": customer_id,
                "maxResults": max_results,
                "orderBy": order_by
            }

            if query:
                request_params["query"] = query

            # Make API call
            result = service.mobiledevices().list(**request_params).execute()
            devices = result.get("mobiledevices", [])

            if not devices:
                return [TextContent(
                    type="text",
                    text="No mobile devices found in the domain"
                )]

            # Format response
            response = f"Found {len(devices)} mobile device(s):\n\n"

            for i, device in enumerate(devices, 1):
                name = device.get("name", ["Unknown"])[0] if device.get("name") else "Unknown"
                email = device.get("email", ["Unknown"])[0] if device.get("email") else "Unknown"
                model = device.get("model", "Unknown")
                os_version = device.get("os", "Unknown")
                status = device.get("status", "Unknown")
                last_sync = device.get("lastSync", "Unknown")
                device_id = device.get("resourceId", "Unknown")

                response += f"{i}. {name}\n"
                response += f"   👤 User: {email}\n"
                response += f"   📱 Model: {model}\n"
                response += f"   🔧 OS: {os_version}\n"
                response += f"   🟢 Status: {status}\n"
                response += f"   🔄 Last Sync: {last_sync}\n"
                response += f"   🆔 Device ID: {device_id}\n\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing mobile devices: {e}")
            raise AdminMCPError(f"Failed to list mobile devices: {str(e)}")


class GetMobileDeviceHandler(AdminToolHandler):
    """Handler for getting details about a specific mobile device."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_mobile_device")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get detailed information about a specific mobile device",
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
                    "device_id": {
                        "type": "string",
                        "description": "Resource ID of the mobile device"
                    }
                },
                "required": [USER_ID_ARG, "device_id"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            device_id = arguments["device_id"]

            logger.info(f"Getting mobile device details for: {device_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Get device details
            device = service.mobiledevices().get(
                customerId=customer_id,
                resourceId=device_id
            ).execute()

            # Format response
            response = f"Mobile Device Details for '{device_id}':\n\n"

            names = device.get("name", [])
            emails = device.get("email", [])

            response += f"📱 Name: {names[0] if names else 'Unknown'}\n"
            response += f"👤 User: {emails[0] if emails else 'Unknown'}\n"
            response += f"📱 Model: {device.get('model', 'Unknown')}\n"
            response += f"🔧 OS: {device.get('os', 'Unknown')}\n"
            response += f"🟢 Status: {device.get('status', 'Unknown')}\n"
            response += f"🔄 Last Sync: {device.get('lastSync', 'Unknown')}\n"
            response += f"🆔 Device ID: {device.get('resourceId', 'Unknown')}\n"
            response += f"📡 IMEI: {device.get('imei', 'Unknown')}\n"
            response += f"📶 Network: {device.get('networkOperator', 'Unknown')}\n"
            response += f"🔋 Type: {device.get('type', 'Unknown')}\n"

            # Security settings
            if device.get("managedAccountIsOnOwnerProfile") is not None:
                response += f"\n🔒 Security:\n"
                response += f"   - Managed Account on Owner Profile: {device.get('managedAccountIsOnOwnerProfile')}\n"
                response += f"   - Device Password Status: {device.get('devicePasswordStatus', 'Unknown')}\n"
                response += f"   - Encryption Status: {device.get('encryptionStatus', 'Unknown')}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting mobile device details: {e}")
            raise AdminMCPError(f"Failed to get mobile device details: {str(e)}")


class ManageMobileDeviceHandler(AdminToolHandler):
    """Handler for managing mobile device actions (approve, block, wipe)."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_mobile_device")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Perform management actions on a mobile device (approve, block, wipe, delete)",
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
                    "device_id": {
                        "type": "string",
                        "description": "Resource ID of the mobile device"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform on the device",
                        "enum": ["approve", "block", "cancel_remote_wipe_then_activate", "cancel_remote_wipe_then_block", "admin_remote_wipe", "admin_account_wipe", "delete"]
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation for destructive actions (wipe, delete)",
                        "default": False
                    }
                },
                "required": [USER_ID_ARG, "device_id", "action"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            device_id = arguments["device_id"]
            action = arguments["action"]
            confirm = arguments.get("confirm", False)

            # Check for destructive actions
            destructive_actions = ["admin_remote_wipe", "admin_account_wipe", "delete"]
            if action in destructive_actions and not confirm:
                return [TextContent(
                    type="text",
                    text=f"❌ Action '{action}' requires explicit confirmation. Set 'confirm' to true to proceed."
                )]

            logger.info(f"Performing action '{action}' on mobile device: {device_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Perform the action
            if action == "delete":
                service.mobiledevices().delete(
                    customerId=customer_id,
                    resourceId=device_id
                ).execute()
                response = f"✅ Successfully deleted mobile device: {device_id}"
            else:
                # For other actions, use the action endpoint
                service.mobiledevices().action(
                    customerId=customer_id,
                    resourceId=device_id,
                    body={"action": action}
                ).execute()

                action_messages = {
                    "approve": "approved",
                    "block": "blocked",
                    "cancel_remote_wipe_then_activate": "cancelled remote wipe and activated",
                    "cancel_remote_wipe_then_block": "cancelled remote wipe and blocked",
                    "admin_remote_wipe": "initiated admin remote wipe on",
                    "admin_account_wipe": "initiated admin account wipe on"
                }

                response = f"✅ Successfully {action_messages.get(action, action)} device: {device_id}"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error managing mobile device: {e}")
            raise AdminMCPError(f"Failed to manage mobile device: {str(e)}")


class ListChromeDevicesHandler(AdminToolHandler):
    """Handler for listing Chrome OS devices."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_chrome_devices")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="List Chrome OS devices in a Google Workspace domain",
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
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of devices to return",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 500
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query to filter devices (optional)"
                    },
                    "order_by": {
                        "type": "string",
                        "description": "Sort order for results",
                        "enum": ["annotatedLocation", "annotatedUser", "lastSync", "notes", "serialNumber", "status", "supportEndDate"],
                        "default": "lastSync"
                    },
                    "org_unit_path": {
                        "type": "string",
                        "description": "Organization unit path to filter devices (optional)"
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            max_results = arguments.get("max_results", 100)
            query = arguments.get("query")
            order_by = arguments.get("order_by", "lastSync")
            org_unit_path = arguments.get("org_unit_path")

            logger.info(f"Listing Chrome devices for customer: {customer_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Build request parameters
            request_params = {
                "customerId": customer_id,
                "maxResults": max_results,
                "orderBy": order_by
            }

            if query:
                request_params["query"] = query
            if org_unit_path:
                request_params["orgUnitPath"] = org_unit_path

            # Make API call
            result = service.chromeosdevices().list(**request_params).execute()
            devices = result.get("chromeosdevices", [])

            if not devices:
                return [TextContent(
                    type="text",
                    text="No Chrome OS devices found in the domain"
                )]

            # Format response
            response = f"Found {len(devices)} Chrome OS device(s):\n\n"

            for i, device in enumerate(devices, 1):
                device_id = device.get("deviceId", "Unknown")
                serial_number = device.get("serialNumber", "Unknown")
                status = device.get("status", "Unknown")
                last_sync = device.get("lastSync", "Unknown")
                model = device.get("model", "Unknown")
                os_version = device.get("osVersion", "Unknown")
                user = device.get("annotatedUser", "Unknown")
                location = device.get("annotatedLocation", "Unknown")

                response += f"{i}. Chrome Device\n"
                response += f"   🆔 Device ID: {device_id}\n"
                response += f"   📱 Serial: {serial_number}\n"
                response += f"   📱 Model: {model}\n"
                response += f"   🔧 OS Version: {os_version}\n"
                response += f"   👤 User: {user}\n"
                response += f"   📍 Location: {location}\n"
                response += f"   🟢 Status: {status}\n"
                response += f"   🔄 Last Sync: {last_sync}\n\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error listing Chrome devices: {e}")
            raise AdminMCPError(f"Failed to list Chrome devices: {str(e)}")


class GetChromeDeviceHandler(AdminToolHandler):
    """Handler for getting details about a specific Chrome OS device."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_chrome_device")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get detailed information about a specific Chrome OS device",
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
                    "device_id": {
                        "type": "string",
                        "description": "Device ID of the Chrome OS device"
                    }
                },
                "required": [USER_ID_ARG, "device_id"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            device_id = arguments["device_id"]

            logger.info(f"Getting Chrome device details for: {device_id}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "directory_v1")

            # Get device details
            device = service.chromeosdevices().get(
                customerId=customer_id,
                deviceId=device_id
            ).execute()

            # Format response
            response = f"Chrome OS Device Details for '{device_id}':\n\n"
            response += f"🆔 Device ID: {device.get('deviceId', 'Unknown')}\n"
            response += f"📱 Serial Number: {device.get('serialNumber', 'Unknown')}\n"
            response += f"📱 Model: {device.get('model', 'Unknown')}\n"
            response += f"🔧 OS Version: {device.get('osVersion', 'Unknown')}\n"
            response += f"🔧 Platform Version: {device.get('platformVersion', 'Unknown')}\n"
            response += f"🔧 Firmware Version: {device.get('firmwareVersion', 'Unknown')}\n"
            response += f"👤 Annotated User: {device.get('annotatedUser', 'Unknown')}\n"
            response += f"📍 Annotated Location: {device.get('annotatedLocation', 'Unknown')}\n"
            response += f"🟢 Status: {device.get('status', 'Unknown')}\n"
            response += f"🔄 Last Sync: {device.get('lastSync', 'Unknown')}\n"
            response += f"📂 Org Unit Path: {device.get('orgUnitPath', 'Unknown')}\n"
            response += f"📝 Notes: {device.get('notes', 'No notes')}\n"
            response += f"🛡️ Support End Date: {device.get('supportEndDate', 'Unknown')}\n"

            # Additional hardware info
            if device.get("macAddress"):
                response += f"🌐 MAC Address: {device.get('macAddress')}\n"
            if device.get("ethernetMacAddress"):
                response += f"🔌 Ethernet MAC: {device.get('ethernetMacAddress')}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting Chrome device details: {e}")
            raise AdminMCPError(f"Failed to get Chrome device details: {str(e)}")


# Export all device handlers
DEVICE_HANDLERS: List[AdminToolHandler] = [
    ListMobileDevicesHandler(),
    GetMobileDeviceHandler(),
    ManageMobileDeviceHandler(),
    ListChromeDevicesHandler(),
    GetChromeDeviceHandler()
]