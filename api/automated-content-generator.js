/**
 * Automated Content Generator - Node.js Version
 * Runs RSS monitoring, AI scoring, and blog post generation
 */

const fetch = require('node-fetch');
const { Client } = require('@notionhq/client');

// Environment variables
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const NOTION_API_KEY = process.env.NOTION_API_KEY;
const NOTION_DB_ID = process.env.NOTION_DB_ID;

// RSS Sources
const RSS_SOURCES = [
    'https://openai.com/blog/rss.xml',
    'https://ai.googleblog.com/feeds/posts/default',
    'https://www.producthunt.com/feed?category=artificial-intelligence',
    'https://venturebeat.com/ai/feed/',
    'https://techcrunch.com/category/artificial-intelligence/feed/',
    'https://blog.adobe.com/en/topics/firefly/feed.xml',
    'https://engineering.linkedin.com/blog.rss'
];

class AutomatedContentGenerator {
    constructor() {
        this.notion = new Client({ auth: NOTION_API_KEY });
    }

    async fetchRSSContent() {
        console.log('🔍 Fetching RSS content...');
        
        const articles = [];
        
        for (const rssUrl of RSS_SOURCES) {
            try {
                console.log(`📡 Processing ${rssUrl}`);
                
                const response = await fetch(rssUrl);
                const text = await response.text();
                
                // Simple RSS parsing (basic implementation)
                const items = this.parseRSS(text);
                
                for (const item of items.slice(0, 3)) { // Limit to 3 per feed
                    articles.push({
                        title: item.title || '',
                        link: item.link || '',
                        summary: item.description || '',
                        published: item.pubDate || '',
                        source: rssUrl,
                        tags: []
                    });
                }
                
                console.log(`✅ Found ${items.length} articles from ${rssUrl}`);
                
            } catch (error) {
                console.error(`❌ Error fetching ${rssUrl}:`, error.message);
            }
        }
        
        console.log(`📝 Total articles fetched: ${articles.length}`);
        return articles;
    }

    parseRSS(xmlText) {
        // Basic RSS parsing - extract items between <item> tags
        const items = [];
        const itemRegex = /<item>([\s\S]*?)<\/item>/g;
        let match;
        
        while ((match = itemRegex.exec(xmlText)) !== null) {
            const itemContent = match[1];
            
            const title = this.extractTag(itemContent, 'title');
            const link = this.extractTag(itemContent, 'link');
            const description = this.extractTag(itemContent, 'description');
            const pubDate = this.extractTag(itemContent, 'pubDate');
            
            if (title) {
                items.push({
                    title: this.cleanText(title),
                    link: this.cleanText(link),
                    description: this.cleanText(description),
                    pubDate: this.cleanText(pubDate)
                });
            }
        }
        
        return items;
    }

    extractTag(content, tagName) {
        const regex = new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)<\\/${tagName}>`, 'i');
        const match = content.match(regex);
        return match ? match[1].trim() : '';
    }

    cleanText(text) {
        return text
            .replace(/<[^>]*>/g, '') // Remove HTML tags
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .trim();
    }

    async scoreContent(article) {
        console.log(`🎯 Scoring: ${article.title.substring(0, 50)}...`);
        
        const prompt = `Score this article for relevance to AI headshots and personal branding:

Title: ${article.title}
Summary: ${article.summary}

Rate on a scale of 1-10:
1. Relevance to AI headshots/personal branding
2. Virality potential (engagement, shareability)
3. Quality of content

Respond with JSON: {"relevance": X, "virality": Y, "quality": Z, "reasoning": "explanation"}`;

        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${OPENAI_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: 'gpt-4',
                    messages: [{ role: 'user', content: prompt }],
                    temperature: 0.3
                })
            });

            const data = await response.json();
            const scoreData = JSON.parse(data.choices[0].message.content);
            
            const overallScore = (scoreData.relevance + scoreData.virality + scoreData.quality) / 3;
            
            return {
                relevance: scoreData.relevance,
                virality: scoreData.virality,
                quality: scoreData.quality,
                overall: overallScore,
                reasoning: scoreData.reasoning
            };
            
        } catch (error) {
            console.error('❌ Error scoring content:', error);
            return { relevance: 0, virality: 0, quality: 0, overall: 0, reasoning: 'Error' };
        }
    }

    async generateBlogPost(article, scores) {
        console.log(`✍️ Generating blog post: ${article.title.substring(0, 50)}...`);
        
        const prompt = `Create a blog post for Brightface.ai (AI headshot service) based on this article:

Original Article:
Title: ${article.title}
Summary: ${article.summary}
Link: ${article.link}

Scoring:
Relevance: ${scores.relevance}/10
Virality: ${scores.virality}/10
Quality: ${scores.quality}/10
Reasoning: ${scores.reasoning}

Create a blog post that:
1. Connects the article to AI headshots and personal branding
2. Provides value to professionals looking to improve their online presence
3. Includes actionable insights
4. Maintains a professional but engaging tone
5. Includes relevant hashtags

Format as JSON:
{
    "title": "Blog post title",
    "excerpt": "Brief description",
    "content": "Full blog post content in markdown",
    "tags": ["tag1", "tag2", "tag3"],
    "seo_title": "SEO optimized title",
    "seo_description": "SEO meta description"
}`;

        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${OPENAI_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: 'gpt-4',
                    messages: [{ role: 'user', content: prompt }],
                    temperature: 0.7
                })
            });

            const data = await response.json();
            const blogData = JSON.parse(data.choices[0].message.content);
            
            blogData.original_article = article;
            blogData.scores = scores;
            blogData.generated_at = new Date().toISOString();
            
            return blogData;
            
        } catch (error) {
            console.error('❌ Error generating blog post:', error);
            return null;
        }
    }

    async publishToNotion(blogPost) {
        console.log(`📝 Publishing to Notion: ${blogPost.title.substring(0, 50)}...`);
        
        try {
            const slug = blogPost.title
                .toLowerCase()
                .replace(/[^a-z0-9\s-]/g, '')
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-')
                .trim();

            const pageData = {
                parent: { database_id: NOTION_DB_ID },
                properties: {
                    Name: { title: [{ text: { content: blogPost.title } }] },
                    Slug: { rich_text: [{ text: { content: slug } }] },
                    Excerpt: { rich_text: [{ text: { content: blogPost.excerpt } }] },
                    Status: { select: { name: 'Draft' } },
                    Tags: { multi_select: blogPost.tags.map(tag => ({ name: tag })) },
                    'SEO Title': { rich_text: [{ text: { content: blogPost.seo_title } }] },
                    'SEO Description': { rich_text: [{ text: { content: blogPost.seo_description } }] },
                    'Publish Date': { date: { start: new Date().toISOString().split('T')[0] } }
                },
                children: [
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [{ text: { content: blogPost.content } }]
                        }
                    }
                ]
            };

            const response = await this.notion.pages.create(pageData);
            console.log(`✅ Published to Notion: ${response.id}`);
            return true;
            
        } catch (error) {
            console.error('❌ Error publishing to Notion:', error);
            return false;
        }
    }

    async runAutomation() {
        console.log('🚀 Starting automated content generation...');
        
        try {
            // Fetch RSS content
            const articles = await this.fetchRSSContent();
            
            if (articles.length === 0) {
                console.log('❌ No articles found');
                return { success: false, message: 'No articles found' };
            }

            let publishedCount = 0;
            
            // Process articles (limit to 2 for testing)
            for (const article of articles.slice(0, 2)) {
                // Score content
                const scores = await this.scoreContent(article);
                
                // Only proceed if scores are good enough
                if (scores.overall >= 4.0) { // Lowered threshold for testing
                    console.log(`✅ High-scoring content found: ${scores.overall}/10`);
                    
                    // Generate blog post
                    const blogPost = await this.generateBlogPost(article, scores);
                    
                    if (blogPost) {
                        // Publish to Notion
                        const success = await this.publishToNotion(blogPost);
                        
                        if (success) {
                            publishedCount++;
                            console.log(`🎉 Successfully published: ${blogPost.title}`);
                        } else {
                            console.log(`❌ Failed to publish: ${blogPost.title}`);
                        }
                    }
                } else {
                    console.log(`⏭️ Skipping low-scoring content: ${scores.overall}/10`);
                }
            }
            
            console.log('✅ Automation complete!');
            return { 
                success: true, 
                message: `Processed ${articles.length} articles, published ${publishedCount} posts`,
                articlesProcessed: articles.length,
                postsPublished: publishedCount
            };
            
        } catch (error) {
            console.error('❌ Error in automation:', error);
            return { success: false, error: error.message };
        }
    }
}

module.exports = async (req, res) => {
    try {
        console.log(`🕐 Automated content generation started at ${new Date().toISOString()}`);
        
        // Check required environment variables
        if (!OPENAI_API_KEY || !NOTION_API_KEY || !NOTION_DB_ID) {
            return res.status(500).json({
                success: false,
                error: 'Missing required environment variables',
                required: ['OPENAI_API_KEY', 'NOTION_API_KEY', 'NOTION_DB_ID']
            });
        }
        
        // Initialize the content generator
        const generator = new AutomatedContentGenerator();
        
        // Run the automation
        const result = await generator.runAutomation();
        
        res.status(200).json({
            ...result,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('❌ Error in cron job:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
};
