# 🤖 Automated Content Engine Setup

## 🎯 **What This Does**

Your content engine will now automatically:

1. **📡 Monitor RSS Feeds**: Check AI/tech news sources every Monday & Thursday
2. **🎯 Score Content**: Use AI to evaluate relevance to AI headshots/personal branding
3. **✍️ Generate Blog Posts**: Create original content connecting news to your business
4. **📝 Publish to Notion**: Automatically add posts to your blog database
5. **🌐 Update Your Blog**: New posts appear on your website instantly

## 🔧 **Setup Steps**

### **1. Add Environment Variables to Vercel**

You need to add these to your Vercel project:

```bash
# Required for AI content generation
vercel env add OPENAI_API_KEY
# Your OpenAI API key (get from https://platform.openai.com/api-keys)

# Required for content tracking
vercel env add GOOGLE_SHEETS_ID  
# Your Google Sheets ID for content ledger

# Optional: Enable auto-posting
vercel env add AUTO_POST
# Set to "true" to enable automatic posting
```

### **2. Deploy the Updated System**

```bash
git add .
git commit -m "Add automated content generation"
git push
vercel --prod
```

### **3. Test the Automation**

```bash
# Test the content generator manually
curl https://contentengine-blond.vercel.app/api/automated-content-generator
```

## ⏰ **Schedule**

- **Runs**: Every Monday & Thursday at 11:00 AM UTC
- **Processes**: Up to 3 high-scoring articles per run
- **Threshold**: Only content scoring 7+/10 gets published

## 📊 **RSS Sources Monitored**

- OpenAI Blog
- Google AI Blog  
- Product Hunt AI
- VentureBeat AI
- TechCrunch AI
- Adobe Firefly Blog
- LinkedIn Engineering Blog

## 🎯 **Content Scoring**

AI evaluates each article on:
- **Relevance** (1-10): How relevant to AI headshots/personal branding
- **Virality** (1-10): Engagement and shareability potential  
- **Quality** (1-10): Content quality and value

Only articles with **7+ overall score** get turned into blog posts.

## 📝 **Generated Content**

Each blog post includes:
- **Title**: SEO-optimized headline
- **Excerpt**: Brief description
- **Content**: Full article in markdown
- **Tags**: Relevant categories
- **SEO Meta**: Title and description
- **Slug**: URL-friendly identifier

## 🔍 **Monitoring**

Check your automation:
- **Vercel Logs**: View cron job execution
- **Notion Database**: See new published posts
- **Your Blog**: Visit `https://contentengine-blond.vercel.app/blog`

## 🛠️ **Customization**

### **Change Schedule**
Edit `vercel.json` cron schedule:
```json
"crons": [
  {
    "path": "/api/automated-content-generator", 
    "schedule": "0 11 * * 1,4"  // Mon/Thu 11:00 AM UTC
  }
]
```

### **Add RSS Sources**
Edit `config.py` RSS_SOURCES list:
```python
RSS_SOURCES = [
    'https://your-feed-url.com/rss',
    # ... existing feeds
]
```

### **Adjust Scoring Threshold**
Edit `automated_content_generator.py`:
```python
if scores['overall'] >= 7.0:  # Change this threshold
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **No posts generated**: Check OpenAI API key and scoring threshold
2. **Cron not running**: Verify Vercel Pro plan (required for cron jobs)
3. **Notion errors**: Check API key and database permissions
4. **RSS errors**: Verify feed URLs are accessible

### **Manual Testing**

```bash
# Test RSS fetching
python3 automated_content_generator.py

# Test individual components
python3 -c "from automated_content_generator import AutomatedContentGenerator; g = AutomatedContentGenerator(); print(g.fetch_rss_content())"
```

## 🎉 **Success Indicators**

- ✅ Cron job runs without errors
- ✅ New posts appear in Notion database
- ✅ Posts show up on your blog website
- ✅ Content is relevant and high-quality

## 📈 **Next Steps**

1. **Monitor**: Check first few automated posts
2. **Refine**: Adjust scoring criteria if needed
3. **Scale**: Add more RSS sources
4. **Integrate**: Connect to social media posting
5. **Analyze**: Track performance and engagement

Your content engine is now fully automated! 🚀
