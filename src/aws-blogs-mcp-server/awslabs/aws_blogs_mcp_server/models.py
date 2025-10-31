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
"""Data models for AWS Blogs MCP Server."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BlogPost(BaseModel):
    """Blog post from AWS blogs."""

    title: str
    url: str
    summary: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


class BlogCategory(BaseModel):
    """Blog category information."""

    name: str
    slug: str
    url: str
    description: Optional[str] = None
    rss_url: Optional[str] = None


class SearchResult(BaseModel):
    """Search result from AWS blogs search."""

    title: str
    url: str
    summary: Optional[str] = None
    published_date: Optional[datetime] = None
    category: Optional[str] = None
    relevance_score: Optional[float] = None