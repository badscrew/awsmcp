FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY awslabs/ ./awslabs/
COPY LICENSE NOTICE ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Health check
COPY docker-healthcheck.sh /usr/local/bin/
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["/usr/local/bin/docker-healthcheck.sh"]

# Run the MCP server
CMD ["python", "-m", "awslabs.aws_blogs_mcp_server.server"]