"""
AWS Lambda entry point.
Triggered by EventBridge at 09:00 and 17:00 daily.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import EmailAgent


def lambda_handler(event, context):
    agent = EmailAgent()

    if not agent.initialize():
        return {"statusCode": 500, "body": "Failed to initialize agent"}

    drafts = agent.process_emails()

    if drafts:
        agent.present_drafts(drafts)

    return {
        "statusCode": 200,
        "body": f"Processed {len(drafts)} draft(s)",
    }
