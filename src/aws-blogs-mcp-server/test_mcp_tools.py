#!/usr/bin/env python3
"""
Test the MCP server tools directly.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the MCP Context since we don't have the full MCP framework
class MockContext:
    pass

# Import the server functions
from awslabs.aws_blogs_mcp_server.server import (
    list_blog_categories,
    get_recent_posts,
    search_blog_posts,
    get_rss_feed,
    read_blog_post,
)


async def test_list_categories():
    """Test listing blog categories."""
    print("=== Testing list_blog_categories ===")
    
    try:
        ctx = MockContext()
        categories = await list_blog_categories(ctx)
        
        print(f"✅ Found {len(categories)} categories:")
        for cat in categories[:5]:  # Show first 5
            print(f"  - {cat.name} ({cat.slug})")
            print(f"    URL: {cat.url}")
            print(f"    RSS: {cat.rss_url}")
        
        if len(categories) > 5:
            print(f"  ... and {len(categories) - 5} more")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_get_recent_posts():
    """Test getting recent posts."""
    print("=== Testing get_recent_posts ===")
    
    try:
        ctx = MockContext()
        
        # Test getting recent posts from AWS blog
        posts = await get_recent_posts(ctx, category="aws", limit=5)
        
        print(f"✅ Found {len(posts)} recent AWS blog posts:")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post.title}")
            print(f"     Published: {post.published_date}")
            print(f"     Category: {post.category}")
            print(f"     URL: {post.url}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_search_posts():
    """Test searching blog posts."""
    print("=== Testing search_blog_posts ===")
    
    try:
        ctx = MockContext()
        
        # Test searching for AI-related posts
        results = await search_blog_posts(ctx, query="AI", category="aws", limit=3)
        
        print(f"✅ Found {len(results)} search results for 'AI':")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.title}")
            print(f"     Relevance: {result.relevance_score}")
            print(f"     Published: {result.published_date}")
            print(f"     URL: {result.url}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_get_rss_feed():
    """Test getting RSS feed."""
    print("=== Testing get_rss_feed ===")
    
    try:
        ctx = MockContext()
        
        # Test getting RSS feed for machine learning blog
        posts = await get_rss_feed(ctx, category="machine-learning", limit=3)
        
        print(f"✅ Found {len(posts)} posts from ML blog RSS feed:")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post.title}")
            print(f"     Published: {post.published_date}")
            print(f"     Author: {post.author}")
            print(f"     URL: {post.url}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_read_blog_post():
    """Test reading a blog post."""
    print("=== Testing read_blog_post ===")
    
    try:
        ctx = MockContext()
        
        # Get a recent post URL first
        posts = await get_recent_posts(ctx, category="aws", limit=1)
        
        if posts:
            blog_url = posts[0].url
            print(f"Testing with URL: {blog_url}")
            
            # Read the blog post with a small max_length for testing
            content = await read_blog_post(ctx, url=blog_url, max_length=1000, start_index=0)
            
            print(f"✅ Successfully read blog post:")
            print(f"Content length: {len(content)} characters")
            print("\nFirst 500 characters:")
            print(content[:500])
            print("...")
            
        else:
            print("❌ No recent posts found to test with")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def main():
    """Run all MCP tool tests."""
    print("🧪 Testing AWS Blogs MCP Server Tools\n")
    
    await test_list_categories()
    await test_get_recent_posts()
    await test_search_posts()
    await test_get_rss_feed()
    await test_read_blog_post()
    
    print("🎉 All MCP tool tests completed!")


if __name__ == "__main__":
    asyncio.run(main())