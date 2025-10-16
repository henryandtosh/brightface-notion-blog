/**
 * Express API Server for Notion Blog Integration
 * Provides REST endpoints for your website to fetch blog posts
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const NotionBlogAPI = require('./notion-api');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Notion API
const notionAPI = new NotionBlogAPI(
    process.env.NOTION_API_KEY,
    process.env.NOTION_DB_ID
);

/**
 * GET /api/blog/posts
 * Fetch all published blog posts
 */
app.get('/api/blog/posts', async (req, res) => {
    try {
        console.log('🔍 Fetching published posts...');
        const posts = await notionAPI.getPublishedPosts();
        console.log(`📝 Found ${posts.length} posts`);
        res.json({
            success: true,
            data: posts,
            count: posts.length
        });
    } catch (error) {
        console.error('❌ Error fetching posts:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * GET /api/blog/posts/:slug
 * Fetch a specific blog post by slug
 */
app.get('/api/blog/posts/:slug', async (req, res) => {
    try {
        const posts = await notionAPI.getPublishedPosts();
        const post = posts.find(p => p.slug === req.params.slug);
        
        if (!post) {
            return res.status(404).json({
                success: false,
                error: 'Post not found'
            });
        }

        res.json({
            success: true,
            data: post
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * GET /api/blog/rss
 * Generate RSS feed for blog posts
 */
app.get('/api/blog/rss', async (req, res) => {
    try {
        const rss = await notionAPI.generateRSSFeed();
        res.set('Content-Type', 'application/rss+xml');
        res.send(rss);
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * GET /api/blog/health
 * Health check endpoint
 */
app.get('/api/blog/health', (req, res) => {
    res.json({
        success: true,
        message: 'Notion Blog API is running',
        timestamp: new Date().toISOString()
    });
});

/**
 * Error handling middleware
 */
app.use((error, req, res, next) => {
    console.error('API Error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error'
    });
});

/**
 * 404 handler
 */
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Notion Blog API running on port ${PORT}`);
    console.log(`📝 Available endpoints:`);
    console.log(`   GET /api/blog/posts - Fetch all posts`);
    console.log(`   GET /api/blog/posts/:slug - Fetch specific post`);
    console.log(`   GET /api/blog/rss - RSS feed`);
    console.log(`   GET /api/blog/health - Health check`);
});

module.exports = app;
