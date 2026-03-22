# Getting Started Guide - Human-in-the-Loop Gmail Agent

## Prerequisites

- Python 3.9 or higher
- Google account with Gmail enabled
- VS Code (optional, for enhanced integration)

## Complete Setup Instructions

### Step 1: Prepare Google Cloud Project

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Click "Create Project"
   - Name it (e.g., "Gmail Agent")
   - Wait for creation to complete

2. **Enable Gmail API**
   - In Google Cloud Console, search for "Gmail API"
   - Click on it
   - Click "Enable"
   - Wait for enablement

3. **Create OAuth2 Credentials**
   - Go to "Credentials" in the left menu
   - Click "Create Credentials"
   - Choose "OAuth client ID"
   - Select "Desktop Application"
   - Click "Create"
   - Download the JSON file as `credentials.json`

4. **Save Credentials File**
   - Download the credentials JSON
   - Save in project root as `credentials.json`
   - Keep this file private (never commit to git)

### Step 2: Clone and Setup Project

```bash
# Navigate to the project directory
cd email-course-automation

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your information
# Open .env and fill in:
# - GOOGLE_CLIENT_ID (from credentials.json or setup_oauth.py)
# - GOOGLE_CLIENT_SECRET (from credentials.json or setup_oauth.py)
# - USER_EMAIL (your Gmail address)
# - SCHEDULE_TIME_1 and SCHEDULE_TIME_2 (desired run times)
# - TIMEZONE (your timezone, e.g., America/New_York)
```

### Step 4: Run OAuth2 Setup

```bash
# Run the OAuth2 setup wizard
python setup_oauth.py

# Follow the prompts:
# 1. A browser window will open
# 2. Sign in with your Gmail account
# 3. Grant permissions to the application
# 4. The script will display your credentials
# 5. Copy the credentials and paste them into .env file
```

### Step 5: Configure Allowed Authors

Edit `config.json` and add the email addresses you want the agent to process:

```json
{
  "allowedAuthors": [
    "colleague@company.com",
    "friend@example.com",
    "mentor@organization.org"
  ],
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

## Running the Agent

### Manual Mode (One-Time)

Process emails immediately:

```bash
python src/main.py --mode manual
```

This will:
1. Connect to Gmail
2. Fetch unread emails from allowed authors
3. Generate professional draft responses
4. Save drafts to `./data/drafts/`
5. Present results for approval

### Scheduled Mode (Continuous)

Run automatically at configured times:

```bash
python src/main.py --mode scheduled
```

The agent will:
1. Check for new emails at 9 AM and 5 PM (by default)
2. Generate drafts automatically
3. Wait for your approval
4. Keep running in the background

To stop scheduled mode, press `Ctrl+C`

## Approving and Sending Drafts

### Method 1: Interactive Approval

```bash
python verify_drafts.py ./data/drafts/drafts_*.json
```

You'll see each draft with options:
- `y` - Send this draft
- `n` - Skip this draft
- `q` - Quit and stop processing

### Method 2: Approve All

Send all drafts without confirmation:

```bash
python verify_drafts.py ./data/drafts/drafts_*.json --approve-all
```

### Method 3: Edit Before Sending

1. Open the markdown files in `./data/drafts/`
2. Edit the draft content as needed
3. Save the file
4. Run verify_drafts.py to send

## File Structure After Complete Setup

```
email-course-automation/
├── venv/                          # Virtual environment (auto-created)
├── .env                           # Your credentials (DO NOT COMMIT)
├── credentials.json               # Gmail OAuth creds (DO NOT COMMIT)
├── config.json                    # Your settings
├── .github/
│   └── copilot-instructions.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── gmail_handler.py
│   ├── draft_generator.py
│   ├── scheduler.py
│   ├── persistence.py
│   └── vscode_handler.py
├── data/
│   ├── drafts/                    # Generated drafts (*.md and *.json)
│   └── processed_emails.json      # Tracking database
├── example_usage.py
├── setup_oauth.py
├── verify_drafts.py
└── README.md
```

## Troubleshooting

### "credentials.json not found"
- Download it from Google Cloud Console
- Save it in the project root directory
- Run `python setup_oauth.py` again

### "No emails found"
- Check `config.json` - verify author emails are correct
- Ensure those authors have sent you unread emails
- The agent only processes unread emails

### "Gmail authentication failed"
- Verify .env file has correct credentials
- Check that Gmail API is enabled in Google Cloud
- Try running `python setup_oauth.py` again
- Delete `./data/gmail_token.pickle` and retry

### "Scheduling not working"
- Verify timezone is correct in .env
- Use 24-hour format (HH:MM) for times
- Check system time is correct
- Run with: `python src/main.py --mode scheduled`

### "ModuleNotFoundError: No module named 'google'"
- Activate your virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Next Steps

1. ✅ Complete the setup above
2. 📧 Send yourself a test email from an allowed author
3. ▶️ Run: `python src/main.py --mode manual`
4. 📋 Review the generated drafts
5. ✓ Approve your first draft: `python verify_drafts.py ./data/drafts/drafts_*.json`
6. ⏰ Set up scheduled runs: `python src/main.py --mode scheduled`

## Key Security Reminders

- **Never commit** `.env` file to git
- **Never commit** `credentials.json` to git
- Keep your OAuth2 credentials private
- Regularly review the `allowed_authors` list
- Monitor the `processed_emails.json` for suspicious activity

## Additional Resources

- See `README.md` for detailed documentation
- See `.github/copilot-instructions.md` for workspace context
- See `example_usage.py` for code examples
- Check individual module docstrings for API details

---

**Questions?** Review the README.md or check the inline code documentation.

**Ready to go!** 🚀

