#!/usr/bin/env python3
"""
Test script for AWS Blogs MCP Server functionality.
Tests the core functions without the MCP framework.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from awslabs.aws_blogs_mcp_server.utils import (
    AWS_BLOG_CATEGORIES,
    fetch_url_content,
    clean_html_content,
    extract_blog_metadata,
)
import feedparser
import httpx


async def test_blog_categories():
    """Test that blog categories are properly configured."""
    print("=== Testing Blog Categories ===")
    print(f"Found {len(AWS_BLOG_CATEGORIES)} blog categories:")
    
    for slug, info in list(AWS_BLOG_CATEGORIES.items())[:3]:  # Test first 3
        print(f"  - {slug}: {info['name']}")
        print(f"    URL: {info['url']}")
        print(f"    RSS: {info['rss']}")
    
    print("✅ Blog categories test passed\n")


async def test_rss_feed():
    """Test RSS feed parsing."""
    print("=== Testing RSS Feed Parsing ===")
    
    try:
        # Test AWS News blog RSS feed
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        print(f"Testing RSS feed: {rss_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        if feed.entries:
            print(f"✅ Successfully parsed RSS feed with {len(feed.entries)} entries")
            
            # Show first entry
            entry = feed.entries[0]
            print(f"  Latest post: {entry.get('title', 'No title')}")
            print(f"  URL: {entry.get('link', 'No URL')}")
            print(f"  Published: {entry.get('published', 'No date')}")
        else:
            print("❌ No entries found in RSS feed")
            
    except Exception as e:
        print(f"❌ RSS feed test failed: {e}")
    
    print()


async def test_blog_post_reading():
    """Test reading a blog post."""
    print("=== Testing Blog Post Reading ===")
    
    try:
        # Get a recent blog post URL from RSS
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        if feed.entries:
            blog_url = feed.entries[0].get('link')
            print(f"Testing blog post: {blog_url}")
            
            # Fetch the blog post content
            html_content = await fetch_url_content(blog_url)
            print(f"✅ Successfully fetched blog post ({len(html_content)} characters)")
            
            # Test HTML cleaning and markdown conversion
            markdown_content = clean_html_content(html_content)
            print(f"✅ Successfully converted to markdown ({len(markdown_content)} characters)")
            
            # Test metadata extraction
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            metadata = extract_blog_metadata(soup, blog_url)
            
            print("✅ Extracted metadata:")
            for key, value in metadata.items():
                if value:
                    print(f"  {key}: {value}")
            
            # Show a snippet of the markdown
            snippet = markdown_content[:300] + "..." if len(markdown_content) > 300 else markdown_content
            print(f"\nMarkdown snippet:\n{snippet}")
            
        else:
            print("❌ No blog posts found to test")
            
    except Exception as e:
        print(f"❌ Blog post reading test failed: {e}")
    
    print()


async def test_search_functionality():
    """Test search functionality using RSS feeds."""
    print("=== Testing Search Functionality ===")
    
    try:
        search_query = "lambda"
        print(f"Searching for: '{search_query}'")
        
        # Search in AWS blog RSS feed
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        # Simple search implementation
        results = []
        query_lower = search_query.lower()
        
        for entry in feed.entries[:20]:  # Check first 20 entries
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            
            relevance_score = 0
            if query_lower in title.lower():
                relevance_score += 2
            if query_lower in summary.lower():
                relevance_score += 1
            
            if relevance_score > 0:
                results.append({
                    'title': title,
                    'url': entry.get('link', ''),
                    'relevance': relevance_score
                })
        
        if results:
            print(f"✅ Found {len(results)} matching posts:")
            for i, result in enumerate(results[:3], 1):  # Show top 3
                print(f"  {i}. {result['title']} (relevance: {result['relevance']})")
                print(f"     {result['url']}")
        else:
            print(f"❌ No posts found matching '{search_query}'")
            
    except Exception as e:
        print(f"❌ Search functionality test failed: {e}")
    
    print()


async def main():
    """Run all tests."""
    print("🧪 Testing AWS Blogs MCP Server Functionality\n")
    
    await test_blog_categories()
    await test_rss_feed()
    await test_blog_post_reading()
    await test_search_functionality()
    
    print("🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())