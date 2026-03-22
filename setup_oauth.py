"""
Gmail OAuth2 Setup Guide
Run this script to obtain your Google OAuth2 credentials
"""
import json
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def setup_oauth():
    """
    Interactive OAuth2 setup for Gmail API
    """
    print("=" * 60)
    print("Gmail OAuth2 Setup")
    print("=" * 60)
    print()
    
    # Check for existing credentials.json
    creds_file = Path("credentials.json")
    if not creds_file.exists():
        print("⚠️  credentials.json not found!")
        print()
        print("SETUP INSTRUCTIONS:")
        print("-" * 60)
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable the Gmail API")
        print("4. Create OAuth 2.0 Client ID (Desktop Application)")
        print("5. Download the credentials JSON file")
        print("6. Save it as 'credentials.json' in this directory")
        print()
        return False
    
    try:
        # Create the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
        
        print("🔐 Starting OAuth2 authentication flow...")
        print("   A browser window will open. Please sign in with your Gmail account.")
        print()
        
        # Run the flow
        creds = flow.run_local_server(port=8080)
        
        # Extract credentials
        client_id = creds.client_id if hasattr(creds, 'client_id') else ""
        client_secret = creds.client_secret if hasattr(creds, 'client_secret') else ""
        
        print()
        print("✓ OAuth2 authentication successful!")
        print()
        print("ADD THESE TO YOUR .env FILE:")
        print("-" * 60)
        print(f'GOOGLE_CLIENT_ID={client_id}')
        print(f'GOOGLE_CLIENT_SECRET={client_secret}')
        print('GOOGLE_REDIRECT_URI=http://localhost:8080/')
        print()
        
        # Read credentials.json to extract client info
        with open("credentials.json", "r") as f:
            cred_data = json.load(f)
            client_info = cred_data.get("installed", {})
            
            print("OR copy from credentials.json:")
            print("-" * 60)
            for key, value in client_info.items():
                if key in ["client_id", "client_secret"]:
                    print(f'{key}: {value}')
        
        print()
        print("NEXT STEPS:")
        print("-" * 60)
        print("1. Copy the credentials to your .env file")
        print("2. Run: python src/main.py --mode manual")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth2 setup failed: {str(e)}")
        return False


if __name__ == '__main__':
    setup_oauth()
