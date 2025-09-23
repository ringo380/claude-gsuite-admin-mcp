#!/usr/bin/env python3
"""Entry point script for Claude GSuite Admin MCP server."""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the server
from claude_gsuite_admin.server import main

if __name__ == "__main__":
    asyncio.run(main())