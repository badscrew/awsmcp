# AWS Blogs MCP Server

Model Context Protocol (MCP) server for AWS Blogs

This MCP server provides tools to access AWS blog posts, search for content, and browse different blog categories.

## Features

- **Read Blog Posts**: Fetch and convert AWS blog posts to markdown format
- **Search Blogs**: Search across AWS blog posts by keywords and categories
- **List Blog Categories**: Get available AWS blog categories
- **Browse Recent Posts**: Get recent posts from specific blog categories
- **RSS Feed Access**: Access RSS feeds for different blog categories

## Prerequisites

### Installation Requirements

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python 3.10 or newer using `uv python install 3.10` (or a more recent version)

## Installation

### For Development

1. Clone the repository and navigate to the server directory
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run the example:
   ```bash
   python example_usage.py
   ```

### Using Docker

Build and run with Docker:

```bash
docker build -t aws-blogs-mcp-server .
docker run --rm -i aws-blogs-mcp-server
```

### For Production Use

Configure the MCP server in your MCP client configuration:

```json
{
  "mcpServers": {
    "awslabs.aws-blogs-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-blogs-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Or using Docker:

```json
{
  "mcpServers": {
    "awslabs.aws-blogs-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--interactive",
        "--env",
        "FASTMCP_LOG_LEVEL=ERROR",
        "aws-blogs-mcp-server:latest"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `FASTMCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `WARNING` |

## Basic Usage

Example queries:
- "Find recent AWS blog posts about machine learning"
- "Read the latest AWS blog post about EC2"
- "Search for blog posts about serverless architecture"
- "Show me recent posts from the AWS Security blog"

## Tools

### read_blog_post

Fetches an AWS blog post and converts it to markdown format.

```python
read_blog_post(url: str, max_length: int, start_index: int) -> str
```

### search_blog_posts

Searches AWS blog posts by keywords and optionally filters by category.

```python
search_blog_posts(query: str, category: str, limit: int) -> list[dict]
```

### list_blog_categories

Gets available AWS blog categories.

```python
list_blog_categories() -> list[dict]
```

### get_recent_posts

Gets recent posts from a specific blog category or all categories.

```python
get_recent_posts(category: str, limit: int) -> list[dict]
```

### get_rss_feed

Gets RSS feed content for a specific blog category.

```python
get_rss_feed(category: str, limit: int) -> list[dict]
```