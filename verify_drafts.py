"""
Draft Verification & Sending Script
Verify and send approved drafts
"""
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import config
from gmail_handler import GmailHandler
from persistence import EmailPersistence


class DraftVerifier:
    """Manages draft verification and sending"""
    
    def __init__(self):
        self.config = config
        self.persistence = EmailPersistence(config.processed_emails_db)
        self.gmail_handler = GmailHandler(
            config.google_client_id,
            config.google_client_secret,
            config.google_redirect_uri
        )
        self.authenticated = False
    
    def initialize(self) -> bool:
        """Initialize and authenticate"""
        if not self.gmail_handler.authenticate():
            print("❌ Gmail authentication failed")
            return False
        self.authenticated = True
        return True
    
    def send_draft(self, draft_id: str) -> bool:
        """Send a draft by ID"""
        if not self.authenticated:
            print("Not authenticated")
            return False
        
        return self.gmail_handler.send_draft(draft_id)
    
    def load_drafts_json(self, file_path: str) -> list:
        """Load drafts from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading drafts: {str(e)}")
            return []
    
    def verify_and_send(self, draft_file: str, approve_all: bool = False) -> int:
        """
        Load drafts and optionally send them
        Returns number of drafts sent
        """
        drafts = self.load_drafts_json(draft_file)
        
        if not drafts:
            print("❌ No drafts found in file")
            return 0
        
        print(f"📋 Found {len(drafts)} draft(s)")
        print()
        
        sent_count = 0
        
        for idx, draft in enumerate(drafts, 1):
            print(f"Draft {idx}:")
            print(f"  To: {draft.get('original_sender', 'Unknown')}")
            print(f"  Subject: {draft.get('draft_subject', 'No Subject')}")
            print()
            
            if approve_all:
                # Send without confirmation
                if self.gmail_handler.send_draft(draft.get('email_id', '')):
                    print(f"  ✓ Sent")
                    sent_count += 1
                else:
                    print(f"  ❌ Failed to send")
            else:
                # Ask for confirmation
                while True:
                    response = input("  Send this draft? (y/n/q): ").lower().strip()
                    if response in ['y', 'yes']:
                        if self.gmail_handler.send_draft(draft.get('email_id', '')):
                            print(f"  ✓ Sent")
                            sent_count += 1
                        else:
                            print(f"  ❌ Failed to send")
                        break
                    elif response in ['n', 'no']:
                        print(f"  ⊘ Skipped")
                        break
                    elif response == 'q':
                        print(f"\n✓ Verification stopped (sent {sent_count} draft(s))")
                        return sent_count
                    else:
                        print("  Please enter y, n, or q")
            
            print()
        
        print(f"✅ Verification complete - {sent_count} draft(s) sent")
        return sent_count


def main():
    parser = argparse.ArgumentParser(description='Verify and send email drafts')
    parser.add_argument(
        'file',
        help='Path to drafts JSON file'
    )
    parser.add_argument(
        '--approve-all',
        action='store_true',
        help='Send all drafts without confirmation'
    )
    
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    
    verifier = DraftVerifier()
    if not verifier.initialize():
        sys.exit(1)
    
    sent = verifier.verify_and_send(args.file, args.approve_all)
    sys.exit(0 if sent > 0 else 1)


if __name__ == '__main__':
    main()
