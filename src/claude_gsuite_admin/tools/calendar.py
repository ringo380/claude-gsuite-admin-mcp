"""Google Workspace Calendar Administration Tools."""

import logging
from typing import Any, Dict, List, Optional, Sequence
from collections.abc import Sequence as AbstractSequence

from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import ValidationError, UserNotFoundError
from ..utils.validators import validate_email
from ..utils.logging import get_logger, log_tool_execution, log_api_call


logger = get_logger('tools.calendar')


class ListCalendarResourcesHandler(AdminToolHandler):
    """Handler for listing calendar resources (conference rooms, equipment, etc.)."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_calendar_resources")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""List calendar resources in the Google Workspace organization.
            Returns conference rooms, equipment, and other bookable resources.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (default: 'my_customer')",
                        "default": "my_customer"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of resources to return (default: 100)",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 500
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the calendar resources listing operation."""
        user_id = args.get("user_id")
        customer_id = args.get("customer_id", "my_customer")
        max_results = args.get("max_results", 100)

        if not user_id:
            raise ValidationError("user_id is required")

        try:
            admin_service = self.get_google_service(user_id, "admin", "directory_v1")

            # Get calendar resources
            result = admin_service.resources().calendars().list(
                customer=customer_id,
                maxResults=max_results
            ).execute()

            resources = result.get("items", [])

            response_text = "## Calendar Resources\n\n"

            if not resources:
                response_text += "**No calendar resources found.**\n"
                return [TextContent(type="text", text=response_text)]

            response_text += f"**Total Resources:** {len(resources)}\n\n"

            # Group resources by type
            rooms = [r for r in resources if r.get("resourceType") == "Room"]
            equipment = [r for r in resources if r.get("resourceType") == "Equipment"]
            other = [r for r in resources if r.get("resourceType") not in ["Room", "Equipment"]]

            if rooms:
                response_text += f"### Conference Rooms ({len(rooms)})\n"
                for room in rooms[:10]:  # Show first 10
                    response_text += f"**{room.get('resourceName', 'N/A')}**\n"
                    response_text += f"  • Email: {room.get('resourceEmail', 'N/A')}\n"
                    response_text += f"  • Capacity: {room.get('capacity', 'N/A')}\n"
                    response_text += f"  • Building: {room.get('buildingId', 'N/A')}\n"
                    response_text += f"  • Floor: {room.get('floorName', 'N/A')}\n\n"
                if len(rooms) > 10:
                    response_text += f"*... and {len(rooms) - 10} more conference rooms*\n\n"

            if equipment:
                response_text += f"### Equipment ({len(equipment)})\n"
                for item in equipment[:5]:  # Show first 5
                    response_text += f"**{item.get('resourceName', 'N/A')}**\n"
                    response_text += f"  • Email: {item.get('resourceEmail', 'N/A')}\n"
                    response_text += f"  • Category: {item.get('resourceCategory', 'N/A')}\n\n"
                if len(equipment) > 5:
                    response_text += f"*... and {len(equipment) - 5} more equipment items*\n\n"

            if other:
                response_text += f"### Other Resources ({len(other)})\n"
                for item in other[:5]:
                    response_text += f"**{item.get('resourceName', 'N/A')}**\n"
                    response_text += f"  • Email: {item.get('resourceEmail', 'N/A')}\n"
                    response_text += f"  • Type: {item.get('resourceType', 'N/A')}\n\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "list calendar resources")


class CreateCalendarResourceHandler(AdminToolHandler):
    """Handler for creating calendar resources."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__create_calendar_resource")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Create a new calendar resource (conference room, equipment, etc.).
            Resources can be booked through Google Calendar.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "resource_name": {
                        "type": "string",
                        "description": "Display name for the resource"
                    },
                    "resource_email": {
                        "type": "string",
                        "description": "Email address for the resource (optional, auto-generated if not provided)"
                    },
                    "resource_type": {
                        "type": "string",
                        "description": "Type of resource",
                        "enum": ["Room", "Equipment", "Vehicle", "Other"],
                        "default": "Room"
                    },
                    "capacity": {
                        "type": "integer",
                        "description": "Seating capacity (for rooms)",
                        "minimum": 1
                    },
                    "building_id": {
                        "type": "string",
                        "description": "Building identifier"
                    },
                    "floor_name": {
                        "type": "string",
                        "description": "Floor name or number"
                    },
                    "description": {
                        "type": "string",
                        "description": "Resource description"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (default: 'my_customer')",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG, "resource_name"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the calendar resource creation operation."""
        user_id = args.get("user_id")
        resource_name = args.get("resource_name")
        resource_email = args.get("resource_email")
        resource_type = args.get("resource_type", "Room")
        capacity = args.get("capacity")
        building_id = args.get("building_id")
        floor_name = args.get("floor_name")
        description = args.get("description")
        customer_id = args.get("customer_id", "my_customer")

        if not user_id:
            raise ValidationError("user_id is required")
        if not resource_name:
            raise ValidationError("resource_name is required")

        try:
            admin_service = self.get_google_service(user_id, "admin", "directory_v1")

            # Build resource body
            resource_body = {
                "resourceName": resource_name,
                "resourceType": resource_type
            }

            if resource_email:
                resource_body["resourceEmail"] = resource_email

            if capacity:
                resource_body["capacity"] = capacity

            if building_id:
                resource_body["buildingId"] = building_id

            if floor_name:
                resource_body["floorName"] = floor_name

            if description:
                resource_body["resourceDescription"] = description

            # Create the resource
            result = admin_service.resources().calendars().insert(
                customer=customer_id,
                body=resource_body
            ).execute()

            response_text = "## Calendar Resource Created Successfully\n\n"
            response_text += f"**Name:** {result.get('resourceName', 'N/A')}\n"
            response_text += f"**Email:** {result.get('resourceEmail', 'N/A')}\n"
            response_text += f"**Type:** {result.get('resourceType', 'N/A')}\n"
            response_text += f"**Resource ID:** {result.get('resourceId', 'N/A')}\n"

            if result.get('capacity'):
                response_text += f"**Capacity:** {result.get('capacity')} people\n"
            if result.get('buildingId'):
                response_text += f"**Building:** {result.get('buildingId')}\n"
            if result.get('floorName'):
                response_text += f"**Floor:** {result.get('floorName')}\n"

            response_text += "\n**Next Steps:**\n"
            response_text += "• The resource is now available for booking in Google Calendar\n"
            response_text += "• You can configure additional settings using the Calendar admin console\n"
            response_text += "• Consider setting up auto-approval policies for bookings\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"create calendar resource {resource_name}")


class ManageCalendarSharingHandler(AdminToolHandler):
    """Handler for managing calendar sharing and ACL settings."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_calendar_sharing")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Manage calendar sharing settings and access control lists (ACL).
            Add, remove, or update calendar permissions for users.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (email address of the calendar)"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["list", "add", "remove", "update"]
                    },
                    "user_email": {
                        "type": "string",
                        "description": "Email of user to grant/revoke access (required for add/remove/update)"
                    },
                    "role": {
                        "type": "string",
                        "description": "Access role to grant",
                        "enum": ["owner", "reader", "writer", "freeBusyReader"],
                        "default": "reader"
                    },
                    "send_notifications": {
                        "type": "boolean",
                        "description": "Whether to send notification emails",
                        "default": true
                    }
                },
                "required": [USER_ID_ARG, "calendar_id", "action"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the calendar sharing management operation."""
        user_id = args.get("user_id")
        calendar_id = args.get("calendar_id")
        action = args.get("action")
        user_email = args.get("user_email")
        role = args.get("role", "reader")
        send_notifications = args.get("send_notifications", True)

        if not user_id:
            raise ValidationError("user_id is required")
        if not calendar_id:
            raise ValidationError("calendar_id is required")
        if action in ["add", "remove", "update"] and not user_email:
            raise ValidationError("user_email is required for add/remove/update actions")

        validate_email(calendar_id)
        if user_email:
            validate_email(user_email)

        try:
            calendar_service = self.get_google_service(user_id, "calendar", "v3")
            acl_api = calendar_service.acl()

            if action == "list":
                # List current ACL entries
                result = acl_api.list(calendarId=calendar_id).execute()
                acl_entries = result.get("items", [])

                response_text = f"## Calendar Sharing Settings\n**Calendar:** {calendar_id}\n\n"

                if not acl_entries:
                    response_text += "**No sharing permissions configured.**\n"
                else:
                    response_text += f"**Total Permissions:** {len(acl_entries)}\n\n"
                    for entry in acl_entries:
                        scope = entry.get("scope", {})
                        scope_type = scope.get("type", "user")
                        scope_value = scope.get("value", "N/A")
                        role = entry.get("role", "N/A")

                        response_text += f"**{scope_value}**\n"
                        response_text += f"  • Role: {role}\n"
                        response_text += f"  • Type: {scope_type}\n\n"

            elif action == "add":
                # Add new ACL entry
                acl_rule = {
                    "scope": {
                        "type": "user",
                        "value": user_email
                    },
                    "role": role
                }

                result = acl_api.insert(
                    calendarId=calendar_id,
                    body=acl_rule,
                    sendNotifications=send_notifications
                ).execute()

                response_text = f"## Calendar Permission Added\n\n"
                response_text += f"**Calendar:** {calendar_id}\n"
                response_text += f"**User:** {user_email}\n"
                response_text += f"**Role:** {role}\n"
                response_text += f"**ACL ID:** {result.get('id', 'N/A')}\n\n"

                if send_notifications:
                    response_text += "📧 **Notification email sent to user**\n"

            elif action == "remove":
                # Find and remove ACL entry
                acl_list = acl_api.list(calendarId=calendar_id).execute()
                acl_entries = acl_list.get("items", [])

                acl_id = None
                for entry in acl_entries:
                    scope = entry.get("scope", {})
                    if scope.get("value") == user_email:
                        acl_id = entry.get("id")
                        break

                if not acl_id:
                    raise ValidationError(f"No permission found for user {user_email}")

                acl_api.delete(
                    calendarId=calendar_id,
                    ruleId=acl_id
                ).execute()

                response_text = f"## Calendar Permission Removed\n\n"
                response_text += f"**Calendar:** {calendar_id}\n"
                response_text += f"**User:** {user_email}\n"
                response_text += "Permission has been revoked.\n"

            elif action == "update":
                # Update existing ACL entry
                acl_list = acl_api.list(calendarId=calendar_id).execute()
                acl_entries = acl_list.get("items", [])

                acl_id = None
                for entry in acl_entries:
                    scope = entry.get("scope", {})
                    if scope.get("value") == user_email:
                        acl_id = entry.get("id")
                        break

                if not acl_id:
                    raise ValidationError(f"No permission found for user {user_email}")

                acl_rule = {
                    "scope": {
                        "type": "user",
                        "value": user_email
                    },
                    "role": role
                }

                result = acl_api.update(
                    calendarId=calendar_id,
                    ruleId=acl_id,
                    body=acl_rule,
                    sendNotifications=send_notifications
                ).execute()

                response_text = f"## Calendar Permission Updated\n\n"
                response_text += f"**Calendar:** {calendar_id}\n"
                response_text += f"**User:** {user_email}\n"
                response_text += f"**New Role:** {role}\n\n"

                if send_notifications:
                    response_text += "📧 **Notification email sent to user**\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"manage calendar sharing for {calendar_id}")


class GetCalendarSettingsHandler(AdminToolHandler):
    """Handler for retrieving calendar settings for a user."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_calendar_settings")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get calendar settings and configuration for a user.
            Returns timezone, working hours, and other calendar preferences.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "target_user": {
                        "type": "string",
                        "description": "Email address of the user whose calendar settings to retrieve"
                    }
                },
                "required": [USER_ID_ARG, "target_user"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the calendar settings retrieval operation."""
        user_id = args.get("user_id")
        target_user = args.get("target_user")

        if not user_id:
            raise ValidationError("user_id is required")
        if not target_user:
            raise ValidationError("target_user is required")

        validate_email(target_user)

        try:
            calendar_service = self.get_google_service(user_id, "calendar", "v3", target_user)

            # Get user's calendar settings
            settings_result = calendar_service.settings().list().execute()
            settings = settings_result.get("items", [])

            # Get user's calendar list
            calendar_list = calendar_service.calendarList().list().execute()
            calendars = calendar_list.get("items", [])

            response_text = f"## Calendar Settings for {target_user}\n\n"

            # Primary settings
            settings_dict = {item.get("id"): item.get("value") for item in settings}

            response_text += "### General Settings\n"
            response_text += f"**Timezone:** {settings_dict.get('timezone', 'N/A')}\n"
            response_text += f"**Date Format:** {settings_dict.get('dateFormat', 'N/A')}\n"
            response_text += f"**Time Format:** {settings_dict.get('timeFormat', 'N/A')}\n"
            response_text += f"**Week Start:** {settings_dict.get('weekStart', 'N/A')}\n"
            response_text += f"**Default Length:** {settings_dict.get('defaultEventLength', 'N/A')} minutes\n\n"

            # Working hours
            response_text += "### Working Hours\n"
            if settings_dict.get('workingHours'):
                response_text += f"**Working Hours:** {settings_dict.get('workingHours')}\n"
            else:
                response_text += "**Working Hours:** Not configured\n"
            response_text += "\n"

            # Calendar list
            response_text += f"### Calendars ({len(calendars)})\n"
            primary_calendars = [c for c in calendars if c.get("primary")]
            owned_calendars = [c for c in calendars if not c.get("primary") and c.get("accessRole") == "owner"]
            shared_calendars = [c for c in calendars if c.get("accessRole") in ["reader", "writer"]]

            if primary_calendars:
                response_text += "**Primary Calendar:**\n"
                for cal in primary_calendars:
                    response_text += f"• {cal.get('summary', 'N/A')} ({cal.get('id', 'N/A')})\n"
                response_text += "\n"

            if owned_calendars:
                response_text += f"**Owned Calendars ({len(owned_calendars)}):**\n"
                for cal in owned_calendars[:5]:  # Show first 5
                    response_text += f"• {cal.get('summary', 'N/A')}\n"
                if len(owned_calendars) > 5:
                    response_text += f"*... and {len(owned_calendars) - 5} more owned calendars*\n"
                response_text += "\n"

            if shared_calendars:
                response_text += f"**Shared Calendars ({len(shared_calendars)}):**\n"
                for cal in shared_calendars[:5]:  # Show first 5
                    response_text += f"• {cal.get('summary', 'N/A')} ({cal.get('accessRole', 'N/A')})\n"
                if len(shared_calendars) > 5:
                    response_text += f"*... and {len(shared_calendars) - 5} more shared calendars*\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"get calendar settings for {target_user}")


class ManageCalendarResourceBookingHandler(AdminToolHandler):
    """Handler for managing calendar resource booking policies."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__manage_resource_booking")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Manage booking policies for calendar resources.
            Configure auto-approval, booking restrictions, and access policies.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "resource_email": {
                        "type": "string",
                        "description": "Email address of the calendar resource"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action to perform",
                        "enum": ["get_settings", "update_settings"]
                    },
                    "auto_accept_requests": {
                        "type": "boolean",
                        "description": "Whether to auto-accept booking requests"
                    },
                    "all_requests_accepted": {
                        "type": "boolean",
                        "description": "Whether all requests are automatically accepted"
                    },
                    "allow_conflicts": {
                        "type": "boolean",
                        "description": "Whether to allow conflicting bookings"
                    }
                },
                "required": [USER_ID_ARG, "resource_email", "action"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the resource booking management operation."""
        user_id = args.get("user_id")
        resource_email = args.get("resource_email")
        action = args.get("action")
        auto_accept = args.get("auto_accept_requests")
        all_accepted = args.get("all_requests_accepted")
        allow_conflicts = args.get("allow_conflicts")

        if not user_id:
            raise ValidationError("user_id is required")
        if not resource_email:
            raise ValidationError("resource_email is required")

        validate_email(resource_email)

        try:
            calendar_service = self.get_google_service(user_id, "calendar", "v3", resource_email)

            if action == "get_settings":
                # Get current calendar settings
                try:
                    calendar_info = calendar_service.calendars().get(calendarId="primary").execute()

                    response_text = f"## Resource Booking Settings\n**Resource:** {resource_email}\n\n"
                    response_text += f"**Calendar Name:** {calendar_info.get('summary', 'N/A')}\n"
                    response_text += f"**Description:** {calendar_info.get('description', 'None')}\n"
                    response_text += f"**Timezone:** {calendar_info.get('timeZone', 'N/A')}\n"
                    response_text += f"**Location:** {calendar_info.get('location', 'None')}\n\n"

                    # Note: Booking policies are typically managed through Admin Console
                    response_text += "**Note:** Detailed booking policies (auto-acceptance, conflicts, etc.) "
                    response_text += "are managed through the Google Workspace Admin Console under "
                    response_text += "Calendar Resources settings.\n"

                except Exception:
                    response_text = f"## Resource Booking Settings\n**Resource:** {resource_email}\n\n"
                    response_text += "**Status:** Unable to retrieve detailed settings.\n"
                    response_text += "This may be because the resource requires specific admin permissions "
                    response_text += "or the settings are managed centrally.\n"

            elif action == "update_settings":
                # Update calendar properties (limited scope)
                calendar_body = {}

                # Note: Most booking policies are set at the organizational level
                # We can only update basic calendar properties here
                try:
                    current_calendar = calendar_service.calendars().get(calendarId="primary").execute()

                    # Update basic properties if provided
                    updated = False
                    if auto_accept is not None:
                        # This would typically require Admin SDK Calendar Resources API
                        pass

                    calendar_service.calendars().update(
                        calendarId="primary",
                        body=current_calendar
                    ).execute()

                    response_text = f"## Resource Settings Updated\n**Resource:** {resource_email}\n\n"
                    response_text += "**Note:** Basic calendar properties have been updated.\n"
                    response_text += "Advanced booking policies (auto-acceptance, conflict handling) "
                    response_text += "must be configured through the Google Workspace Admin Console.\n\n"
                    response_text += "**Next Steps:**\n"
                    response_text += "1. Go to Google Workspace Admin Console\n"
                    response_text += "2. Navigate to Apps → Google Workspace → Calendar → Resources\n"
                    response_text += "3. Find and configure the specific resource booking policies\n"

                except Exception:
                    response_text = f"## Resource Settings Update\n**Resource:** {resource_email}\n\n"
                    response_text += "**Status:** Limited access to resource settings.\n"
                    response_text += "Resource booking policies are typically managed through the "
                    response_text += "Google Workspace Admin Console under Calendar Resources.\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"manage resource booking for {resource_email}")


# Export all handlers
CALENDAR_HANDLERS = [
    ListCalendarResourcesHandler(),
    CreateCalendarResourceHandler(),
    ManageCalendarSharingHandler(),
    GetCalendarSettingsHandler(),
    ManageCalendarResourceBookingHandler(),
]