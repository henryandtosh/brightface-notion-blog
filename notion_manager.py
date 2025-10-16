"""
Notion Integration for Brightface Content Engine
Handles blog draft creation and management in Notion
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import requests

from models import BlogDraft, ContentItem
from config import Config

logger = logging.getLogger(__name__)

class NotionManager:
    """Manages Notion integration for blog drafts"""
    
    def __init__(self):
        self.api_key = Config.NOTION_API_KEY
        self.database_id = Config.NOTION_DB_ID
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_blog_draft(self, content_item: ContentItem) -> Optional[str]:
        """Create a blog draft in Notion"""
        try:
            if not content_item.generated_content or not content_item.generated_content.blog:
                logger.error("No blog content to create in Notion")
                return None
            
            blog_draft = content_item.generated_content.blog
            
            # Prepare the page data
            page_data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": blog_draft.title
                                }
                            }
                        ]
                    },
                    "Slug": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": blog_draft.slug
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": "Draft"
                        }
                    },
                    "SEO Description": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": blog_draft.meta_description
                                }
                            }
                        ]
                    },
                    "Author": {
                        "people": [
                            {
                                "object": "user",
                                "name": "Brightface AI"
                            }
                        ]
                    },
                    "Tags": {
                        "multi_select": [
                            {"name": "AI Headshots"},
                            {"name": "Personal Branding"},
                            {"name": "Content Marketing"}
                        ]
                    },
                    "Source URL": {
                        "url": content_item.rss_item.url
                    },
                    "Created Date": {
                        "date": {
                            "start": datetime.now().isoformat()
                        }
                    },
                    "Relevance Score": {
                        "number": content_item.score.relevance_score if content_item.score else 0
                    },
                    "Virality Score": {
                        "number": content_item.score.virality_score if content_item.score else 0
                    }
                },
                "children": self._create_blog_content_blocks(blog_draft)
            }
            
            # Create the page
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                page_id = result["id"]
                page_url = f"https://notion.so/{page_id.replace('-', '')}"
                
                logger.info(f"Created Notion blog draft: {page_url}")
                return page_url
            else:
                logger.error(f"Failed to create Notion page: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Notion blog draft: {e}")
            return None
    
    def _create_blog_content_blocks(self, blog_draft: BlogDraft) -> list:
        """Create Notion content blocks from blog draft"""
        blocks = []
        
        # Add meta description as a callout
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"SEO Description: {blog_draft.meta_description}"
                        }
                    }
                ],
                "icon": {
                    "emoji": "📝"
                }
            }
        })
        
        # Add outline
        if blog_draft.outline:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "Article Outline"
                            }
                        }
                    ]
                }
            })
            
            for item in blog_draft.outline:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": item
                                }
                            }
                        ]
                    }
                })
        
        # Add the main content
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Article Content"
                        }
                    }
                ]
            }
        })
        
        # Parse markdown content into Notion blocks
        content_blocks = self._parse_markdown_to_blocks(blog_draft.body_md)
        blocks.extend(content_blocks)
        
        # Add source information
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Source Information"
                        }
                    }
                ]
            }
        })
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"Original article: {blog_draft.title}",
                            "link": {
                                "url": "https://example.com"  # Will be replaced with actual source URL
                            }
                        }
                    }
                ]
            }
        })
        
        return blocks
    
    def _parse_markdown_to_blocks(self, markdown_content: str) -> list:
        """Parse markdown content into Notion blocks"""
        blocks = []
        lines = markdown_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('## '):
                # H2 heading
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[3:]
                                }
                            }
                        ]
                    }
                })
            elif line.startswith('### '):
                # H3 heading
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[4:]
                                }
                            }
                        ]
                    }
                })
            elif line.startswith('- '):
                # Bullet point
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[2:]
                                }
                            }
                        ]
                    }
                })
            elif line.startswith('1. '):
                # Numbered list
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line[3:]
                                }
                            }
                        ]
                    }
                })
            else:
                # Regular paragraph
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": line
                                }
                            }
                        ]
                    }
                })
        
        return blocks
    
    def update_blog_status(self, page_id: str, status: str) -> bool:
        """Update the status of a blog draft"""
        try:
            update_data = {
                "properties": {
                    "Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            }
            
            response = requests.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Updated blog status to {status}")
                return True
            else:
                logger.error(f"Failed to update blog status: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating blog status: {e}")
            return False
    
    def get_blog_drafts(self, status: str = "Draft") -> list:
        """Get blog drafts with specific status"""
        try:
            query_data = {
                "filter": {
                    "property": "Status",
                    "select": {
                        "equals": status
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/databases/{self.database_id}/query",
                headers=self.headers,
                json=query_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("results", [])
            else:
                logger.error(f"Failed to get blog drafts: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting blog drafts: {e}")
            return []
    
    def create_database(self) -> bool:
        """Create the blog drafts database in Notion"""
        try:
            # This would typically be done manually in Notion
            # But we can provide the schema
            database_schema = {
                "Title": {"title": {}},
                "Slug": {"rich_text": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Draft", "color": "yellow"},
                            {"name": "Ready", "color": "blue"},
                            {"name": "Published", "color": "green"},
                            {"name": "Archived", "color": "gray"}
                        ]
                    }
                },
                "SEO Description": {"rich_text": {}},
                "Author": {"people": {}},
                "Tags": {"multi_select": {}},
                "Source URL": {"url": {}},
                "Created Date": {"date": {}},
                "Relevance Score": {"number": {}},
                "Virality Score": {"number": {}}
            }
            
            logger.info("Database schema created. Please create the database manually in Notion with this schema.")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            return False
