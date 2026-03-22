#!/usr/bin/env python3
"""
Debug script to check what emails the agent can see
"""
import sys
sys.path.insert(0, 'src')

from config import Config
from gmail_handler import GmailHandler

def debug_emails():
    # Create fresh config instance
    fresh_config = Config()
    
    print("🔍 Debugging email search...")
    print(f"Config file path: {fresh_config.config_file}")
    print(f"Config file exists: {fresh_config.config_file.exists()}")
    
    # Read file directly
    import json
    try:
        with open(fresh_config.config_file, 'r') as f:
            direct_data = json.load(f)
        print(f"Direct file read - allowedAuthors: {direct_data.get('allowedAuthors', [])}")
    except Exception as e:
        print(f"Error reading file directly: {e}")
    
    print(f"Config class - allowed authors: {fresh_config.allowed_authors}")
    print(f"Raw config data keys: {list(fresh_config.config_data.keys())}")
    print()

    # Initialize handler with fresh config
    handler = GmailHandler(
        fresh_config.google_client_id,
        fresh_config.google_client_secret,
        fresh_config.google_redirect_uri
    )

    # Authenticate
    if not handler.authenticate():
        print("❌ Authentication failed")
        return

    print("✅ Authenticated successfully")
    print()

    # Get emails with fresh config (last 2 minutes)
    emails = handler.get_filtered_emails(fresh_config.allowed_authors, minutes=2)
    print(f"📧 Found {len(emails)} emails matching criteria (last 2 minutes)")
    print()

    if emails:
        print("📋 Email details:")
        print("-" * 50)
        for i, email in enumerate(emails, 1):
            print(f"{i}. From: {email.get('sender', 'Unknown')}")
            print(f"   Subject: {email.get('subject', 'No Subject')}")
            print(f"   ID: {email.get('id', 'N/A')}")
            print(f"   Snippet: {email.get('snippet', '')[:100]}...")
            print()
    else:
        print("❌ No emails found. Possible reasons:")
        print("  - No unread emails from allowed authors")
        print("  - Emails are older than 1 day")
        print("  - Emails have attachments (automatically skipped)")
        print("  - Check your Gmail for unread emails")

if __name__ == '__main__':
    debug_emails()