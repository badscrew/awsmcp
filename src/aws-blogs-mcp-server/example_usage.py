#!/usr/bin/env python3
"""
Example usage of the AWS Blogs MCP Server.

This script demonstrates how to use the MCP server tools.
Run this after installing dependencies with: pip install -e .
"""

import asyncio
from mcp.server.fastmcp import Context
from awslabs.aws_blogs_mcp_server.server import (
    list_blog_categories,
    get_recent_posts,
    search_blog_posts,
)


async def main():
    """Example usage of AWS Blogs MCP Server tools."""
    ctx = Context()
    
    print("=== AWS Blogs MCP Server Example ===\n")
    
    # List available blog categories
    print("1. Available Blog Categories:")
    categories = await list_blog_categories(ctx)
    for cat in categories[:5]:  # Show first 5
        print(f"   - {cat.name} ({cat.slug})")
        print(f"     URL: {cat.url}")
    print(f"   ... and {len(categories) - 5} more categories\n")
    
    # Get recent posts from machine learning blog
    print("2. Recent Machine Learning Blog Posts:")
    ml_posts = await get_recent_posts(ctx, category="machine-learning", limit=3)
    for post in ml_posts:
        print(f"   - {post.title}")
        print(f"     Published: {post.published_date}")
        print(f"     URL: {post.url}")
        print()
    
    # Search for posts about Lambda
    print("3. Search Results for 'Lambda':")
    search_results = await search_blog_posts(ctx, query="Lambda", limit=3)
    for result in search_results:
        print(f"   - {result.title}")
        print(f"     URL: {result.url}")
        print(f"     Relevance: {result.relevance_score}")
        print()


if __name__ == "__main__":
    asyncio.run(main())