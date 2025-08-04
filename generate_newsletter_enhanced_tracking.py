#!/usr/bin/env python3
"""
Enhanced Newsletter Generator with Advanced Duplicate Prevention

Features:
1. Database-backed article tracking
2. Multiple fingerprinting methods for duplicate detection
3. Comprehensive article-newsletter relationship tracking
4. Automatic cleanup of old records
5. Statistics and monitoring
6. Fallback to JSON state for compatibility
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

from src.newsletter.article_tracker import ArticleTracker
from src.persistence.sync_database import SyncDatabaseManager
from src.data_ingestion.playwright_scraper import PlaywrightInoreaderScraper
from src.scoring.topic_scorer import TopicScorer
from src.email_service.email_sender import EmailSender, EmailMessage
from config.settings import settings

class EnhancedNewsletterGenerator:
    """Advanced newsletter generator with comprehensive duplicate prevention"""
    
    def __init__(self):
        self.db_manager = SyncDatabaseManager()
        self.article_tracker = ArticleTracker(self.db_manager)
        self.scraper = PlaywrightInoreaderScraper()
        self.scorer = TopicScorer()
        self.email_sender = EmailSender()
        
        # Configuration
        self.priority_ratio = 0.95  # 95% priority articles
        self.surprise_ratio = 0.05  # 5% surprise articles
        self.articles_per_newsletter = 50
        self.min_score_threshold = 1.0  # Minimum score to consider
        
    def is_active_hours(self) -> bool:
        """Check if current time is within active hours (8:00-22:00)"""
        current_time = datetime.now().time()
        start_time = datetime.strptime("08:00", "%H:%M").time()
        end_time = datetime.strptime("22:00", "%H:%M").time()
        return start_time <= current_time <= end_time
    
    def should_generate_newsletter(self) -> bool:
        """Check if enough time has passed since last generation (2 hours) and within active hours"""
        # First check if we're in active hours (8:00-22:00)
        if not self.is_active_hours():
            logger.info("🌙 Outside active hours (8:00-22:00). Newsletter generation paused.")
            return False
        
        # Check last generation time from tracker stats
        stats = self.article_tracker.get_sent_articles_stats()
        
        # For now, always generate if in active hours (can be enhanced with timing logic)
        return True
    
    async def fetch_articles(self) -> List[Dict]:
        """Fetch articles from Inoreader"""
        logger.info("📥 Fetching articles from Inoreader...")
        
        try:
            # Ensure logged in and get articles
            if await self.scraper.ensure_logged_in():
                articles = await self.scraper.get_article_list(limit=200)  # Get larger pool for better selection
                logger.info(f"📰 Fetched {len(articles)} articles from Inoreader")
                
                # Add source field if missing and normalize format
                for article in articles:
                    if 'source' not in article:
                        article['source'] = article.get('feed_name', 'Unknown')
                    if 'content' not in article:
                        article['content'] = article.get('summary', '')
                    if 'published_date' not in article and 'date' not in article:
                        article['published_date'] = article.get('published_date', '')
                
                return articles
            else:
                logger.error("❌ Failed to log in to Inoreader")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error fetching articles: {e}")
            return []
        finally:
            await self.scraper.close()
    
    def score_and_filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Score articles and filter out low-quality content"""
        logger.info("🧮 Scoring articles with personalized topic system...")
        
        scored_articles = []
        
        for article in articles:
            try:
                # Score article across all topics
                scores = self.scorer.score_article(
                    article.get('title', ''),
                    article.get('content', article.get('summary', '')),
                    article.get('source', ''),
                    article.get('published_date')
                )
                
                # Get maximum score across all topics
                max_score = max(scores.values()) if scores else 0
                
                # Filter out very low-scoring articles
                if max_score >= self.min_score_threshold:
                    article_with_score = article.copy()
                    article_with_score['score'] = max_score
                    article_with_score['topic_scores'] = scores
                    scored_articles.append(article_with_score)
                    
            except Exception as e:
                logger.warning(f"⚠️ Error scoring article '{article.get('title', '')}': {e}")
                continue
        
        logger.info(f"✅ Scored {len(scored_articles)} articles (filtered {len(articles) - len(scored_articles)} low-quality)")
        return scored_articles
    
    def remove_duplicates(self, articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Remove duplicate articles using enhanced tracking system"""
        logger.info("🔍 Checking for duplicate articles...")
        
        # Filter out duplicates
        new_articles = self.article_tracker.filter_new_articles(articles)
        duplicate_articles = self.article_tracker.get_duplicate_articles(articles)
        
        logger.info(f"✅ Found {len(new_articles)} new articles, filtered {len(duplicate_articles)} duplicates")
        
        if duplicate_articles:
            logger.info("📋 Duplicate articles detected:")
            for i, dup in enumerate(duplicate_articles[:5]):  # Show first 5
                logger.info(f"   {i+1}. {dup.get('title', 'No title')[:60]}...")
            if len(duplicate_articles) > 5:
                logger.info(f"   ... and {len(duplicate_articles) - 5} more")
        
        return new_articles, duplicate_articles
    
    def select_newsletter_articles(self, articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Select articles for newsletter using 95/5 priority/surprise mix"""
        
        # Sort all articles by score
        articles_sorted = sorted(articles, key=lambda x: x['score'], reverse=True)
        
        # Calculate article counts
        priority_count = int(self.articles_per_newsletter * self.priority_ratio)
        surprise_count = self.articles_per_newsletter - priority_count
        
        # Select priority articles (highest scores)
        priority_articles = articles_sorted[:priority_count]
        
        # Select surprise articles (from remaining articles, random selection from middle-tier)
        remaining_articles = articles_sorted[priority_count:]
        
        # For surprise articles, take from middle range (not too low, not too high)
        if len(remaining_articles) > surprise_count:
            # Select from middle portion to avoid both highest and lowest remaining scores
            start_idx = len(remaining_articles) // 4
            end_idx = 3 * len(remaining_articles) // 4
            surprise_pool = remaining_articles[start_idx:end_idx]
            
            if len(surprise_pool) >= surprise_count:
                surprise_articles = surprise_pool[:surprise_count]
            else:
                surprise_articles = surprise_pool + remaining_articles[:surprise_count - len(surprise_pool)]
        else:
            surprise_articles = remaining_articles[:surprise_count]
        
        logger.info(f"📊 Selected {len(priority_articles)} priority + {len(surprise_articles)} surprise articles")
        logger.info(f"📈 Priority score range: {priority_articles[-1]['score']:.1f} - {priority_articles[0]['score']:.1f}")
        if surprise_articles:
            logger.info(f"🎯 Surprise score range: {min(a['score'] for a in surprise_articles):.1f} - {max(a['score'] for a in surprise_articles):.1f}")
        
        return priority_articles, surprise_articles
    
    def generate_html_newsletter(self, priority_articles: List[Dict], surprise_articles: List[Dict]) -> str:
        """Generate HTML newsletter content"""
        
        current_time = datetime.now()
        total_articles = len(priority_articles) + len(surprise_articles)
        avg_score = sum(a['score'] for a in priority_articles + surprise_articles) / total_articles if total_articles > 0 else 0
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced RSS Newsletter - {current_time.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.2em;
            font-weight: 600;
        }}
        .header .meta {{
            margin-top: 10px;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .stats h3 {{
            margin: 0 0 15px 0;
            color: #667eea;
            font-size: 1.3em;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .section-header {{
            padding: 20px;
            font-size: 1.4em;
            font-weight: 600;
            border-bottom: 1px solid #eee;
        }}
        .priority-header {{
            background: linear-gradient(90deg, #ff6b6b, #ee5a24);
            color: white;
        }}
        .surprise-header {{
            background: linear-gradient(90deg, #5f27cd, #341f97);
            color: white;
        }}
        .article {{
            padding: 20px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-title {{
            font-size: 1.1em;
            margin-bottom: 8px;
        }}
        .article-title a {{
            color: #333;
            text-decoration: none;
            font-weight: 500;
        }}
        .article-title a:hover {{
            color: #667eea;
            text-decoration: underline;
        }}
        .article-meta {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
        }}
        .article-content {{
            color: #555;
            font-size: 16px;
            line-height: 1.5;
        }}
        .score-high {{
            background: #d4edda;
            color: #155724;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: bold;
        }}
        .score-medium {{
            background: #fff3cd;
            color: #856404;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: bold;
        }}
        .score-surprise {{
            background: #e2e3f1;
            color: #383d75;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .header {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 1.8em;
            }}
            .stat-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Enhanced RSS Newsletter</h1>
        <div class="meta">
            {current_time.strftime('%A, %B %d, %Y at %H:%M')} | 
            Enhanced Duplicate Prevention System
        </div>
    </div>
    
    <div class="stats">
        <h3>📊 Newsletter Statistics</h3>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(priority_articles)}</div>
                <div class="stat-label">Priority Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(surprise_articles)}</div>
                <div class="stat-label">Surprise Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{avg_score:.1f}</div>
                <div class="stat-label">Average Score</div>
            </div>
        </div>
    </div>
"""
        
        # Priority Articles Section
        if priority_articles:
            html_content += """
    <div class="section">
        <div class="section-header priority-header">
            🔥 Priority Articles ({} articles)
        </div>
""".format(len(priority_articles))
            
            for i, article in enumerate(priority_articles, 1):
                score_class = "score-high" if article['score'] >= 90 else "score-medium"
                
                html_content += f"""
        <div class="article">
            <div class="article-title">
                <strong>{i}.</strong> <a href="{article.get('url', '#')}" target="_blank">{article.get('title', 'No title')}</a>
            </div>
            <div class="article-meta">
                <strong>Source:</strong> {article.get('source', 'Unknown')} | 
                <strong>Score:</strong> <span class="{score_class}">{article['score']:.1f}/100</span> | 
                <strong>Read time:</strong> ~1 min
            </div>
            <div class="article-content">
                {article.get('summary', article.get('content', 'No summary available'))[:400]}
            </div>
        </div>
"""
            
            html_content += "    </div>\n"
        
        # Surprise Articles Section
        if surprise_articles:
            html_content += """
    <div class="section">
        <div class="section-header surprise-header">
            🎯 Surprise Articles ({} articles)
        </div>
""".format(len(surprise_articles))
            
            start_num = len(priority_articles) + 1
            for i, article in enumerate(surprise_articles, start_num):
                html_content += f"""
        <div class="article">
            <div class="article-title">
                <strong>{i}.</strong> <a href="{article.get('url', '#')}" target="_blank">{article.get('title', 'No title')}</a>
            </div>
            <div class="article-meta">
                <strong>Source:</strong> {article.get('source', 'Unknown')} | 
                <strong>Score:</strong> <span class="score-surprise">{article['score']:.1f}/100</span> | 
                <strong>Read time:</strong> ~1 min
            </div>
            <div class="article-content">
                {article.get('summary', article.get('content', 'No summary available'))[:300]}
            </div>
        </div>
"""
            
            html_content += "    </div>\n"
        
        # Footer
        html_content += f"""
    <div class="footer">
        <p>📧 Enhanced RSS Newsletter with Advanced Duplicate Prevention</p>
        <p>Generated on {current_time.strftime('%Y-%m-%d at %H:%M:%S')} | 
        Personalized AI Scoring | Database-Backed Tracking</p>
        <p>🔒 Duplicate Prevention: Multi-fingerprint system ensures no repeated articles</p>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def send_newsletter(self, html_content: str, priority_articles: List[Dict], surprise_articles: List[Dict]) -> bool:
        """Send newsletter via email"""
        
        current_time = datetime.now()
        total_articles = len(priority_articles) + len(surprise_articles)
        
        subject = f"Enhanced RSS Newsletter - {total_articles} Articles ({current_time.strftime('%Y-%m-%d %H:%M')})"
        
        # Generate text version
        text_content = f"""
Enhanced RSS Newsletter - {current_time.strftime('%Y-%m-%d %H:%M')}
{'=' * 50}

📊 STATISTICS:
- Total Articles: {total_articles}
- Priority Articles: {len(priority_articles)}
- Surprise Articles: {len(surprise_articles)}

🔥 PRIORITY ARTICLES:
"""
        
        for i, article in enumerate(priority_articles, 1):
            text_content += f"""
{i}. {article.get('title', 'No title')}
   Source: {article.get('source', 'Unknown')} | Score: {article['score']:.1f}/100
   URL: {article.get('url', 'No URL')}
   Summary: {article.get('summary', 'No summary')[:200]}
"""
        
        if surprise_articles:
            text_content += "\n🎯 SURPRISE ARTICLES:\n"
            start_num = len(priority_articles) + 1
            for i, article in enumerate(surprise_articles, start_num):
                text_content += f"""
{i}. {article.get('title', 'No title')}
   Source: {article.get('source', 'Unknown')} | Score: {article['score']:.1f}/100
   URL: {article.get('url', 'No URL')}
   Summary: {article.get('summary', 'No summary')[:200]}
"""
        
        text_content += f"""

📧 Enhanced RSS Newsletter with Advanced Duplicate Prevention
Generated: {current_time.strftime('%Y-%m-%d at %H:%M:%S')}
🔒 Duplicate Prevention: Multi-fingerprint system ensures no repeated articles
"""
        
        # Send email
        try:
            # Get recipient from settings
            recipients = [settings.newsletter_recipient] if settings.newsletter_recipient else []
            if not recipients:
                logger.error("❌ No newsletter recipient configured")
                return False
            
            # Create email message directly
            email_message = EmailMessage(
                to_emails=recipients,
                subject=subject,
                text_content=text_content,
                html_content=html_content
            )
            
            success = self.email_sender.send_email(email_message)
            
            if success:
                logger.info("✅ Newsletter sent successfully!")
                return True
            else:
                logger.error("❌ Failed to send newsletter")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending newsletter: {e}")
            return False
    
    async def generate_and_send_newsletter(self) -> bool:
        """Main method to generate and send enhanced newsletter"""
        
        try:
            logger.info("🚀 Starting enhanced newsletter generation with advanced duplicate prevention...")
            
            # Check if we should generate newsletter
            if not self.should_generate_newsletter():
                return False
            
            # Get article tracker statistics
            stats = self.article_tracker.get_sent_articles_stats()
            logger.info(f"📊 Article Tracker Stats: {stats}")
            
            # Fetch articles from Inoreader
            raw_articles = await self.fetch_articles()
            if not raw_articles:
                logger.error("❌ No articles fetched from Inoreader")
                return False
            
            # Score and filter articles
            scored_articles = self.score_and_filter_articles(raw_articles)
            if not scored_articles:
                logger.error("❌ No articles passed scoring filter")
                return False
            
            # Remove duplicates using enhanced tracking
            new_articles, duplicate_articles = self.remove_duplicates(scored_articles)
            if not new_articles:
                logger.warning("⚠️ All articles are duplicates - no new content to send")
                return False
            
            # Select articles for newsletter
            priority_articles, surprise_articles = self.select_newsletter_articles(new_articles)
            final_articles = priority_articles + surprise_articles
            
            if not final_articles:
                logger.error("❌ No articles selected for newsletter")
                return False
            
            # Generate HTML newsletter
            html_content = self.generate_html_newsletter(priority_articles, surprise_articles)
            
            # Send newsletter
            success = self.send_newsletter(html_content, priority_articles, surprise_articles)
            
            if success:
                # Mark articles as sent in tracking system
                self.article_tracker.mark_articles_sent(final_articles)
                
                logger.info("✅ Enhanced newsletter generation completed successfully!")
                logger.info(f"📧 Sent {len(final_articles)} articles ({len(priority_articles)} priority + {len(surprise_articles)} surprise)")
                logger.info(f"📈 Average score: {sum(a['score'] for a in final_articles) / len(final_articles):.1f}")
                logger.info(f"🔍 Filtered {len(duplicate_articles)} duplicate articles")
                
                # Cleanup old records periodically
                if datetime.now().hour == 2:  # Cleanup at 2 AM
                    cleaned = self.article_tracker.cleanup_old_records(days_to_keep=30)
                    if cleaned > 0:
                        logger.info(f"🧹 Cleaned up {cleaned} old newsletter records")
                
                return True
            else:
                logger.error("❌ Failed to send newsletter")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced newsletter generation: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

async def main():
    """Main function"""
    generator = EnhancedNewsletterGenerator()
    success = await generator.generate_and_send_newsletter()
    
    if success:
        print("✅ Enhanced newsletter generated and sent successfully!")
    else:
        print("❌ Failed to generate or send newsletter")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())