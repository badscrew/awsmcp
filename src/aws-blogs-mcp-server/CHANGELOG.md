# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-31

### Added
- Initial release of AWS Blogs MCP Server
- `read_blog_post` tool for fetching and converting blog posts to markdown
- `search_blog_posts` tool for searching across AWS blog posts
- `list_blog_categories` tool for getting available blog categories
- `get_recent_posts` tool for retrieving recent posts from categories
- `get_rss_feed` tool for accessing RSS feeds
- Support for major AWS blog categories (AWS News, Machine Learning, Security, etc.)
- Pagination support for long blog posts
- Metadata extraction (title, author, date, category)
- RSS feed parsing and search functionality