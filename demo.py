#!/usr/bin/env python3
"""
Example script demonstrating the Brightface Content Engine
"""
import logging
from datetime import datetime

from models import RSSItem, ContentScore, RiskFlag
from rss_manager import RSSManager
from scoring_ai import ScoringAI
from quality_filter import QualityFilter
from content_ai import ContentAI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_content_processing():
    """Demonstrate the content processing pipeline"""
    print("🚀 Brightface Content Engine Demo")
    print("=" * 50)
    
    # Initialize components
    rss_manager = RSSManager()
    scoring_ai = ScoringAI()
    quality_filter = QualityFilter()
    content_ai = ContentAI()
    
    # Create a sample RSS item
    sample_item = RSSItem(
        title="AI-Powered Headshots Transform Professional Branding",
        summary="New AI technology is revolutionizing how professionals create headshots, with tools that can generate high-quality photos from just a few reference images. This technology is particularly valuable for remote workers and entrepreneurs who need professional photos for LinkedIn profiles and business materials.",
        full_text="Artificial intelligence is transforming the professional photography industry, particularly in the realm of headshots and personal branding. Recent developments in AI-powered image generation have made it possible to create high-quality professional headshots without the need for expensive photo shoots or professional photographers. These tools analyze facial features, lighting, and composition to generate realistic, professional-looking photos that can be used across various platforms including LinkedIn, company websites, and marketing materials. The technology is especially beneficial for remote workers, entrepreneurs, and small business owners who need professional photos but may not have access to traditional photography services or the budget for custom photo shoots.",
        source="techcrunch.com",
        url="https://techcrunch.com/2024/01/15/ai-headshots-professional-branding",
        published_date=datetime.now(),
        url_hash="sample123"
    )
    
    print(f"📰 Sample Article: {sample_item.title}")
    print(f"Source: {sample_item.source}")
    print(f"Summary: {sample_item.summary[:100]}...")
    print()
    
    # Step 1: Score the content
    print("🤖 Step 1: AI Scoring")
    print("-" * 20)
    
    score = scoring_ai.score_content(sample_item)
    if score:
        print(f"✓ Relevance Score: {score.relevance_score}/10")
        print(f"✓ Virality Score: {score.virality_score}/10")
        print(f"✓ Freshness: {score.freshness_days} days")
        print(f"✓ Angles: {', '.join(score.angles)}")
        print(f"✓ Hook: {score.one_line_take}")
        print(f"✓ Keywords: {', '.join(score.keywords)}")
        print(f"✓ Risk Flags: {[flag.value for flag in score.risk_flags]}")
    else:
        print("✗ Scoring failed")
        return
    
    print()
    
    # Step 2: Quality filter
    print("🔍 Step 2: Quality Filter")
    print("-" * 20)
    
    passed, reason = quality_filter.filter_by_score(sample_item, score)
    if passed:
        print(f"✓ Passed quality filter: {reason}")
    else:
        print(f"✗ Rejected: {reason}")
        return
    
    print()
    
    # Step 3: Generate content
    print("✍️ Step 3: Content Generation")
    print("-" * 20)
    
    generated_content = content_ai.generate_content(sample_item, score)
    if generated_content:
        print("✓ Generated content successfully")
        print()
        
        # Show LinkedIn post
        print("📱 LinkedIn Post:")
        print("-" * 15)
        print(generated_content.linkedin.text)
        print(f"Hashtags: {' '.join(generated_content.linkedin.hashtags)}")
        print()
        
        # Show X post
        print("🐦 X (Twitter) Post:")
        print("-" * 15)
        print(generated_content.x.text)
        print(f"Hashtags: {' '.join(generated_content.x.hashtags)}")
        print()
        
        # Show blog draft
        print("📝 Blog Draft:")
        print("-" * 15)
        print(f"Title: {generated_content.blog.title}")
        print(f"Slug: {generated_content.blog.slug}")
        print(f"Meta Description: {generated_content.blog.meta_description}")
        print(f"Outline: {generated_content.blog.outline}")
        print(f"Body Length: {len(generated_content.blog.body_md)} characters")
        print()
        
        # Step 4: Final quality check
        print("🛡️ Step 4: Final Quality Check")
        print("-" * 20)
        
        # Create a content item for final check
        from models import ContentItem, ContentStatus
        content_item = ContentItem(
            rss_item=sample_item,
            score=score,
            generated_content=generated_content,
            status=ContentStatus.APPROVED
        )
        
        passed, reason = quality_filter.filter_generated_content(content_item)
        if passed:
            print(f"✓ Final quality check passed: {reason}")
            print()
            print("🎉 Content is ready for publishing!")
        else:
            print(f"✗ Final quality check failed: {reason}")
    else:
        print("✗ Content generation failed")

def demo_rss_feeds():
    """Demonstrate RSS feed fetching"""
    print("\n📡 RSS Feed Demo")
    print("=" * 30)
    
    rss_manager = RSSManager()
    
    # Fetch a few items from RSS feeds
    print("Fetching RSS feeds...")
    items = rss_manager.fetch_rss_feeds()
    
    if items:
        print(f"✓ Fetched {len(items)} items")
        print("\nSample items:")
        for i, item in enumerate(items[:3], 1):
            print(f"{i}. {item.title}")
            print(f"   Source: {item.source}")
            print(f"   URL: {item.url}")
            print()
    else:
        print("✗ No items fetched")

if __name__ == "__main__":
    try:
        demo_content_processing()
        demo_rss_feeds()
    except Exception as e:
        print(f"Demo failed: {e}")
        logging.error(f"Demo error: {e}")
