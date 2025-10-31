# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""AWS Blogs MCP Server implementation."""

import os
import sys
import httpx
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional

from awslabs.aws_blogs_mcp_server.models import BlogPost, BlogCategory, SearchResult
from awslabs.aws_blogs_mcp_server.utils import (
    AWS_BLOG_CATEGORIES,
    DEFAULT_USER_AGENT,
    clean_html_content,
    extract_blog_metadata,
    fetch_url_content,
    parse_date_string,
)

from loguru import logger
from mcp.server.fastmcp import Context, FastMCP
from pydantic import Field


# Set up logging
logger.remove()
logger.add(sys.stderr, level=os.getenv('FASTMCP_LOG_LEVEL', 'WARNING'))


mcp = FastMCP(
    'awslabs.aws-blogs-mcp-server',
    instructions="""
    # AWS Blogs MCP Server

    This server provides tools to access AWS blog posts, search for content, and browse different blog categories.

    ## Best Practices

    - For long blog posts, make multiple calls to `read_blog_post` with different `start_index` values for pagination
    - When searching, use specific technical terms and AWS service names for better results
    - Use `get_recent_posts` to discover the latest content in specific categories
    - Use `list_blog_categories` to see all available blog categories
    - Always cite the blog post URL when providing information to users
    - Use RSS feeds via `get_rss_feed` for programmatic access to recent posts

    ## Tool Selection Guide

    - Use `search_blog_posts` when: You need to find blog posts about specific topics or AWS services
    - Use `read_blog_post` when: You have a specific blog post URL and need its full content
    - Use `get_recent_posts` when: You want to see the latest posts from a category or all categories
    - Use `list_blog_categories` when: You need to see what blog categories are available
    - Use `get_rss_feed` when: You need structured data about recent posts in a category
    """,
    dependencies=[
        'pydantic',
        'httpx',
        'beautifulsoup4',
        'markdownify',
        'feedparser',
    ],
)


@mcp.tool()
async def read_blog_post(
    ctx: Context,
    url: str = Field(description='URL of the AWS blog post to read'),
    max_length: int = Field(
        default=5000,
        description='Maximum number of characters to return.',
        gt=0,
        lt=1000000,
    ),
    start_index: int = Field(
        default=0,
        description='Starting character index for pagination.',
        ge=0,
    ),
) -> str:
    """
    Fetch and convert an AWS blog post to markdown format.

    ## Usage

    This tool retrieves the content of an AWS blog post and converts it to markdown format.
    For long blog posts, you can make multiple calls with different start_index values to retrieve
    the entire content in chunks.

    ## URL Requirements

    - Must be from the aws.amazon.com/blogs domain
    - Should be a valid blog post URL

    ## Example URLs

    - https://aws.amazon.com/blogs/aws/introducing-aws-rtb-fabric/
    - https://aws.amazon.com/blogs/machine-learning/build-accurate-ai-applications/
    - https://aws.amazon.com/blogs/security/new-security-features/

    ## Output Format

    The output is formatted as markdown text with:
    - Preserved headings and structure
    - Code blocks for examples
    - Lists and tables converted to markdown format
    - Metadata about the post (title, author, date, category)

    ## Handling Long Posts

    If the response indicates the content was truncated, make another call with start_index
    set to the end of the previous response to continue reading.

    Args:
        ctx: MCP context for logging and error handling
        url: URL of the AWS blog post to read
        max_length: Maximum number of characters to return
        start_index: Starting character index for pagination

    Returns:
        Markdown content of the AWS blog post with metadata
    """
    try:
        # Validate URL
        if not url.startswith('https://aws.amazon.com/blogs/'):
            raise ValueError('URL must be from aws.amazon.com/blogs domain')

        logger.info(f'Fetching blog post: {url}')
        
        # Fetch the content
        html_content = await fetch_url_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        metadata = extract_blog_metadata(soup, url)
        
        # Convert to markdown
        markdown_content = clean_html_content(html_content)
        
        # Add metadata header
        metadata_header = f"# {metadata.get('title', 'AWS Blog Post')}\n\n"
        if metadata.get('author'):
            metadata_header += f"**Author:** {metadata['author']}\n"
        if metadata.get('published_date'):
            metadata_header += f"**Published:** {metadata['published_date']}\n"
        if metadata.get('category'):
            metadata_header += f"**Category:** {metadata['category']}\n"
        metadata_header += f"**URL:** {url}\n\n---\n\n"
        
        full_content = metadata_header + markdown_content
        
        # Handle pagination
        if start_index >= len(full_content):
            return "No more content available."
        
        end_index = start_index + max_length
        result = full_content[start_index:end_index]
        
        if end_index < len(full_content):
            result += f"\n\n[Content truncated. Use start_index={end_index} to continue reading.]"
        
        return result
        
    except Exception as e:
        logger.error(f'Error reading blog post {url}: {e}')
        return f'Error reading blog post: {str(e)}'


@mcp.tool()
async def search_blog_posts(
    ctx: Context,
    query: str = Field(description='Search query for blog posts'),
    category: Optional[str] = Field(
        default=None,
        description='Optional blog category to filter results (e.g., "machine-learning", "security")'
    ),
    limit: int = Field(default=10, description='Maximum number of results to return', ge=1, le=50),
) -> List[SearchResult]:
    """
    Search AWS blog posts by keywords and optionally filter by category.

    ## Usage

    This tool searches across AWS blog posts for content matching your query.
    You can optionally filter results by blog category.

    ## Search Tips

    - Use specific AWS service names for better results (e.g., "EC2", "Lambda", "S3")
    - Include technical terms and concepts
    - Use quotes for exact phrase matching
    - Combine service names with use cases (e.g., "Lambda serverless architecture")

    ## Available Categories

    Use `list_blog_categories` to see all available categories, or use these common ones:
    - aws (AWS News Blog)
    - machine-learning
    - security
    - compute
    - database
    - containers
    - architecture

    Args:
        ctx: MCP context for logging and error handling
        query: Search query string
        category: Optional category filter
        limit: Maximum number of results

    Returns:
        List of search results with titles, URLs, summaries, and metadata
    """
    try:
        logger.info(f'Searching blog posts: query="{query}", category="{category}"')
        
        results = []
        
        # If category is specified, search only that category's RSS feed
        if category and category in AWS_BLOG_CATEGORIES:
            rss_url = AWS_BLOG_CATEGORIES[category]['rss']
            feed_results = await _search_rss_feed(rss_url, query, limit)
            results.extend(feed_results)
        else:
            # Search across multiple categories
            categories_to_search = [category] if category and category in AWS_BLOG_CATEGORIES else list(AWS_BLOG_CATEGORIES.keys())
            
            for cat in categories_to_search[:5]:  # Limit to 5 categories to avoid too many requests
                try:
                    rss_url = AWS_BLOG_CATEGORIES[cat]['rss']
                    feed_results = await _search_rss_feed(rss_url, query, limit // len(categories_to_search) + 1)
                    results.extend(feed_results)
                except Exception as e:
                    logger.warning(f'Error searching category {cat}: {e}')
                    continue
        
        # Sort by relevance and limit results
        results = sorted(results, key=lambda x: x.relevance_score or 0, reverse=True)[:limit]
        
        return results
        
    except Exception as e:
        logger.error(f'Error searching blog posts: {e}')
        return []


@mcp.tool()
async def list_blog_categories(ctx: Context) -> List[BlogCategory]:
    """
    Get available AWS blog categories.

    ## Usage

    This tool returns a list of all available AWS blog categories that you can use
    for filtering searches or getting recent posts.

    Returns:
        List of blog categories with names, URLs, and RSS feed URLs
    """
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
        
        return categories
        
    except Exception as e:
        logger.error(f'Error listing blog categories: {e}')
        return []


@mcp.tool()
async def get_recent_posts(
    ctx: Context,
    category: Optional[str] = Field(
        default=None,
        description='Blog category to get posts from (optional, defaults to all categories)'
    ),
    limit: int = Field(default=10, description='Maximum number of posts to return', ge=1, le=50),
) -> List[BlogPost]:
    """
    Get recent posts from a specific blog category or all categories.

    ## Usage

    This tool retrieves the most recent blog posts from AWS blogs.
    You can specify a category to get posts from a specific blog, or leave it empty
    to get recent posts from all categories.

    ## Available Categories

    Use `list_blog_categories` to see all available categories.

    Args:
        ctx: MCP context for logging and error handling
        category: Optional category filter
        limit: Maximum number of posts to return

    Returns:
        List of recent blog posts with metadata
    """
    try:
        logger.info(f'Getting recent posts: category="{category}", limit={limit}')
        
        posts = []
        
        if category and category in AWS_BLOG_CATEGORIES:
            # Get posts from specific category
            rss_url = AWS_BLOG_CATEGORIES[category]['rss']
            category_posts = await _get_posts_from_rss(rss_url, limit)
            posts.extend(category_posts)
        else:
            # Get posts from all categories
            for cat_slug, cat_info in list(AWS_BLOG_CATEGORIES.items())[:5]:  # Limit to 5 categories
                try:
                    rss_url = cat_info['rss']
                    category_posts = await _get_posts_from_rss(rss_url, limit // 5 + 1)
                    posts.extend(category_posts)
                except Exception as e:
                    logger.warning(f'Error getting posts from {cat_slug}: {e}')
                    continue
        
        # Sort by published date and limit results
        posts = sorted(posts, key=lambda x: x.published_date or datetime.min, reverse=True)[:limit]
        
        return posts
        
    except Exception as e:
        logger.error(f'Error getting recent posts: {e}')
        return []


@mcp.tool()
async def get_rss_feed(
    ctx: Context,
    category: str = Field(description='Blog category to get RSS feed for'),
    limit: int = Field(default=20, description='Maximum number of entries to return', ge=1, le=100),
) -> List[BlogPost]:
    """
    Get RSS feed content for a specific blog category.

    ## Usage

    This tool retrieves and parses the RSS feed for a specific AWS blog category,
    providing structured access to recent posts.

    ## Available Categories

    Use `list_blog_categories` to see all available categories.

    Args:
        ctx: MCP context for logging and error handling
        category: Blog category slug (e.g., "machine-learning", "security")
        limit: Maximum number of entries to return

    Returns:
        List of blog posts from the RSS feed
    """
    try:
        if category not in AWS_BLOG_CATEGORIES:
            raise ValueError(f'Unknown category: {category}. Use list_blog_categories to see available options.')
        
        logger.info(f'Getting RSS feed for category: {category}')
        
        rss_url = AWS_BLOG_CATEGORIES[category]['rss']
        posts = await _get_posts_from_rss(rss_url, limit)
        
        return posts
        
    except Exception as e:
        logger.error(f'Error getting RSS feed for {category}: {e}')
        return []


# Helper functions

async def _search_rss_feed(rss_url: str, query: str, limit: int) -> List[SearchResult]:
    """Search within an RSS feed for matching posts."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
            
        feed = feedparser.parse(response.text)
        results = []
        query_lower = query.lower()
        
        for entry in feed.entries[:limit * 2]:  # Get more entries to search through
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
                    published_date=published_date.isoformat() if published_date else None,
                    relevance_score=relevance_score
                )
                results.append(result)
        
        return results[:limit]
        
    except Exception as e:
        logger.error(f'Error searching RSS feed {rss_url}: {e}')
        return []


async def _get_posts_from_rss(rss_url: str, limit: int) -> List[BlogPost]:
    """Get posts from an RSS feed."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(rss_url, timeout=30.0)
            response.raise_for_status()
            
        feed = feedparser.parse(response.text)
        posts = []
        
        for entry in feed.entries[:limit]:
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            
            # Extract category from RSS URL
            category = None
            for cat_slug, cat_info in AWS_BLOG_CATEGORIES.items():
                if cat_info['rss'] == rss_url:
                    category = cat_info['name']
                    break
            
            post = BlogPost(
                title=entry.get('title', ''),
                url=entry.get('link', ''),
                summary=entry.get('summary', ''),
                author=entry.get('author', ''),
                published_date=published_date.isoformat() if published_date else None,
                category=category
            )
            posts.append(post)
        
        return posts
        
    except Exception as e:
        logger.error(f'Error getting posts from RSS feed {rss_url}: {e}')
        return []


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == '__main__':
    main()