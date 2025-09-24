"""Google Workspace Domain Management Tools."""

import logging
from typing import Any, Dict, List, Optional, Sequence
from collections.abc import Sequence as AbstractSequence

from mcp.types import Tool, TextContent

from ..core.tool_handler import AdminToolHandler, USER_ID_ARG
from ..core.exceptions import ValidationError, DomainNotFoundError
from ..utils.validators import validate_email
from ..utils.logging import get_logger, log_tool_execution, log_api_call


logger = get_logger('tools.domains')


class ListDomainsHandler(AdminToolHandler):
    """Handler for listing Google Workspace domains."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__list_domains")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""List all domains in the Google Workspace organization.
            Returns primary domain and all domain aliases with their verification status.""",
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
                    }
                },
                "required": [USER_ID_ARG]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the domain listing operation."""
        user_id = args.get("user_id")
        if not user_id:
            raise ValidationError("user_id is required")

        customer_id = args.get("customer_id", "my_customer")

        try:
            service = self.get_google_service(user_id, "admin", "directory_v1")

            # Get domains
            domains_result = service.domains().list(customer=customer_id).execute()
            domains = domains_result.get("domains", [])

            if not domains:
                response_text = "No domains found in this Google Workspace organization."
                return [TextContent(type="text", text=response_text)]

            response_text = "## Google Workspace Domains\n\n"

            primary_domains = [d for d in domains if d.get("isPrimary", False)]
            alias_domains = [d for d in domains if not d.get("isPrimary", False)]

            if primary_domains:
                response_text += "### Primary Domain\n"
                for domain in primary_domains:
                    response_text += f"**{domain['domainName']}**\n"
                    response_text += f"  • Status: {domain.get('verified', False) and 'Verified ✓' or 'Unverified ⚠️'}\n"
                    response_text += f"  • Creation Time: {domain.get('creationTime', 'N/A')}\n\n"

            if alias_domains:
                response_text += "### Domain Aliases\n"
                for domain in alias_domains:
                    response_text += f"**{domain['domainName']}**\n"
                    response_text += f"  • Status: {domain.get('verified', False) and 'Verified ✓' or 'Unverified ⚠️'}\n"
                    response_text += f"  • Creation Time: {domain.get('creationTime', 'N/A')}\n\n"

            response_text += f"**Total domains:** {len(domains)}\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, "list domains")


class GetDomainHandler(AdminToolHandler):
    """Handler for getting detailed domain information."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__get_domain")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get detailed information about a specific domain.
            Returns domain verification status, DNS records, and configuration details.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "domain_name": {
                        "type": "string",
                        "description": "Domain name to retrieve information for"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (default: 'my_customer')",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG, "domain_name"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the domain info retrieval operation."""
        user_id = args.get("user_id")
        domain_name = args.get("domain_name")
        customer_id = args.get("customer_id", "my_customer")

        if not user_id:
            raise ValidationError("user_id is required")
        if not domain_name:
            raise ValidationError("domain_name is required")

        try:
            service = self.get_google_service(user_id, "admin", "directory_v1")

            # Get domain details
            domain_result = service.domains().get(
                customer=customer_id,
                domainName=domain_name
            ).execute()

            response_text = f"## Domain Information: {domain_name}\n\n"
            response_text += f"**Domain Name:** {domain_result['domainName']}\n"
            response_text += f"**Primary Domain:** {'Yes' if domain_result.get('isPrimary', False) else 'No'}\n"
            response_text += f"**Verified:** {'Yes ✓' if domain_result.get('verified', False) else 'No ⚠️'}\n"
            response_text += f"**Creation Time:** {domain_result.get('creationTime', 'N/A')}\n\n"

            # Get domain aliases
            try:
                aliases_result = service.domainAliases().list(customer=customer_id).execute()
                domain_aliases = aliases_result.get("domainAliases", [])

                if domain_aliases:
                    response_text += "### Domain Aliases\n"
                    for alias in domain_aliases:
                        if alias.get('parentDomainName') == domain_name:
                            response_text += f"• {alias['domainAliasName']}\n"
                            response_text += f"  - Verified: {'Yes ✓' if alias.get('verified', False) else 'No ⚠️'}\n"
                    response_text += "\n"
            except Exception:
                # Aliases might not be accessible for all domains
                pass

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"get domain {domain_name}")


class AddDomainAliasHandler(AdminToolHandler):
    """Handler for adding domain aliases."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__add_domain_alias")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Add a domain alias to the Google Workspace organization.
            Domain aliases allow users to have email addresses at multiple domains.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "domain_alias_name": {
                        "type": "string",
                        "description": "Domain alias to add (e.g., 'alias.example.com')"
                    },
                    "parent_domain_name": {
                        "type": "string",
                        "description": "Parent domain name (optional, defaults to primary domain)"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (default: 'my_customer')",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG, "domain_alias_name"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the domain alias addition operation."""
        user_id = args.get("user_id")
        domain_alias_name = args.get("domain_alias_name")
        parent_domain_name = args.get("parent_domain_name")
        customer_id = args.get("customer_id", "my_customer")

        if not user_id:
            raise ValidationError("user_id is required")
        if not domain_alias_name:
            raise ValidationError("domain_alias_name is required")

        try:
            service = self.get_google_service(user_id, "admin", "directory_v1")

            # If no parent domain specified, get the primary domain
            if not parent_domain_name:
                domains_result = service.domains().list(customer=customer_id).execute()
                domains = domains_result.get("domains", [])
                primary_domains = [d for d in domains if d.get("isPrimary", False)]
                if primary_domains:
                    parent_domain_name = primary_domains[0]["domainName"]
                else:
                    raise ValidationError("Could not determine primary domain")

            # Create domain alias
            domain_alias_body = {
                "domainAliasName": domain_alias_name,
                "parentDomainName": parent_domain_name
            }

            result = service.domainAliases().insert(
                customer=customer_id,
                body=domain_alias_body
            ).execute()

            response_text = f"## Domain Alias Added Successfully\n\n"
            response_text += f"**Alias Domain:** {result['domainAliasName']}\n"
            response_text += f"**Parent Domain:** {result['parentDomainName']}\n"
            response_text += f"**Verified:** {'Yes ✓' if result.get('verified', False) else 'No ⚠️'}\n\n"

            if not result.get('verified', False):
                response_text += "**Next Steps:**\n"
                response_text += "1. Verify domain ownership by adding DNS records\n"
                response_text += "2. Configure MX records to route email properly\n"
                response_text += "3. Wait for verification to complete (can take up to 24 hours)\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"add domain alias {domain_alias_name}")


class DeleteDomainAliasHandler(AdminToolHandler):
    """Handler for deleting domain aliases."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__delete_domain_alias")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Delete a domain alias from the Google Workspace organization.
            WARNING: This will permanently remove the domain alias and may affect email delivery.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "domain_alias_name": {
                        "type": "string",
                        "description": "Domain alias to delete"
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirm deletion (must be true)"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (default: 'my_customer')",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG, "domain_alias_name", "confirm"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the domain alias deletion operation."""
        user_id = args.get("user_id")
        domain_alias_name = args.get("domain_alias_name")
        confirm = args.get("confirm")
        customer_id = args.get("customer_id", "my_customer")

        if not user_id:
            raise ValidationError("user_id is required")
        if not domain_alias_name:
            raise ValidationError("domain_alias_name is required")
        if not confirm:
            raise ValidationError("confirm must be true to delete domain alias")

        try:
            service = self.get_google_service(user_id, "admin", "directory_v1")

            # Delete domain alias
            service.domainAliases().delete(
                customer=customer_id,
                domainAliasName=domain_alias_name
            ).execute()

            response_text = f"## Domain Alias Deleted Successfully\n\n"
            response_text += f"**Deleted:** {domain_alias_name}\n\n"
            response_text += "**Important Notes:**\n"
            response_text += "• Email addresses using this domain alias are no longer valid\n"
            response_text += "• DNS records can be removed from your domain registrar\n"
            response_text += "• Changes may take up to 24 hours to propagate fully\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"delete domain alias {domain_alias_name}")


class VerifyDomainHandler(AdminToolHandler):
    """Handler for domain verification operations."""

    def __init__(self):
        super().__init__("mcp__gsuite_admin__verify_domain")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Get domain verification information and status.
            Returns the verification token and instructions for domain verification.""",
            inputSchema={
                "type": "object",
                "properties": {
                    USER_ID_ARG: {
                        "type": "string",
                        "description": "Admin user email performing the operation"
                    },
                    "domain_name": {
                        "type": "string",
                        "description": "Domain name to verify"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (default: 'my_customer')",
                        "default": "my_customer"
                    }
                },
                "required": [USER_ID_ARG, "domain_name"]
            }
        )

    def run_tool(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the domain verification operation."""
        user_id = args.get("user_id")
        domain_name = args.get("domain_name")
        customer_id = args.get("customer_id", "my_customer")

        if not user_id:
            raise ValidationError("user_id is required")
        if not domain_name:
            raise ValidationError("domain_name is required")

        try:
            service = self.get_google_service(user_id, "admin", "directory_v1")

            # Get domain verification status
            domain_result = service.domains().get(
                customer=customer_id,
                domainName=domain_name
            ).execute()

            response_text = f"## Domain Verification Status: {domain_name}\n\n"

            is_verified = domain_result.get('verified', False)
            response_text += f"**Current Status:** {'Verified ✓' if is_verified else 'Unverified ⚠️'}\n\n"

            if not is_verified:
                response_text += "**Verification Instructions:**\n\n"
                response_text += "To verify domain ownership, you need to:\n\n"
                response_text += "1. **Add a TXT record to your DNS:**\n"
                response_text += f"   - Host/Name: @ (or leave blank for root domain)\n"
                response_text += f"   - Type: TXT\n"
                response_text += f"   - Value: Contact Google Workspace support for verification token\n\n"

                response_text += "2. **Alternative methods:**\n"
                response_text += "   - Upload an HTML file to your website root\n"
                response_text += "   - Add a meta tag to your website homepage\n"
                response_text += "   - Use Google Analytics or Google Tag Manager\n\n"

                response_text += "3. **After adding DNS record:**\n"
                response_text += "   - Wait for DNS propagation (up to 24 hours)\n"
                response_text += "   - Verification will happen automatically\n"
                response_text += "   - You can check status using this tool\n"
            else:
                response_text += "**Domain is already verified!**\n\n"
                response_text += "This domain can be used for:\n"
                response_text += "• Creating user accounts\n"
                response_text += "• Email routing and delivery\n"
                response_text += "• Google Workspace services\n"

            return [TextContent(type="text", text=response_text)]

        except Exception as e:
            self.handle_google_api_error(e, f"verify domain {domain_name}")


# Export all handlers
DOMAIN_HANDLERS = [
    ListDomainsHandler(),
    GetDomainHandler(),
    AddDomainAliasHandler(),
    DeleteDomainAliasHandler(),
    VerifyDomainHandler(),
]