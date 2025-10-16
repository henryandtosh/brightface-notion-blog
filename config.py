"""
Brightface Content Engine - Configuration and Constants
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Brightface Content Engine"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4'  # Using gpt-4 instead of gpt-5 as specified
    
    # LinkedIn Configuration
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    LINKEDIN_PAGE_ID = os.getenv('LINKEDIN_PAGE_ID')
    
    # Twitter/X Configuration
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    # Notion Configuration (optional)
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    NOTION_DB_ID = os.getenv('NOTION_DB_ID')
    
    # Content Engine Configuration
    DEFAULT_UTM_CAMPAIGN = os.getenv('DEFAULT_UTM_CAMPAIGN', 'autopost')
    AUTO_POST = os.getenv('AUTO_POST', 'false').lower() == 'true'
    POSTING_SCHEDULE_ENABLED = os.getenv('POSTING_SCHEDULE_ENABLED', 'true').lower() == 'true'
    
    # Blog-focused configuration
    BLOG_ONLY_MODE = os.getenv('BLOG_ONLY_MODE', 'true').lower() == 'true'
    BLOG_PUBLISHING_SCHEDULE = os.getenv('BLOG_PUBLISHING_SCHEDULE', '0 11 * * 1,4')  # Mon/Thu 11:00
    
    # RSS Sources
    RSS_SOURCES = os.getenv('RSS_SOURCES', '').split(',') if os.getenv('RSS_SOURCES') else [
        'https://openai.com/blog/rss.xml',
        'https://ai.googleblog.com/feeds/posts/default',
        'https://www.producthunt.com/feed?category=artificial-intelligence',
        'https://venturebeat.com/ai/feed/',
        'https://techcrunch.com/category/artificial-intelligence/feed/',
        'https://blog.adobe.com/en/topics/firefly/feed.xml',
        'https://engineering.linkedin.com/blog.rss'
    ]
    
    # Content Quality Thresholds
    MIN_RELEVANCE_SCORE = 7
    MIN_VIRALITY_SCORE = 6
    MAX_FRESHNESS_DAYS = 21
    
    # Posting Schedule (UK time)
    POSTING_TIMES = ['08:30', '10:00', '15:30', '17:00']
    
    # Brand Configuration
    BRANDFACE_URL = 'https://brightface.ai'
    BRAND_HASHTAGS = ['#AIHeadshots', '#PersonalBranding']
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            'OPENAI_API_KEY',
            'NOTION_API_KEY',
            'NOTION_DB_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
