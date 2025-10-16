"""
AI Scoring System for Brightface Content Engine
"""
import json
import logging
from typing import Optional
from openai import OpenAI
from datetime import datetime

from models import RSSItem, ContentScore, RiskFlag
from config import Config

logger = logging.getLogger(__name__)

class ScoringAI:
    """AI system for scoring content relevance and virality"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.system_prompt = """You are an editorial analyst for brightface.ai (AI headshots & personal branding). Score incoming content for how well it can be turned into an engaging post that promotes brightface without sounding salesy."""
    
    def score_content(self, rss_item: RSSItem) -> Optional[ContentScore]:
        """Score an RSS item for relevance and virality"""
        try:
            user_prompt = self._build_scoring_prompt(rss_item)
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse and validate the response
            content_score = self._parse_scoring_response(result, rss_item)
            
            logger.info(f"Scored item '{rss_item.title}': relevance={content_score.relevance_score}, virality={content_score.virality_score}")
            return content_score
            
        except Exception as e:
            logger.error(f"Error scoring content '{rss_item.title}': {e}")
            return None
    
    def _build_scoring_prompt(self, rss_item: RSSItem) -> str:
        """Build the scoring prompt for the AI"""
        return f"""Article:
- Title: {rss_item.title}
- Summary: {rss_item.summary}
- Source: {rss_item.source}
- URL: {rss_item.url}

Task:
1) Relevance: does this help our audience with AI headshots, personal branding, LinkedIn optimization, AI content tools, or startup/creator growth?
2) Freshness: is this still timely (<= 14 days) or evergreen?
3) Angle: suggest 1–2 "brightface angles" that connect this topic to: (a) first impressions, (b) profile photos, (c) ai-assisted self-presentation.
4) Risk: any compliance/claims risk?

Return JSON exactly:
{{
  "relevance_score": 0-10,
  "virality_score": 0-10,
  "freshness_days": integer,
  "angles": ["...", "..."],
  "risk_flags": ["none" | "medical claim" | "copyright" | "privacy" | "unverified benchmark"],
  "one_line_take": "12–18 word hook",
  "keywords": ["3–6 seo/hashtag terms"]
}}"""
    
    def _parse_scoring_response(self, result: dict, rss_item: RSSItem) -> ContentScore:
        """Parse and validate the AI scoring response"""
        try:
            # Calculate freshness days
            freshness_days = 0
            if rss_item.published_date:
                freshness_days = (datetime.now() - rss_item.published_date).days
            
            # Parse risk flags
            risk_flags = []
            if isinstance(result.get('risk_flags'), list):
                for flag in result['risk_flags']:
                    try:
                        risk_flags.append(RiskFlag(flag))
                    except ValueError:
                        risk_flags.append(RiskFlag.NONE)
            else:
                risk_flags = [RiskFlag.NONE]
            
            # Ensure angles is a list
            angles = result.get('angles', [])
            if isinstance(angles, str):
                angles = [angles]
            
            # Ensure keywords is a list
            keywords = result.get('keywords', [])
            if isinstance(keywords, str):
                keywords = [keywords]
            
            return ContentScore(
                relevance_score=int(result.get('relevance_score', 0)),
                virality_score=int(result.get('virality_score', 0)),
                freshness_days=freshness_days,
                angles=angles,
                risk_flags=risk_flags,
                one_line_take=result.get('one_line_take', ''),
                keywords=keywords
            )
            
        except Exception as e:
            logger.error(f"Error parsing scoring response: {e}")
            # Return default scores if parsing fails
            return ContentScore(
                relevance_score=0,
                virality_score=0,
                freshness_days=0,
                angles=[],
                risk_flags=[RiskFlag.NONE],
                one_line_take="",
                keywords=[]
            )
    
    def batch_score_content(self, rss_items: list[RSSItem]) -> list[tuple[RSSItem, Optional[ContentScore]]]:
        """Score multiple RSS items in batch"""
        results = []
        
        for item in rss_items:
            score = self.score_content(item)
            results.append((item, score))
        
        return results
