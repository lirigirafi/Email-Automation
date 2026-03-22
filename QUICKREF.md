# Quick Reference Guide

## Command Cheat Sheet

### Initial Setup
```bash
# 1. Create environment
python -m venv venv

# 2. Activate environment
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate          # Windows

# 3. Install dependencies  
pip install -r requirements.txt

# 4. OAuth2 setup
python setup_oauth.py

# 5. Configure
cp .env.example .env
# Edit .env with your credentials
# Edit config.json with allowed authors
```

### Running the Agent

```bash
# One-time run
python src/main.py --mode manual

# Continuous scheduling
python src/main.py --mode scheduled

# Verify and send drafts
python verify_drafts.py ./data/drafts/drafts_*.json

# Send all without asking
python verify_drafts.py ./data/drafts/drafts_*.json --approve-all
```

### Configuration Changes

```bash
# Add new author to config.json
# Edit config.json "allowedAuthors" array

# Change schedule times
# Edit .env "SCHEDULE_TIME_1" and "SCHEDULE_TIME_2"

# Change timezone
# Edit .env "TIMEZONE"

# Reset processed emails
python -c "from src.persistence import EmailPersistence; EmailPersistence().reset()"
```

## File Locations

```
.env                           ← Your credentials (secret!)
credentials.json               ← Gmail OAuth (secret!)
config.json                    ← Author whitelist & settings
data/drafts/                   ← Generated drafts (*.md)
data/processed_emails.json     ← Tracking database
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GOOGLE_CLIENT_ID` | OAuth2 ID | `abc123.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | OAuth2 Secret | `your_secret_xyz` |
| `GOOGLE_REDIRECT_URI` | OAuth callback | `http://localhost:8080/` |
| `USER_EMAIL` | Your Gmail | `you@gmail.com` |
| `SCHEDULE_TIME_1` | First run | `09:00` |
| `SCHEDULE_TIME_2` | Second run | `17:00` |
| `TIMEZONE` | Timezone | `America/New_York` |

## Config.json Settings

```json
{
  "allowedAuthors": ["email@example.com"],
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

## Module Overview

| Module | Purpose | Key Classes |
|--------|---------|------------|
| `main.py` | Entry point | `EmailAgent` |
| `config.py` | Configuration | `Config` |
| `gmail_handler.py` | Gmail API | `GmailHandler` |
| `draft_generator.py` | Draft creation | `DraftGenerator` |
| `scheduler.py` | Job scheduling | `EmailScheduler` |
| `persistence.py` | Email tracking | `EmailPersistence` |
| `vscode_handler.py` | VS Code integration | `VSCodeHandler` |

## Common Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | Activate venv: `source venv/bin/activate` |
| No emails | Check config.json authors |
| Auth fails | Run `python setup_oauth.py` again |
| Time zone issues | Verify TIMEZONE in .env uses proper format |
| Duplicate drafts | Run: `python -c "from src.persistence import EmailPersistence; EmailPersistence().reset()"` |

## Dependencies

```
google-auth-oauthlib==1.2.0       # Google OAuth
google-auth-httplib2==0.2.0       # Google Auth HTTP
google-api-python-client==2.107.0 # Gmail API
python-dotenv==1.0.0              # .env loading
schedule==1.2.0                   # Job scheduling
pytz==2024.1                       # Timezone support
```

## Draft File Format

### Markdown Format (draft_*.md)
```markdown
# Email Draft for Approval

## Original Email
- **From:** sender@example.com
- **Subject:** Original Subject

## Your Draft Response

**To:** sender@example.com
**Subject:** Re: Original Subject

Your response text here...

## Actions
- [✓ APPROVE & SEND](#approve-and-send)
- [✎ EDIT DRAFT](#edit-draft)
- [✗ DISCARD](#discard)
```

### JSON Format (drafts_*.json)
```json
[
  {
    "draft_subject": "Re: Hello",
    "draft_body": "Thanks for your email...",
    "original_sender": "user@example.com",
    "original_subject": "Hello",
    "template_used": "acknowledgement",
    "email_id": "abc123"
  }
]
```

## Workflow Quick Start

```
1. python setup_oauth.py          # Get credentials
2. cp .env.example .env            # Create .env
3. Edit .env                       # Add your credentials
4. Edit config.json                # Add allowed authors
5. python src/main.py --mode manual     # First run
6. Review drafts in data/drafts/
7. python verify_drafts.py [file] # Send approved
```

## Performance Tips

- **Batch Processing**: Let emails accumulate, then process all at once
- **Fast Approval**: Use `--approve-all` for trusted templates
- **Selective Sending**: Review each draft individually
- **Template Customization**: Create custom templates for common scenarios

## Security Checklist

- ✅ Never commit `.env`
- ✅ Never commit `credentials.json`
- ✅ Use `.env.example` as template
- ✅ Review `allowedAuthors` regularly
- ✅ Check processed emails database
- ✅ Monitor draft customizations

## Getting Help

1. **Setup Issues**: See `GETTING_STARTED.md`
2. **Workflow**: See `WORKFLOW.md`
3. **Full Docs**: See `README.md`
4. **Code Examples**: See `example_usage.py`
5. **Module Details**: Check docstrings in `src/`

## Keyboard Shortcuts

When running `verify_drafts.py`:
- `y` or `yes` - Send this draft
- `n` or `no` - Skip this draft
- `q` - Quit and stop

## File Cleanup

```bash
# Clean generated drafts (safe)
rm -r data/drafts/*

# Reset processed emails (reprocess all)
rm data/processed_emails.json
python -c "from src.persistence import EmailPersistence; EmailPersistence()"

# Clean all runtime data
rm -r data/*
```

## Advanced

### Custom Draft Template
Edit `src/draft_generator.py` TEMPLATES dictionary

### Adjust Scheduling
Edit `.env` SCHEDULE_TIME_* and TIMEZONE

### Change Email Filters
Edit `config.json` emailFilters section

### Modify Response Tone
Edit `src/draft_generator.py` FRIENDLY_OPENINGS and FRIENDLY_CLOSINGS

---

**Pro Tip**: Bookmark this guide for quick reference! 📌
