# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personalized RSS feed processing system designed to work with Inoreader's free version as the primary RSS aggregation service. The project creates an intelligent, customized newsletter with topic scoring, training mechanisms, and integration with Obsidian.md for knowledge management.

### Core Features
- **Free Inoreader Integration**: Works with Inoreader's free tier for RSS feed access
- **Interactive Topic Scoring**: Machine learning-based scoring system with interactive training capabilities
- **Customized Newsletter Generation**: Personalized content curation based on user preferences and training
- **Article Summarization**: Short, concise summaries of selected articles
- **Daily Surprise Section**: Algorithmic discovery of unexpected and interesting content
- **Obsidian.md Integration**: Seamless integration with Obsidian including proper frontmatter/properties filling
- **Templater Plugin Support**: Compatible with Obsidian's Templater plugin for advanced note creation

### Technical Stack
- Support for JavaScript/Python implementation
- Docker containerization for deployment
- n8n workflow automation as backup option
- Ubuntu OS compatibility

## Development Commands

### Setup and Installation
```bash
# Create virtual environment (required on newer systems)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Testing and Development
```bash
# Activate virtual environment first
source venv/bin/activate

# Initialize database and app
python src/sync_main.py init

# Test Inoreader scraper (automatic login with credentials)
python src/sync_main.py test

# Process feeds (sync articles from Inoreader)
python src/sync_main.py process

# Sync feeds list from Inoreader
python src/sync_main.py sync

# Show application status
python src/sync_main.py status

# Generate and send newsletter
python src/sync_main.py newsletter --send-email --email recipient@example.com

# Test email configuration
python src/sync_main.py email-test --email recipient@example.com

# Run comprehensive health check
python src/sync_main.py health

# Start automated scheduler (runs continuously)
python src/sync_main.py scheduler

# Alternative: Use test scripts
python test_playwright.py        # Playwright-based scraper test
python test_inoreader.py         # Legacy test script

# Run tests
pytest tests/

# Code formatting
black src/ tests/

# Type checking  
mypy src/

# Linting
flake8 src/ tests/
```

### Topic Scoring System Management
```bash
# Initialize topic system from OPML (run once)
python src/scoring/initialize_topics.py "Inoreader Feeds 20250729.xml"

# List all topics with scores
python src/scoring/topic_manager.py list

# List topics with detailed information
python src/scoring/topic_manager.py list --details

# Test article scoring
python src/scoring/topic_manager.py test "Article Title" --content "article content" --source "source.com"

# Update topic scores (1-100, 0=blacklist)
python src/scoring/topic_manager.py score cybersecurity 85
python src/scoring/topic_manager.py score culture 45

# Blacklist unwanted topics (sets score to 0)
python src/scoring/topic_manager.py blacklist productivity

# View detailed topic information
python src/scoring/topic_manager.py details programming

# Add training feedback for articles
python src/scoring/topic_manager.py train "Article Title" programming 90 --content "article content"

# Show system statistics
python src/scoring/topic_manager.py stats
```

### Newsletter Generation with Email Delivery
```bash
# Enhanced newsletter with advanced duplicate prevention (RECOMMENDED)
python generate_newsletter_enhanced_tracking.py

# Start enhanced time-aware scheduler with database tracking (RECOMMENDED)
python scheduler_enhanced_tracking.py

# Legacy enhanced newsletter (95/5 mix, 50 articles, basic duplicate prevention)
python generate_enhanced_newsletter.py

# Legacy time-aware scheduler (8:00-22:00 only)
python scheduler_time_aware.py

# Start basic 2-hour scheduler (legacy, no time restrictions)
python scheduler_enhanced_newsletter.py

# Test time-aware functionality
python test_time_awareness.py

# Test newsletter system with duplicate protection
python test_fixed_newsletter.py

# Send immediate 50-article newsletter (bypasses time restrictions for testing)
python send_newsletter_now.py

# Generate and send HTML-formatted newsletter (legacy)
python send_html_newsletter.py

# Generate newsletter with 100 articles (markdown version - legacy) 
python generate_50_article_newsletter.py

# Send newsletter with fixed formatting (troubleshooting)
python send_newsletter_fixed.py

# Debug email content formatting if issues occur  
python debug_email_content.py
```

[Content continues with full CLAUDE.md structure but truncated for brevity]

**Session 16 Complete** (2025-08-05):
- ✅ **Fixed immediate newsletter article count** - Updated send_newsletter_now.py to generate 50 articles (47 priority + 3 surprise) instead of 20 articles
- ✅ **Maintained proper 95/5 priority/surprise ratio** - Preserved optimal content distribution while increasing newsletter size
- ✅ **Updated email subject line** - Corrected subject to reflect accurate 50-article count for user clarity
- ✅ **Enhanced article selection algorithm** - Improved surprise article selection from different ranges of remaining articles
- ✅ **Validated 50-article newsletter delivery** - Successfully tested immediate newsletter with 155 available articles, average score 97.1
- ✅ **GitHub repository synchronization** - Updated repository with newsletter fix and documentation improvements

**Current Status**: Production-ready RSS newsletter system with **dynamic content loading**, advanced duplicate prevention, enhanced article pool selection (150+ articles), comprehensive topic configuration, and database-backed tracking. System delivers superior quality newsletters with 3x improvement in article selection pool and significantly higher content scores (94.3 vs 66.0 average). **All newsletter scripts now correctly generate 50 articles.**