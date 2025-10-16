#!/usr/bin/env python3
"""
Automated Content Generator for Brightface Blog
Runs on a schedule to generate blog posts from RSS feeds
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import feedparser
from openai import OpenAI
from notion_client import Client

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

class AutomatedContentGenerator:
    def __init__(self):
        self.config = Config()
        self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        self.notion_client = Client(auth=self.config.NOTION_API_KEY)
        
        # Google Sheets is optional
        self.sheets_enabled = bool(self.config.GOOGLE_SHEETS_ID)
        
    def fetch_rss_content(self) -> List[Dict[str, Any]]:
        """Fetch content from RSS feeds"""
        print("🔍 Fetching RSS content...")
        
        articles = []
        for rss_url in self.config.RSS_SOURCES:
            try:
                feed = feedparser.parse(rss_url)
                print(f"📡 Processing {rss_url}: {len(feed.entries)} articles")
                
                for entry in feed.entries[:5]:  # Limit to 5 per feed
                    article = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': rss_url,
                        'tags': [tag.term for tag in entry.get('tags', [])]
                    }
                    articles.append(article)
                    
            except Exception as e:
                print(f"❌ Error fetching {rss_url}: {e}")
                
        print(f"📝 Total articles fetched: {len(articles)}")
        return articles
    
    def score_content(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Score content for relevance and virality"""
        print(f"🎯 Scoring: {article['title'][:50]}...")
        
        prompt = f"""
        Score this article for relevance to AI headshots and personal branding:
        
        Title: {article['title']}
        Summary: {article['summary']}
        Tags: {', '.join(article['tags'])}
        
        Rate on a scale of 1-10:
        1. Relevance to AI headshots/personal branding
        2. Virality potential (engagement, shareability)
        3. Quality of content
        
        Respond with JSON: {{"relevance": X, "virality": Y, "quality": Z, "reasoning": "explanation"}}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            score_data = json.loads(response.choices[0].message.content)
            
            # Calculate overall score
            overall_score = (score_data['relevance'] + score_data['virality'] + score_data['quality']) / 3
            
            return {
                'relevance': score_data['relevance'],
                'virality': score_data['virality'],
                'quality': score_data['quality'],
                'overall': overall_score,
                'reasoning': score_data['reasoning']
            }
            
        except Exception as e:
            print(f"❌ Error scoring content: {e}")
            return {'relevance': 0, 'virality': 0, 'quality': 0, 'overall': 0, 'reasoning': 'Error'}
    
    def generate_blog_post(self, article: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a blog post from the article"""
        print(f"✍️ Generating blog post: {article['title'][:50]}...")
        
        prompt = f"""
        Create a blog post for Brightface.ai (AI headshot service) based on this article:
        
        Original Article:
        Title: {article['title']}
        Summary: {article['summary']}
        Link: {article['link']}
        
        Scoring:
        Relevance: {scores['relevance']}/10
        Virality: {scores['virality']}/10
        Quality: {scores['quality']}/10
        Reasoning: {scores['reasoning']}
        
        Create a blog post that:
        1. Connects the article to AI headshots and personal branding
        2. Provides value to professionals looking to improve their online presence
        3. Includes actionable insights
        4. Maintains a professional but engaging tone
        5. Includes relevant hashtags
        
        Format as JSON:
        {{
            "title": "Blog post title",
            "excerpt": "Brief description",
            "content": "Full blog post content in markdown",
            "tags": ["tag1", "tag2", "tag3"],
            "seo_title": "SEO optimized title",
            "seo_description": "SEO meta description"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            blog_data = json.loads(response.choices[0].message.content)
            
            # Add metadata
            blog_data['original_article'] = article
            blog_data['scores'] = scores
            blog_data['generated_at'] = datetime.now().isoformat()
            
            return blog_data
            
        except Exception as e:
            print(f"❌ Error generating blog post: {e}")
            return None
    
    def publish_to_notion(self, blog_post: Dict[str, Any]) -> bool:
        """Publish the blog post to Notion"""
        print(f"📝 Publishing to Notion: {blog_post['title'][:50]}...")
        
        try:
            # Generate slug from title
            slug = blog_post['title'].lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '')
            
            # Create the page in Notion
            page_data = {
                "parent": {"database_id": self.config.NOTION_DB_ID},
                "properties": {
                    "Name": {"title": [{"text": {"content": blog_post['title']}}]},
                    "Slug": {"rich_text": [{"text": {"content": slug}}]},
                    "Excerpt": {"rich_text": [{"text": {"content": blog_post['excerpt']}}]},
                    "Status": {"select": {"name": "Published"}},
                    "Tags": {"multi_select": [{"name": tag} for tag in blog_post['tags']]},
                    "SEO Title": {"rich_text": [{"text": {"content": blog_post['seo_title']}}]},
                    "SEO Description": {"rich_text": [{"text": {"content": blog_post['seo_description']}}]},
                    "Publish Date": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}
                },
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": blog_post['content']}}]
                        }
                    }
                ]
            }
            
            response = self.notion_client.pages.create(**page_data)
            print(f"✅ Published to Notion: {response['id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error publishing to Notion: {e}")
            return False
    
    def run_automation(self):
        """Run the full automation process"""
        print("🚀 Starting automated content generation...")
        
        # Fetch RSS content
        articles = self.fetch_rss_content()
        
        if not articles:
            print("❌ No articles found")
            return
        
        # Process articles
        for article in articles[:3]:  # Limit to 3 articles per run
            # Score content
            scores = self.score_content(article)
            
            # Only proceed if scores are good enough
            if scores['overall'] >= 7.0:
                print(f"✅ High-scoring content found: {scores['overall']}/10")
                
                # Generate blog post
                blog_post = self.generate_blog_post(article, scores)
                
                if blog_post:
                    # Publish to Notion
                    success = self.publish_to_notion(blog_post)
                    
                    if success:
                        print(f"🎉 Successfully published: {blog_post['title']}")
                    else:
                        print(f"❌ Failed to publish: {blog_post['title']}")
            else:
                print(f"⏭️ Skipping low-scoring content: {scores['overall']}/10")
        
        print("✅ Automation complete!")

def main():
    """Main function"""
    generator = AutomatedContentGenerator()
    generator.run_automation()

if __name__ == "__main__":
    main()
