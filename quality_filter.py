"""
Quality Filters for Brightface Content Engine
"""
import re
import logging
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

from models import RSSItem, ContentScore, ContentItem, ContentStatus, RiskFlag, GeneratedContent
from config import Config

logger = logging.getLogger(__name__)

class QualityFilter:
    """Quality filters for content processing"""
    
    def __init__(self):
        # Banned phrases for safety
        self.banned_phrases = [
            r'study shows',
            r'research proves',
            r'scientists found',
            r'medical study',
            r'clinical trial',
            r'perfect\s+face',
            r'flawless\s+skin',
            r'celebrity\s+look',
            r'facial\s+surgery',
            r'botox',
            r'plastic\s+surgery'
        ]
        
        # Compile regex patterns
        self.banned_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.banned_phrases]
    
    def filter_by_score(self, rss_item: RSSItem, score: ContentScore) -> Tuple[bool, str]:
        """
        First quality filter: Check relevance and virality scores
        Returns: (pass, reason)
        """
        # Check relevance score
        if score.relevance_score < Config.MIN_RELEVANCE_SCORE:
            return False, f"Relevance score too low: {score.relevance_score} < {Config.MIN_RELEVANCE_SCORE}"
        
        # Check virality score
        if score.virality_score < Config.MIN_VIRALITY_SCORE:
            return False, f"Virality score too low: {score.virality_score} < {Config.MIN_VIRALITY_SCORE}"
        
        # Check freshness
        if score.freshness_days > Config.MAX_FRESHNESS_DAYS:
            # Check for evergreen keywords
            evergreen_keywords = ['guide', 'how to', 'checklist', 'tutorial', 'tips']
            title_lower = rss_item.title.lower()
            summary_lower = rss_item.summary.lower()
            
            if not any(keyword in title_lower or keyword in summary_lower for keyword in evergreen_keywords):
                return False, f"Content too old: {score.freshness_days} days > {Config.MAX_FRESHNESS_DAYS}"
        
        # Check risk flags
        if RiskFlag.MEDICAL_CLAIM in score.risk_flags:
            return False, "Contains medical claims"
        
        if RiskFlag.COPYRIGHT in score.risk_flags:
            return False, "Copyright risk detected"
        
        if RiskFlag.PRIVACY in score.risk_flags:
            return False, "Privacy risk detected"
        
        return True, "Passed all quality checks"
    
    def filter_generated_content(self, content_item: ContentItem) -> Tuple[bool, str]:
        """
        Second quality filter: Check generated content for safety and compliance
        Returns: (pass, reason)
        """
        if not content_item.generated_content:
            return False, "No generated content to filter"
        
        generated = content_item.generated_content
        
        # Check LinkedIn post
        linkedin_result = self._check_social_post(generated.linkedin, "LinkedIn")
        if not linkedin_result[0]:
            return linkedin_result
        
        # Check X post
        x_result = self._check_social_post(generated.x, "X")
        if not x_result[0]:
            return x_result
        
        # Check blog content
        blog_result = self._check_blog_content(generated.blog)
        if not blog_result[0]:
            return blog_result
        
        return True, "All generated content passed quality checks"
    
    def _check_social_post(self, post, platform: str) -> Tuple[bool, str]:
        """Check a social media post for compliance"""
        text = post.text.lower()
        
        # Check for banned phrases
        for pattern in self.banned_patterns:
            if pattern.search(text):
                return False, f"{platform} post contains banned phrase"
        
        # Check hashtag count
        hashtag_count = len(post.hashtags)
        if platform == "LinkedIn" and hashtag_count > 4:
            return False, f"{platform} post has too many hashtags: {hashtag_count} > 4"
        elif platform == "X" and hashtag_count > 2:
            return False, f"{platform} post has too many hashtags: {hashtag_count} > 2"
        
        # Check for UTM link
        if Config.BRANDFACE_URL not in post.text:
            return False, f"{platform} post missing Brightface link"
        
        # Check for CTA
        if "try brightface" not in text:
            return False, f"{platform} post missing CTA"
        
        return True, f"{platform} post passed checks"
    
    def _check_blog_content(self, blog) -> Tuple[bool, str]:
        """Check blog content for compliance"""
        text = blog.body_md.lower()
        
        # Check for banned phrases
        for pattern in self.banned_patterns:
            if pattern.search(text):
                return False, "Blog content contains banned phrase"
        
        # Check for Brightface link
        if Config.BRANDFACE_URL not in text:
            return False, "Blog content missing Brightface link"
        
        # Check for invented statistics
        stat_patterns = [
            r'\d+%\s+of\s+',
            r'\d+\s+out\s+of\s+\d+',
            r'studies\s+show',
            r'research\s+indicates'
        ]
        
        for pattern in stat_patterns:
            if re.search(pattern, text):
                return False, "Blog content may contain invented statistics"
        
        return True, "Blog content passed checks"
    
    def should_hold_for_review(self, rss_item: RSSItem, score: ContentScore) -> Tuple[bool, str]:
        """Determine if content should be held for manual review"""
        # Borderline relevance score
        if 6 <= score.relevance_score < Config.MIN_RELEVANCE_SCORE:
            return True, f"Borderline relevance score: {score.relevance_score}"
        
        # Borderline virality score
        if 5 <= score.virality_score < Config.MIN_VIRALITY_SCORE:
            return True, f"Borderline virality score: {score.virality_score}"
        
        # Risk flags present
        if any(flag != RiskFlag.NONE for flag in score.risk_flags):
            return True, f"Risk flags present: {score.risk_flags}"
        
        return False, "No review needed"
    
    def filter_blog_content(self, content_item: ContentItem) -> Tuple[bool, str]:
        """
        Blog-specific quality filter: Check blog content for safety and compliance
        Returns: (pass, reason)
        """
        if not content_item.generated_content or not content_item.generated_content.blog:
            return False, "No blog content to filter"
        
        blog = content_item.generated_content.blog
        
        # Check for banned phrases
        text = blog.body_md.lower()
        for pattern in self.banned_patterns:
            if pattern.search(text):
                return False, "Blog content contains banned phrase"
        
        # Check for Brightface link
        if Config.BRANDFACE_URL not in blog.body_md:
            return False, "Blog content missing Brightface link"
        
        # Check for invented statistics
        stat_patterns = [
            r'\d+%\s+of\s+',
            r'\d+\s+out\s+of\s+\d+',
            r'studies\s+show',
            r'research\s+indicates'
        ]
        
        for pattern in stat_patterns:
            if re.search(pattern, text):
                return False, "Blog content may contain invented statistics"
        
        # Check blog-specific requirements
        if len(blog.title) > 60:
            return False, "Blog title too long (should be <= 60 characters)"
        
        if len(blog.meta_description) < 140 or len(blog.meta_description) > 160:
            return False, "Meta description length invalid (should be 140-160 characters)"
        
        if len(blog.body_md) < 600 or len(blog.body_md) > 900:
            return False, "Blog body length invalid (should be 600-900 words)"
        
        if not blog.slug:
            return False, "Blog slug missing"
        
        if not blog.outline or len(blog.outline) < 3:
            return False, "Blog outline too short (should have at least 3 sections)"
        
        return True, "Blog content passed all checks"
    
    def get_filter_summary(self, content_items: List[ContentItem]) -> dict:
        """Get summary of filtering results"""
        total = len(content_items)
        passed = sum(1 for item in item.status == ContentStatus.APPROVED for item in content_items)
        rejected = sum(1 for item in item.status == ContentStatus.REJECTED for item in content_items)
        held = sum(1 for item in item.status == ContentStatus.HELD_FOR_REVIEW for item in content_items)
        
        return {
            'total_items': total,
            'passed': passed,
            'rejected': rejected,
            'held_for_review': held,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }
