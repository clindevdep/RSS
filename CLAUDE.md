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

*Commands will be added here once build scripts and package management files are created.*

## Architecture

### System Overview
The RSS processing system follows a modular, event-driven architecture designed for scalability and maintainability. The system processes RSS feeds from Inoreader, applies ML-based scoring, generates personalized content, and integrates seamlessly with Obsidian.md.

### Core Components

#### 1. Data Ingestion Layer
- **Inoreader API Client**: Interfaces with Inoreader's free tier API
- **Feed Processor**: Parses and normalizes RSS content
- **Rate Limiter**: Manages API call frequency within free tier limits

#### 2. Content Processing Engine
- **Article Parser**: Extracts and cleans article content
- **Metadata Extractor**: Identifies topics, categories, and key information
- **Content Validator**: Ensures data quality and completeness

#### 3. Intelligence Layer
- **Topic Scoring System**: ML-based relevance scoring with user training feedback
- **Learning Engine**: Adapts to user preferences through interactive training
- **Surprise Discovery**: Algorithm to identify unexpected/interesting content
- **Summarization Engine**: Generates concise article summaries

#### 4. Newsletter Generation
- **Content Curator**: Selects articles based on scores and preferences
- **Template Engine**: Formats content into newsletter structure
- **Daily Surprise Compiler**: Assembles unexpected findings section

#### 5. Obsidian Integration Layer
- **Note Generator**: Creates Obsidian-compatible markdown files
- **Frontmatter Manager**: Populates YAML properties correctly
- **Templater Bridge**: Interfaces with Obsidian's Templater plugin
- **Vault Synchronizer**: Manages file placement and organization

#### 6. Data Persistence
- **User Preferences Store**: Training data and scoring preferences
- **Content Cache**: Processed articles and metadata
- **Training History**: ML model evolution tracking

### Technical Architecture

#### Deployment Options
1. **Docker Containerized**: Multi-container setup with orchestration
2. **Local Installation**: Direct Python/Node.js environment
3. **n8n Workflow**: Visual workflow automation (backup option)

#### Data Flow
```
Inoreader API → Content Processing → ML Scoring → Newsletter Generation → Obsidian Integration
     ↓                ↓                ↓               ↓                    ↓
Rate Limiting → Article Parsing → Training Loop → Template Engine → Note Creation
```

#### Technology Stack
- **Backend**: Python (FastAPI/Flask) for ML/NLP, Node.js for API integrations
- **ML/NLP**: scikit-learn, transformers, spaCy for content analysis
- **Database**: SQLite (development), PostgreSQL (production)
- **Scheduling**: Cron jobs or APScheduler for periodic processing
- **API**: RESTful APIs with authentication and rate limiting

### Integration Points

#### Inoreader Free Tier Considerations
- 1000 API calls per day limit
- No real-time updates (polling-based)
- Limited search functionality
- Subscription list access only

#### Obsidian.md Compatibility
- Markdown file format with YAML frontmatter
- Templater plugin variable support
- Proper file naming and organization
- Link and tag structure preservation

### Scalability Considerations
- Modular design allows independent scaling of components
- Event-driven architecture supports async processing
- Caching strategies to minimize API calls
- Horizontal scaling capability for high-volume processing

## Configuration

The repository includes Claude Code permissions configuration in `.claude/settings.local.json` that allows specific bash commands for file exploration.

### Environment Variables

API keys and sensitive configuration are stored in `~/.env` which is sourced by `~/.zshrc`:
- `TAVILY_API_KEY`: Required for Tavily MCP server (web search capabilities)
- `FIRECRAWL_API_KEY`: Required for Firecrawl MCP server (web scraping and crawling capabilities)
- `GITHUB_PERSONAL_ACCESS_TOKEN`: Required for GitHub MCP server (repository and file operations)
- `INOREADER_APP_ID`: Required for Inoreader API integration (to be added)
- `INOREADER_API_KEY`: Required for Inoreader API authentication (to be added)

**Privacy Notice**: Actual API keys and tokens are stored locally in environment files and are never committed to the repository or shared publicly.

## MCP Servers

- **context7**: Added via `claude mcp add context7 -s user npx @upstash/context7-mcp` - ✅ Connected - Provides up-to-date code documentation and examples directly from source repositories.
- **tavily**: Added with API key configuration in `~/.claude.json` using `npx @mcptools/mcp-tavily` - ✅ Connected - Provides web search capabilities for current information and research.
- **firecrawl**: Added with API key configuration in `~/.claude.json` using `npx firecrawl-mcp` - ✅ Connected - Provides advanced web scraping, crawling, and content extraction with JavaScript rendering support.
- **github**: Added with API key configuration in `~/.claude.json` using `npx @modelcontextprotocol/server-github` - ✅ Connected - Provides GitHub repository operations including file uploads, repository management, issues, pull requests, and workflow management.

## User Rules

- **Keep GitHub records**: Always maintain proper GitHub commit history and branching to enable easy rollback if needed. Create meaningful commits with clear messages to facilitate project recovery and version management.
- **Obsidian.md as PKS**: Obsidian.md is the preferred Personal Knowledge System (PKS) for this project. All integrations and knowledge management features should be designed with Obsidian compatibility as a priority.
- **Clarify assignments through questions**: Often ask questions to make assignments more clear. Use numbered option lists when presenting choices. Ask for free input when needed to better understand requirements.

## Security & Privacy Guidelines

- **NO sensitive information** (API keys, tokens, passwords) should ever be committed to this repository
- All sensitive configuration is stored in local environment files (`~/.env`) 
- Web searches and external API calls should never include private or sensitive data
- Review all code and commits before pushing to ensure no secrets are exposed