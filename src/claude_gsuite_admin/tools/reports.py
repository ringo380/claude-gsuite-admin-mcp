"""Google Workspace Reports and Auditing Tools."""

import logging
from typing import Any, Dict, List, Sequence
from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import AdminMCPError, ValidationError
from ..auth.oauth_manager import OAuthManager

logger = logging.getLogger(__name__)


class GetUsageReportsHandler(AdminToolHandler):
    """Handler for getting Google Workspace usage reports."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_usage_reports")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get usage reports for Google Workspace applications and services",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "user_key": {
                        "type": "string",
                        "description": "User email or 'all' for domain-wide reports",
                        "default": "all"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date for the report (YYYY-MM-DD format, or 'today' for most recent)"
                    },
                    "parameters": {
                        "type": "string",
                        "description": "Comma-separated list of parameters (e.g., 'gmail:num_emails_sent,gmail:num_emails_received')",
                        "default": "accounts:num_users,accounts:used_quota_in_mb"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 1000,
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": [USER_ID_ARG, "date"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            user_key = arguments.get("user_key", "all")
            date = arguments["date"]
            parameters = arguments.get("parameters", "accounts:num_users,accounts:used_quota_in_mb")
            max_results = arguments.get("max_results", 1000)

            # Handle 'today' date
            if date == "today":
                from datetime import datetime, timedelta
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            logger.info(f"Getting usage reports for {parameters} on {date}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "reports_v1")

            # Get usage reports
            result = service.userUsageReport().get(
                userKey=user_key,
                date=date,
                parameters=parameters,
                maxResults=max_results
            ).execute()

            usage_reports = result.get("usageReports", [])

            if not usage_reports:
                return [TextContent(
                    type="text",
                    text=f"No usage reports found for {parameters} on {date}"
                )]

            # Format response
            response = f"Usage Report for {parameters} on {date}:\n\n"

            if user_key == "all":
                response += f"Found {len(usage_reports)} user reports:\n\n"
            else:
                response += f"Usage report for {user_key}:\n\n"

            for i, report in enumerate(usage_reports, 1):
                entity = report.get("entity", {})
                user_email = entity.get("userEmail", "Unknown")
                profile_id = entity.get("profileId", "Unknown")

                if user_key == "all":
                    response += f"{i}. User: {user_email}\n"
                    response += f"   Profile ID: {profile_id}\n"

                parameters = report.get("parameters", [])
                if parameters:
                    response += f"   📊 Usage Data:\n"
                    for param in parameters[:10]:  # Limit to first 10 parameters
                        name = param.get("name", "Unknown")
                        if "value" in param:
                            if isinstance(param["value"], dict):
                                # Handle different value types
                                if "intValue" in param["value"]:
                                    value = param["value"]["intValue"]
                                elif "stringValue" in param["value"]:
                                    value = param["value"]["stringValue"]
                                elif "boolValue" in param["value"]:
                                    value = param["value"]["boolValue"]
                                else:
                                    value = str(param["value"])
                            else:
                                value = param["value"]
                            response += f"     - {name}: {value}\n"

                if user_key == "all":
                    response += "\n"

                # Limit output for readability
                if i >= 10 and user_key == "all":
                    remaining = len(usage_reports) - 10
                    if remaining > 0:
                        response += f"... and {remaining} more users\n"
                    break

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting usage reports: {e}")
            raise AdminMCPError(f"Failed to get usage reports: {str(e)}")


class GetAuditActivitiesHandler(AdminToolHandler):
    """Handler for getting Google Workspace audit activity reports."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_audit_activities")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get audit activity logs for Google Workspace applications",
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
                    "application_name": {
                        "type": "string",
                        "description": "Application to get audit logs for",
                        "enum": ["admin", "calendar", "chat", "drive", "gcp", "gplus", "groups", "groups_enterprise", "jamboard", "login", "meet", "mobile", "rules", "saml", "token", "user_accounts"],
                        "default": "admin"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time for audit logs (ISO format or 'today', '1d', '7d', '30d')"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time for audit logs (ISO format, optional)"
                    },
                    "actor_email": {
                        "type": "string",
                        "description": "Filter by specific user email (optional)"
                    },
                    "event_name": {
                        "type": "string",
                        "description": "Filter by specific event name (optional)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of activities to return",
                        "default": 1000,
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": [USER_ID_ARG, "start_time"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            application_name = arguments.get("application_name", "admin")
            start_time = arguments["start_time"]
            end_time = arguments.get("end_time")
            actor_email = arguments.get("actor_email")
            event_name = arguments.get("event_name")
            max_results = arguments.get("max_results", 1000)

            # Handle relative time formats
            from datetime import datetime, timedelta
            if start_time in ["today", "1d"]:
                start_time = (datetime.now() - timedelta(days=1)).isoformat() + "Z"
            elif start_time == "7d":
                start_time = (datetime.now() - timedelta(days=7)).isoformat() + "Z"
            elif start_time == "30d":
                start_time = (datetime.now() - timedelta(days=30)).isoformat() + "Z"

            logger.info(f"Getting audit activities for {application_name} since {start_time}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "reports_v1")

            # Build request parameters
            request_params = {
                "customerId": customer_id,
                "applicationName": application_name,
                "userKey": "all",  # Required parameter
                "startTime": start_time,
                "maxResults": max_results
            }

            if end_time:
                request_params["endTime"] = end_time
            if actor_email:
                request_params["actorEmail"] = actor_email  # Fixed parameter name
            if event_name:
                request_params["eventName"] = event_name

            # Get audit activities
            result = service.activities().list(**request_params).execute()
            activities = result.get("items", [])

            if not activities:
                return [TextContent(
                    type="text",
                    text=f"No audit activities found for {application_name} since {start_time}"
                )]

            # Format response
            response = f"Audit Activities for {application_name} since {start_time}:\n\n"
            response += f"Found {len(activities)} activities:\n\n"

            for i, activity in enumerate(activities, 1):
                actor = activity.get("actor", {})
                actor_email = actor.get("email", "Unknown")
                actor_profile_id = actor.get("profileId", "Unknown")

                time = activity.get("id", {}).get("time", "Unknown")
                unique_qualifier = activity.get("id", {}).get("uniqueQualifier", "Unknown")

                events = activity.get("events", [])

                response += f"{i}. Activity at {time}\n"
                response += f"   👤 Actor: {actor_email} (ID: {actor_profile_id})\n"
                response += f"   🆔 Qualifier: {unique_qualifier}\n"

                if events:
                    response += f"   📋 Events:\n"
                    for event in events[:3]:  # Limit to first 3 events
                        event_type = event.get("type", "Unknown")
                        event_name = event.get("name", "Unknown")
                        response += f"     - {event_type}: {event_name}\n"

                        # Show parameters if available
                        parameters = event.get("parameters", [])
                        if parameters:
                            for param in parameters[:2]:  # Show first 2 parameters
                                param_name = param.get("name", "Unknown")
                                param_value = param.get("value", "Unknown")
                                response += f"       * {param_name}: {param_value}\n"

                response += "\n"

                # Limit output for readability
                if i >= 20:
                    remaining = len(activities) - 20
                    if remaining > 0:
                        response += f"... and {remaining} more activities\n"
                    break

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting audit activities: {e}")
            raise AdminMCPError(f"Failed to get audit activities: {str(e)}")


class GetCustomerUsageReportsHandler(AdminToolHandler):
    """Handler for getting customer-level usage reports."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_customer_usage_reports")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get customer-level usage reports for Google Workspace domain",
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
                    "date": {
                        "type": "string",
                        "description": "Date for the report (YYYY-MM-DD format, or 'today' for most recent)"
                    },
                    "parameters": {
                        "type": "string",
                        "description": "Comma-separated list of parameters to include",
                        "default": "accounts:total_quota_in_mb,accounts:used_quota_in_mb,accounts:num_users"
                    }
                },
                "required": [USER_ID_ARG, "date"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            customer_id = arguments.get("customer_id", "my_customer")
            date = arguments["date"]
            parameters = arguments.get("parameters", "accounts:total_quota_in_mb,accounts:used_quota_in_mb,accounts:num_users")

            # Handle 'today' date
            if date == "today":
                from datetime import datetime, timedelta
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            logger.info(f"Getting customer usage reports for {date}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "reports_v1")

            # Get customer usage reports
            result = service.customerUsageReports().get(
                customerId=customer_id,
                date=date,
                parameters=parameters
            ).execute()

            usage_reports = result.get("usageReports", [])

            if not usage_reports:
                return [TextContent(
                    type="text",
                    text=f"No customer usage reports found for {date}"
                )]

            # Format response
            response = f"Customer Usage Report for {date}:\n\n"

            for report in usage_reports:
                entity = report.get("entity", {})
                entity_type = entity.get("type", "Unknown")
                customer_id_reported = entity.get("customerId", "Unknown")

                response += f"📊 Customer: {customer_id_reported} (Type: {entity_type})\n"

                parameters_data = report.get("parameters", [])
                if parameters_data:
                    response += f"📈 Usage Metrics:\n"
                    for param in parameters_data:
                        name = param.get("name", "Unknown")
                        if "value" in param:
                            if isinstance(param["value"], dict):
                                # Handle different value types
                                if "intValue" in param["value"]:
                                    value = param["value"]["intValue"]
                                elif "stringValue" in param["value"]:
                                    value = param["value"]["stringValue"]
                                elif "boolValue" in param["value"]:
                                    value = param["value"]["boolValue"]
                                else:
                                    value = str(param["value"])
                            else:
                                value = param["value"]

                            # Format storage values
                            if "quota" in name and isinstance(value, (int, str)) and str(value).isdigit():
                                value_int = int(value)
                                if value_int > 1024**3:  # GB
                                    formatted_value = f"{value_int / (1024**3):.2f} GB"
                                elif value_int > 1024**2:  # MB
                                    formatted_value = f"{value_int / (1024**2):.2f} MB"
                                else:
                                    formatted_value = f"{value} bytes"
                                response += f"   • {name}: {formatted_value}\n"
                            else:
                                response += f"   • {name}: {value}\n"

                response += "\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting customer usage reports: {e}")
            raise AdminMCPError(f"Failed to get customer usage reports: {str(e)}")


class GetDomainInsightsHandler(AdminToolHandler):
    """Handler for getting domain insights and security reports."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_domain_insights")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="Get domain insights including security, user activity, and application usage",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "User ID for authentication (email address)"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date for the insights (YYYY-MM-DD format, or 'today')"
                    },
                    "insight_type": {
                        "type": "string",
                        "description": "Type of insights to retrieve",
                        "enum": ["security", "usage", "activity", "apps"],
                        "default": "security"
                    }
                },
                "required": [USER_ID_ARG, "date"]
            }
        )

    def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        try:
            user_id = arguments[USER_ID_ARG]
            date = arguments["date"]
            insight_type = arguments.get("insight_type", "security")

            # Handle 'today' date
            if date == "today":
                from datetime import datetime, timedelta
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            logger.info(f"Getting domain insights for {insight_type} on {date}")

            # Get authenticated service
            oauth_manager = OAuthManager()
            service = oauth_manager.get_service(user_id, "admin", "reports_v1")

            response = f"Domain Insights for {date} - {insight_type.title()} Report:\n\n"

            if insight_type == "security":
                # Get login activities for security insights
                try:
                    from datetime import datetime
                    start_time = f"{date}T00:00:00Z"

                    result = service.activities().list(
                        customerId="my_customer",
                        applicationName="login",
                        userKey="all",  # Required parameter
                        startTime=start_time,
                        maxResults=100
                    ).execute()

                    activities = result.get("items", [])

                    if activities:
                        response += f"🔐 Security Activity Summary:\n"
                        response += f"   📊 Total login events: {len(activities)}\n\n"

                        # Analyze login patterns
                        login_types = {}
                        failed_logins = 0
                        suspicious_activities = 0

                        for activity in activities[:20]:  # Analyze first 20
                            events = activity.get("events", [])
                            for event in events:
                                event_name = event.get("name", "unknown")
                                login_types[event_name] = login_types.get(event_name, 0) + 1

                                if "fail" in event_name.lower():
                                    failed_logins += 1
                                if "suspicious" in event_name.lower():
                                    suspicious_activities += 1

                        response += f"📈 Login Event Breakdown:\n"
                        for event_type, count in list(login_types.items())[:5]:
                            response += f"   • {event_type}: {count}\n"

                        if failed_logins > 0:
                            response += f"\n⚠️  Security Alerts:\n"
                            response += f"   • Failed logins: {failed_logins}\n"

                        if suspicious_activities > 0:
                            response += f"   • Suspicious activities: {suspicious_activities}\n"

                    else:
                        response += "No security activities found for this date.\n"

                except Exception as e:
                    response += f"Could not retrieve detailed security data: {str(e)}\n"

            elif insight_type == "usage":
                # Get usage data
                try:
                    result = service.customerUsageReports().get(
                        customerId="my_customer",
                        date=date,
                        parameters="accounts:num_users,accounts:total_quota_in_mb,accounts:used_quota_in_mb"
                    ).execute()

                    usage_reports = result.get("usageReports", [])
                    if usage_reports:
                        response += f"📊 Domain Usage Summary:\n"
                        for report in usage_reports:
                            params = report.get("parameters", [])
                            for param in params:
                                name = param.get("name", "Unknown")
                                value = param.get("value", {})
                                if "intValue" in value:
                                    val = value["intValue"]
                                    if "quota" in name:
                                        val_gb = int(val) / (1024**3)
                                        response += f"   • {name}: {val_gb:.2f} GB\n"
                                    else:
                                        response += f"   • {name}: {val}\n"
                    else:
                        response += "No usage data available for this date.\n"
                except Exception as e:
                    response += f"Could not retrieve usage data: {str(e)}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"Error getting domain insights: {e}")
            raise AdminMCPError(f"Failed to get domain insights: {str(e)}")


# Export all report handlers
REPORT_HANDLERS: List[AdminToolHandler] = [
    GetUsageReportsHandler(),
    GetAuditActivitiesHandler(),
    GetCustomerUsageReportsHandler(),
    GetDomainInsightsHandler()
]