# Brightface Content Engine

Automated content engine for brightface.ai that turns curated AI/branding/photography news into on-brand posts for LinkedIn & X, and long-form blog drafts.

## Features

- RSS feed monitoring and content curation
- AI-powered relevance and virality scoring
- Automated social media post generation
- Quality filters and safety checks
- Google Sheets integration for content tracking
- LinkedIn and X posting automation
- Blog draft generation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (see `.env.example`)

3. Run the content engine:
```bash
python main.py
```

## Configuration

The engine uses environment variables for API keys and configuration. See `.env.example` for required variables.

## Architecture

- **RSS Feeds**: Monitor AI/branding/photography news sources
- **Scoring AI**: Rate content for relevance and virality
- **Content AI**: Generate social posts and blog drafts
- **Quality Filters**: Ensure brand safety and compliance
- **Publishers**: Post to LinkedIn and X automatically
- **Storage**: Track everything in Google Sheets
