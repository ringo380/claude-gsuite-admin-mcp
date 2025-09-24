# Multi-stage build for Claude GSuite Admin MCP Server
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml setup.py ./
COPY src/ src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GSUITE_OAUTH_DIR=/app/oauth \
    GSUITE_GAUTH_FILE=/app/config/.gauth.json \
    GSUITE_ACCOUNTS_FILE=/app/config/.accounts.json

# Add labels
LABEL maintainer="ryan@robworks.info" \
      description="Claude CLI Google Workspace Admin MCP Server" \
      version="${VERSION:-latest}" \
      build_date="${BUILD_DATE}" \
      vcs_ref="${VCS_REF}"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r mcp && useradd -r -g mcp mcp

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Create directories
RUN mkdir -p /app/oauth /app/config /app/logs && \
    chown -R mcp:mcp /app

# Copy configuration examples
COPY .gauth.json.example /app/config/
COPY .accounts.json.example /app/config/

# Copy scripts
COPY scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.py

# Switch to non-root user
USER mcp

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose default MCP port
EXPOSE 8000

# Set default command
CMD ["claude-gsuite-admin-mcp"]