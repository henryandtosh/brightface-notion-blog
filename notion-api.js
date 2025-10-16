/**
 * Notion API Integration for Brightface Blog
 * Fetches blog posts from Notion and formats them for website display
 */

const { Client } = require('@notionhq/client');

class NotionBlogAPI {
    constructor(apiKey, databaseId) {
        this.notion = new Client({ auth: apiKey });
        this.databaseId = databaseId;
    }

    /**
     * Fetch all published blog posts from Notion
     */
    async getPublishedPosts() {
        try {
            const response = await this.notion.databases.query({
                database_id: this.databaseId,
                filter: {
                    property: 'Published',
                    checkbox: {
                        equals: true
                    }
                },
                sorts: [
                    {
                        property: 'Publish Date',
                        direction: 'descending'
                    }
                ]
            });
            return await this.formatPosts(response.results);
        } catch (error) {
            console.error('Error fetching posts:', error);
            return [];
        }
    }

    /**
     * Fetch a specific blog post by slug
     */
    async getPostBySlug(slug) {
        try {
            const response = await this.notion.databases.query({
                database_id: this.databaseId,
                filter: {
                    property: 'Slug',
                    rich_text: {
                        equals: slug
                    }
                }
            });

            if (response.results.length === 0) {
                return null;
            }

            return await this.formatPost(response.results[0]);
        } catch (error) {
            console.error('Error fetching post:', error);
            return null;
        }
    }

    /**
     * Format multiple posts for display
     */
    async formatPosts(posts) {
        return Promise.all(posts.map(post => this.formatPost(post)));
    }

    /**
     * Format a single post for display
     */
    async formatPost(post) {
        const properties = post.properties;
        const title = this.getPropertyValue(properties.Name, 'title');
        const slug = this.getPropertyValue(properties.Slug, 'rich_text') || this.generateSlug(title);
        
        return {
            id: post.id,
            title: title,
            slug: slug,
            excerpt: this.getPropertyValue(properties.Excerpt, 'rich_text'),
            publishDate: this.getPropertyValue(properties['Publish Date'], 'date'),
            tags: this.getPropertyValue(properties.Tags, 'multi_select'),
            author: this.getPropertyValue(properties.Author, 'people'),
            seoTitle: this.getPropertyValue(properties['SEO Title'], 'rich_text'),
            seoDescription: this.getPropertyValue(properties['SEO Description'], 'rich_text'),
            coverImage: this.getPropertyValue(properties['Cover Image'], 'files'),
            icon: post.icon,
            cover: post.cover,
            content: await this.getPostContent(post.id),
            url: `/blog/${slug}`,
            createdAt: post.created_time,
            updatedAt: post.last_edited_time
        };
    }

    /**
     * Generate a URL-friendly slug from title
     */
    generateSlug(title) {
        if (!title) return 'untitled';
        return title
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '') // Remove special characters
            .replace(/\s+/g, '-') // Replace spaces with hyphens
            .replace(/-+/g, '-') // Replace multiple hyphens with single
            .trim();
    }

    /**
     * Extract property value based on type
     */
    getPropertyValue(property, type) {
        if (!property || !property[type]) return null;
        
        switch (type) {
            case 'title':
                return property.title[0]?.plain_text || '';
            case 'rich_text':
                return property.rich_text[0]?.plain_text || '';
            case 'date':
                return property.date?.start || null;
            case 'multi_select':
                return property.multi_select.map(tag => tag.name);
            case 'people':
                return property.people.map(person => person.name);
            case 'files':
                return property.files[0]?.file?.url || null;
            case 'checkbox':
                return property.checkbox;
            default:
                return null;
        }
    }

    /**
     * Get the full content of a blog post
     */
    async getPostContent(pageId) {
        try {
            const response = await this.notion.blocks.children.list({
                block_id: pageId
            });

            return this.formatContent(response.results);
        } catch (error) {
            console.error('Error fetching post content:', error);
            return [];
        }
    }

    /**
     * Format Notion blocks - return raw blocks for proper formatting
     */
    formatContent(blocks) {
        return {
            blocks: blocks,
            children: blocks
        };
    }

    /**
     * Generate RSS feed for blog posts
     */
    async generateRSSFeed() {
        const posts = await this.getPublishedPosts();
        const siteUrl = 'https://brightface.ai';
        
        const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>Brightface Blog</title>
        <description>AI headshots and personal branding insights</description>
        <link>${siteUrl}/blog</link>
        <atom:link href="${siteUrl}/blog/rss.xml" rel="self" type="application/rss+xml"/>
        ${posts.map(post => `
        <item>
            <title>${post.title}</title>
            <description>${post.excerpt}</description>
            <link>${siteUrl}${post.url}</link>
            <guid>${siteUrl}${post.url}</guid>
            <pubDate>${new Date(post.publishDate).toUTCString()}</pubDate>
        </item>`).join('')}
    </channel>
</rss>`;
        
        return rss;
    }
}

module.exports = NotionBlogAPI;
