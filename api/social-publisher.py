"""
Vercel Serverless Function: Social Publisher
Runs at scheduled times to post approved content to social media
"""
import os
import sys
import json
import logging
from datetime import datetime
import random

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_manager import GoogleSheetsManager
from social_publishers import SocialMediaManager
from models import ContentStatus
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Main handler for social media publishing"""
    try:
        logger.info("Starting social media publishing")
        
        # Initialize components
        sheets_manager = GoogleSheetsManager()
        social_manager = SocialMediaManager()
        
        # Get approved content from sheets
        approved_content = get_approved_content(sheets_manager)
        
        if not approved_content:
            logger.info("No approved content to publish")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No approved content to publish',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        # Select content to post (random selection for variety)
        content_to_post = random.choice(approved_content)
        
        posted_count = 0
        results = {}
        
        # Post to social media if auto-post is enabled
        if Config.AUTO_POST:
            try:
                results = social_manager.post_to_all_platforms(content_to_post)
                
                if any(results.values()):
                    content_to_post.status = ContentStatus.POSTED
                    content_to_post.posted_at = datetime.now()
                    posted_count = 1
                    logger.info(f"Posted content: {results}")
                else:
                    content_to_post.status = ContentStatus.QUEUED
                    logger.warning("Failed to post content, queued for retry")
                
                # Update in sheets
                sheets_manager.update_content_item(content_to_post)
                
            except Exception as e:
                logger.error(f"Error posting content: {e}")
                content_to_post.status = ContentStatus.QUEUED
                sheets_manager.update_content_item(content_to_post)
        else:
            logger.info("Auto-post disabled, content remains in review queue")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Social publishing completed',
                'posted_count': posted_count,
                'results': results,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error in social publisher: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def get_approved_content(sheets_manager):
    """Get approved content from Google Sheets"""
    try:
        # This is a simplified implementation
        # In production, you'd query the sheets for approved content
        # For now, we'll return an empty list
        return []
    except Exception as e:
        logger.error(f"Error getting approved content: {e}")
        return []

# Vercel expects this to be the main handler
def main(request):
    return handler(request)
