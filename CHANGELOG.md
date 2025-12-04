# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-03

### Added
- Initial release of MMM-LunchMenu module
- Docker-based scraper service for fetching menu data
- Configurable environment variables for customization
- Weekend fallback feature (shows Monday's menu on weekends)
- Automatic daily scraping on schedule
- Beautiful HTML output styled for MagicMirror²
- Comprehensive README with customization guide
- Example Docker Compose configuration

### Features
- Lightweight HTTP-based scraping (no browser automation required)
- Configurable regex patterns for different website structures
- Timezone-aware date handling
- Automatic retry logic for failed scrapes
- Clean, readable menu display

