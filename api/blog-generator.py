"""
Vercel Serverless Function: Blog Generator
Focuses on blog draft generation and Notion integration
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rss_manager import RSSManager
from scoring_ai import ScoringAI
from quality_filter import QualityFilter
from content_ai import ContentAI
from notion_manager import NotionManager
from sheets_manager import GoogleSheetsManager
from models import ContentItem, ContentStatus
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Main handler for blog generation"""
    try:
        logger.info("Starting blog generation cycle")
        
        # Initialize components
        rss_manager = RSSManager()
        scoring_ai = ScoringAI()
        quality_filter = QualityFilter()
        content_ai = ContentAI()
        notion_manager = NotionManager()
        sheets_manager = GoogleSheetsManager()
        
        # Load previously seen URLs
        seen_urls = sheets_manager.get_seen_urls()
        rss_manager.load_seen_urls(set(seen_urls))
        
        # Fetch RSS feeds
        rss_items = rss_manager.fetch_rss_feeds()
        logger.info(f"Fetched {len(rss_items)} new RSS items")
        
        if not rss_items:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No new RSS items found',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        processed_count = 0
        blog_drafts_created = 0
        notion_pages_created = 0
        
        # Process each item for blog generation
        for rss_item in rss_items:
            try:
                # Score the content
                score = scoring_ai.score_content(rss_item)
                if not score:
                    continue
                
                # Create content item
                content_item = ContentItem(
                    rss_item=rss_item,
                    score=score,
                    status=ContentStatus.SCORED
                )
                
                # Apply quality filter (focus on blog-relevant content)
                passed, reason = quality_filter.filter_by_score(rss_item, score)
                
                if passed:
                    # Generate blog content only
                    generated_content = content_ai.generate_blog_content(rss_item, score)
                    if generated_content:
                        content_item.generated_content = generated_content
                        
                        # Final quality check for blog content
                        final_passed, final_reason = quality_filter.filter_blog_content(content_item)
                        
                        if final_passed:
                            content_item.status = ContentStatus.APPROVED
                            blog_drafts_created += 1
                            
                            # Create Notion page
                            notion_url = notion_manager.create_blog_draft(content_item)
                            if notion_url:
                                notion_pages_created += 1
                                logger.info(f"Created Notion page: {notion_url}")
                            
                            # Log to sheets
                            sheets_manager.log_content_item(content_item, platform="blog")
                        else:
                            content_item.status = ContentStatus.HELD_FOR_REVIEW
                            content_item.review_reason = final_reason
                            logger.info(f"Blog content held for review: {final_reason}")
                    else:
                        content_item.status = ContentStatus.REJECTED
                        logger.warning(f"Failed to generate blog content for '{rss_item.title}'")
                else:
                    content_item.status = ContentStatus.REJECTED
                    logger.info(f"Content rejected: {reason}")
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing item '{rss_item.title}': {e}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Blog generation completed',
                'processed_items': processed_count,
                'blog_drafts_created': blog_drafts_created,
                'notion_pages_created': notion_pages_created,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error in blog generator: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

# Vercel expects this to be the main handler
def main(request):
    return handler(request)
