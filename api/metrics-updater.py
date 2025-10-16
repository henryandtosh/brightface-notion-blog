"""
Vercel Serverless Function: Metrics Updater
Runs daily to update engagement metrics for posted content
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_manager import GoogleSheetsManager
from social_publishers import SocialMediaManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Main handler for metrics updating"""
    try:
        logger.info("Starting metrics update")
        
        # Initialize components
        sheets_manager = GoogleSheetsManager()
        social_manager = SocialMediaManager()
        
        # Get recently posted content (last 7 days)
        recent_posts = get_recent_posts(sheets_manager)
        
        if not recent_posts:
            logger.info("No recent posts to update metrics for")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No recent posts to update',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        updated_count = 0
        
        # Update metrics for each post
        for post in recent_posts:
            try:
                metrics = social_manager.update_engagement_metrics(post)
                
                if metrics:
                    # Update in sheets
                    sheets_manager.update_engagement_metrics(post['post_url'], metrics)
                    updated_count += 1
                    logger.info(f"Updated metrics for {post['post_url']}: {metrics}")
                
            except Exception as e:
                logger.error(f"Error updating metrics for {post.get('post_url', 'unknown')}: {e}")
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Metrics update completed',
                'updated_count': updated_count,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error in metrics updater: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def get_recent_posts(sheets_manager):
    """Get recently posted content from Google Sheets"""
    try:
        # This is a simplified implementation
        # In production, you'd query the sheets for recent posts
        # For now, we'll return an empty list
        return []
    except Exception as e:
        logger.error(f"Error getting recent posts: {e}")
        return []

# Vercel expects this to be the main handler
def main(request):
    return handler(request)
