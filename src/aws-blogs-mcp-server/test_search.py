#!/usr/bin/env python3
"""
Test search functionality with different terms.
"""

import asyncio
import sys
import os
import httpx
import feedparser

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from awslabs.aws_blogs_mcp_server.utils import AWS_BLOG_CATEGORIES


async def test_search_with_term(search_term):
    """Test search with a specific term."""
    print(f"=== Searching for: '{search_term}' ===")
    
    try:
        # Search in AWS blog RSS feed
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        # Simple search implementation
        results = []
        query_lower = search_term.lower()
        
        for entry in feed.entries:
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
                    'relevance': relevance_score,
                    'published': entry.get('published', '')
                })
        
        if results:
            print(f"✅ Found {len(results)} matching posts:")
            for i, result in enumerate(results[:5], 1):  # Show top 5
                print(f"  {i}. {result['title']} (relevance: {result['relevance']})")
                print(f"     Published: {result['published']}")
                print(f"     URL: {result['url']}")
                print()
        else:
            print(f"❌ No posts found matching '{search_term}'")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    print()


async def show_recent_posts():
    """Show recent posts to see what's available."""
    print("=== Recent AWS Blog Posts ===")
    
    try:
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        print(f"Recent posts from AWS News Blog:")
        for i, entry in enumerate(feed.entries[:10], 1):
            title = entry.get('title', 'No title')
            published = entry.get('published', 'No date')
            print(f"  {i}. {title}")
            print(f"     Published: {published}")
            print()
            
    except Exception as e:
        print(f"❌ Failed to get recent posts: {e}")


async def main():
    """Test search with various terms."""
    await show_recent_posts()
    
    # Test with terms that are likely to appear in AWS blogs
    search_terms = [
        "AI",
        "machine learning", 
        "security",
        "EC2",
        "S3",
        "Nova",
        "Bedrock",
        "serverless"
    ]
    
    for term in search_terms:
        await test_search_with_term(term)


if __name__ == "__main__":
    asyncio.run(main())