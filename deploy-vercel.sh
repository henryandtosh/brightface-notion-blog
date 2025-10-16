#!/bin/bash
# Vercel Deployment Script for Brightface Content Engine

echo "🚀 Deploying Brightface Content Engine to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel:"
    vercel login
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure environment variables in Vercel dashboard"
echo "2. Upload Google credentials as base64"
echo "3. Test functions manually"
echo "4. Monitor cron job execution"
echo ""
echo "🌐 Your dashboard will be available at:"
echo "https://your-app.vercel.app/api/dashboard"
echo ""
echo "📚 See VERCEL_DEPLOYMENT.md for detailed instructions"
