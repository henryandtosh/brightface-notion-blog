"""
Main Content Engine Automation Flow
"""
import os
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from models import ContentItem, ContentStatus
from rss_manager import RSSManager
from scoring_ai import ScoringAI
from quality_filter import QualityFilter
from content_ai import ContentAI
from sheets_manager import GoogleSheetsManager
from social_publishers import SocialMediaManager
from config import Config

logger = logging.getLogger(__name__)

class ContentEngine:
    """Main content engine orchestrator"""
    
    def __init__(self):
        self.rss_manager = RSSManager()
        self.scoring_ai = ScoringAI()
        self.quality_filter = QualityFilter()
        self.content_ai = ContentAI()
        self.sheets_manager = GoogleSheetsManager()
        self.social_manager = SocialMediaManager()
        
        # Load previously seen URLs
        self._load_seen_urls()
    
    def _load_seen_urls(self):
        """Load previously seen URLs from Google Sheets"""
        try:
            seen_urls = self.sheets_manager.get_seen_urls()
            self.rss_manager.load_seen_urls(set(seen_urls))
            logger.info(f"Loaded {len(seen_urls)} previously seen URLs")
        except Exception as e:
            logger.error(f"Error loading seen URLs: {e}")
    
    def run_content_cycle(self) -> Dict[str, Any]:
        """Run a complete content processing cycle"""
        logger.info("Starting content processing cycle")
        
        cycle_stats = {
            'start_time': datetime.now(),
            'rss_items_fetched': 0,
            'items_scored': 0,
            'items_passed_filter': 0,
            'content_generated': 0,
            'items_posted': 0,
            'items_held_for_review': 0,
            'errors': []
        }
        
        try:
            # Step 1: Fetch RSS feeds
            logger.info("Fetching RSS feeds...")
            rss_items = self.rss_manager.fetch_rss_feeds()
            cycle_stats['rss_items_fetched'] = len(rss_items)
            logger.info(f"Fetched {len(rss_items)} new RSS items")
            
            if not rss_items:
                logger.info("No new RSS items found")
                return cycle_stats
            
            # Step 2: Score content
            logger.info("Scoring content...")
            scored_items = []
            for rss_item in rss_items:
                try:
                    score = self.scoring_ai.score_content(rss_item)
                    if score:
                        content_item = ContentItem(
                            rss_item=rss_item,
                            score=score,
                            status=ContentStatus.SCORED
                        )
                        scored_items.append(content_item)
                        cycle_stats['items_scored'] += 1
                except Exception as e:
                    logger.error(f"Error scoring item '{rss_item.title}': {e}")
                    cycle_stats['errors'].append(f"Scoring error: {e}")
            
            # Step 3: Apply quality filters
            logger.info("Applying quality filters...")
            filtered_items = []
            for content_item in scored_items:
                try:
                    passed, reason = self.quality_filter.filter_by_score(
                        content_item.rss_item, 
                        content_item.score
                    )
                    
                    if passed:
                        content_item.status = ContentStatus.APPROVED
                        filtered_items.append(content_item)
                        cycle_stats['items_passed_filter'] += 1
                    else:
                        content_item.status = ContentStatus.REJECTED
                        logger.info(f"Item rejected: {reason}")
                        
                        # Check if should be held for review
                        should_review, review_reason = self.quality_filter.should_hold_for_review(
                            content_item.rss_item, 
                            content_item.score
                        )
                        if should_review:
                            content_item.status = ContentStatus.HELD_FOR_REVIEW
                            content_item.review_reason = review_reason
                            cycle_stats['items_held_for_review'] += 1
                        
                        # Log to sheets
                        self.sheets_manager.log_content_item(content_item)
                        
                except Exception as e:
                    logger.error(f"Error filtering item '{content_item.rss_item.title}': {e}")
                    cycle_stats['errors'].append(f"Filtering error: {e}")
            
            # Step 4: Generate content
            logger.info("Generating content...")
            generated_items = []
            for content_item in filtered_items:
                try:
                    generated_content = self.content_ai.generate_content(
                        content_item.rss_item,
                        content_item.score
                    )
                    
                    if generated_content:
                        # Add UTM parameters
                        content_item.generated_content = self.content_ai.add_utm_parameters(
                            generated_content, 
                            "both"
                        )
                        content_item.status = ContentStatus.APPROVED
                        generated_items.append(content_item)
                        cycle_stats['content_generated'] += 1
                    else:
                        content_item.status = ContentStatus.REJECTED
                        logger.warning(f"Failed to generate content for '{content_item.rss_item.title}'")
                        
                except Exception as e:
                    logger.error(f"Error generating content for '{content_item.rss_item.title}': {e}")
                    cycle_stats['errors'].append(f"Content generation error: {e}")
            
            # Step 5: Final quality check
            logger.info("Final quality check...")
            final_items = []
            for content_item in generated_items:
                try:
                    passed, reason = self.quality_filter.filter_generated_content(content_item)
                    
                    if passed:
                        final_items.append(content_item)
                    else:
                        content_item.status = ContentStatus.HELD_FOR_REVIEW
                        content_item.review_reason = reason
                        cycle_stats['items_held_for_review'] += 1
                        logger.info(f"Content held for review: {reason}")
                        
                except Exception as e:
                    logger.error(f"Error in final quality check: {e}")
                    cycle_stats['errors'].append(f"Final quality check error: {e}")
            
            # Step 6: Post content (if auto-post is enabled)
            if Config.AUTO_POST and final_items:
                logger.info("Posting content to social media...")
                for content_item in final_items:
                    try:
                        results = self.social_manager.post_to_all_platforms(content_item)
                        
                        if any(results.values()):
                            content_item.status = ContentStatus.POSTED
                            cycle_stats['items_posted'] += 1
                            logger.info(f"Posted content: {results}")
                        else:
                            content_item.status = ContentStatus.QUEUED
                            logger.warning("Failed to post content, queued for retry")
                        
                        # Log to sheets
                        self.sheets_manager.log_content_item(content_item)
                        
                    except Exception as e:
                        logger.error(f"Error posting content: {e}")
                        cycle_stats['errors'].append(f"Posting error: {e}")
            else:
                # Log all items to sheets for review
                for content_item in final_items:
                    self.sheets_manager.log_content_item(content_item)
            
            # Step 7: Update engagement metrics (for previously posted content)
            self._update_engagement_metrics()
            
        except Exception as e:
            logger.error(f"Error in content cycle: {e}")
            cycle_stats['errors'].append(f"Cycle error: {e}")
        
        cycle_stats['end_time'] = datetime.now()
        cycle_stats['duration'] = (cycle_stats['end_time'] - cycle_stats['start_time']).total_seconds()
        
        logger.info(f"Content cycle completed: {cycle_stats}")
        return cycle_stats
    
    def _update_engagement_metrics(self):
        """Update engagement metrics for posted content"""
        try:
            # This would typically fetch metrics for recently posted content
            # For now, we'll implement a placeholder
            logger.info("Updating engagement metrics...")
        except Exception as e:
            logger.error(f"Error updating engagement metrics: {e}")
    
    def schedule_posting(self):
        """Schedule content posting at optimal times"""
        if not Config.POSTING_SCHEDULE_ENABLED:
            return
        
        # Schedule posting at random times within the specified windows
        for time_str in Config.POSTING_TIMES:
            schedule.every().day.at(time_str).do(self._scheduled_post)
        
        logger.info(f"Scheduled posting at times: {Config.POSTING_TIMES}")
    
    def _scheduled_post(self):
        """Execute scheduled posting"""
        try:
            logger.info("Executing scheduled post")
            
            # Get queued content
            queued_items = self._get_queued_content()
            
            if queued_items:
                # Select random item to post
                item = random.choice(queued_items)
                results = self.social_manager.post_to_all_platforms(item)
                
                if any(results.values()):
                    item.status = ContentStatus.POSTED
                    self.sheets_manager.update_content_item(item)
                    logger.info(f"Scheduled post successful: {results}")
                else:
                    logger.warning("Scheduled post failed")
            else:
                logger.info("No queued content to post")
                
        except Exception as e:
            logger.error(f"Error in scheduled post: {e}")
    
    def _get_queued_content(self) -> List[ContentItem]:
        """Get content queued for posting"""
        # This would typically query the Google Sheets for queued items
        # For now, return empty list
        return []
    
    def run_scheduler(self):
        """Run the content engine scheduler"""
        logger.info("Starting content engine scheduler")
        
        # Schedule RSS fetching every 2 hours
        schedule.every(2).hours.do(self.run_content_cycle)
        
        # Schedule posting times
        self.schedule_posting()
        
        # Run initial cycle
        self.run_content_cycle()
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self):
        """Run the content engine once"""
        logger.info("Running content engine once")
        return self.run_content_cycle()

def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed")
        return
    
    # Initialize and run content engine
    engine = ContentEngine()
    
    # Run once or continuously based on environment
    if os.getenv('RUN_ONCE', 'false').lower() == 'true':
        engine.run_once()
    else:
        engine.run_scheduler()

if __name__ == "__main__":
    main()
