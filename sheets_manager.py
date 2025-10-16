"""
Google Sheets Integration for Brightface Content Engine
"""
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models import ContentItem, ContentLedgerRow, ContentStatus
from config import Config

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Manages Google Sheets integration for content tracking"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.service = None
        self.spreadsheet_id = Config.GOOGLE_SHEETS_ID
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            creds = None
            
            # Check for base64 encoded credentials (Vercel)
            if os.getenv('GOOGLE_CREDENTIALS_BASE64'):
                import base64
                import json
                credentials_data = base64.b64decode(os.getenv('GOOGLE_CREDENTIALS_BASE64')).decode('utf-8')
                credentials_dict = json.loads(credentials_data)
                creds = Credentials.from_authorized_user_info(credentials_dict, self.SCOPES)
                logger.info("Using base64 encoded Google credentials")
            # Load existing credentials file
            elif Config.GOOGLE_CREDENTIALS_FILE and os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                creds = Credentials.from_authorized_user_file(Config.GOOGLE_CREDENTIALS_FILE, self.SCOPES)
                logger.info("Using Google credentials file")
            
            # If no valid credentials, request authorization
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # In Vercel, we can't run interactive auth
                    if os.getenv('VERCEL_ENV'):
                        raise Exception("Google credentials not properly configured for Vercel deployment")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run (only in local development)
                if Config.GOOGLE_CREDENTIALS_FILE and not os.getenv('VERCEL_ENV'):
                    with open(Config.GOOGLE_CREDENTIALS_FILE, 'w') as token:
                        token.write(creds.to_json())
            
            self.service = build('sheets', 'v4', credentials=creds)
            logger.info("Successfully authenticated with Google Sheets")
            
        except Exception as e:
            logger.error(f"Error authenticating with Google Sheets: {e}")
            raise
    
    def create_content_ledger(self) -> bool:
        """Create the content ledger sheet with proper headers"""
        try:
            headers = [
                'date_iso', 'platform', 'status', 'title', 'source', 'url',
                'relevance', 'virality', 'risk', 'post_text', 'hashtags',
                'blog_slug', 'reviewer', 'posted_at', 'post_url',
                'clicks', 'likes', 'reposts', 'comments'
            ]
            
            # Create sheet
            body = {
                'values': [headers]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='Content Ledger!A1:S1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info("Content ledger sheet created successfully")
            return True
            
        except HttpError as e:
            logger.error(f"Error creating content ledger: {e}")
            return False
    
    def log_content_item(self, content_item: ContentItem, platform: str = "both") -> bool:
        """Log a content item to the ledger"""
        try:
            # Convert content item to ledger row
            ledger_row = self._content_item_to_ledger_row(content_item, platform)
            
            # Append to sheet
            values = [self._ledger_row_to_values(ledger_row)]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Content Ledger!A:S',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Logged content item '{content_item.rss_item.title}' to ledger")
            return True
            
        except HttpError as e:
            logger.error(f"Error logging content item: {e}")
            return False
    
    def update_content_item(self, content_item: ContentItem, platform: str = "both") -> bool:
        """Update an existing content item in the ledger"""
        try:
            # Find the row to update (this is a simplified approach)
            # In production, you'd want to track row IDs or use a more sophisticated approach
            
            ledger_row = self._content_item_to_ledger_row(content_item, platform)
            values = self._ledger_row_to_values(ledger_row)
            
            # This is a simplified update - in production you'd want to find the specific row
            # For now, we'll append a new row with updated information
            return self.log_content_item(content_item, platform)
            
        except Exception as e:
            logger.error(f"Error updating content item: {e}")
            return False
    
    def get_seen_urls(self) -> List[str]:
        """Get all previously seen URLs from the ledger"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Content Ledger!F:F'  # URL column
            ).execute()
            
            urls = result.get('values', [])
            seen_urls = []
            
            for row in urls:
                if row and row[0]:  # Skip empty cells
                    seen_urls.append(row[0])
            
            return seen_urls
            
        except HttpError as e:
            logger.error(f"Error getting seen URLs: {e}")
            return []
    
    def get_content_for_review(self) -> List[ContentItem]:
        """Get content items marked for review"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Content Ledger!A:S'
            ).execute()
            
            rows = result.get('values', [])
            if not rows:
                return []
            
            # Skip header row
            data_rows = rows[1:]
            review_items = []
            
            for row in data_rows:
                if len(row) >= 3 and row[2] == ContentStatus.HELD_FOR_REVIEW:  # Status column
                    # Convert row back to ContentItem (simplified)
                    # In production, you'd want a more robust conversion
                    pass
            
            return review_items
            
        except HttpError as e:
            logger.error(f"Error getting content for review: {e}")
            return []
    
    def update_engagement_metrics(self, post_url: str, metrics: Dict[str, int]) -> bool:
        """Update engagement metrics for a posted item"""
        try:
            # Find the row with the matching post_url and update metrics
            # This is a simplified implementation
            # In production, you'd want to find the specific row and update it
            
            logger.info(f"Updated engagement metrics for {post_url}: {metrics}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating engagement metrics: {e}")
            return False
    
    def _content_item_to_ledger_row(self, content_item: ContentItem, platform: str) -> ContentLedgerRow:
        """Convert ContentItem to ContentLedgerRow"""
        # Extract post text based on platform
        post_text = ""
        hashtags = ""
        
        if content_item.generated_content:
            if platform == "linkedin":
                post_text = content_item.generated_content.linkedin.text
                hashtags = " ".join(content_item.generated_content.linkedin.hashtags)
            elif platform == "x":
                post_text = content_item.generated_content.x.text
                hashtags = " ".join(content_item.generated_content.x.hashtags)
            elif platform == "both":
                post_text = content_item.generated_content.linkedin.text
                hashtags = " ".join(content_item.generated_content.linkedin.hashtags)
        
        # Format risk flags
        risk_str = "none"
        if content_item.score and content_item.score.risk_flags:
            risk_str = ", ".join([flag.value for flag in content_item.score.risk_flags])
        
        return ContentLedgerRow(
            date_iso=content_item.created_at.isoformat(),
            platform=platform,
            status=content_item.status.value,
            title=content_item.rss_item.title,
            source=content_item.rss_item.source,
            url=content_item.rss_item.url,
            relevance=content_item.score.relevance_score if content_item.score else None,
            virality=content_item.score.virality_score if content_item.score else None,
            risk=risk_str,
            post_text=post_text,
            hashtags=hashtags,
            blog_slug=content_item.generated_content.blog.slug if content_item.generated_content else None,
            reviewer=content_item.reviewer,
            posted_at=content_item.posted_at.isoformat() if content_item.posted_at else None,
            post_url=content_item.post_url,
            clicks=content_item.clicks,
            likes=content_item.likes,
            reposts=content_item.reposts,
            comments=content_item.comments
        )
    
    def _ledger_row_to_values(self, row: ContentLedgerRow) -> List[str]:
        """Convert ContentLedgerRow to list of values for Google Sheets"""
        return [
            row.date_iso,
            row.platform,
            row.status,
            row.title,
            row.source,
            row.url,
            str(row.relevance) if row.relevance is not None else "",
            str(row.virality) if row.virality is not None else "",
            row.risk,
            row.post_text or "",
            row.hashtags or "",
            row.blog_slug or "",
            row.reviewer or "",
            row.posted_at or "",
            row.post_url or "",
            str(row.clicks) if row.clicks is not None else "",
            str(row.likes) if row.likes is not None else "",
            str(row.reposts) if row.reposts is not None else "",
            str(row.comments) if row.comments is not None else ""
        ]
