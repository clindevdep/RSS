#!/usr/bin/env python3
"""
Generate newsletter with 50 most important articles and send to nofchi@gmail.com
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

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

async def main():
    """Generate newsletter with 50 top articles and send to nofchi@gmail.com"""
    
    try:
        from data_ingestion.playwright_scraper import PlaywrightInoreaderScraper
        from scoring.topic_scorer import TopicScorer
        from email_service.email_sender import EmailSender
        
        logger.info("🚀 Starting 50-article newsletter generation for nofchi@gmail.com...")
        
        # Step 1: Scrape articles from Inoreader
        logger.info("📰 Fetching articles from Inoreader...")
        scraper = PlaywrightInoreaderScraper()
        
        if not await scraper.ensure_logged_in():
            logger.error("❌ Failed to login to Inoreader")
            return
        
        # Get many articles for better selection (aim for 100+)
        articles = await scraper.get_article_list(limit=150)
        await scraper.close()
        
        if not articles:
            logger.error("❌ No articles found")
            return
        
        logger.info(f"✅ Retrieved {len(articles)} articles from Inoreader")
        
        # Step 2: Score articles using personalized topic system
        logger.info("🎯 Scoring articles with 100-topic personalized system...")
        topic_scorer = TopicScorer()
        
        scored_articles = []
        for article in articles:
            try:
                # Create comprehensive content for scoring
                title = article.get('title', '')
                summary = article.get('summary', '')
                source = article.get('feed_name', '')
                url = article.get('url', '')
                
                # Score the article
                scores_dict = topic_scorer.score_article(
                    title=title,
                    content=f"{title} {summary}",
                    source=source
                )
                
                # Get the maximum score across all topics as the overall score
                score = max(scores_dict.values()) if scores_dict else 0.0
                
                # Get top 3 topics from scores dict
                topics = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)[:3]
                topics = [topic[0] for topic in topics if topic[1] > 0]
                
                scored_articles.append({
                    'title': title,
                    'url': url,
                    'feed_name': source,
                    'summary': summary,
                    'date': article.get('date', datetime.now().isoformat()),
                    'score': score,
                    'topics': topics[:5],  # Top 5 matching topics
                    'read_time': max(1, len(summary.split()) // 200) if summary else 1
                })
                
            except Exception as e:
                logger.warning(f"Failed to score article '{article.get('title', 'Unknown')}': {e}")
                continue
        
        if not scored_articles:
            logger.error("❌ No articles could be scored")
            return
        
        logger.info(f"📊 Successfully scored {len(scored_articles)} articles")
        
        # Step 3: Sort by score and select top 50
        scored_articles.sort(key=lambda x: x['score'], reverse=True)
        top_50_articles = scored_articles[:50]
        
        logger.info(f"📈 Selected top 50 articles")
        logger.info(f"📊 Score range: {top_50_articles[0]['score']:.1f} (highest) to {top_50_articles[-1]['score']:.1f} (lowest)")
        avg_score = sum(a['score'] for a in top_50_articles) / len(top_50_articles)
        logger.info(f"📈 Average relevance score: {avg_score:.1f}")
        
        # Step 4: Create newsletter content
        logger.info("📝 Generating newsletter content...")
        
        # Create newsletter header
        today = datetime.now()
        newsletter_content = f"""# Daily RSS Digest - {today.strftime('%B %d, %Y')}
*Generated on {today.strftime('%B %d, %Y at %H:%M')} with your personalized 100-topic scoring system*
*📊 {len(top_50_articles)} articles selected from {len(articles)} sources*

---

## 🔥 Top Priority Articles (Score ≥ 70)

"""
        
        high_priority = [a for a in top_50_articles if a['score'] >= 70]
        medium_priority = [a for a in top_50_articles if 50 <= a['score'] < 70]
        daily_surprise = [a for a in top_50_articles if a['score'] < 50]
        
        logger.info(f"📊 Article distribution: {len(high_priority)} high priority, {len(medium_priority)} medium priority, {len(daily_surprise)} daily surprise")
        
        # Add high priority articles
        for i, article in enumerate(high_priority, 1):
            topics_str = ' '.join([f"#{topic}" for topic in article['topics'][:3]])
            newsletter_content += f"""### {i}. [{article['title']}]({article['url']})
**Source:** {article['feed_name']} | **Score:** {article['score']:.1f}/100 | **Read time:** ~{article['read_time']} min

{article['summary'][:200]}{"..." if len(article['summary']) > 200 else ""}

**Topics:** {topics_str}

---

"""
        
        # Add medium priority section
        if medium_priority:
            newsletter_content += """## ⭐ Medium Priority Articles (Score 50-69)

"""
            for i, article in enumerate(medium_priority, 1):
                topics_str = ' '.join([f"#{topic}" for topic in article['topics'][:3]])
                newsletter_content += f"""### {i}. [{article['title']}]({article['url']})
**Source:** {article['feed_name']} | **Score:** {article['score']:.1f}/100

{article['summary'][:150]}{"..." if len(article['summary']) > 150 else ""}

**Topics:** {topics_str}

---

"""
        
        # Add daily surprise section
        if daily_surprise:
            newsletter_content += """## 🎯 Daily Surprise Articles (Hidden Gems)

"""
            for i, article in enumerate(daily_surprise, 1):
                topics_str = ' '.join([f"#{topic}" for topic in article['topics'][:3]])
                newsletter_content += f"""### {i}. [{article['title']}]({article['url']})
**Source:** {article['feed_name']} | **Score:** {article['score']:.1f}/100

{article['summary'][:150]}{"..." if len(article['summary']) > 150 else ""}

**Topics:** {topics_str}

---

"""
        
        # Add footer
        newsletter_content += f"""

---

*🤖 Newsletter generated by RSS Processing System with 100-topic personalized scoring*
*📊 Your top interests: AI/ML ({len([a for a in top_50_articles if any(t in ['artificial_intelligence', 'machine_learning'] for t in a['topics'])])} articles), European Politics, Cybersecurity, Science & Research*
*📈 Articles curated from your Inoreader subscriptions based on personal preferences*
*⚡ Processing completed in real-time from {len(articles)} source articles*

"""
        
        # Step 5: Save newsletter locally
        output_dir = Path("output/newsletters")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"newsletter_50_articles_{today.strftime('%Y%m%d_%H%M%S')}.md"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(newsletter_content)
        
        logger.info(f"💾 Newsletter saved to: {output_path}")
        logger.info(f"📄 Newsletter length: {len(newsletter_content)} characters")
        
        # Step 6: Send via email
        logger.info("📧 Sending newsletter to nofchi@gmail.com...")
        
        # Import the working HTML functions
        sys.path.insert(0, os.path.dirname(__file__))
        from send_html_newsletter import markdown_to_html
        from email_service.email_sender import EmailSender, EmailMessage
        import re
        
        subject = f"Daily RSS Digest - {today.strftime('%B %d, %Y')} ({len(top_50_articles)} articles, avg score {avg_score:.1f})"
        
        # Convert to HTML
        html_content = markdown_to_html(newsletter_content)
        text_content = re.sub(r'<[^>]+>', '', html_content)  # Strip HTML tags
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)  # Clean up spacing
        
        # Create email sender and message
        sender = EmailSender()
        message = EmailMessage(
            to_emails=["nofchi@gmail.com"],
            subject=subject,
            text_content=text_content,
            html_content=html_content
        )
        
        success = sender.send_email(message)
        
        if success:
            logger.info("✅ Newsletter sent successfully to nofchi@gmail.com!")
            logger.info(f"📧 Subject: {subject}")
            logger.info(f"📊 Total articles: {len(top_50_articles)}")
            logger.info(f"📈 Average score: {avg_score:.1f}")
            logger.info(f"🔥 High priority articles: {len(high_priority)}")
            logger.info(f"⭐ Medium priority articles: {len(medium_priority)}")
            logger.info(f"🎯 Daily surprise articles: {len(daily_surprise)}")
        else:
            logger.error("❌ Failed to send newsletter")
        
        logger.info("🎉 Newsletter generation and delivery complete!")
        return success
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("✅ 50-article newsletter generated and sent to nofchi@gmail.com!")
    else:
        print("❌ Newsletter generation/sending failed")