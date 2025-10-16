# 🚀 Notion API Integration Setup Guide

## Overview
This integration connects your Notion "Blog Posts" database directly to your brightface.ai website via API. No extra costs, full control, and automatic updates when you publish in Notion.

## 📋 Prerequisites
- ✅ Notion Plus plan (you have this)
- ✅ "Brightface Blog" integration created in Notion
- ✅ "Blog Posts" database with proper structure
- ✅ Node.js installed on your system

## 🛠️ Installation Steps

### Step 1: Install Dependencies
```bash
npm install
```

### Step 2: Set Up Environment Variables
Create a `.env` file with your Notion credentials:

```env
# Notion API Configuration
NOTION_API_KEY=your_integration_token_here
NOTION_DB_ID=your_database_id_here

# Server Configuration
PORT=3001
NODE_ENV=development
```

**To get these values:**
1. **NOTION_API_KEY**: From your "Brightface Blog" integration settings
2. **NOTION_DB_ID**: From your "Blog Posts" database URL

### Step 3: Test the Integration
```bash
npm test
```

This will verify your Notion connection and show any published posts.

### Step 4: Start the API Server
```bash
npm start
```

The server will run on `http://localhost:3001`

### Step 5: View the Demo
Open `demo.html` in your browser to see the integration in action.

## 🔌 API Endpoints

### `GET /api/blog/posts`
Fetch all published blog posts
```json
{
  "success": true,
  "data": [
    {
      "id": "post-id",
      "title": "Post Title",
      "slug": "post-slug",
      "excerpt": "Post excerpt...",
      "publishDate": "2024-01-15",
      "tags": ["AI", "Headshots"],
      "author": ["Kenneth Muir"],
      "url": "/blog/post-slug",
      "content": [...]
    }
  ],
  "count": 1
}
```

### `GET /api/blog/posts/:slug`
Fetch a specific post by slug
```json
{
  "success": true,
  "data": {
    "id": "post-id",
    "title": "Post Title",
    "slug": "post-slug",
    "content": [...],
    "seoTitle": "SEO Title",
    "seoDescription": "SEO Description"
  }
}
```

### `GET /api/blog/rss`
Generate RSS feed for your blog

### `GET /api/blog/health`
Health check endpoint

## 🎨 Integration with Your Website

### Option 1: Direct API Calls
```javascript
// Fetch all posts
const response = await fetch('https://your-domain.com/api/blog/posts');
const posts = await response.json();

// Display posts
posts.data.forEach(post => {
    console.log(post.title, post.excerpt);
});
```

### Option 2: Static Site Generation
```javascript
// Generate static pages at build time
const posts = await notionAPI.getPublishedPosts();
posts.forEach(post => {
    generateStaticPage(post);
});
```

### Option 3: Server-Side Rendering
```javascript
// Render posts on the server
app.get('/blog', async (req, res) => {
    const posts = await notionAPI.getPublishedPosts();
    res.render('blog', { posts });
});
```

## 📝 Notion Database Structure

Your "Blog Posts" database should have these properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| Name | Title | ✅ | Blog post title |
| Slug | Rich Text | ✅ | URL-friendly identifier |
| Published | Checkbox | ✅ | Whether post is live |
| Publish Date | Date | ✅ | When to publish |
| Excerpt | Rich Text | ❌ | Short description |
| Tags | Multi-select | ❌ | Categories/tags |
| Author | People | ❌ | Post author |
| SEO Title | Rich Text | ❌ | SEO-optimized title |
| SEO Description | Rich Text | ❌ | Meta description |
| Cover Image | Files | ❌ | Featured image |

## 🚀 Deployment Options

### Option 1: Vercel (Recommended)
1. Push code to GitHub
2. Connect to Vercel
3. Add environment variables
4. Deploy automatically

### Option 2: Your Existing Server
1. Upload files to your server
2. Install dependencies: `npm install`
3. Set environment variables
4. Start with PM2: `pm2 start server.js`

### Option 3: Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

## 🔧 Customization

### Custom Styling
Edit `demo.html` to match your website's design:
- Update CSS variables
- Change color scheme
- Modify layout structure

### Additional Fields
Add more properties to your Notion database:
- Reading time
- Difficulty level
- Related posts
- Custom metadata

### Caching
Implement caching for better performance:
```javascript
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

async function getCachedPosts() {
    const cached = cache.get('posts');
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data;
    }
    
    const posts = await notionAPI.getPublishedPosts();
    cache.set('posts', { data: posts, timestamp: Date.now() });
    return posts;
}
```

## 🐛 Troubleshooting

### Common Issues

**1. "Unauthorized" Error**
- Check your NOTION_API_KEY
- Verify integration has database access
- Ensure database ID is correct

**2. "No posts found"**
- Check "Published" checkbox is true
- Verify "Publish Date" is set
- Ensure database properties match expected names

**3. "Connection refused"**
- Make sure server is running on port 3001
- Check firewall settings
- Verify Node.js is installed

### Debug Mode
Enable debug logging:
```javascript
const DEBUG = process.env.NODE_ENV === 'development';
if (DEBUG) {
    console.log('Debug: API response', response);
}
```

## 📈 Next Steps

1. **Test the integration** with your existing posts
2. **Customize the styling** to match your brand
3. **Deploy to production** (Vercel recommended)
4. **Set up custom domain** (blog.brightface.ai)
5. **Add analytics** and SEO optimization
6. **Implement search** functionality
7. **Add comments** system if needed

## 🎯 Benefits

- ✅ **No extra costs** - uses your existing Notion Plus
- ✅ **Full control** - customize everything
- ✅ **Automatic updates** - publish in Notion, live on website
- ✅ **SEO optimized** - proper meta tags and structure
- ✅ **Mobile responsive** - works on all devices
- ✅ **Fast loading** - optimized API responses
- ✅ **RSS feed** - for subscribers and SEO

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Run `npm test` to verify setup
3. Check server logs for errors
4. Verify Notion database structure

---

**Ready to launch your Notion-powered blog! 🚀**
