"""
Simple dashboard for Vercel
"""
def handler(request):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brightface Content Engine Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 30px; }
        h1 { color: #333; margin-bottom: 30px; text-align: center; }
        .status { padding: 10px; border-radius: 6px; margin-bottom: 20px; background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .btn { background: #007bff; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; text-decoration: none; text-align: center; display: inline-block; margin: 5px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Brightface Content Engine Dashboard</h1>
        
        <div class="status">
            <strong>Status:</strong> System is running and ready for configuration
        </div>
        
        <h3>Available Endpoints:</h3>
        <a href="/api/test" class="btn">Test API</a>
        <a href="/api/blog-generator" class="btn">Generate Blog Content</a>
        <a href="/api/rss-processor" class="btn">Process RSS Feeds</a>
        
        <h3>Next Steps:</h3>
        <ol>
            <li>Add environment variables in Vercel dashboard</li>
            <li>Configure Notion API key and database ID</li>
            <li>Add OpenAI API key</li>
            <li>Test blog generation</li>
        </ol>
        
        <h3>Environment Variables Needed:</h3>
        <ul>
            <li><code>NOTION_API_KEY</code> - Your Notion integration token</li>
            <li><code>NOTION_DB_ID</code> - Your Notion database ID</li>
            <li><code>OPENAI_API_KEY</code> - Your OpenAI API key</li>
            <li><code>GOOGLE_SHEETS_ID</code> - Your Google Sheets ID</li>
        </ul>
    </div>
</body>
</html>
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
        },
        'body': html_content
    }
