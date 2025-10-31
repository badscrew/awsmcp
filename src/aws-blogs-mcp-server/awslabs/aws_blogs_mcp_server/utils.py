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
"""Utility functions for AWS Blogs MCP Server."""

import re
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from loguru import logger
from typing import Optional
from datetime import datetime


DEFAULT_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)

# Known AWS blog categories and their RSS feeds
AWS_BLOG_CATEGORIES = {
    'aws': {
        'name': 'AWS News Blog',
        'url': 'https://aws.amazon.com/blogs/aws/',
        'rss': 'https://aws.amazon.com/blogs/aws/feed/',
    },
    'architecture': {
        'name': 'AWS Architecture Blog',
        'url': 'https://aws.amazon.com/blogs/architecture/',
        'rss': 'https://aws.amazon.com/blogs/architecture/feed/',
    },
    'compute': {
        'name': 'AWS Compute Blog',
        'url': 'https://aws.amazon.com/blogs/compute/',
        'rss': 'https://aws.amazon.com/blogs/compute/feed/',
    },
    'containers': {
        'name': 'Containers',
        'url': 'https://aws.amazon.com/blogs/containers/',
        'rss': 'https://aws.amazon.com/blogs/containers/feed/',
    },
    'database': {
        'name': 'Database',
        'url': 'https://aws.amazon.com/blogs/database/',
        'rss': 'https://aws.amazon.com/blogs/database/feed/',
    },
    'developer': {
        'name': 'AWS Developer Tools Blog',
        'url': 'https://aws.amazon.com/blogs/developer/',
        'rss': 'https://aws.amazon.com/blogs/developer/feed/',
    },
    'devops': {
        'name': 'AWS DevOps Blog',
        'url': 'https://aws.amazon.com/blogs/devops/',
        'rss': 'https://aws.amazon.com/blogs/devops/feed/',
    },
    'machine-learning': {
        'name': 'AWS Machine Learning Blog',
        'url': 'https://aws.amazon.com/blogs/machine-learning/',
        'rss': 'https://aws.amazon.com/blogs/machine-learning/feed/',
    },
    'networking-and-content-delivery': {
        'name': 'Networking & Content Delivery',
        'url': 'https://aws.amazon.com/blogs/networking-and-content-delivery/',
        'rss': 'https://aws.amazon.com/blogs/networking-and-content-delivery/feed/',
    },
    'security': {
        'name': 'AWS Security Blog',
        'url': 'https://aws.amazon.com/blogs/security/',
        'rss': 'https://aws.amazon.com/blogs/security/feed/',
    },
    'storage': {
        'name': 'AWS Storage Blog',
        'url': 'https://aws.amazon.com/blogs/storage/',
        'rss': 'https://aws.amazon.com/blogs/storage/feed/',
    },
}


def clean_html_content(html_content: str) -> str:
    """Clean and convert HTML content to markdown."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer']):
            script.decompose()
        
        # Find the main content area
        main_content = None
        
        # Try different selectors for blog post content
        content_selectors = [
            'article',
            '.post-content',
            '.entry-content', 
            '.blog-post-content',
            'main',
            '#main-content'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup
        
        # Convert to markdown
        markdown_content = md(str(main_content), heading_style='ATX')
        
        # Clean up the markdown
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        markdown_content = re.sub(r'^\s+', '', markdown_content, flags=re.MULTILINE)
        
        return markdown_content.strip()
        
    except Exception as e:
        logger.error(f'Error cleaning HTML content: {e}')
        return html_content


def extract_blog_metadata(soup: BeautifulSoup, url: str) -> dict:
    """Extract metadata from a blog post."""
    metadata = {'url': url}
    
    try:
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            metadata['title'] = title_elem.get_text().strip()
        
        # Extract author
        author_selectors = [
            '.author',
            '.post-author', 
            '.entry-author',
            '[rel="author"]',
            '.byline'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                metadata['author'] = author_elem.get_text().strip()
                break
        
        # Extract published date
        date_selectors = [
            'time[datetime]',
            '.published',
            '.post-date',
            '.entry-date'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text().strip()
                try:
                    # Try to parse the date
                    metadata['published_date'] = parse_date_string(date_str)
                    break
                except:
                    continue
        
        # Extract category from URL or content
        if '/blogs/' in url:
            url_parts = url.split('/blogs/')
            if len(url_parts) > 1:
                category_part = url_parts[1].split('/')[0]
                if category_part in AWS_BLOG_CATEGORIES:
                    metadata['category'] = AWS_BLOG_CATEGORIES[category_part]['name']
        
    except Exception as e:
        logger.error(f'Error extracting metadata: {e}')
    
    return metadata


def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse various date string formats."""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None


async def fetch_url_content(url: str, user_agent: str = DEFAULT_USER_AGENT) -> str:
    """Fetch content from a URL."""
    try:
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': user_agent}
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.error(f'Error fetching URL {url}: {e}')
        raise