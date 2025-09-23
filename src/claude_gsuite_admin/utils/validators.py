"""Input validation utilities for Google Workspace Admin MCP."""

import re
from typing import Optional
from ..core.exceptions import ValidationError


# Email validation regex pattern
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Domain validation regex pattern
DOMAIN_PATTERN = re.compile(
    r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.?[a-zA-Z]{2,}$'
)

# User ID pattern (can be email or Google user ID)
USER_ID_PATTERN = re.compile(
    r'^(?:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[0-9]{21})$'
)

# Group email pattern (stricter for group emails)
GROUP_EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Organizational unit path pattern
ORG_UNIT_PATTERN = re.compile(
    r'^(/[a-zA-Z0-9\s\-_\.]+)*/?$'
)


def validate_email(email: str, field_name: str = "email") -> None:
    """Validate an email address format."""
    if not email or not isinstance(email, str):
        raise ValidationError(f"Email must be a non-empty string", field_name)

    email = email.strip()
    if not EMAIL_PATTERN.match(email):
        raise ValidationError(f"Invalid email format: {email}", field_name)


def validate_domain(domain: str, field_name: str = "domain") -> None:
    """Validate a domain name format."""
    if not domain or not isinstance(domain, str):
        raise ValidationError(f"Domain must be a non-empty string", field_name)

    domain = domain.strip().lower()
    if not DOMAIN_PATTERN.match(domain):
        raise ValidationError(f"Invalid domain format: {domain}", field_name)


def validate_user_id(user_id: str, field_name: str = "user_id") -> None:
    """Validate a user ID (can be email or Google user ID)."""
    if not user_id or not isinstance(user_id, str):
        raise ValidationError(f"User ID must be a non-empty string", field_name)

    user_id = user_id.strip()
    if not USER_ID_PATTERN.match(user_id):
        raise ValidationError(f"Invalid user ID format: {user_id}", field_name)


def validate_group_id(group_id: str, field_name: str = "group_id") -> None:
    """Validate a group ID (usually email format)."""
    if not group_id or not isinstance(group_id, str):
        raise ValidationError(f"Group ID must be a non-empty string", field_name)

    group_id = group_id.strip()
    if not GROUP_EMAIL_PATTERN.match(group_id):
        raise ValidationError(f"Invalid group email format: {group_id}", field_name)


def validate_org_unit(org_unit_path: str, field_name: str = "org_unit_path") -> None:
    """Validate an organizational unit path."""
    if not org_unit_path or not isinstance(org_unit_path, str):
        raise ValidationError(f"Organizational unit path must be a non-empty string", field_name)

    org_unit_path = org_unit_path.strip()

    # Root OU is always valid
    if org_unit_path == "/":
        return

    if not ORG_UNIT_PATTERN.match(org_unit_path):
        raise ValidationError(f"Invalid organizational unit path format: {org_unit_path}", field_name)

    # Additional validation rules
    if org_unit_path.startswith("//") or "//" in org_unit_path:
        raise ValidationError(f"Organizational unit path cannot contain consecutive slashes", field_name)

    if len(org_unit_path) > 255:
        raise ValidationError(f"Organizational unit path too long (max 255 characters)", field_name)


def validate_password_strength(password: str, field_name: str = "password") -> None:
    """Validate password meets minimum security requirements."""
    if not password or not isinstance(password, str):
        raise ValidationError(f"Password must be a non-empty string", field_name)

    # Google Workspace password requirements
    if len(password) < 8:
        raise ValidationError(f"Password must be at least 8 characters long", field_name)

    if len(password) > 100:
        raise ValidationError(f"Password must be no more than 100 characters long", field_name)

    # Check for at least one character from different categories
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password)

    if not (has_lower and has_upper and (has_digit or has_special)):
        raise ValidationError(
            f"Password must contain at least one lowercase letter, one uppercase letter, "
            f"and one digit or special character", field_name
        )


def validate_name(name: str, field_name: str = "name", max_length: int = 60) -> None:
    """Validate a person's name (first name, last name, etc.)."""
    if not name or not isinstance(name, str):
        raise ValidationError(f"Name must be a non-empty string", field_name)

    name = name.strip()
    if not name:
        raise ValidationError(f"Name cannot be empty or whitespace only", field_name)

    if len(name) > max_length:
        raise ValidationError(f"Name must be no more than {max_length} characters long", field_name)

    # Check for invalid characters (basic validation)
    if any(c in name for c in '<>{}[]()&;'):
        raise ValidationError(f"Name contains invalid characters", field_name)


def validate_phone_number(phone: str, field_name: str = "phone") -> None:
    """Validate a phone number format."""
    if not phone or not isinstance(phone, str):
        raise ValidationError(f"Phone number must be a non-empty string", field_name)

    phone = phone.strip()

    # Remove common formatting characters
    cleaned_phone = re.sub(r'[\s\-\(\)\+\.]', '', phone)

    # Basic validation - should be mostly digits
    if not re.match(r'^\+?[0-9]{7,15}$', cleaned_phone):
        raise ValidationError(f"Invalid phone number format: {phone}", field_name)


def validate_suspension_reason(reason: str, field_name: str = "suspension_reason") -> None:
    """Validate a suspension reason."""
    if not reason or not isinstance(reason, str):
        raise ValidationError(f"Suspension reason must be a non-empty string", field_name)

    reason = reason.strip()
    if not reason:
        raise ValidationError(f"Suspension reason cannot be empty", field_name)

    if len(reason) > 500:
        raise ValidationError(f"Suspension reason must be no more than 500 characters", field_name)


def validate_query_string(query: str, field_name: str = "query") -> None:
    """Validate a search query string."""
    if not query or not isinstance(query, str):
        raise ValidationError(f"Query must be a non-empty string", field_name)

    query = query.strip()
    if not query:
        raise ValidationError(f"Query cannot be empty or whitespace only", field_name)

    if len(query) > 500:
        raise ValidationError(f"Query must be no more than 500 characters", field_name)


def validate_page_size(page_size: int, min_size: int = 1, max_size: int = 500, field_name: str = "page_size") -> None:
    """Validate page size for paginated results."""
    if not isinstance(page_size, int):
        raise ValidationError(f"Page size must be an integer", field_name)

    if page_size < min_size:
        raise ValidationError(f"Page size must be at least {min_size}", field_name)

    if page_size > max_size:
        raise ValidationError(f"Page size must be no more than {max_size}", field_name)


def validate_boolean_string(value: str, field_name: str) -> bool:
    """Validate and convert a string to boolean."""
    if not isinstance(value, (str, bool)):
        raise ValidationError(f"{field_name} must be a boolean or string", field_name)

    if isinstance(value, bool):
        return value

    value = value.strip().lower()
    if value in ('true', '1', 'yes', 'on'):
        return True
    elif value in ('false', '0', 'no', 'off'):
        return False
    else:
        raise ValidationError(f"Invalid boolean value: {value}", field_name)


def validate_sort_order(order: str, valid_fields: list, field_name: str = "order_by") -> None:
    """Validate sort order field."""
    if not order or not isinstance(order, str):
        raise ValidationError(f"Sort order must be a non-empty string", field_name)

    order = order.strip()
    if order not in valid_fields:
        raise ValidationError(f"Invalid sort field: {order}. Valid options: {', '.join(valid_fields)}", field_name)