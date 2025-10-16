"""
Content AI System for Brightface Content Engine
"""
import json
import logging
from typing import Optional
from openai import OpenAI
from datetime import datetime

from models import RSSItem, ContentScore, GeneratedContent, SocialPost, BlogDraft
from config import Config

logger = logging.getLogger(__name__)

class ContentAI:
    """AI system for generating social posts and blog content"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.system_prompt = """You are the voice of brightface.ai. Tone: confident, modern, helpful, lightly playful. Avoid hype. Connect ideas to personal branding and first impressions. Never fabricate facts; cite only what's provided."""
    
    def generate_content(self, rss_item: RSSItem, score: ContentScore) -> Optional[GeneratedContent]:
        """Generate social posts and blog content from scored RSS item"""
        try:
            user_prompt = self._build_content_prompt(rss_item, score)
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse and validate the response
            generated_content = self._parse_content_response(result)
            
            logger.info(f"Generated content for '{rss_item.title}'")
            return generated_content
            
        except Exception as e:
            logger.error(f"Error generating content for '{rss_item.title}': {e}")
            return None
    
    def _build_content_prompt(self, rss_item: RSSItem, score: ContentScore) -> str:
        """Build the content generation prompt"""
        # Build hashtags string
        hashtags_str = ", ".join(score.keywords[:4])  # Limit to 4 keywords
        
        return f"""Context:
Title: {rss_item.title}
Source: {rss_item.source}
Summary: {rss_item.summary}
Angle(s): {', '.join(score.angles)}
Hook: {score.one_line_take}
URL: {rss_item.url}

Brand rules:
- Mention how great first impressions + profile photos drive outcomes.
- Include CTA: "Try Brightface to upgrade your profile photo" with link https://brightface.ai/?utm_source={{platform}}&utm_campaign={Config.DEFAULT_UTM_CAMPAIGN}&utm_medium=social
- Use 2–4 tasteful hashtags from {hashtags_str} + #AIHeadshots #PersonalBranding
- No emojis at start of sentences; 0–2 total is fine.

Produce JSON exactly:
{{
  "linkedin": {{
    "text": "120–220 words, 2–3 short paragraphs, 1 bullet list if natural. End with CTA + link.",
    "hashtags": ["#...", "#..."]
  }},
  "x": {{
    "text": "230–260 chars, 1 sentence hook + 1 insight + CTA + link",
    "hashtags": ["#...", "#..."]
  }},
  "blog": {{
    "title": "SEO title <= 60 chars including 'AI headshots' or 'personal branding' when relevant",
    "slug": "kebab-case",
    "meta_description": "140–160 chars",
    "outline": ["H2 ...", "H2 ...", "H2 ..."],
    "body_md": "600–900 words markdown. Include a short intro, 3–5 H2s, one checklist, and a soft CTA section linking to brightface.ai. Insert the source URL once in 'Further reading'. No invented stats."
  }}
}}"""
    
    def _parse_content_response(self, result: dict) -> GeneratedContent:
        """Parse and validate the AI content response"""
        try:
            # Parse LinkedIn post
            linkedin_data = result.get('linkedin', {})
            linkedin_post = SocialPost(
                text=linkedin_data.get('text', ''),
                hashtags=linkedin_data.get('hashtags', [])
            )
            
            # Parse X post
            x_data = result.get('x', {})
            x_post = SocialPost(
                text=x_data.get('text', ''),
                hashtags=x_data.get('hashtags', [])
            )
            
            # Parse blog draft
            blog_data = result.get('blog', {})
            blog_draft = BlogDraft(
                title=blog_data.get('title', ''),
                slug=blog_data.get('slug', ''),
                meta_description=blog_data.get('meta_description', ''),
                outline=blog_data.get('outline', []),
                body_md=blog_data.get('body_md', '')
            )
            
            return GeneratedContent(
                linkedin=linkedin_post,
                x=x_post,
                blog=blog_draft
            )
            
        except Exception as e:
            logger.error(f"Error parsing content response: {e}")
            # Return empty content if parsing fails
            return GeneratedContent(
                linkedin=SocialPost(text="", hashtags=[]),
                x=SocialPost(text="", hashtags=[]),
                blog=BlogDraft(title="", slug="", meta_description="", outline=[], body_md="")
            )
    
    def add_utm_parameters(self, content: GeneratedContent, platform: str) -> GeneratedContent:
        """Add UTM parameters to links in generated content"""
        utm_params = f"?utm_source={platform}&utm_campaign={Config.DEFAULT_UTM_CAMPAIGN}&utm_medium=social"
        brightface_url = f"{Config.BRANDFACE_URL}{utm_params}"
        
        # Update LinkedIn text
        linkedin_text = content.linkedin.text.replace(
            "https://brightface.ai/?utm_source={platform}&utm_campaign=autopost&utm_medium=social",
            brightface_url
        )
        
        # Update X text
        x_text = content.x.text.replace(
            "https://brightface.ai/?utm_source={platform}&utm_campaign=autopost&utm_medium=social",
            brightface_url
        )
        
        # Update blog content
        blog_text = content.blog.body_md.replace(
            "https://brightface.ai/?utm_source={platform}&utm_campaign=autopost&utm_medium=social",
            brightface_url
        )
        
        return GeneratedContent(
            linkedin=SocialPost(text=linkedin_text, hashtags=content.linkedin.hashtags),
            x=SocialPost(text=x_text, hashtags=content.x.hashtags),
            blog=BlogDraft(
                title=content.blog.title,
                slug=content.blog.slug,
                meta_description=content.blog.meta_description,
                outline=content.blog.outline,
                body_md=blog_text
            )
        )
    
    def generate_blog_content(self, rss_item: RSSItem, score: ContentScore) -> Optional[GeneratedContent]:
        """Generate blog content only (for blog-focused mode)"""
        try:
            user_prompt = self._build_blog_prompt(rss_item, score)
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse and validate the response
            generated_content = self._parse_blog_response(result, rss_item, score)
            
            logger.info(f"Generated blog content for '{rss_item.title}'")
            return generated_content
            
        except Exception as e:
            logger.error(f"Error generating blog content for '{rss_item.title}': {e}")
            return None
    
    def _build_blog_prompt(self, rss_item: RSSItem, score: ContentScore) -> str:
        """Build the blog-focused content generation prompt"""
        # Build hashtags string
        hashtags_str = ", ".join(score.keywords[:4])  # Limit to 4 keywords
        
        return f"""Context:
Title: {rss_item.title}
Source: {rss_item.source}
Summary: {rss_item.summary}
Angle(s): {', '.join(score.angles)}
Hook: {score.one_line_take}
URL: {rss_item.url}

Brand rules:
- Focus on AI headshots, personal branding, and professional photography
- Include CTA: "Try Brightface to upgrade your profile photo" with link https://brightface.ai/?utm_source=blog&utm_campaign={Config.DEFAULT_UTM_CAMPAIGN}&utm_medium=content
- Use 2–4 tasteful hashtags from {hashtags_str} + #AIHeadshots #PersonalBranding
- No emojis at start of sentences; 0–2 total is fine.

Produce JSON exactly:
{{
  "blog": {{
    "title": "SEO title <= 60 chars including 'AI headshots' or 'personal branding' when relevant",
    "slug": "kebab-case",
    "meta_description": "140–160 chars",
    "outline": ["H2 ...", "H2 ...", "H2 ..."],
    "body_md": "600–900 words markdown. Include a short intro, 3–5 H2s, one checklist, and a soft CTA section linking to brightface.ai. Insert the source URL once in 'Further reading'. No invented stats."
  }}
}}"""
    
    def _parse_blog_response(self, result: dict, rss_item: RSSItem, score: ContentScore) -> GeneratedContent:
        """Parse and validate the blog-focused AI response"""
        try:
            # Parse blog draft
            blog_data = result.get('blog', {})
            blog_draft = BlogDraft(
                title=blog_data.get('title', ''),
                slug=blog_data.get('slug', ''),
                meta_description=blog_data.get('meta_description', ''),
                outline=blog_data.get('outline', []),
                body_md=blog_data.get('body_md', '')
            )
            
            # Add UTM parameters to blog content
            utm_params = f"?utm_source=blog&utm_campaign={Config.DEFAULT_UTM_CAMPAIGN}&utm_medium=content"
            brightface_url = f"{Config.BRANDFACE_URL}{utm_params}"
            
            # Update blog content with UTM
            blog_text = blog_draft.body_md.replace(
                "https://brightface.ai/?utm_source=blog&utm_campaign=autopost&utm_medium=content",
                brightface_url
            )
            
            blog_draft.body_md = blog_text
            
            # Create empty social posts for compatibility
            from models import SocialPost
            empty_linkedin = SocialPost(text="", hashtags=[])
            empty_x = SocialPost(text="", hashtags=[])
            
            return GeneratedContent(
                linkedin=empty_linkedin,
                x=empty_x,
                blog=blog_draft
            )
            
        except Exception as e:
            logger.error(f"Error parsing blog response: {e}")
            # Return empty content if parsing fails
            from models import SocialPost
            return GeneratedContent(
                linkedin=SocialPost(text="", hashtags=[]),
                x=SocialPost(text="", hashtags=[]),
                blog=BlogDraft(title="", slug="", meta_description="", outline=[], body_md="")
            )
    
    def validate_content_length(self, content: GeneratedContent) -> Tuple[bool, List[str]]:
        """Validate content meets length requirements"""
        issues = []
        
        # Check LinkedIn length
        if len(content.linkedin.text) < 120 or len(content.linkedin.text) > 220:
            issues.append(f"LinkedIn post length: {len(content.linkedin.text)} chars (should be 120-220)")
        
        # Check X length
        if len(content.x.text) < 230 or len(content.x.text) > 260:
            issues.append(f"X post length: {len(content.x.text)} chars (should be 230-260)")
        
        # Check blog title length
        if len(content.blog.title) > 60:
            issues.append(f"Blog title length: {len(content.blog.title)} chars (should be <= 60)")
        
        # Check meta description length
        if len(content.blog.meta_description) < 140 or len(content.blog.meta_description) > 160:
            issues.append(f"Meta description length: {len(content.blog.meta_description)} chars (should be 140-160)")
        
        # Check blog body length
        if len(content.blog.body_md) < 600 or len(content.blog.body_md) > 900:
            issues.append(f"Blog body length: {len(content.blog.body_md)} words (should be 600-900)")
        
        return len(issues) == 0, issues
