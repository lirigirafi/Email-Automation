---
title: Human-in-the-Loop Gmail Agent
description: Python-based email automation with Gmail API integration and manual approval workflow
applyTo: 
  - "**/*.py"
  - "**/*.json"
  - "**/*.md"
---

# Human-in-the-Loop Gmail Agent - Workspace Instructions

## Project Overview

A Python agent that automates Gmail email responses with **strict human approval** before sending. Features OAuth2 integration, email filtering, draft generation, and VS Code integration.

### Core Requirements Met
- ✅ Gmail API with OAuth2 authentication
- ✅ Email filtering by author whitelist (config.json)
- ✅ Scheduled runs (9 AM, 5 PM) + manual triggers
- ✅ Attachment detection and flagging
- ✅ Friendly yet professional response tone
- ✅ Human-in-the-Loop workflow (no auto-sending)
- ✅ Draft tracking to prevent duplicates
- ✅ VS Code integration (markdown + JSON formats)

## Quick Start Commands

### 1. Initial Setup
```bash
# Activate environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup Gmail OAuth2
python setup_oauth.py
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
# Edit config.json with allowed authors
```

### 3. Run Agent
```bash
# Manual run (one-time)
python src/main.py --mode manual

# Scheduled run (continuous, 9 AM & 5 PM)
python src/main.py --mode scheduled

# Verify and send drafts
python verify_drafts.py ./data/drafts/drafts_*.json
```

## Project Structure Overview

- **src/** - Core Python modules
  - `main.py` - Entry point and orchestration
  - `gmail_handler.py` - Gmail API integration
  - `draft_generator.py` - Response generation
  - `scheduler.py` - Job scheduling
  - `persistence.py` - Email tracking
  - `config.py` - Configuration loader
  - `vscode_handler.py` - VS Code integration

- **data/** - Runtime files
  - `drafts/` - Generated draft markdown files
  - `processed_emails.json` - Tracking database

- **config.json** - Whitelist authors and settings
- **.env** - Gmail API credentials (create from .env.example)
- **requirements.txt** - Python dependencies
- **setup_oauth.py** - OAuth2 setup helper
- **verify_drafts.py** - Draft approval & sending script

## Configuration Files

### config.json
```json
{
  "allowedAuthors": ["author@example.com"],
  "draftSettings": {
    "tone": "friendly_professional",
    "maxDraftLength": 500
  },
  "emailFilters": {
    "skipAttachments": true,
    "daysToCheck": 1
  }
}
```

### .env (Create from .env.example)
```env
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
USER_EMAIL=your_email@gmail.com
SCHEDULE_TIME_1=09:00
SCHEDULE_TIME_2=17:00
TIMEZONE=America/New_York
```

## Workflow

1. **Fetch** - Pull unread emails from allowed authors
2. **Filter** - Skip attachments, avoid duplicates
3. **Generate** - Create professional response drafts
4. **Present** - Show drafts in VS Code or terminal
5. **Approve** - Manual verification before sending
6. **Track** - Record processed emails to avoid duplicates

## Key Features

- **No Auto-Sending**: All drafts require explicit human approval
- **Smart Templates**: Automatically selects response type (question, acknowledgment, info request)
- **Friendly Tone**: Professional yet warm language
- **Attachment Detection**: Automatically flags for manual review
- **Deduplication**: Tracks processed emails
- **Flexible Scheduling**: 9 AM & 5 PM by default, customizable
- **VS Code Integration**: View/approve drafts in editor
- **OAuth2 Security**: Secure Gmail authentication

## Development Notes

- Language: Python 3.9+
- Main Dependencies: google-api-python-client, python-dotenv, schedule, pytz
- No database required (uses JSON files for tracking)
- Modular design for easy extension

## Common Tasks

### Add New Allowed Author
Edit `config.json`:
```json
"allowedAuthors": [
  "existing_author@example.com",
  "new_author@example.com"
]
```

### Change Scheduling Times
Edit `.env`:
```env
SCHEDULE_TIME_1=08:00
SCHEDULE_TIME_2=18:00
```

### Customize Draft Templates
Edit `src/draft_generator.py` TEMPLATES dictionary

### Reset Processing History
```bash
python -c "from src.persistence import EmailPersistence; EmailPersistence().reset()"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth authentication fails | Verify credentials.json and .env settings |
| No emails found | Check allowed authors in config.json |
| Scheduling not working | Verify timezone, use 24-hour time format |
| Drafts not creating | Check Gmail API is enabled |

## Security Best Practices

1. Never commit `.env` or `credentials.json`
2. Use `.env.example` as template
3. Regularly review draft templates
4. Test with staging account first
5. Restrict author whitelist to trusted senders

## Next Steps

1. Copy `.env.example` to `.env`
2. Run `python setup_oauth.py` for Gmail setup
3. Update `config.json` with your authors
4. Test with `python src/main.py --mode manual`
5. Set up scheduled runs with `--mode scheduled`

---

**Remember**: This is a human-in-the-loop system. No emails are sent automatically!
