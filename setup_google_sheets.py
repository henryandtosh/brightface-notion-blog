#!/usr/bin/env python3
"""
Google Sheets Setup Script for Content Ledger
Creates the proper structure for tracking content
"""

import os
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def setup_google_sheets():
    """Set up Google Sheets with proper structure"""
    
    # Check if we have credentials
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("📝 Please download your Google service account credentials:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Sheets API")
        print("4. Create Service Account credentials")
        print("5. Download as JSON and save as 'credentials.json'")
        return False
    
    try:
        # Load credentials
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build service
        service = build('sheets', 'v4', credentials=creds)
        
        # Get sheet ID from config
        sheet_id = Config.GOOGLE_SHEETS_ID
        if not sheet_id:
            print("❌ GOOGLE_SHEETS_ID not set in environment variables")
            return False
        
        # Define headers
        headers = [
            'Date',
            'Source',
            'Title', 
            'Link',
            'Relevance Score',
            'Virality Score',
            'Quality Score',
            'Overall Score',
            'Status',
            'Notion ID',
            'Blog Post Title',
            'Generated At',
            'Reasoning'
        ]
        
        # Set up the sheet
        print(f"📊 Setting up Google Sheet: {sheet_id}")
        
        # Clear existing content
        service.spreadsheets().values().clear(
            spreadsheetId=sheet_id,
            range='A1:Z1000'
        ).execute()
        
        # Add headers
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='A1:M1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # Format headers
        requests = [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 0.2,
                                'green': 0.4,
                                'blue': 0.8
                            },
                            'textFormat': {
                                'foregroundColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                },
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={'requests': requests}
        ).execute()
        
        print("✅ Google Sheets setup complete!")
        print(f"📊 Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Google Sheets: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Setting up Google Sheets for Content Ledger...")
    
    if setup_google_sheets():
        print("🎉 Setup complete! Your content ledger is ready.")
    else:
        print("❌ Setup failed. Please check your configuration.")

if __name__ == "__main__":
    main()
