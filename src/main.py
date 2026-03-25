"""
Human-in-the-Loop Gmail Agent
Main entry point and orchestration logic
"""
import sys
import os
import webbrowser
from pathlib import Path
from typing import List

_IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from gmail_handler import GmailHandler
from ai_draft_generator import AIDraftGenerator
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
        self.authenticated = False

    def initialize(self) -> bool:
        """Initialize agent and authenticate with Gmail"""
        print("=" * 60)
        print("Human-in-the-Loop Gmail Agent")
        print("=" * 60)
        print()

        if not self.config.validate():
            print("\n⚠️  Configuration validation failed!")
            print("Please check your .env file and config.json")
            return False

        print("🔐 Authenticating with Gmail...")
        if not self.gmail_handler.authenticate():
            print("❌ Failed to authenticate with Gmail")
            return False

        self.authenticated = True
        print()
        return True

    def process_emails(self) -> List[dict]:
        """Fetch new emails since last run, generate drafts."""
        print("📧 Processing emails...")
        print(f"  Allowed authors: {len(self.config.allowed_authors)}")

        last_run = self.persistence.get_last_run()
        if last_run:
            import calendar
            after_epoch = int(calendar.timegm(last_run.timetuple()))
            print(f"  Checking since last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            after_epoch = None
            print("  No previous run found — checking all unread emails")

        emails = self.gmail_handler.get_filtered_emails(
            self.config.allowed_authors,
            after_epoch=after_epoch
        )
        self.persistence.save_last_run()

        if not emails:
            print("  ✓ No new emails found")
            return []

        print(f"  ✓ Found {len(emails)} email(s)")

        new_emails = [e for e in emails if not self.persistence.is_processed(e['id'])]
        if not new_emails:
            print("  ✓ All emails already processed")
            return []

        print(f"  ✓ {len(new_emails)} new email(s) to process")
        print("\n✍️  Generating drafts...")

        drafts = []
        for email in new_emails:
            draft = self.draft_generator.generate_draft(email)
            drafts.append(draft)
            print(f"  ✓ Draft for: {email['sender']}")
            self.persistence.mark_processed(email['id'])

        return drafts

    def present_drafts(self, drafts: List[dict]):
        """Save each draft to Gmail. Opens in browser when running locally."""
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
                print(f"  Draft ready: {url}")
                if not _IS_LAMBDA:
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
                        webbrowser.open(url)
            else:
                print(f"  ⚠ Failed to create Gmail draft for {draft['original_sender']}")

    def run(self):
        """Initialize and process emails. Called by Lambda or local CLI."""
        if not self.initialize():
            sys.exit(1)
        drafts = self.process_emails()
        if drafts:
            self.present_drafts(drafts)
        else:
            print("No new emails to process")


if __name__ == '__main__':
    EmailAgent().run()
