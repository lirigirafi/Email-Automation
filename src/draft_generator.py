"""
Draft generation module
Creates friendly yet professional email responses
"""
from typing import Dict, List
import re


class DraftGenerator:
    """Generates draft email responses"""
    
    FRIENDLY_OPENINGS = [
        "Hi {name},",
        "Hello {name},",
        "Thanks for reaching out, {name}!",
        "Great to hear from you, {name}!"
    ]
    
    FRIENDLY_CLOSINGS = [
        "Best regards,",
        "All the best,",
        "Warm regards,",
        "Thanks again!",
        "Looking forward to hearing from you!"
    ]
    
    TEMPLATES = {
        "acknowledgement": """Hi {name},

Thanks for your email regarding {subject}. I appreciate you reaching out!

I wanted to let you know that I've reviewed your message and will get back to you shortly with a detailed response.

{custom_message}

{closing}
{sender_name}""",
        
        "question_response": """Hi {name},

Thank you for your question about {subject}. Great question!

{custom_message}

If you need any further clarification or have additional questions, please don't hesitate to reach out.

{closing}
{sender_name}""",
        
        "information_request": """Hi {name},

Thanks for reaching out about {subject}. I'd be happy to help!

{custom_message}

Feel free to let me know if you need any additional information or have follow-up questions.

{closing}
{sender_name}""",
        
        "general": """Hi {name},

Thanks for your email about {subject}.

{custom_message}

{closing}
{sender_name}"""
    }
    
    def __init__(self, sender_name: str = "Your Name", sender_email: str = ""):
        self.sender_name = sender_name
        self.sender_email = sender_email
    
    def generate_draft(self, email_data: Dict, context: str = "") -> Dict:
        """
        Generate a draft response for an email
        
        Args:
            email_data: Dict with 'sender', 'subject', 'body'
            context: Optional custom context/message to include
        
        Returns:
            Dict with draft_subject, draft_body, original_sender
        """
        sender_name = self._extract_name(email_data.get('sender', ''))
        subject = email_data.get('subject', 'No Subject')
        
        # Determine template based on subject/body analysis
        template_type = self._analyze_email_type(email_data.get('body', ''), subject)
        
        # Generate custom message if context provided, otherwise use generic
        if context:
            custom_message = f"Here's what I wanted to share:\n\n{context}"
        else:
            custom_message = "I'll be in touch with more details soon."
        
        # Create draft
        opening = self.FRIENDLY_OPENINGS[0].format(name=sender_name.split()[0])
        closing = self.FRIENDLY_CLOSINGS[0]
        
        draft_body = self.TEMPLATES.get(template_type, self.TEMPLATES["general"]).format(
            name=sender_name.split()[0] if sender_name else "there",
            subject=subject,
            custom_message=custom_message,
            closing=closing,
            sender_name=self.sender_name
        )
        
        draft_subject = f"Re: {subject}"
        
        return {
            'draft_subject': draft_subject,
            'draft_body': draft_body,
            'original_sender': email_data.get('sender', ''),
            'original_subject': subject,
            'template_used': template_type,
            'email_id': email_data.get('id', '')
        }
    
    def _extract_name(self, email_string: str) -> str:
        """Extract name from email string like 'John Doe <john@example.com>'"""
        match = re.match(r'([^<]+)<', email_string)
        if match:
            return match.group(1).strip()
        return email_string.split('@')[0]
    
    def _analyze_email_type(self, body: str, subject: str) -> str:
        """Analyze email to determine appropriate template"""
        body_lower = body.lower()
        subject_lower = subject.lower()
        
        # Keywords for different email types
        question_keywords = ['?', "can you", "could you", "would you", "do you", "how do"]
        ack_keywords = ["i wanted to reach out", "following up", "just checking in"]
        info_keywords = ["please send", "i need", "can you provide", "information"]
        
        question_count = sum(1 for kw in question_keywords if kw in body_lower)
        ack_count = sum(1 for kw in ack_keywords if kw in body_lower)
        info_count = sum(1 for kw in info_keywords if kw in body_lower)
        
        if question_count > ack_count and question_count > info_count:
            return "question_response"
        elif info_count > ack_count:
            return "information_request"
        elif ack_count > 0:
            return "acknowledgement"
        else:
            return "general"
    
    def generate_batch_drafts(self, emails: List[Dict]) -> List[Dict]:
        """Generate drafts for multiple emails"""
        drafts = []
        for email in emails:
            draft = self.generate_draft(email)
            drafts.append(draft)
        return drafts
    
    def customize_draft(self, draft: Dict, custom_message: str) -> Dict:
        """Customize an existing draft with custom message"""
        draft['draft_body'] = draft['draft_body'].replace(
            "Here's what I wanted to share:\n\nI'll be in touch with more details soon.",
            f"Here's what I wanted to share:\n\n{custom_message}"
        )
        return draft
