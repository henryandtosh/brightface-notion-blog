"""
Vercel Cron Job for Automated Content Generation
Runs every Monday and Thursday at 11:00 AM UTC
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_content_generator import AutomatedContentGenerator

def handler(request):
    """Vercel serverless function handler"""
    try:
        print(f"🕐 Cron job started at {datetime.now()}")
        
        # Initialize the content generator
        generator = AutomatedContentGenerator()
        
        # Run the automation
        generator.run_automation()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'success': True,
                'message': 'Automated content generation completed',
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"❌ Error in cron job: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }
