"""
Human-in-the-Loop Gmail Agent
Main entry point and orchestration logic
"""
import sys
import argparse
import webbrowser
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from gmail_handler import GmailHandler
from ai_draft_generator import AIDraftGenerator
from scheduler import EmailScheduler
from persistence import EmailPersistence


class EmailAgent:
    """Main agent orchestrating email processing workflow"""
    
    def __init__(self):
        self.config = config
        self.persistence = EmailPersistence(config.processed_emails_db)
        self.gmail_handler = GmailHandler(
            config.google_client_id,
            config.google_client_secret,
            config.google_redirect_uri
        )
        self.draft_generator = AIDraftGenerator()
        self.scheduler = EmailScheduler(config.timezone)
        self.authenticated = False
    
    def initialize(self) -> bool:
        """Initialize agent and authenticate with Gmail"""
        print("=" * 60)
        print("Human-in-the-Loop Gmail Agent")
        print("=" * 60)
        print()
        
        # Validate configuration
        if not self.config.validate():
            print("\n⚠️  Configuration validation failed!")
            print("Please check your .env file and config.json")
            return False
        
        # Authenticate with Gmail
        print("🔐 Authenticating with Gmail...")
        if not self.gmail_handler.authenticate():
            print("❌ Failed to authenticate with Gmail")
            return False
        
        self.authenticated = True
        print()
        return True
    
    def process_emails(self, minutes: int = None) -> List[dict]:
        """
        Main workflow:
        1. Fetch new emails from allowed authors
        2. Generate drafts
        3. Present to user for approval
        """
        print("📧 Processing emails...")
        print(f"DEBUG allowedAuthors: {self.config.allowed_authors}")
        print(f"  Allowed authors: {len(self.config.allowed_authors)}")
        # Use passed minutes or default to config interval
        interval_minutes = minutes if minutes is not None else self.config.schedule_interval_minutes
        emails = self.gmail_handler.get_filtered_emails(
            self.config.allowed_authors,
            minutes=interval_minutes
        )
        if not emails:
            print("  ✓ No new emails found")
            return []
        print(f"  ✓ Found {len(emails)} email(s)")
        # Filter out already processed emails
        new_emails = []
        for email in emails:
            if not self.persistence.is_processed(email['id']):
                new_emails.append(email)
        if not new_emails:
            print("  ✓ All emails already processed")
            return []
        print(f"  ✓ {len(new_emails)} new email(s) to process")
        # Generate drafts
        print("\n✍️  Generating drafts...")
        drafts = []
        for email in new_emails:
            draft = self.draft_generator.generate_draft(email)
            drafts.append(draft)
            print(f"  ✓ Draft for: {email['sender']}")
            self.persistence.mark_processed(email['id'])
        return drafts
    
    def present_drafts(self, drafts: List[dict]):
        """Save each draft to Gmail and open it in the browser."""
        if not drafts:
            return
        for draft in drafts:
            message_id = self.gmail_handler.create_draft(
                to=draft['original_sender'],
                subject=draft['draft_subject'],
                body=draft['draft_body'],
            )
            if message_id:
                url = f"https://mail.google.com/mail/u/0/#drafts/{message_id}"
                print(f"  Opening draft in Chrome: {url}")
                chrome_paths = [
                    "C:/Program Files/Google/Chrome/Application/chrome.exe %s",
                    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s",
                ]
                opened = False
                for path in chrome_paths:
                    try:
                        webbrowser.get(path).open(url)
                        opened = True
                        break
                    except Exception:
                        continue
                if not opened:
                    webbrowser.open(url)  # fallback to default browser
            else:
                print(f"  ⚠ Failed to create Gmail draft for {draft['original_sender']}")
    
    def schedule_runs(self):
        """Schedule automatic runs at configured interval (default every 2 minutes)"""
        print("⏰ Scheduling automated runs...")
        
        interval = self.config.schedule_interval_minutes
        self.scheduler.schedule_every_minutes(interval, self._scheduled_job)
        
        print(f"\nScheduler watching (timezone: {self.config.timezone})")
        print(f"Next run: {self.scheduler.get_next_run()}")
    
    def _scheduled_job(self):
        """Job function for scheduled runs"""
        drafts = self.process_emails()
        if drafts:
            self.present_drafts(drafts)
    
    def run_manual(self):
        """Manually trigger email processing for the last 2 minutes."""
        print("\n🚀 Manual trigger started (last 2 minutes)")
        drafts = self.process_emails(minutes=2)
        if drafts:
            self.present_drafts(drafts)
        else:
            print("No new emails to process")

    def run_scheduled(self):
        """Run with scheduler."""
        if not self.initialize():
            return
        self.schedule_runs()
        try:
            self.scheduler.start_scheduler(interval=10)
        except KeyboardInterrupt:
            print("\n✓ Agent stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Human-in-the-Loop Gmail Agent'
    )
    parser.add_argument(
        '--mode',
        choices=['manual', 'scheduled'],
        default='manual',
        help='Run mode: manual (one-time) or scheduled (continuous)'
    )
    parser.add_argument(
        '--no-schedule',
        action='store_true',
        help='Skip automatic scheduling, require manual verification'
    )
    
    args = parser.parse_args()
    
    agent = EmailAgent()
    
    if args.mode == 'manual':
        if not agent.initialize():
            sys.exit(1)
        agent.run_manual()
    else:
        agent.run_scheduled()


if __name__ == '__main__':
    main()
