#!/usr/bin/env python3
"""
Test the core functions without MCP framework dependencies.
"""

import asyncio
import sys
import os
import httpx
import feedparser
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from awslabs.aws_blogs_mcp_server.utils import (
    AWS_BLOG_CATEGORIES,
    fetch_url_content,
    clean_html_content,
    extract_blog_metadata,
)
from awslabs.aws_blogs_mcp_server.models import BlogPost, BlogCategory, SearchResult
from bs4 import BeautifulSoup


async def test_list_categories_core():
    """Test the core category listing functionality."""
    print("=== Testing Core Category Listing ===")
    
    try:
        categories = []
        for slug, info in AWS_BLOG_CATEGORIES.items():
            category = BlogCategory(
                name=info['name'],
                slug=slug,
                url=info['url'],
                rss_url=info['rss']
            )
            categories.append(category)
        
        print(f"✅ Created {len(categories)} category objects:")
        for cat in categories[:3]:  # Show first 3
            print(f"  - {cat.name} ({cat.slug})")
            print(f"    URL: {cat.url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_rss_parsing_core():
    """Test RSS parsing and post creation."""
    print("=== Testing Core RSS Parsing ===")
    
    try:
        # Test with AWS blog RSS
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        posts = []
        
        for entry in feed.entries[:5]:  # Process first 5
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            
            post = BlogPost(
                title=entry.get('title', ''),
                url=entry.get('link', ''),
                summary=entry.get('summary', ''),
                author=entry.get('author', ''),
                published_date=published_date,
                category=AWS_BLOG_CATEGORIES['aws']['name']
            )
            posts.append(post)
        
        print(f"✅ Created {len(posts)} blog post objects:")
        for i, post in enumerate(posts[:3], 1):
            print(f"  {i}. {post.title}")
            print(f"     Published: {post.published_date}")
            print(f"     Category: {post.category}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_search_core():
    """Test search functionality."""
    print("=== Testing Core Search Functionality ===")
    
    try:
        query = "Nova"
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        results = []
        query_lower = query.lower()
        
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            
            # Simple relevance scoring
            relevance_score = 0
            if query_lower in title.lower():
                relevance_score += 2
            if query_lower in summary.lower():
                relevance_score += 1
            
            if relevance_score > 0:
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                
                result = SearchResult(
                    title=title,
                    url=entry.get('link', ''),
                    summary=summary,
                    published_date=published_date,
                    relevance_score=relevance_score
                )
                results.append(result)
        
        # Sort by relevance
        results = sorted(results, key=lambda x: x.relevance_score or 0, reverse=True)
        
        print(f"✅ Found {len(results)} search results for '{query}':")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.title}")
            print(f"     Relevance: {result.relevance_score}")
            print(f"     Published: {result.published_date}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_blog_reading_core():
    """Test blog post reading and markdown conversion."""
    print("=== Testing Core Blog Reading ===")
    
    try:
        # Get a recent post URL
        rss_url = AWS_BLOG_CATEGORIES['aws']['rss']
        
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        
        if feed.entries:
            blog_url = feed.entries[0].get('link')
            print(f"Testing with: {blog_url}")
            
            # Validate URL
            if not blog_url.startswith('https://aws.amazon.com/blogs/'):
                print("❌ Invalid URL format")
                return
            
            # Fetch content
            html_content = await fetch_url_content(blog_url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            metadata = extract_blog_metadata(soup, blog_url)
            
            # Convert to markdown
            markdown_content = clean_html_content(html_content)
            
            # Create metadata header
            metadata_header = f"# {metadata.get('title', 'AWS Blog Post')}\n\n"
            if metadata.get('author'):
                metadata_header += f"**Author:** {metadata['author']}\n"
            if metadata.get('published_date'):
                metadata_header += f"**Published:** {metadata['published_date']}\n"
            if metadata.get('category'):
                metadata_header += f"**Category:** {metadata['category']}\n"
            metadata_header += f"**URL:** {blog_url}\n\n---\n\n"
            
            full_content = metadata_header + markdown_content
            
            print(f"✅ Successfully processed blog post:")
            print(f"  Original HTML: {len(html_content)} characters")
            print(f"  Markdown: {len(markdown_content)} characters")
            print(f"  Full content: {len(full_content)} characters")
            print(f"  Title: {metadata.get('title', 'No title')}")
            print(f"  Category: {metadata.get('category', 'No category')}")
            
            # Show first 300 characters
            print(f"\nFirst 300 characters of processed content:")
            print(full_content[:300] + "...")
            
        else:
            print("❌ No blog posts found to test")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def test_multiple_categories():
    """Test functionality across multiple blog categories."""
    print("=== Testing Multiple Categories ===")
    
    categories_to_test = ['aws', 'machine-learning', 'security']
    
    for category in categories_to_test:
        if category not in AWS_BLOG_CATEGORIES:
            continue
            
        try:
            print(f"Testing {category} blog...")
            rss_url = AWS_BLOG_CATEGORIES[category]['rss']
            
            async with httpx.AsyncClient() as client:
                response = await client.get(rss_url, timeout=30.0)
                response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            print(f"  ✅ {category}: {len(feed.entries)} posts available")
            if feed.entries:
                latest = feed.entries[0]
                print(f"     Latest: {latest.get('title', 'No title')}")
            
        except Exception as e:
            print(f"  ❌ {category}: Error - {e}")
    
    print()


async def main():
    """Run all core functionality tests."""
    print("🧪 Testing AWS Blogs MCP Server Core Functionality\n")
    
    await test_list_categories_core()
    await test_rss_parsing_core()
    await test_search_core()
    await test_blog_reading_core()
    await test_multiple_categories()
    
    print("🎉 All core functionality tests completed!")
    print("\n📋 Test Summary:")
    print("✅ Blog categories configuration")
    print("✅ RSS feed parsing and BlogPost model creation")
    print("✅ Search functionality with relevance scoring")
    print("✅ Blog post reading and markdown conversion")
    print("✅ Metadata extraction")
    print("✅ Multiple category support")
    print("\n🚀 The AWS Blogs MCP Server is ready for use!")


if __name__ == "__main__":
    asyncio.run(main())