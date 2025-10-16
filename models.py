"""
Data models for the Brightface Content Engine
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ContentStatus(str, Enum):
    """Status of content items"""
    PENDING = "pending"
    SCORED = "scored"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"
    QUEUED = "queued"
    HELD_FOR_REVIEW = "held_for_review"
    ARCHIVED = "archived"

class RiskFlag(str, Enum):
    """Risk flags for content"""
    NONE = "none"
    MEDICAL_CLAIM = "medical claim"
    COPYRIGHT = "copyright"
    PRIVACY = "privacy"
    UNVERIFIED_BENCHMARK = "unverified benchmark"

class RSSItem(BaseModel):
    """RSS feed item"""
    title: str
    summary: str
    full_text: Optional[str] = None
    source: str
    url: str
    published_date: Optional[datetime] = None
    url_hash: str = Field(..., description="Hash of URL for deduplication")

class ContentScore(BaseModel):
    """AI-generated content score"""
    relevance_score: int = Field(..., ge=0, le=10)
    virality_score: int = Field(..., ge=0, le=10)
    freshness_days: int
    angles: List[str]
    risk_flags: List[RiskFlag]
    one_line_take: str
    keywords: List[str]

class SocialPost(BaseModel):
    """Social media post content"""
    text: str
    hashtags: List[str]

class BlogDraft(BaseModel):
    """Blog post draft"""
    title: str
    slug: str
    meta_description: str
    outline: List[str]
    body_md: str

class GeneratedContent(BaseModel):
    """AI-generated content for all platforms"""
    linkedin: SocialPost
    x: SocialPost
    blog: BlogDraft

class ContentItem(BaseModel):
    """Complete content item with all metadata"""
    # Original RSS data
    rss_item: RSSItem
    
    # AI scoring
    score: Optional[ContentScore] = None
    
    # Generated content
    generated_content: Optional[GeneratedContent] = None
    
    # Processing metadata
    status: ContentStatus = ContentStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Publishing metadata
    planned_publish_time: Optional[datetime] = None
    posted_at: Optional[datetime] = None
    post_url: Optional[str] = None
    
    # Engagement metrics
    clicks: Optional[int] = None
    likes: Optional[int] = None
    reposts: Optional[int] = None
    comments: Optional[int] = None
    
    # Review metadata
    reviewer: Optional[str] = None
    review_reason: Optional[str] = None

class ContentLedgerRow(BaseModel):
    """Row structure for Google Sheets content ledger"""
    date_iso: str
    platform: str
    status: str
    title: str
    source: str
    url: str
    relevance: Optional[int] = None
    virality: Optional[int] = None
    risk: str
    post_text: Optional[str] = None
    hashtags: Optional[str] = None
    blog_slug: Optional[str] = None
    reviewer: Optional[str] = None
    posted_at: Optional[str] = None
    post_url: Optional[str] = None
    clicks: Optional[int] = None
    likes: Optional[int] = None
    reposts: Optional[int] = None
    comments: Optional[int] = None
