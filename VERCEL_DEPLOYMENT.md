# 🚀 Brightface Content Engine - Vercel Deployment Guide

## Overview

This guide will help you deploy the Brightface Content Engine to Vercel, leveraging their serverless functions and cron jobs for automated content processing.

## 🏗️ Vercel Architecture

The system is now designed for Vercel with:

- **Serverless Functions**: Each component runs as a separate function
- **Cron Jobs**: Automated scheduling using Vercel's cron feature
- **Web Dashboard**: Real-time monitoring and manual controls
- **Environment Variables**: Secure configuration management

## 📁 Project Structure

```
contentengine/
├── api/                          # Vercel serverless functions
│   ├── rss-processor.py          # RSS processing (every 2 hours)
│   ├── social-publisher.py       # Social posting (4x daily)
│   ├── metrics-updater.py        # Metrics update (daily)
│   ├── content-generator.py      # Manual content generation
│   └── dashboard.py              # Web dashboard
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Python dependencies
├── env.vercel                    # Environment variables template
└── [core modules]                # All existing modules
```

## 🚀 Quick Deployment

### 1. Prerequisites

- Vercel account (free tier works)
- GitHub repository with your code
- API keys for OpenAI, Google Sheets, LinkedIn, Twitter

### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from your project directory
vercel

# Follow the prompts:
# - Link to existing project? No
# - Project name: brightface-content-engine
# - Directory: ./
# - Override settings? No
```

### 3. Configure Environment Variables

In your Vercel dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add all variables from `env.vercel`
3. Set `AUTO_POST=false` initially for testing

### 4. Upload Google Credentials

Since Vercel doesn't support file uploads directly:

1. Convert `credentials.json` to base64:
   ```bash
   base64 -i credentials.json
   ```
2. Add as environment variable `GOOGLE_CREDENTIALS_BASE64`
3. Update `sheets_manager.py` to decode it

## ⚙️ Configuration

### Environment Variables

**Required:**
```bash
OPENAI_API_KEY=sk-...
GOOGLE_SHEETS_ID=1ABC...
GOOGLE_CREDENTIALS_BASE64=eyJ0eXBlIjoi...
```

**Optional (for posting):**
```bash
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...
LINKEDIN_PAGE_ID=...
LINKEDIN_ACCESS_TOKEN=...

TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
TWITTER_BEARER_TOKEN=...
```

**Configuration:**
```bash
AUTO_POST=false                    # Start in review mode
DEFAULT_UTM_CAMPAIGN=autopost
RSS_SOURCES=https://openai.com/blog/rss.xml,https://ai.googleblog.com/feeds/posts/default,...
```

### Cron Schedule

The system runs automatically:

- **RSS Processing**: Every 2 hours (`0 */2 * * *`)
- **Social Posting**: 4 times daily (`30 8,10,15,17 * * *`)
- **Metrics Update**: Daily at 2 AM (`0 2 * * *`)

## 🎛️ Manual Controls

### Web Dashboard

Visit `https://your-app.vercel.app/api/dashboard` for:

- Real-time system status
- Manual content generation
- RSS processing trigger
- Social posting trigger
- Metrics update trigger

### API Endpoints

**Manual Triggers:**
- `GET /api/content-generator` - Generate content now
- `GET /api/rss-processor` - Process RSS feeds now
- `GET /api/social-publisher` - Post to social media now
- `GET /api/metrics-updater` - Update engagement metrics

**Dashboard:**
- `GET /api/dashboard` - Web interface

## 📊 Monitoring

### Vercel Dashboard

- **Functions**: Monitor execution times and errors
- **Cron Jobs**: Check scheduled execution status
- **Logs**: Real-time function logs

### Google Sheets

- **Content Ledger**: All processed content
- **Review Queue**: Items awaiting approval
- **Engagement Metrics**: Post performance data

### Function Logs

```bash
# View logs in Vercel CLI
vercel logs

# Or check in Vercel dashboard
# Functions → [function-name] → Logs
```

## 🔧 Customization

### Adding RSS Sources

Edit `env.vercel` or Vercel environment variables:
```bash
RSS_SOURCES=https://new-source.com/rss,https://another-source.com/feed
```

### Adjusting Schedule

Edit `vercel.json`:
```json
{
  "crons": [
    {
      "path": "/api/rss-processor",
      "schedule": "0 */1 * * *"  // Every hour instead of 2 hours
    }
  ]
}
```

### Quality Thresholds

Update `config.py`:
```python
MIN_RELEVANCE_SCORE = 8  # Stricter filtering
MIN_VIRALITY_SCORE = 7   # Higher engagement focus
```

## 🚨 Troubleshooting

### Common Issues

**Function Timeout:**
- Increase `maxDuration` in `vercel.json`
- Optimize function performance
- Split large operations

**Environment Variables:**
- Check variable names match exactly
- Ensure no extra spaces
- Verify API keys are valid

**Google Sheets Access:**
- Verify `GOOGLE_SHEETS_ID` is correct
- Check `credentials.json` permissions
- Ensure Sheets API is enabled

**Cron Jobs Not Running:**
- Check Vercel Pro plan (required for cron)
- Verify cron syntax in `vercel.json`
- Check function logs for errors

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Functions

Test individual functions:
```bash
# Test RSS processor
curl https://your-app.vercel.app/api/rss-processor

# Test content generator
curl https://your-app.vercel.app/api/content-generator
```

## 💰 Cost Considerations

### Vercel Pricing

**Hobby Plan (Free):**
- 100GB bandwidth
- 100 serverless function executions
- No cron jobs

**Pro Plan ($20/month):**
- Unlimited bandwidth
- 1M serverless function executions
- Cron jobs included
- Team collaboration

### Optimization Tips

- Use cron jobs efficiently (not too frequent)
- Optimize function execution time
- Monitor usage in Vercel dashboard
- Consider caching for repeated operations

## 🔄 Updates and Maintenance

### Deploying Updates

```bash
# Deploy changes
vercel --prod

# Or push to GitHub (if connected)
git push origin main
```

### Environment Updates

1. Update variables in Vercel dashboard
2. Redeploy functions
3. Test with manual triggers

### Monitoring Health

- Check function success rates
- Monitor error logs
- Verify cron job execution
- Review Google Sheets data

## 🎯 Production Checklist

- [ ] All environment variables configured
- [ ] Google Sheets API enabled
- [ ] Social media APIs configured
- [ ] Cron jobs scheduled correctly
- [ ] Dashboard accessible
- [ ] Test functions manually
- [ ] Monitor for 24 hours
- [ ] Enable `AUTO_POST=true` when ready

## 🆘 Support

### Vercel Support
- Documentation: https://vercel.com/docs
- Community: https://github.com/vercel/vercel/discussions

### Content Engine Support
- Check logs in Vercel dashboard
- Review Google Sheets for data
- Test individual functions
- Monitor cron job execution

## 🎉 Success!

Once deployed, your Brightface Content Engine will:

1. **Automatically fetch** RSS feeds every 2 hours
2. **Score and filter** content for relevance
3. **Generate** LinkedIn/X posts and blog drafts
4. **Post to social media** at optimal times
5. **Track everything** in Google Sheets
6. **Provide a dashboard** for monitoring

The system runs 24/7 on Vercel's global infrastructure, ensuring reliable automated content generation for your brand! 🚀
