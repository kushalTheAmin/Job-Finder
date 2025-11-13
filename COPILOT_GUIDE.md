# 🤖 Copilot Guide - Job Finder

This guide is specifically designed for AI coding assistants (like Claude, GitHub Copilot, ChatGPT, etc.) to help users quickly set up, modify, and troubleshoot the Job Finder system.

---

## Quick Reference for Users

When working with an AI assistant on this project, use these phrases to reference specific documentation:

| User Says | AI Should Reference |
|-----------|---------------------|
| "Help me set up Job Finder" | [SETUP_GUIDE.md](SETUP_GUIDE.md) |
| "Convert my resume" | [tools/README.md](tools/README.md) + `tools/resume_converter.py` |
| "Configure job search" | `config.yaml` + [FEATURES.md](FEATURES.md#10-configuration-system) |
| "How does matching work?" | [FEATURES.md](FEATURES.md#3-intelligent-job-matching) |
| "Customize resume settings" | [FEATURES.md](FEATURES.md#4-smart-resume-customization) |
| "Deploy to Google Cloud" | [SETUP_GUIDE.md](SETUP_GUIDE.md#part-6-deploy-to-google-cloud) |
| "Add a new job source" | `src/scrapers/` + [ARCHITECTURE.md](ARCHITECTURE.md#2-scrapers) |
| "Modify email template" | `src/notifier/email_sender.py` + [FEATURES.md](FEATURES.md#7-email-notifications) |
| "Check project structure" | [ARCHITECTURE.md](ARCHITECTURE.md#project-structure) |
| "Fix deployment issue" | [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) |

---

## File Location Map

### Core Files (Users Will Edit These)

```
📄 .env                     # API keys, secrets (copy from .env.template)
📄 config.yaml              # Job search preferences, matching settings
📄 data/master_resume.json  # User's resume in JSON format
```

### Setup & Documentation

```
📄 README.md               # Main overview
📄 SETUP_GUIDE.md          # Step-by-step setup (START HERE!)
📄 FEATURES.md             # Detailed feature docs
📄 ARCHITECTURE.md         # System architecture
📄 COPILOT_GUIDE.md        # This file
📄 .env.template           # Template for .env file
```

### Source Code

```
src/
├── scrapers/              # Job search modules
│   ├── aggregator.py      # Coordinates all scrapers
│   ├── linkedin_scraper.py
│   ├── indeed_scraper.py
│   ├── adzuna_scraper.py
│   └── jsearch_scraper.py
│
├── matcher/
│   └── job_matcher.py     # AI-powered job matching
│
├── resume/
│   ├── smart_customizer.py    # Story-based customizer (NEW)
│   ├── story_builder.py       # Story templates
│   ├── ats_optimizer.py       # ATS optimization
│   ├── interview_prep.py      # Prep guide generator
│   ├── pdf_generator.py       # PDF generation
│   ├── doc_generator.py       # DOCX generation
│   ├── resume_modifier.py     # Applies modifications
│   └── resume_validator.py    # Validates changes
│
├── notifier/
│   └── email_sender.py    # Email notifications
│
└── storage/
    ├── firestore_db.py    # Database operations
    └── gdrive.py          # Google Drive uploads
```

### Tools & Tests

```
tools/
├── resume_converter.py    # Convert PDF/DOCX → JSON (IMPORTANT!)
└── README.md              # Converter documentation

tests/
├── test_simple.py
├── test_resume_modifier.py
├── test_resume_generation.py
└── test_with_real_data.py
```

### Deployment

```
deploy/
├── main.py               # Cloud Function entry point
├── orchestrator.py       # Cloud orchestrator
├── deploy.sh             # Deployment script
└── requirements.txt      # Cloud dependencies
```

---

## Common Tasks - Quick Commands

### Initial Setup

```bash
# 1. Convert resume to JSON (FIRST STEP!)
python tools/resume_converter.py

# 2. Copy environment template
cp .env.template .env
# Then edit .env with your API keys

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test locally
python main.py

# 5. Deploy to cloud
cd deploy && ./deploy.sh
```

### Configuration Changes

```bash
# Edit job search preferences
nano config.yaml  # or use any editor

# Common settings to change:
# - job_search.default_titles
# - job_search.default_locations
# - matching.min_match_percentage
# - resume_customization.modification_level
```

### Deployment

```bash
# Deploy to Google Cloud
cd deploy
./deploy.sh

# View logs
gcloud functions logs read job-finder --region=us-central1 --limit=50

# Test cloud function
gcloud scheduler jobs run job-finder-daily --location=us-central1
```

### Debugging

```bash
# Test locally with verbose output
python main.py

# Check Firestore data
gcloud firestore databases describe --database=(default)

# View Cloud Function details
gcloud functions describe job-finder --region=us-central1
```

---

## AI Assistant Instructions

When helping users with Job Finder:

### 1. Always Start with Resume Conversion

**The resume converter is the gateway tool.** Nothing works without `master_resume.json`.

```markdown
First, let's convert your resume to JSON format:

1. Run: `python tools/resume_converter.py`
2. Follow the prompts to upload your PDF/DOCX or paste text
3. Choose "AI-Powered" conversion (recommended)
4. The tool will save to `data/master_resume.json`

This file is required for the system to work.
```

### 2. Configuration First, Code Later

Most user needs can be met with configuration changes, not code:

```markdown
To change job search criteria, edit `config.yaml`:

```yaml
job_search:
  default_titles:
    - "Your Desired Title"
  default_locations:
    - "Your Location"
```

Then redeploy: `cd deploy && ./deploy.sh`
```

### 3. Reference Documentation

Always point users to the right documentation:

```markdown
For detailed setup instructions, see:
- [SETUP_GUIDE.md](SETUP_GUIDE.md#part-1-convert-your-resume-most-important)

For feature explanations, see:
- [FEATURES.md](FEATURES.md#2-job-search--scraping)
```

### 4. Provide Context-Aware Help

#### Example: User wants to add a new job source

```markdown
To add a new job scraper:

1. Create a new file in `src/scrapers/` (e.g., `glassdoor_scraper.py`)

2. Implement the scraper following this template:

```python
from typing import List
import requests

class GlassdoorScraper:
    def search(self, title: str, location: str) -> List[dict]:
        # Implementation
        jobs = []
        # ... scraping logic ...
        return jobs

    def parse_job(self, raw_data) -> dict:
        return {
            "id": "...",
            "title": "...",
            "company": "...",
            "location": "...",
            "description": "...",
            "url": "...",
            "source": "glassdoor"
        }
```

3. Add to `src/scrapers/aggregator.py`:
```python
from .glassdoor_scraper import GlassdoorScraper

# In search_all_sources method:
if "glassdoor" in enabled_sources:
    futures[executor.submit(glassdoor.search, ...)] = "glassdoor"
```

4. Enable in `config.yaml`:
```yaml
sources:
  enabled:
    - "glassdoor"
```

See [ARCHITECTURE.md](ARCHITECTURE.md#2-scrapers) for architecture details.
```

### 5. Troubleshooting Protocol

When users report errors:

1. **Ask for error message** and logs
2. **Check logs**: `gcloud functions logs read job-finder --region=us-central1`
3. **Reference troubleshooting**: [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting)
4. **Test locally first**: `python main.py`
5. **Check configuration**: `.env` and `config.yaml`

### 6. Code Modification Guidelines

When suggesting code changes:

✅ **DO**:
- Show exact file path: `src/matcher/job_matcher.py`
- Provide complete code blocks
- Explain what the code does
- Mention any dependencies
- Suggest testing: `python -m pytest tests/`

❌ **DON'T**:
- Make changes without explaining
- Forget to update requirements.txt if adding packages
- Skip testing steps
- Modify .env (it's gitignored and personal)

---

## Common User Requests & Solutions

### "I want to search for different jobs"

```markdown
Edit `config.yaml`:

```yaml
job_search:
  default_titles:
    - "Data Scientist"
    - "ML Engineer"
  default_locations:
    - "San Francisco, CA"
    - "Remote"
```

Then redeploy: `cd deploy && ./deploy.sh`
```

### "I want more/fewer job matches"

```markdown
Edit `config.yaml`:

```yaml
matching:
  min_match_percentage: 50  # Lower = more jobs
  max_jobs_per_day: 20      # Increase limit
```

Lower percentage = more jobs, but lower quality matches.
```

### "Resume modifications are too aggressive"

```markdown
Edit `config.yaml`:

```yaml
resume_customization:
  modification_level: conservative  # Was: moderate
  min_confidence_score: 80           # Was: 65 (higher = safer)
  max_skills_to_add: 3               # Was: 5 (fewer changes)
```
```

### "I want to add my skill to the system"

```markdown
Edit `data/master_resume.json`:

```json
{
  "skills": {
    "programming_languages": ["Python", "JavaScript", "Go"],  // Add Go
    "cloud_devops": ["AWS", "Docker", "Terraform"]  // Add Terraform
  },
  "experience": [
    {
      "responsibilities": [
        "Built infrastructure using Terraform..."  // Add to experience
      ],
      "technologies": ["Python", "AWS", "Terraform"]  // Add here too
    }
  ]
}
```

OR use the converter again: `python tools/resume_converter.py`
```

### "Email isn't sending"

```markdown
Check these:

1. **Gmail App Password**: 16 characters, no spaces
   - Verify in `.env`: `GMAIL_APP_PASSWORD=abcd...`
   - Must have 2FA enabled on Google account

2. **Test locally**:
   ```bash
   python main.py
   ```
   Check for email errors in output

3. **Check Gmail quota**: 500 emails/day limit

4. **Verify config**:
   ```yaml
   notifications:
     send_email: true
     email_to: ""  # Empty = uses GMAIL_USER from .env
   ```

See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) for more.
```

### "How do I change the schedule?"

```markdown
Edit `config.yaml`:

```yaml
schedule:
  run_time: "09:00"  # 9 AM
  timezone: "America/Los_Angeles"
  run_days: [0, 1, 2, 3, 4]  # Monday-Friday
```

Then update Cloud Scheduler:

```bash
gcloud scheduler jobs update http job-finder-daily \
  --location=us-central1 \
  --schedule="0 9 * * 1-5" \
  --time-zone="America/Los_Angeles"
```

Cron format: `0 9 * * 1-5` = 9 AM, Monday-Friday
```

### "I want to modify the email template"

```markdown
Edit `src/notifier/email_sender.py`:

Find the `_create_html_email()` method:

```python
def _create_html_email(self, jobs, date):
    html = """
    <html>
      <head>
        <style>
          /* Your custom CSS here */
        </style>
      </head>
      <body>
        <!-- Your custom HTML here -->
      </body>
    </html>
    """
    return html
```

Modify the HTML/CSS as needed, then redeploy.
```

### "How do I add Slack notifications?"

```markdown
Create `src/notifier/slack_sender.py`:

```python
import requests

class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_jobs(self, jobs):
        for job in jobs:
            message = {
                "text": f"🎯 New Job Match: {job['title']} at {job['company']}",
                "attachments": [{
                    "text": f"Match: {job['match']}%\nLocation: {job['location']}\nURL: {job['url']}"
                }]
            }
            requests.post(self.webhook_url, json=message)
```

Add to orchestrator and config.yaml. See [FEATURES.md](FEATURES.md) for patterns.
```

---

## Testing Commands

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_simple.py

# Test with verbose output
python -m pytest tests/ -v

# Test locally (end-to-end)
python main.py

# Test Cloud Function locally
cd deploy
functions-framework --target=main --debug
```

---

## Environment Variables Reference

**File**: `.env` (copy from `.env.template`)

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | [Cloud Console](https://console.cloud.google.com/) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | Created in [Setup Part 6](SETUP_GUIDE.md#step-66-create-service-account) |
| `ADZUNA_APP_ID` | Adzuna API ID | [Adzuna Developer](https://developer.adzuna.com/) |
| `ADZUNA_APP_KEY` | Adzuna API key | [Adzuna Developer](https://developer.adzuna.com/) |
| `JSEARCH_API_KEY` | RapidAPI key | [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) |
| `GMAIL_USER` | Your Gmail address | Your Gmail account |
| `GMAIL_APP_PASSWORD` | Gmail app password | [Google App Passwords](https://myaccount.google.com/apppasswords) |
| `GOOGLE_DRIVE_FOLDER_ID` | Drive folder ID | From folder URL: `/folders/[ID]` |

---

## Dependencies Reference

### Local Development
```bash
pip install -r requirements.txt
```

Key packages:
- `google-cloud-aiplatform` - Vertex AI
- `google-cloud-firestore` - Database
- `google-cloud-storage` - File storage
- `WeasyPrint` - PDF generation
- `python-docx` - DOCX generation
- `PyPDF2` - PDF reading
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing

### Cloud Deployment
```bash
# Automatically installed during deployment
# See: deploy/requirements.txt
```

---

## Quick Debugging Checklist

When something doesn't work:

- [ ] `.env` file exists and has all required variables
- [ ] `master_resume.json` exists in `data/` folder
- [ ] `config.yaml` has valid job titles and locations
- [ ] API keys are correct (test them individually)
- [ ] Google Cloud project has billing enabled
- [ ] All required APIs are enabled (see [SETUP_GUIDE.md](SETUP_GUIDE.md#step-64-enable-required-apis))
- [ ] Service account has correct permissions
- [ ] Google Drive folder is shared with service account
- [ ] Firestore database is created
- [ ] Cloud Function is deployed without errors
- [ ] Test locally first: `python main.py`
- [ ] Check logs: `gcloud functions logs read job-finder`

---

## Resources for AI Assistants

When generating code or suggestions:

1. **Resume JSON Structure**: See [FEATURES.md](FEATURES.md#json-structure)
2. **Job Data Model**: See [ARCHITECTURE.md](ARCHITECTURE.md#job-model)
3. **Scraper Pattern**: See [ARCHITECTURE.md](ARCHITECTURE.md#2-scrapers)
4. **Customization Logic**: See `src/resume/smart_customizer.py`
5. **Email Template**: See `src/notifier/email_sender.py`
6. **Configuration Schema**: See `config.yaml` with comments

---

## Example Conversations

### User: "Help me set up this project"

**AI Response**:
```markdown
I'll help you set up Job Finder! Let's start with the most important step:

### Step 1: Convert Your Resume (Required!)

Run the resume converter tool:
```bash
python tools/resume_converter.py
```

This converts your PDF/DOCX resume to the required JSON format.
Follow the prompts, choose "AI-Powered" conversion, and it will save to
`data/master_resume.json`.

Once that's done, we'll move to API keys and configuration.

For the complete setup process, see: [SETUP_GUIDE.md](SETUP_GUIDE.md)
```

### User: "I want to customize the matching algorithm"

**AI Response**:
```markdown
The matching algorithm is in `src/matcher/job_matcher.py`.

Current algorithm (simplified):
```python
# Critical skills (3+ mentions): 40% weight
# Important skills (2-3 mentions): 30% weight
# Nice-to-have skills (1 mention): 15% weight
# Experience level: 10% weight
# Domain fit: 5% weight
```

To modify the weights, edit the `calculate_match_score()` method.

You can also adjust the threshold without code changes:

Edit `config.yaml`:
```yaml
matching:
  min_match_percentage: 70  # Only show 70%+ matches
```

See [FEATURES.md](FEATURES.md#match-score-calculation) for detailed algorithm.
```

---

## Summary for AI Assistants

When helping users with Job Finder:

1. **Start with resume conversion** - it's the gateway
2. **Prefer configuration over code** changes
3. **Always reference documentation** for details
4. **Test locally first** before deploying
5. **Check logs** when troubleshooting
6. **Provide complete examples** with file paths
7. **Explain what code does** and why
8. **Follow the setup order** in SETUP_GUIDE.md

**Most Common User Needs**:
1. Initial setup → [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Resume conversion → `python tools/resume_converter.py`
3. Change job search → Edit `config.yaml`
4. Troubleshooting → Check logs + [SETUP_GUIDE.md#troubleshooting](SETUP_GUIDE.md#troubleshooting)
5. Add features → [ARCHITECTURE.md](ARCHITECTURE.md) + source code

---

**This guide is continuously updated. For the latest docs, see the main README.md.**
