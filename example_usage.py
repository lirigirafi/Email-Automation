"""
Example usage of the Gmail Agent
"""
import sys
from pathlib import Path

# This example demonstrates how to use the EmailAgent
# Uncomment and modify for your use case

if __name__ == '__main__':
    from src.main import EmailAgent
    
    # Create agent instance
    agent = EmailAgent()
    
    # Example 1: Manual one-time run
    print("Example 1: Manual Run")
    print("-" * 40)
    if agent.initialize():
        drafts = agent.process_emails()
        if drafts:
            agent.present_drafts(drafts)
            print(f"\nGenerated {len(drafts)} draft(s)")
    
    # Example 2: Scheduled runs (uncomment to use)
    # print("\nExample 2: Scheduled Runs")
    # print("-" * 40)
    # agent.run_scheduled()
    
    # Example 3: Custom author filtering
    # from src.gmail_handler import GmailHandler
    # handler = GmailHandler(...)
    # emails = handler.get_filtered_emails(
    #     allowed_authors=['specific@author.com'],
    #     days=7  # Check last 7 days
    # )
