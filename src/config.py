"""
Configuration module for Gmail Agent
Loads configuration from config.json and environment variables
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration loader"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / "config.json"
        self.config_data = self._load_config()
        self._load_env()
    
    def _load_config(self) -> dict:
        """Load configuration from config.json (UTF-8 safe)"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_env(self):
        """Load environment variables"""
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        self.google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/')
        self.user_email = os.getenv('USER_EMAIL', '')
        self.draft_output_path = os.getenv('DRAFT_OUTPUT_PATH', './data/drafts')
        self.processed_emails_db = os.getenv('PROCESSED_EMAILS_DB', './data/processed_emails.json')
        self.schedule_time_1 = os.getenv('SCHEDULE_TIME_1', '09:00')
        self.schedule_time_2 = os.getenv('SCHEDULE_TIME_2', '17:00')
        self.schedule_interval_minutes = int(os.getenv('SCHEDULE_INTERVAL_MINUTES', '2'))
        self.timezone = os.getenv('TIMEZONE', 'America/New_York')
    
    @property
    def allowed_authors(self) -> list:
        """Get list of allowed email authors"""
        return self.config_data.get('allowedAuthors', [])
    
    @property
    def draft_settings(self) -> dict:
        """Get draft generation settings"""
        return self.config_data.get('draftSettings', {})
    
    @property
    def email_filters(self) -> dict:
        """Get email filter settings"""
        return self.config_data.get('emailFilters', {})
    
    @property
    def vscode_integration(self) -> dict:
        """Get VS Code integration settings"""
        return self.config_data.get('vscodeIntegration', {})
    
    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.google_client_id or not self.google_client_secret:
            print("ERROR: Google OAuth2 credentials not configured in .env file")
            return False
        if not self.allowed_authors:
            print("WARNING: No allowed authors configured in config.json")
        return True


# Global config instance
config = Config()
