"""
Vercel Serverless Function: Dashboard
Web interface for monitoring and controlling the content engine
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_manager import GoogleSheetsManager
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Main handler for dashboard"""
    try:
        # Get dashboard data
        dashboard_data = get_dashboard_data()
        
        # Return HTML dashboard
        html_content = generate_dashboard_html(dashboard_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': html_content
        }
        
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': f"<h1>Error</h1><p>{str(e)}</p>"
        }

def get_dashboard_data():
    """Get data for the dashboard"""
    try:
        sheets_manager = GoogleSheetsManager()
        
        # Get basic stats (simplified implementation)
        return {
            'total_items': 0,
            'approved_items': 0,
            'posted_items': 0,
            'held_for_review': 0,
            'last_update': datetime.now().isoformat(),
            'auto_post_enabled': Config.AUTO_POST
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            'total_items': 0,
            'approved_items': 0,
            'posted_items': 0,
            'held_for_review': 0,
            'last_update': datetime.now().isoformat(),
            'auto_post_enabled': False,
            'error': str(e)
        }

def generate_dashboard_html(data):
    """Generate HTML dashboard"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brightface Content Engine Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .controls {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            display: inline-block;
            transition: background-color 0.2s;
        }}
        .btn:hover {{
            background: #0056b3;
        }}
        .btn-secondary {{
            background: #6c757d;
        }}
        .btn-secondary:hover {{
            background: #545b62;
        }}
        .status {{
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status.warning {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        .status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .info {{
            background: #e2e3e5;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Brightface Content Engine Dashboard</h1>
        
        <div class="status {'success' if data.get('auto_post_enabled') else 'warning'}">
            <strong>Status:</strong> {'Auto-posting enabled' if data.get('auto_post_enabled') else 'Review mode - manual approval required'}
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{data.get('total_items', 0)}</div>
                <div class="stat-label">Total Items Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data.get('approved_items', 0)}</div>
                <div class="stat-label">Approved Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data.get('posted_items', 0)}</div>
                <div class="stat-label">Posted Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{data.get('held_for_review', 0)}</div>
                <div class="stat-label">Held for Review</div>
            </div>
        </div>
        
        <div class="controls">
            <a href="/api/content-generator" class="btn">Generate Content</a>
            <a href="/api/rss-processor" class="btn">Process RSS Feeds</a>
            <a href="/api/social-publisher" class="btn">Publish to Social</a>
            <a href="/api/metrics-updater" class="btn btn-secondary">Update Metrics</a>
        </div>
        
        <div class="info">
            <h3>📊 System Information</h3>
            <p><strong>Last Update:</strong> {data.get('last_update', 'Unknown')}</p>
            <p><strong>RSS Sources:</strong> {len(Config.RSS_SOURCES)} feeds monitored</p>
            <p><strong>Posting Schedule:</strong> Every 2 hours (RSS), 4 times daily (Social)</p>
            <p><strong>Quality Thresholds:</strong> Relevance ≥7, Virality ≥6</p>
        </div>
        
        {'<div class="status error"><strong>Error:</strong> ' + data.get('error', '') + '</div>' if data.get('error') else ''}
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(() => {{
            window.location.reload();
        }}, 300000);
    </script>
</body>
</html>
    """

# Vercel expects this to be the main handler
def handler(request):
    """Main handler for dashboard"""
    try:
        # Get dashboard data
        dashboard_data = get_dashboard_data()
        
        # Return HTML dashboard
        html_content = generate_dashboard_html(dashboard_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': html_content
        }
        
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': f"<h1>Error</h1><p>{str(e)}</p>"
        }
