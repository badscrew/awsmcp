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
"""Tests for AWS Blogs MCP Server."""

import pytest
from awslabs.aws_blogs_mcp_server.utils import AWS_BLOG_CATEGORIES


def test_blog_categories_structure():
    """Test that blog categories are properly structured."""
    assert len(AWS_BLOG_CATEGORIES) > 0
    
    for slug, info in AWS_BLOG_CATEGORIES.items():
        assert 'name' in info
        assert 'url' in info
        assert 'rss' in info
        assert info['url'].startswith('https://aws.amazon.com/blogs/')
        assert info['rss'].startswith('https://aws.amazon.com/blogs/')
        assert info['rss'].endswith('/feed/')


def test_blog_category_slugs():
    """Test that expected blog categories exist."""
    expected_categories = [
        'aws',
        'machine-learning', 
        'security',
        'compute',
        'architecture'
    ]
    
    for category in expected_categories:
        assert category in AWS_BLOG_CATEGORIES


@pytest.mark.asyncio
async def test_list_blog_categories():
    """Test listing blog categories."""
    from awslabs.aws_blogs_mcp_server.server import list_blog_categories
    from mcp.server.fastmcp import Context
    
    ctx = Context()
    categories = await list_blog_categories(ctx)
    
    assert len(categories) > 0
    assert all(hasattr(cat, 'name') for cat in categories)
    assert all(hasattr(cat, 'slug') for cat in categories)
    assert all(hasattr(cat, 'url') for cat in categories)