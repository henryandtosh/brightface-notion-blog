#!/bin/bash

# 🚀 Notion API Integration Setup Script
# This script sets up the Notion blog integration

echo "🚀 Setting up Notion API Integration for Brightface Blog..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your Notion credentials:"
    echo "   - NOTION_API_KEY: Your integration token"
    echo "   - NOTION_DB_ID: Your database ID"
    echo ""
    echo "🔗 Get these from:"
    echo "   1. Notion integration settings"
    echo "   2. Your 'Blog Posts' database URL"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
fi

# Test the integration
echo "🧪 Testing Notion API connection..."
node test-api.js

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup complete! Your Notion integration is working."
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Start the server: npm start"
    echo "   2. Open demo.html in your browser"
    echo "   3. Add blog posts to your Notion database"
    echo "   4. Set 'Published' to true to see them live"
    echo ""
    echo "📚 For more details, see NOTION_API_SETUP.md"
else
    echo ""
    echo "❌ Setup failed. Please check your .env file and try again."
    echo "   Make sure your NOTION_API_KEY and NOTION_DB_ID are correct."
fi
