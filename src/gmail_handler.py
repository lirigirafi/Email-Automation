"""
Gmail API integration module
Handles authentication, email fetching, and draft management.
Token is stored in S3 when S3_BUCKET env var is set, otherwise local file.
"""
import io
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from typing import List, Optional, Dict
import base64
from email.mime.text import MIMEText
from email.header import Header

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

_S3_BUCKET = os.environ.get("S3_BUCKET")
_TOKEN_S3_KEY = os.environ.get("GMAIL_TOKEN_S3_KEY", "gmail_token.pickle")
_IS_LAMBDA = bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))


class GmailHandler:
    """Manages Gmail API interactions"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.service = None
        self.credentials = None
        self._token_file = './data/gmail_token.pickle'

    # ── token storage helpers ──────────────────────────────────────────────

    def _load_token(self) -> Optional[Credentials]:
        """Load token from S3 or local file."""
        if _S3_BUCKET:
            import boto3
            s3 = boto3.client("s3")
            try:
                obj = s3.get_object(Bucket=_S3_BUCKET, Key=_TOKEN_S3_KEY)
                return pickle.loads(obj["Body"].read())
            except Exception:
                return None
        if os.path.exists(self._token_file):
            with open(self._token_file, "rb") as f:
                return pickle.load(f)
        return None

    def _save_token(self, creds: Credentials):
        """Save token to S3 or local file."""
        data = pickle.dumps(creds)
        if _S3_BUCKET:
            import boto3
            s3 = boto3.client("s3")
            s3.put_object(Bucket=_S3_BUCKET, Key=_TOKEN_S3_KEY, Body=data)
        else:
            os.makedirs(os.path.dirname(self._token_file), exist_ok=True)
            with open(self._token_file, "wb") as f:
                f.write(data)

    # ── auth ───────────────────────────────────────────────────────────────

    def authenticate(self) -> bool:
        """Authenticate with Gmail API using OAuth2."""
        try:
            self.credentials = self._load_token()

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_token(self.credentials)
                elif _IS_LAMBDA:
                    print("ERROR: No valid Gmail token in S3. Run OAuth locally first, then upload the token.")
                    return False
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        './credentials.json', SCOPES, redirect_uri=self.redirect_uri
                    )
                    self.credentials = flow.run_local_server(port=8080)
                    self._save_token(self.credentials)

            self.service = discovery.build('gmail', 'v1', credentials=self.credentials)
            print("✓ Gmail authentication successful")
            return True

        except Exception as e:
            print(f"✗ Gmail authentication failed: {str(e)}")
            return False
    
    def get_filtered_emails(self, allowed_authors: List[str], after_epoch: Optional[int] = None) -> List[Dict]:
        """
        Fetch unread emails from allowed authors received after after_epoch (Unix timestamp).
        Skips emails with attachments.
        """
        try:
            if not self.service:
                print("ERROR: Not authenticated with Gmail")
                return []

            # Build query
            author_query = " OR ".join([f'from:{author}' for author in allowed_authors])
            if after_epoch:
                query = f'is:unread in:inbox ({author_query}) after:{after_epoch}'
            else:
                query = f'is:unread in:inbox ({author_query})'
            print(f"[DEBUG] Gmail query: {query}")
            
            # List messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            print(f"[DEBUG] Gmail returned {len(messages)} message(s) matching query.")
            filtered_emails = []
            
            for message in messages:
                print(f"[DEBUG] Checking message ID: {message['id']}")
                email_data = self._get_message_details(message['id'])
                if email_data:
                    print(f"[DEBUG] Accepted: {email_data.get('sender','?')} | {email_data.get('subject','?')}")
                    filtered_emails.append(email_data)
                else:
                    print(f"[DEBUG] Skipped message ID: {message['id']} (see above for reason)")
            
            print(f"[DEBUG] {len(filtered_emails)} email(s) accepted after filtering.")
            return filtered_emails
            
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            return []
    
    def _get_message_details(self, message_id: str) -> Optional[Dict]:
        """Fetch detailed information for a single message, with debug logging"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            body = self._get_message_body(message['payload'])
            has_attachments = self._has_real_attachments(message['payload'])

            print(f"[DEBUG] Message details: sender={sender}, subject={subject}, has_attachments={has_attachments}")
            # Skip if has attachments
            if has_attachments:
                print(f"⚠ Skipping email from {sender} (has attachments) - flagged for manual review")
                return None
            
            return {
                'id': message_id,
                'sender': sender,
                'subject': subject,
                'body': body,
                'snippet': message.get('snippet', '')[:200],
                'timestamp': message['internalDate']
            }
            
        except Exception as e:
            print(f"Error getting message details: {str(e)}")
            return None
    
    def _has_real_attachments(self, payload: Dict) -> bool:
        """Check if a message has real file attachments (not just multipart text/html parts)"""
        for part in payload.get('parts', []):
            if part.get('filename'):
                return True
            if part.get('parts'):
                if self._has_real_attachments(part):
                    return True
        return False

    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ""
    
    def _get_message_body(self, payload: Dict) -> str:
        """Extract message body from payload"""
        try:
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        return base64.urlsafe_b64decode(
                            part['body'].get('data', '')
                        ).decode('utf-8')
            elif 'body' in payload:
                # Simple message
                return base64.urlsafe_b64decode(
                    payload['body'].get('data', '')
                ).decode('utf-8')
        except Exception as e:
            print(f"Error decoding message body: {str(e)}")
        
        return ""
    
    @staticmethod
    def _extract_email(addr: str) -> str:
        """Extract bare email address from strings like 'Name <email@x.com>'"""
        import re
        m = re.search(r'<([^>]+)>', addr)
        return m.group(1).strip() if m else addr.strip()

    def create_draft(self, to: str, subject: str, body: str) -> Optional[str]:
        """Create a draft email (does not send)"""
        try:
            message = MIMEText(body, 'plain', 'utf-8')
            message['to'] = self._extract_email(to)
            message['subject'] = Header(subject, 'utf-8')

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            draft_object = {
                'message': {
                    'raw': raw_message
                }
            }
            
            draft = self.service.users().drafts().create(
                userId='me',
                body=draft_object
            ).execute()

            message_id = draft.get('message', {}).get('id', '')
            print(f"✓ Draft created: {draft['id']} (message={message_id})")
            return message_id
            
        except Exception as e:
            print(f"Error creating draft: {str(e)}")
            return None
    
    def send_draft(self, draft_id: str) -> bool:
        """Send a draft email"""
        try:
            self.service.users().drafts().send(
                userId='me',
                id=draft_id
            ).execute()
            
            print(f"✓ Draft sent: {draft_id}")
            return True
            
        except Exception as e:
            print(f"Error sending draft: {str(e)}")
            return False
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking as read: {str(e)}")
            return False
