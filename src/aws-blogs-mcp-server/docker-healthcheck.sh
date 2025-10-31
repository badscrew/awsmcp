#!/bin/bash
# Simple health check for the MCP server
# This just checks if the Python process is running

pgrep -f "awslabs.aws_blogs_mcp_server.server" > /dev/null
exit $?