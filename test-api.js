/**
 * Test script for Notion Blog API
 * Run this to verify your Notion integration is working
 */

require('dotenv').config();
const NotionBlogAPI = require('./notion-api');

async function testNotionAPI() {
    console.log('🧪 Testing Notion Blog API...\n');

    // Check environment variables
    if (!process.env.NOTION_API_KEY) {
        console.error('❌ NOTION_API_KEY not found in environment variables');
        return;
    }

    if (!process.env.NOTION_DB_ID) {
        console.error('❌ NOTION_DB_ID not found in environment variables');
        return;
    }

    console.log('✅ Environment variables found');
    console.log(`📝 Database ID: ${process.env.NOTION_DB_ID.substring(0, 8)}...`);

    try {
        // Initialize API
        const notionAPI = new NotionBlogAPI(
            process.env.NOTION_API_KEY,
            process.env.NOTION_DB_ID
        );

        // Test fetching posts
        console.log('\n📖 Fetching published posts...');
        const posts = await notionAPI.getPublishedPosts();
        
        if (posts.length === 0) {
            console.log('ℹ️  No published posts found. Make sure to:');
            console.log('   1. Add a blog post to your Notion database');
            console.log('   2. Set "Published" to true');
            console.log('   3. Add a "Publish Date"');
        } else {
            console.log(`✅ Found ${posts.length} published posts:`);
            posts.forEach((post, index) => {
                console.log(`   ${index + 1}. ${post.title} (${post.slug})`);
            });
        }

        // Test RSS generation
        console.log('\n📡 Testing RSS feed generation...');
        const rss = await notionAPI.generateRSSFeed();
        console.log('✅ RSS feed generated successfully');
        console.log(`   Length: ${rss.length} characters`);

        console.log('\n🎉 All tests passed! Your Notion integration is working.');

    } catch (error) {
        console.error('❌ Error testing Notion API:', error.message);
        
        if (error.message.includes('Unauthorized')) {
            console.log('\n💡 Troubleshooting:');
            console.log('   1. Check your NOTION_API_KEY is correct');
            console.log('   2. Make sure your integration has access to the database');
            console.log('   3. Verify the database ID is correct');
        }
    }
}

// Run the test
testNotionAPI();
