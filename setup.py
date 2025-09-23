"""Setup configuration for Claude Google Workspace Admin MCP Server."""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="claude-gsuite-admin-mcp",
    version="0.1.0",
    author="Ryan Robson",
    author_email="ryan@robworks.info",
    description="A comprehensive Google Workspace Admin MCP server for Claude CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryanrobson/claude-gsuite-admin-mcp",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",
        "Topic :: Office/Business",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "claude-gsuite-admin-mcp=claude_gsuite_admin.server:main",
        ],
    },
    keywords=[
        "google-workspace",
        "gsuite",
        "admin",
        "mcp",
        "claude",
        "administration",
        "directory",
        "oauth",
        "api",
        "management"
    ],
    project_urls={
        "Bug Reports": "https://github.com/ryanrobson/claude-gsuite-admin-mcp/issues",
        "Source": "https://github.com/ryanrobson/claude-gsuite-admin-mcp",
        "Documentation": "https://github.com/ryanrobson/claude-gsuite-admin-mcp/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)