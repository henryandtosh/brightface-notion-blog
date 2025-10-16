# 🚀 Notion Integration Setup for Brightface Content Engine

## Overview

This guide will help you set up Notion integration for your blog-focused content engine, including connecting it to your brightface.ai domain.

## 📋 Prerequisites

- ✅ **Notion Plus Plan** ($8/month) - Already upgraded!
- ✅ **brightface.ai domain** - Your custom domain
- ✅ **Vercel deployment** - For hosting the content engine

## 🔧 Step 1: Create Notion Database

### 1.1 Create New Database

1. Go to your Notion workspace
2. Create a new page called "Brightface Blog Drafts"
3. Add a database with the following properties:

### 1.2 Database Schema

| Property Name | Type | Description |
|---------------|------|-------------|
| **Title** | Title | Blog post title |
| **Slug** | Rich Text | URL-friendly slug |
| **Status** | Select | Draft, Ready, Published, Archived |
| **SEO Description** | Rich Text | Meta description (140-160 chars) |
| **Author** | People | Content author (default: Brightface AI) |
| **Tags** | Multi-select | AI Headshots, Personal Branding, Content Marketing |
| **Source URL** | URL | Original article URL |
| **Created Date** | Date | When draft was created |
| **Relevance Score** | Number | AI relevance score (0-10) |
| **Virality Score** | Number | AI virality score (0-10) |

### 1.3 Status Options

Configure the Status select property with these options:
- **Draft** (Yellow) - Newly created, needs review
- **Ready** (Blue) - Reviewed and ready to publish
- **Published** (Green) - Live on website
- **Archived** (Gray) - Old or rejected content

## 🔑 Step 2: Get Notion API Access

### 2.1 Create Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Fill in details:
   - **Name**: Brightface Content Engine
   - **Logo**: Upload Brightface logo (optional)
   - **Associated workspace**: Select your workspace
4. Click "Submit"

### 2.2 Get API Key

1. Copy the "Internal Integration Token" (starts with `secret_`)
2. This is your `NOTION_API_KEY`

### 2.3 Get Database ID

1. Open your "Brightface Blog Drafts" database
2. Copy the URL: `https://notion.so/your-workspace/DATABASE_ID?v=...`
3. Extract the `DATABASE_ID` from the URL
4. This is your `NOTION_DB_ID`

### 2.4 Share Database with Integration

1. In your database, click "Share" in the top right
2. Click "Add people, emails, groups, or integrations"
3. Search for "Brightface Content Engine"
4. Select your integration and click "Invite"

## 🌐 Step 3: Connect to brightface.ai Domain

### 3.1 Notion Custom Domain Setup

1. Go to your Notion workspace settings
2. Navigate to "Settings & members" → "Domains"
3. Click "Add a domain"
4. Enter: `blog.brightface.ai` (or `brightface.ai/blog`)
5. Follow Notion's DNS setup instructions

### 3.2 DNS Configuration

Add these DNS records to your domain provider:

```
Type: CNAME
Name: blog (or blog.brightface.ai)
Value: notion.so
TTL: 3600
```

### 3.3 SSL Certificate

Notion will automatically provision an SSL certificate for your custom domain.

## ⚙️ Step 4: Configure Environment Variables

### 4.1 Vercel Environment Variables

In your Vercel dashboard, add these variables:

```bash
# Notion Integration
NOTION_API_KEY=secret_your_integration_token_here
NOTION_DB_ID=your_database_id_here

# Blog-focused configuration
BLOG_ONLY_MODE=true
BLOG_PUBLISHING_SCHEDULE=0 11 * * 1,4

# Other required variables
OPENAI_API_KEY=sk-your_openai_key
GOOGLE_SHEETS_ID=your_sheets_id
GOOGLE_CREDENTIALS_BASE64=your_base64_credentials
```

### 4.2 Test Configuration

Test your Notion integration:

```bash
# Test the blog generator
curl https://your-app.vercel.app/api/blog-generator
```

## 🎯 Step 5: Content Workflow

### 5.1 Automated Process

1. **RSS Processing**: Every 2 hours, system fetches new articles
2. **AI Scoring**: Content is scored for relevance and virality
3. **Blog Generation**: AI creates blog drafts (Mon/Thu 11:00 AM)
4. **Notion Creation**: Drafts are automatically created in Notion
5. **Review Process**: You review and edit drafts in Notion
6. **Publishing**: Publish directly from Notion to your website

### 5.2 Manual Controls

- **Web Dashboard**: `https://your-app.vercel.app/api/dashboard`
- **Manual Generation**: `https://your-app.vercel.app/api/blog-generator`
- **Notion Database**: Direct access to all drafts

## 📊 Step 6: Content Management

### 6.1 Draft Review Process

1. **New Drafts**: Appear in Notion with "Draft" status
2. **Review Content**: Edit title, content, SEO description
3. **Update Status**: Change to "Ready" when approved
4. **Publish**: Use your website's publishing workflow
5. **Archive**: Mark as "Archived" when done

### 6.2 Content Quality

- **Relevance Score**: ≥7 required for blog generation
- **Virality Score**: ≥6 required for blog generation
- **Content Length**: 600-900 words
- **SEO Optimized**: Title ≤60 chars, meta description 140-160 chars
- **Brand Compliant**: Includes Brightface CTAs and links

## 🔍 Step 7: Monitoring & Analytics

### 7.1 Notion Analytics

- Track draft creation rates
- Monitor review times
- Analyze content performance
- Manage content pipeline

### 7.2 Vercel Monitoring

- Function execution logs
- Error tracking
- Performance metrics
- Cron job status

## 🚨 Troubleshooting

### Common Issues

**Notion API Errors:**
- Check API key is correct
- Verify database ID is correct
- Ensure integration has access to database

**Domain Connection Issues:**
- Verify DNS records are correct
- Check SSL certificate status
- Test domain accessibility

**Content Generation Issues:**
- Check OpenAI API key
- Verify RSS feeds are working
- Review quality filter settings

### Debug Mode

Enable debug logging in Vercel:
```bash
# Check function logs
vercel logs --follow
```

## 🎉 Success!

Once configured, your system will:

1. **Automatically generate** blog drafts from RSS feeds
2. **Create Notion pages** with full content and metadata
3. **Provide review workflow** in Notion interface
4. **Enable custom domain** access via blog.brightface.ai
5. **Track everything** in Google Sheets and Notion

## 📈 Expected Results

- **2 blog drafts per week** (Monday/Thursday)
- **High-quality content** focused on AI headshots and personal branding
- **SEO-optimized** titles and descriptions
- **Brand-compliant** content with Brightface CTAs
- **Streamlined workflow** from draft to publication

Your blog content engine is now ready to generate high-quality, SEO-optimized blog posts automatically! 🚀
