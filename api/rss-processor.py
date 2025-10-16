"""
Vercel Serverless Function: RSS Processor
Runs every 2 hours to fetch and process RSS feeds
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
from sheets_manager import GoogleSheetsManager
from models import ContentItem, ContentStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Main handler for RSS processing"""
    try:
        logger.info("Starting RSS processing cycle")
        
        # Initialize components
        rss_manager = RSSManager()
        scoring_ai = ScoringAI()
        quality_filter = QualityFilter()
        content_ai = ContentAI()
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
        approved_count = 0
        held_count = 0
        
        # Process each item
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
                
                # Apply quality filter
                passed, reason = quality_filter.filter_by_score(rss_item, score)
                
                if passed:
                    # Generate content
                    generated_content = content_ai.generate_content(rss_item, score)
                    if generated_content:
                        content_item.generated_content = content_ai.add_utm_parameters(
                            generated_content, "both"
                        )
                        
                        # Final quality check
                        final_passed, final_reason = quality_filter.filter_generated_content(content_item)
                        
                        if final_passed:
                            content_item.status = ContentStatus.APPROVED
                            approved_count += 1
                        else:
                            content_item.status = ContentStatus.HELD_FOR_REVIEW
                            content_item.review_reason = final_reason
                            held_count += 1
                    else:
                        content_item.status = ContentStatus.REJECTED
                else:
                    # Check if should be held for review
                    should_review, review_reason = quality_filter.should_hold_for_review(rss_item, score)
                    if should_review:
                        content_item.status = ContentStatus.HELD_FOR_REVIEW
                        content_item.review_reason = review_reason
                        held_count += 1
                    else:
                        content_item.status = ContentStatus.REJECTED
                
                # Log to sheets
                sheets_manager.log_content_item(content_item)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing item '{rss_item.title}': {e}")
                continue
        
        # Update seen URLs
        new_seen_urls = rss_manager.get_seen_urls()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'RSS processing completed',
                'processed_items': processed_count,
                'approved_items': approved_count,
                'held_for_review': held_count,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error in RSS processor: {e}")
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
