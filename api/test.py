"""
Simple test endpoint for Vercel
"""
def handler(request):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': '{"message": "Hello from Brightface Content Engine!", "status": "working"}'
    }
