# 🚀 Vercel Deployment Guide

## Step 1: Push to GitHub

### 1.1 Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Notion API integration for Brightface blog"
```

### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `brightface-notion-blog`
3. Description: `Notion API integration for Brightface blog`
4. Make it **Public** (required for free Vercel)
5. Click "Create repository"

### 1.3 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/brightface-notion-blog.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Vercel

### 2.1 Connect to Vercel
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "New Project"
4. Import your `brightface-notion-blog` repository
5. Click "Import"

### 2.2 Configure Project Settings
- **Framework Preset**: Other
- **Root Directory**: `./` (default)
- **Build Command**: Leave empty (Vercel will auto-detect)
- **Output Directory**: Leave empty
- **Install Command**: `npm install`

### 2.3 Add Environment Variables
In Vercel dashboard, go to Settings → Environment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `NOTION_API_KEY` | `secret_...` | Your Notion integration token |
| `NOTION_DB_ID` | `28bce93d...` | Your database ID |
| `NODE_ENV` | `production` | Environment setting |

### 2.4 Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Get your Vercel URL (e.g., `https://brightface-notion-blog.vercel.app`)

## Step 3: Test Deployment

### 3.1 Test API Endpoints
```bash
# Test health endpoint
curl https://your-app.vercel.app/api/blog/health

# Test posts endpoint
curl https://your-app.vercel.app/api/blog/posts

# Test specific post
curl https://your-app.vercel.app/api/blog/posts/this-is-another-test

# Test RSS feed
curl https://your-app.vercel.app/api/blog/rss
```

### 3.2 Test Demo Interface
Visit: `https://your-app.vercel.app/api/demo`

## Step 4: Custom Domain Setup

### 4.1 Add Domain in Vercel
1. Go to Project Settings → Domains
2. Add `blog.brightface.ai`
3. Follow DNS configuration instructions

### 4.2 Configure DNS
Add these DNS records to your domain provider:

| Type | Name | Value |
|------|------|-------|
| CNAME | `blog` | `cname.vercel-dns.com` |

### 4.3 Verify Domain
- Wait 5-10 minutes for DNS propagation
- Visit `https://blog.brightface.ai/api/blog/health`
- Should return: `{"success":true,"message":"Notion Blog API is running"}`

## 🎯 Expected Results

After deployment, you should have:

✅ **API Endpoints**:
- `https://blog.brightface.ai/api/blog/posts` - All published posts
- `https://blog.brightface.ai/api/blog/posts/:slug` - Specific post
- `https://blog.brightface.ai/api/blog/rss` - RSS feed
- `https://blog.brightface.ai/api/blog/health` - Health check

✅ **Demo Interface**:
- `https://blog.brightface.ai/api/demo` - Live blog preview

✅ **Features**:
- Real-time Notion integration
- Auto-slug generation
- RSS feed for SEO
- Mobile responsive
- No extra costs

## 🔧 Troubleshooting

### Common Issues

**1. "API token is invalid"**
- Check `NOTION_API_KEY` in Vercel environment variables
- Verify integration has database access

**2. "Post not found"**
- Check `NOTION_DB_ID` is correct
- Ensure posts have "Published" set to true

**3. "Function timeout"**
- Vercel has 10-second timeout for free tier
- Consider upgrading to Pro for longer timeouts

**4. "Build failed"**
- Check `package.json` dependencies
- Verify Node.js version compatibility

### Debug Commands

```bash
# Check Vercel logs
vercel logs

# Test locally with production env
NODE_ENV=production npm start

# Verify environment variables
vercel env ls
```

## 📈 Next Steps

1. **Add more content** to Notion database
2. **Customize styling** in demo.html
3. **Add analytics** (Google Analytics, etc.)
4. **Implement caching** for better performance
5. **Add search functionality**
6. **Set up monitoring** (Uptime monitoring, error tracking)

---

**Your Notion-powered blog is now live on Vercel! 🎉**