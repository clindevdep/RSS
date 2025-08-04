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
- **Advanced Duplicate Prevention**: Zero-duplicate newsletter delivery with database-backed article tracking

### Technical Stack
- Support for JavaScript/Python implementation
- Docker containerization for deployment
- n8n workflow automation as backup option
- Ubuntu OS compatibility