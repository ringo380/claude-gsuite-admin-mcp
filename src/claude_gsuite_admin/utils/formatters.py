"""Output formatting utilities for Google Workspace Admin MCP."""

from typing import Any, Dict, List, Optional
from datetime import datetime


def format_user_info(user: Dict[str, Any], detailed: bool = False) -> str:
    """Format user information for display."""
    if not user:
        return "No user data available"

    name = user.get('name', {})
    full_name = name.get('fullName', 'Unknown User')
    email = user.get('primaryEmail', 'No email')

    if not detailed:
        # Simple format for lists
        suspended = user.get('suspended', False)
        status = "🔴 SUSPENDED" if suspended else "🟢 ACTIVE"
        return f"{full_name} ({email}) - {status}"

    # Detailed format
    lines = []
    lines.append(f"👤 {full_name}")
    lines.append(f"📧 Email: {email}")

    # Status
    suspended = user.get('suspended', False)
    if suspended:
        lines.append("🔴 Status: SUSPENDED")
        if user.get('suspensionReason'):
            lines.append(f"   Reason: {user['suspensionReason']}")
    else:
        lines.append("🟢 Status: ACTIVE")

    # Organization
    org_unit = user.get('orgUnitPath', '/')
    lines.append(f"🏢 Org Unit: {org_unit}")

    # Admin status
    if user.get('isAdmin'):
        lines.append("👑 Super Admin")
    elif user.get('isDelegatedAdmin'):
        lines.append("⭐ Delegated Admin")

    # Timestamps
    if user.get('creationTime'):
        creation_time = format_timestamp(user['creationTime'])
        lines.append(f"📅 Created: {creation_time}")

    if user.get('lastLoginTime'):
        last_login = format_timestamp(user['lastLoginTime'])
        lines.append(f"🕐 Last Login: {last_login}")
    else:
        lines.append("🕐 Last Login: Never")

    # Aliases
    aliases = user.get('aliases', [])
    if aliases:
        lines.append(f"📧 Aliases ({len(aliases)}):")
        for alias in aliases[:5]:  # Show first 5 aliases
            lines.append(f"   • {alias}")
        if len(aliases) > 5:
            lines.append(f"   ... and {len(aliases) - 5} more")

    return "\n".join(lines)


def format_group_info(group: Dict[str, Any], detailed: bool = False) -> str:
    """Format group information for display."""
    if not group:
        return "No group data available"

    name = group.get('name', 'Unknown Group')
    email = group.get('email', 'No email')
    description = group.get('description', '')

    if not detailed:
        # Simple format for lists
        member_count = group.get('directMembersCount', 0)
        return f"{name} ({email}) - {member_count} members"

    # Detailed format
    lines = []
    lines.append(f"👥 {name}")
    lines.append(f"📧 Email: {email}")

    if description:
        lines.append(f"📄 Description: {description}")

    # Member counts
    direct_members = group.get('directMembersCount', 0)
    total_members = group.get('directMembersCount', 0)  # API doesn't provide nested count easily
    lines.append(f"👨‍👩‍👧‍👦 Members: {direct_members}")

    # Group settings
    if 'allowExternalMembers' in group:
        external = "Yes" if group['allowExternalMembers'] else "No"
        lines.append(f"🌐 External Members: {external}")

    # Group type/category
    if group.get('adminCreated'):
        lines.append("🔧 Admin Created")

    return "\n".join(lines)


def format_device_info(device: Dict[str, Any], device_type: str = "mobile") -> str:
    """Format device information for display."""
    if not device:
        return "No device data available"

    lines = []

    if device_type == "mobile":
        # Mobile device formatting
        model = device.get('model', 'Unknown Device')
        os_version = device.get('os', 'Unknown OS')
        status = device.get('status', 'Unknown')

        lines.append(f"📱 {model}")
        lines.append(f"💿 OS: {os_version}")
        lines.append(f"📊 Status: {status}")

        if device.get('lastSync'):
            last_sync = format_timestamp(device['lastSync'])
            lines.append(f"🔄 Last Sync: {last_sync}")

        if device.get('userEmail'):
            lines.append(f"👤 User: {device['userEmail']}")

    elif device_type == "chrome":
        # Chrome device formatting
        model = device.get('model', 'Unknown Chrome Device')
        platform = device.get('platformVersion', 'Unknown Platform')
        status = device.get('status', 'Unknown')

        lines.append(f"💻 {model}")
        lines.append(f"🔧 Platform: {platform}")
        lines.append(f"📊 Status: {status}")

        if device.get('lastSync'):
            last_sync = format_timestamp(device['lastSync'])
            lines.append(f"🔄 Last Sync: {last_sync}")

        if device.get('orgUnitPath'):
            lines.append(f"🏢 Org Unit: {device['orgUnitPath']}")

    else:
        # Generic device formatting
        device_id = device.get('deviceId', 'Unknown ID')
        lines.append(f"🔧 Device ID: {device_id}")

    return "\n".join(lines)


def format_report_data(report_data: Dict[str, Any], report_type: str) -> str:
    """Format report data for display."""
    if not report_data:
        return "No report data available"

    lines = []
    lines.append(f"📊 Report Type: {report_type}")

    if report_type == "usage":
        # Usage report formatting
        if 'date' in report_data:
            lines.append(f"📅 Date: {report_data['date']}")

        if 'parameters' in report_data:
            lines.append("📈 Metrics:")
            for param in report_data['parameters']:
                name = param.get('name', 'Unknown')
                value = param.get('intValue', param.get('stringValue', 'N/A'))
                lines.append(f"   • {name}: {value}")

    elif report_type == "audit":
        # Audit report formatting
        if 'id' in report_data:
            lines.append(f"🆔 Event ID: {report_data['id']['uniqueQualifier']}")

        if 'actor' in report_data:
            actor_email = report_data['actor'].get('email', 'Unknown')
            lines.append(f"👤 Actor: {actor_email}")

        if 'events' in report_data:
            lines.append("🎯 Events:")
            for event in report_data['events']:
                event_type = event.get('type', 'Unknown')
                event_name = event.get('name', 'Unknown')
                lines.append(f"   • {event_type}: {event_name}")

        if 'id' in report_data and 'time' in report_data['id']:
            timestamp = format_timestamp(report_data['id']['time'])
            lines.append(f"🕐 Time: {timestamp}")

    else:
        # Generic report formatting
        for key, value in report_data.items():
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"   {key}: {value}")

    return "\n".join(lines)


def format_timestamp(timestamp: str) -> str:
    """Format a timestamp string for display."""
    try:
        # Handle various timestamp formats
        if 'T' in timestamp:
            # ISO format
            if timestamp.endswith('Z'):
                dt = datetime.fromisoformat(timestamp[:-1] + '+00:00')
            elif '+' in timestamp or timestamp.count('-') > 2:
                dt = datetime.fromisoformat(timestamp)
            else:
                dt = datetime.fromisoformat(timestamp)
        else:
            # Assume it's already formatted or a different format
            return timestamp

        # Format for display
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except (ValueError, AttributeError):
        # Return original if parsing fails
        return timestamp


def format_org_unit_info(org_unit: Dict[str, Any], detailed: bool = False) -> str:
    """Format organizational unit information for display."""
    if not org_unit:
        return "No organizational unit data available"

    name = org_unit.get('name', 'Unknown OU')
    path = org_unit.get('orgUnitPath', '/')
    description = org_unit.get('description', '')

    if not detailed:
        return f"{name} ({path})"

    lines = []
    lines.append(f"🏢 {name}")
    lines.append(f"📍 Path: {path}")

    if description:
        lines.append(f"📄 Description: {description}")

    # Parent OU
    parent_path = org_unit.get('parentOrgUnitPath')
    if parent_path and parent_path != path:
        lines.append(f"⬆️  Parent: {parent_path}")

    # Block inheritance
    if 'blockInheritance' in org_unit:
        inheritance = "No" if org_unit['blockInheritance'] else "Yes"
        lines.append(f"🔗 Inherits Settings: {inheritance}")

    return "\n".join(lines)


def format_domain_info(domain: Dict[str, Any]) -> str:
    """Format domain information for display."""
    if not domain:
        return "No domain data available"

    domain_name = domain.get('domainName', 'Unknown Domain')
    verified = domain.get('verified', False)
    primary = domain.get('isPrimary', False)

    lines = []
    lines.append(f"🌐 {domain_name}")

    # Status indicators
    status_parts = []
    if primary:
        status_parts.append("🔷 PRIMARY")
    if verified:
        status_parts.append("✅ VERIFIED")
    else:
        status_parts.append("⚠️  UNVERIFIED")

    lines.append(f"📊 Status: {' | '.join(status_parts)}")

    # Creation time
    if domain.get('creationTime'):
        creation = format_timestamp(domain['creationTime'])
        lines.append(f"📅 Created: {creation}")

    return "\n".join(lines)


def format_error_summary(error: Exception) -> str:
    """Format error information for display."""
    error_type = type(error).__name__
    error_message = str(error)

    lines = []
    lines.append(f"❌ Error: {error_type}")
    lines.append(f"💬 Message: {error_message}")

    # Add specific error details if available
    if hasattr(error, 'error_code'):
        lines.append(f"🔍 Code: {error.error_code}")

    if hasattr(error, 'status_code'):
        lines.append(f"📟 HTTP Status: {error.status_code}")

    return "\n".join(lines)


def format_success_message(action: str, target: str, details: Optional[Dict[str, Any]] = None) -> str:
    """Format a success message."""
    lines = []
    lines.append(f"✅ Successfully {action}: {target}")

    if details:
        lines.append("")
        for key, value in details.items():
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"   {key}: {value}")

    return "\n".join(lines)


def format_table(headers: List[str], rows: List[List[str]], max_width: int = 80) -> str:
    """Format data as a simple text table."""
    if not headers or not rows:
        return "No data to display"

    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Limit column widths to prevent overly wide tables
    max_col_width = max_width // len(headers) - 3
    col_widths = [min(width, max_col_width) for width in col_widths]

    lines = []

    # Header
    header_line = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
    lines.append(header_line)
    lines.append("-" * len(header_line))

    # Rows
    for row in rows:
        row_line = " | ".join(
            str(cell).ljust(col_widths[i])[:col_widths[i]]
            for i, cell in enumerate(row)
        )
        lines.append(row_line)

    return "\n".join(lines)