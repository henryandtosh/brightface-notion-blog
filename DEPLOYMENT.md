# Brightface Content Engine - Deployment Guide

## Overview

The Brightface Content Engine is an automated system that:
- Monitors RSS feeds for AI/branding/photography news
- Scores content for relevance and virality
- Generates LinkedIn and X posts + blog drafts
- Posts content automatically with quality controls
- Tracks everything in Google Sheets

## Quick Start

1. **Install dependencies:**
   ```bash
   python setup.py
   ```

2. **Configure environment:**
   - Copy `env.example` to `.env`
   - Add your API keys (see Configuration section)

3. **Test the system:**
   ```bash
   python qa_tester.py
   ```

4. **Run the engine:**
   ```bash
   python main.py
   ```

## Configuration

### Required Environment Variables

Create a `.env` file with these variables:

```bash
# OpenAI API (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Google Sheets (Required)
GOOGLE_SHEETS_ID=your_google_sheets_id
GOOGLE_CREDENTIALS_FILE=credentials.json

# LinkedIn API (Optional - for posting)
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_PAGE_ID=your_brightface_page_id
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Twitter/X API (Optional - for posting)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Configuration
DEFAULT_UTM_CAMPAIGN=autopost
AUTO_POST=false
POSTING_SCHEDULE_ENABLED=true
RUN_ONCE=false
```

### Google Sheets Setup

1. Create a new Google Sheet
2. Copy the Sheet ID from the URL
3. Enable Google Sheets API in Google Cloud Console
4. Download credentials.json and place in project root
5. The system will automatically create the "Content Ledger" tab

### API Setup

#### OpenAI
- Get API key from https://platform.openai.com/api-keys
- Add to `OPENAI_API_KEY` in `.env`

#### LinkedIn
- Create LinkedIn app at https://www.linkedin.com/developers/
- Get Client ID and Secret
- Request Company Page access
- Generate access token

#### Twitter/X
- Create Twitter app at https://developer.twitter.com/
- Get API keys and tokens
- Generate Bearer token for v2 API

## Usage

### Running the Engine

**Continuous mode (default):**
```bash
python main.py
```

**Run once:**
```bash
RUN_ONCE=true python main.py
```

**Test mode (no posting):**
```bash
AUTO_POST=false python main.py
```

### Testing

**Full QA test:**
```bash
python qa_tester.py
```

**Validate setup:**
```bash
python setup.py validate
```

## Architecture

```
RSS Feeds → Scoring AI → Quality Filter → Content AI → Quality Filter 2 → Publishers → Google Sheets
```

### Components

- **RSS Manager**: Fetches and deduplicates RSS feeds
- **Scoring AI**: Rates content for relevance and virality
- **Quality Filter**: Ensures brand safety and compliance
- **Content AI**: Generates social posts and blog drafts
- **Social Publishers**: Posts to LinkedIn and X
- **Sheets Manager**: Tracks everything in Google Sheets

### Data Flow

1. **RSS Fetching**: Every 2 hours, fetch new items from configured feeds
2. **Scoring**: AI rates each item for relevance (0-10) and virality (0-10)
3. **Filtering**: Items must score ≥7 relevance and ≥6 virality to pass
4. **Content Generation**: AI creates LinkedIn/X posts and blog drafts
5. **Quality Check**: Final safety and compliance check
6. **Publishing**: Post to social media (if AUTO_POST=true) or queue for review
7. **Tracking**: Log everything to Google Sheets

## Monitoring

### Google Sheets Dashboard

The "Content Ledger" sheet tracks:
- All processed content items
- Scores and status
- Posted content and engagement metrics
- Review queue

### Logs

Check logs for:
- RSS feed issues
- AI scoring problems
- Posting failures
- Quality filter results

## Troubleshooting

### Common Issues

**RSS feeds not working:**
- Check feed URLs in `Config.RSS_SOURCES`
- Verify internet connectivity
- Check feed format

**AI scoring failures:**
- Verify OpenAI API key
- Check API quota/limits
- Review prompt formatting

**Google Sheets errors:**
- Verify credentials.json
- Check sheet permissions
- Ensure API is enabled

**Posting failures:**
- Verify social media API keys
- Check rate limits
- Review post content for compliance

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Customization

### Adding RSS Sources

Edit `config.py`:
```python
RSS_SOURCES = [
    'https://your-feed-url.com/rss',
    # ... existing feeds
]
```

### Adjusting Quality Thresholds

Edit `config.py`:
```python
MIN_RELEVANCE_SCORE = 7  # Increase for stricter filtering
MIN_VIRALITY_SCORE = 6   # Increase for higher engagement focus
MAX_FRESHNESS_DAYS = 21  # Decrease for more recent content
```

### Custom Posting Schedule

Edit `config.py`:
```python
POSTING_TIMES = ['09:00', '15:00', '18:00']  # Add/remove times
```

## Production Deployment

### Recommended Setup

1. **Use a VPS/cloud server** (AWS, DigitalOcean, etc.)
2. **Set up process management** (systemd, PM2, etc.)
3. **Configure logging** to files
4. **Set up monitoring** (health checks, alerts)
5. **Backup Google Sheets** regularly

### Security

- Keep API keys secure
- Use environment variables
- Restrict Google Sheets access
- Monitor for unusual activity

### Scaling

- Run multiple instances for different time zones
- Use queue systems for high volume
- Implement caching for RSS feeds
- Consider database for large-scale tracking

## Support

For issues or questions:
1. Check logs for error messages
2. Run QA tests to identify problems
3. Review configuration settings
4. Check API quotas and limits

## License

This project is proprietary to Brightface.ai
