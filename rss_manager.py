"""
RSS Feed Management for Brightface Content Engine
"""
import feedparser
import hashlib
import requests
from datetime import datetime, timedelta
from typing import List, Set, Dict
from urllib.parse import urlparse
import logging

from models import RSSItem
from config import Config

logger = logging.getLogger(__name__)

class RSSManager:
    """Manages RSS feed fetching and deduplication"""
    
    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Brightface Content Engine 1.0'
        })
    
    def fetch_rss_feeds(self) -> List[RSSItem]:
        """Fetch all RSS feeds and return new items"""
        all_items = []
        
        for feed_url in Config.RSS_SOURCES:
            try:
                items = self._fetch_single_feed(feed_url)
                all_items.extend(items)
                logger.info(f"Fetched {len(items)} items from {feed_url}")
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
                continue
        
        # Deduplicate by URL hash
        unique_items = self._deduplicate_items(all_items)
        
        # Filter by freshness
        fresh_items = self._filter_by_freshness(unique_items)
        
        logger.info(f"Total new items after deduplication and freshness filter: {len(fresh_items)}")
        return fresh_items
    
    def _fetch_single_feed(self, feed_url: str) -> List[RSSItem]:
        """Fetch a single RSS feed"""
        try:
            response = self.session.get(feed_url, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            items = []
            for entry in feed.entries:
                try:
                    # Extract basic information
                    title = entry.get('title', '').strip()
                    summary = entry.get('summary', '').strip()
                    url = entry.get('link', '').strip()
                    
                    if not title or not url:
                        continue
                    
                    # Parse published date
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    
                    # Generate URL hash for deduplication
                    url_hash = hashlib.md5(url.encode()).hexdigest()
                    
                    # Extract source domain
                    source = urlparse(url).netloc
                    
                    # Get full text if available
                    full_text = None
                    if hasattr(entry, 'content'):
                        for content in entry.content:
                            if content.get('type') == 'text/html':
                                full_text = content.get('value', '')
                                break
                    
                    # Fallback to summary if no full text
                    if not full_text:
                        full_text = summary
                    
                    item = RSSItem(
                        title=title,
                        summary=summary,
                        full_text=full_text,
                        source=source,
                        url=url,
                        published_date=published_date,
                        url_hash=url_hash
                    )
                    
                    items.append(item)
                    
                except Exception as e:
                    logger.warning(f"Error processing entry from {feed_url}: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
            return []
    
    def _deduplicate_items(self, items: List[RSSItem]) -> List[RSSItem]:
        """Remove duplicate items based on URL hash"""
        unique_items = []
        seen_hashes = set()
        
        for item in items:
            if item.url_hash not in seen_hashes and item.url_hash not in self.seen_urls:
                unique_items.append(item)
                seen_hashes.add(item.url_hash)
                self.seen_urls.add(item.url_hash)
        
        return unique_items
    
    def _filter_by_freshness(self, items: List[RSSItem]) -> List[RSSItem]:
        """Filter items by freshness (within MAX_FRESHNESS_DAYS)"""
        cutoff_date = datetime.now() - timedelta(days=Config.MAX_FRESHNESS_DAYS)
        
        fresh_items = []
        for item in items:
            # If no published date, assume it's fresh
            if not item.published_date:
                fresh_items.append(item)
                continue
            
            # Check if item is within freshness window
            if item.published_date >= cutoff_date:
                fresh_items.append(item)
            else:
                # Check for evergreen keywords
                evergreen_keywords = ['guide', 'how to', 'checklist', 'tutorial', 'tips']
                title_lower = item.title.lower()
                summary_lower = item.summary.lower()
                
                if any(keyword in title_lower or keyword in summary_lower for keyword in evergreen_keywords):
                    fresh_items.append(item)
        
        return fresh_items
    
    def load_seen_urls(self, seen_urls: Set[str]):
        """Load previously seen URLs to avoid reprocessing"""
        self.seen_urls.update(seen_urls)
    
    def get_seen_urls(self) -> Set[str]:
        """Get all seen URLs"""
        return self.seen_urls.copy()
    
    def add_seen_url(self, url_hash: str):
        """Add a URL hash to seen URLs"""
        self.seen_urls.add(url_hash)
