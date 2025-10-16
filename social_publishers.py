"""
Social Media Publishers for Brightface Content Engine
"""
import os
import logging
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime
import time

from models import ContentItem, SocialPost
from config import Config

logger = logging.getLogger(__name__)

class LinkedInPublisher:
    """LinkedIn publishing functionality"""
    
    def __init__(self):
        self.client_id = Config.LINKEDIN_CLIENT_ID
        self.client_secret = Config.LINKEDIN_CLIENT_SECRET
        self.page_id = Config.LINKEDIN_PAGE_ID
        self.access_token = None
        self.token_expires_at = None
    
    def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            # In production, you'd implement OAuth2 flow here
            # For now, we'll assume the access token is provided via environment
            self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
            
            if not self.access_token:
                logger.error("LinkedIn access token not found")
                return False
            
            logger.info("LinkedIn authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            return False
    
    def post_content(self, content_item: ContentItem) -> Optional[str]:
        """Post content to LinkedIn"""
        try:
            if not self.access_token:
                if not self.authenticate():
                    return None
            
            post_data = content_item.generated_content.linkedin
            
            # Prepare LinkedIn UGC post payload
            payload = {
                "author": f"urn:li:organization:{self.page_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_data.text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            response = requests.post(
                'https://api.linkedin.com/v2/ugcPosts',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                post_url = f"https://www.linkedin.com/feed/update/{result.get('id', '').split(':')[-1]}"
                logger.info(f"Posted to LinkedIn: {post_url}")
                return post_url
            else:
                logger.error(f"LinkedIn post failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return None
    
    def get_engagement_metrics(self, post_url: str) -> Dict[str, int]:
        """Get engagement metrics for a LinkedIn post"""
        try:
            # Extract post ID from URL
            post_id = post_url.split('/')[-1]
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            response = requests.get(
                f'https://api.linkedin.com/v2/socialActions/{post_id}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'likes': data.get('numLikes', 0),
                    'comments': data.get('numComments', 0),
                    'reposts': data.get('numShares', 0)
                }
            else:
                logger.warning(f"Could not fetch LinkedIn metrics: {response.status_code}")
                return {'likes': 0, 'comments': 0, 'reposts': 0}
                
        except Exception as e:
            logger.error(f"Error fetching LinkedIn metrics: {e}")
            return {'likes': 0, 'comments': 0, 'reposts': 0}

class TwitterPublisher:
    """Twitter/X publishing functionality"""
    
    def __init__(self):
        self.api_key = Config.TWITTER_API_KEY
        self.api_secret = Config.TWITTER_API_SECRET
        self.access_token = Config.TWITTER_ACCESS_TOKEN
        self.access_secret = Config.TWITTER_ACCESS_SECRET
        self.bearer_token = None
    
    def authenticate(self) -> bool:
        """Authenticate with Twitter API"""
        try:
            # In production, you'd implement OAuth2 flow here
            # For now, we'll assume the bearer token is provided via environment
            self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not self.bearer_token:
                logger.error("Twitter bearer token not found")
                return False
            
            logger.info("Twitter authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Twitter authentication failed: {e}")
            return False
    
    def post_content(self, content_item: ContentItem) -> Optional[str]:
        """Post content to Twitter/X"""
        try:
            if not self.bearer_token:
                if not self.authenticate():
                    return None
            
            post_data = content_item.generated_content.x
            
            # Prepare Twitter v2 API payload
            payload = {
                "text": post_data.text
            }
            
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.twitter.com/2/tweets',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                tweet_id = result.get('data', {}).get('id')
                post_url = f"https://twitter.com/user/status/{tweet_id}"
                logger.info(f"Posted to Twitter: {post_url}")
                return post_url
            else:
                logger.error(f"Twitter post failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}")
            return None
    
    def get_engagement_metrics(self, post_url: str) -> Dict[str, int]:
        """Get engagement metrics for a Twitter post"""
        try:
            # Extract tweet ID from URL
            tweet_id = post_url.split('/')[-1]
            
            headers = {
                'Authorization': f'Bearer {self.bearer_token}'
            }
            
            response = requests.get(
                f'https://api.twitter.com/2/tweets/{tweet_id}?tweet.fields=public_metrics',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('data', {}).get('public_metrics', {})
                return {
                    'likes': metrics.get('like_count', 0),
                    'comments': metrics.get('reply_count', 0),
                    'reposts': metrics.get('retweet_count', 0)
                }
            else:
                logger.warning(f"Could not fetch Twitter metrics: {response.status_code}")
                return {'likes': 0, 'comments': 0, 'reposts': 0}
                
        except Exception as e:
            logger.error(f"Error fetching Twitter metrics: {e}")
            return {'likes': 0, 'comments': 0, 'reposts': 0}

class SocialMediaManager:
    """Manages all social media publishing"""
    
    def __init__(self):
        self.linkedin = LinkedInPublisher()
        self.twitter = TwitterPublisher()
    
    def post_to_all_platforms(self, content_item: ContentItem) -> Dict[str, Optional[str]]:
        """Post content to all configured platforms"""
        results = {}
        
        # Post to LinkedIn
        if Config.LINKEDIN_PAGE_ID:
            linkedin_url = self.linkedin.post_content(content_item)
            results['linkedin'] = linkedin_url
            
            if linkedin_url:
                content_item.post_url = linkedin_url
                content_item.posted_at = datetime.now()
        
        # Post to Twitter/X
        if Config.TWITTER_API_KEY:
            twitter_url = self.twitter.post_content(content_item)
            results['twitter'] = twitter_url
            
            if twitter_url and not content_item.post_url:
                content_item.post_url = twitter_url
                content_item.posted_at = datetime.now()
        
        return results
    
    def update_engagement_metrics(self, content_item: ContentItem) -> Dict[str, Dict[str, int]]:
        """Update engagement metrics for all platforms"""
        metrics = {}
        
        if content_item.post_url:
            if 'linkedin.com' in content_item.post_url:
                metrics['linkedin'] = self.linkedin.get_engagement_metrics(content_item.post_url)
            elif 'twitter.com' in content_item.post_url:
                metrics['twitter'] = self.twitter.get_engagement_metrics(content_item.post_url)
        
        return metrics
