# 🚀 Complete Setup Guide - Job Finder

This guide will walk you through setting up the Job Finder system from scratch. Whether you're a complete beginner or an experienced developer, this guide has you covered.

**⏱️ Estimated Time**: 45-60 minutes for first-time setup

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Convert Your Resume](#part-1-convert-your-resume-most-important)
3. [Part 2: Get API Keys](#part-2-get-api-keys-all-free)
4. [Part 3: Configure Environment](#part-3-configure-environment)
5. [Part 4: Customize Job Search](#part-4-customize-job-search)
6. [Part 5: Test Locally](#part-5-test-locally)
7. [Part 6: Deploy to Google Cloud](#part-6-deploy-to-google-cloud)
8. [Part 7: Set Up Automation](#part-7-set-up-automation)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, make sure you have:

### Required Accounts
- **Google Cloud Account** ([Sign up here](https://cloud.google.com/))
  - Free tier is sufficient for this project
  - Credit card required but won't be charged unless you upgrade
- **Gmail Account** (for sending notifications)
- **Google Drive** (included with Gmail)

### Required Software
- **Python 3.9 or higher** ([Download here](https://www.python.org/downloads/))
  - Check version: `python3 --version`
- **Git** ([Download here](https://git-scm.com/downloads))
  - Check if installed: `git --version`
- **Google Cloud SDK** ([Download here](https://cloud.google.com/sdk/docs/install))
  - Check if installed: `gcloud --version`
- **Text Editor** (VS Code, Sublime Text, or any editor)

### Your Resume
- Have your resume ready in PDF, DOCX, or TXT format
- OR be ready to paste your resume text

---

## Part 1: Convert Your Resume (MOST IMPORTANT!)

**⏱️ Time**: 15 minutes

Your resume needs to be in JSON format for the system to work. We've created a powerful converter tool to make this easy!

### Why This Step is First

The resume converter is the **gateway tool** for this entire system. Without your resume in the correct JSON format, nothing else will work. This tool uses AI to intelligently parse your resume and create the structured data needed.

### Step 1.1: Install Converter Dependencies

```bash
# Navigate to your project directory
cd Job-Finder-

# Install the required packages
pip install PyPDF2 python-docx google-cloud-aiplatform
```

### Step 1.2: Run the Resume Converter

```bash
# Run the interactive converter
python tools/resume_converter.py
```

### Step 1.3: Follow the Interactive Prompts

The converter will guide you through:

1. **Choose Input Method**:
   - PDF file
   - DOCX file
   - TXT file
   - Paste text directly

2. **Choose Conversion Method**:
   - **AI-Powered** (Recommended): Uses Google's Gemini to intelligently parse your resume
   - **Manual Template**: Creates a blank JSON template you fill in manually

3. **Review Output**: The converter shows you the generated JSON

4. **Save**: Saves to `data/master_resume.json`

### What the JSON Format Looks Like

```json
{
  "personal_info": {
    "name": "Your Name",
    "title": "Senior Software Engineer",
    "email": "you@email.com",
    "phone": "+1-234-567-8900",
    "location": "New York, NY",
    "links": {
      "linkedin": "https://linkedin.com/in/yourprofile",
      "github": "https://github.com/yourusername"
    }
  },
  "summary": "2-3 sentence professional summary...",
  "skills": {
    "programming_languages": ["Python", "JavaScript", "Java"],
    "frontend": ["React", "Vue.js", "HTML/CSS"],
    "backend": ["Node.js", "Django", "FastAPI"],
    "databases": ["PostgreSQL", "MongoDB", "Redis"],
    "cloud_devops": ["AWS", "Docker", "Kubernetes"],
    "ai_ml": ["TensorFlow", "PyTorch", "Scikit-learn"],
    "tools": ["Git", "CI/CD", "Agile"]
  },
  "experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Software Engineer",
      "start_date": "2020-01",
      "end_date": "present",
      "location": "New York, NY",
      "responsibilities": [
        "Built scalable microservices serving 1M+ users using Python and AWS",
        "Led team of 5 engineers in developing React-based dashboard",
        "Improved system performance by 40% through optimization"
      ],
      "technologies": ["Python", "React", "AWS", "PostgreSQL"]
    }
  ],
  "education": [...],
  "certifications": [...],
  "projects": [...],
  "achievements": [...]
}
```

### Tips for a Great JSON Resume

1. **Use Action Verbs**: "Built", "Led", "Improved", "Designed"
2. **Include Metrics**: "Increased by 40%", "Serving 1M+ users", "Reduced by 50%"
3. **Be Specific**: Include exact technologies used
4. **Keep It Current**: Focus on recent relevant experience
5. **Be Honest**: Only include skills you actually have

### Updating Your Resume Later

Whenever you update your resume, simply:
1. Run the converter again with your updated resume
2. Or manually edit `data/master_resume.json`
3. Redeploy (if already on cloud): `cd deploy && ./deploy.sh`

---

## Part 2: Get API Keys (All Free!)

**⏱️ Time**: 15-20 minutes

You'll need several API keys. All of these are FREE for the usage levels this project requires.

### 2.1: Adzuna API (Job Search)

**Free Tier**: 1000 calls/month

1. Go to [https://developer.adzuna.com/](https://developer.adzuna.com/)
2. Click "Sign Up" (top right)
3. Fill in your details and verify email
4. Go to your dashboard
5. Copy your **App ID** and **App Key**
6. Keep these handy - you'll add them to `.env` later

### 2.2: JSearch API via RapidAPI (Job Search)

**Free Tier**: 100 requests/month

1. Go to [https://rapidapi.com/](https://rapidapi.com/)
2. Sign up for a free account
3. Go to [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
4. Click "Subscribe to Test" button
5. Select the **FREE plan** (100 requests/month)
6. Copy your **X-RapidAPI-Key** from the code snippets section
7. Keep this handy for `.env` file

### 2.3: Gmail App Password (Email Notifications)

**Note**: This is NOT your regular Gmail password. It's a special app-specific password.

1. Go to [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Under "Signing in to Google", enable **2-Step Verification** (if not already enabled)
3. Go back to Security settings
4. Search for "App passwords" or go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
5. Select app: **Mail**
6. Select device: **Other (Custom name)**
7. Enter name: "Job Finder"
8. Click "Generate"
9. **COPY THE 16-CHARACTER PASSWORD** (no spaces)
10. Keep this very secure - you'll add it to `.env`

**Important**: This password lets apps send emails from your Gmail. Keep it secret!

### 2.4: Google Drive Folder ID (Resume Storage)

1. Go to [https://drive.google.com](https://drive.google.com)
2. Create a new folder: "Job Finder Resumes" (or any name you like)
3. Open the folder (double-click it)
4. Look at the URL in your browser - it should look like:
   ```
   https://drive.google.com/drive/folders/1ABcDEfGhIjKlMnOpQrStUvWxYz123456
   ```
5. Copy the long string after `/folders/` (that's your folder ID)
6. Keep this for the `.env` file

### 2.5: Google Cloud Project

We'll set this up in detail in Part 6, but for now:

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Click "Select a project" dropdown at the top
3. Click "New Project"
4. Enter project name: "job-finder" (or your choice)
5. Click "Create"
6. Copy your project ID (shown below project name)
7. Keep this for the `.env` file

---

## Part 3: Configure Environment

**⏱️ Time**: 5 minutes

Now let's set up your environment variables with all those API keys.

### Step 3.1: Copy the Template

```bash
# In your project root directory
cp .env.template .env
```

### Step 3.2: Edit the .env File

Open `.env` in your text editor and fill in the values:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id-here

# Service account (we'll create this in Part 6)
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json

# Adzuna API
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# JSearch API
JSEARCH_API_KEY=your-rapidapi-key

# Gmail Configuration
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password

# Google Drive Folder ID
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id
```

### Step 3.3: Verify Your .env File

Make sure:
- No spaces around the `=` signs
- No quotes around values (unless they contain spaces)
- Gmail app password is 16 characters with no spaces
- All IDs and keys are copied correctly

**IMPORTANT**: The `.env` file is in `.gitignore` and will NEVER be committed to git. Keep it secure!

---

## Part 4: Customize Job Search

**⏱️ Time**: 10 minutes

Configure what jobs you're looking for by editing `config.yaml`.

### Step 4.1: Open config.yaml

```bash
# Open in your text editor
# The file is in the root directory
```

### Step 4.2: Set Job Search Preferences

```yaml
job_search:
  # Job titles you're interested in
  default_titles:
    - "Senior Full Stack Software Engineer"
    - "Lead Developer"
    - "Principal Engineer"  # Add as many as you want

  # Locations you're willing to work
  default_locations:
    - "New York, NY"
    - "San Francisco, CA"
    - "Remote"  # Always include Remote!

  # Your experience level
  experience_level: "Senior"  # Entry, Mid, Senior, Lead, Principal

  # Job types
  job_types:
    - "Full-time"
    # - "Contract"  # Uncomment if you want contract roles

  # Required skills (jobs must have these)
  required_skills:
    - "Python"
    - "JavaScript"
    # Add your must-have skills

  # Preferred skills (nice to have)
  preferred_skills:
    - "AI/ML"
    - "Cloud"
    - "Docker"
```

### Step 4.3: Configure Matching Settings

```yaml
matching:
  # Only show jobs with at least this % match
  min_match_percentage: 60  # Lower = more jobs, higher = better matches

  # Max jobs to process per day
  max_jobs_per_day: 10  # Adjust based on how many you want

  # Sort by match score (best matches first)
  sort_by_match: true
```

### Step 4.4: Configure Resume Customization

```yaml
resume_customization:
  # Balance between authentic and keywords
  authenticity_balance: 70  # 70% authentic, 30% keywords

  # How aggressive should modifications be?
  modification_level: moderate  # conservative, moderate, aggressive

  # Max skills to add per resume
  max_skills_to_add: 5

  # Minimum confidence score to add something
  min_confidence_score: 65  # 0-100

  # Generate interview prep guides?
  generate_interview_prep: true
```

### Step 4.5: Set Your Schedule

```yaml
schedule:
  # Time to run daily (24-hour format)
  run_time: "08:00"  # 8 AM

  # Timezone
  timezone: "America/New_York"  # Change to your timezone

  # Days to run (0 = Monday, 6 = Sunday)
  run_days: [0, 1, 2, 3, 4]  # Monday-Friday
```

### Step 4.6: Configure Notifications

```yaml
notifications:
  # Leave empty to use GMAIL_USER from .env
  email_to: ""

  # Send email notifications
  send_email: true

  # Upload to Google Drive
  upload_to_drive: true

  # Leave empty to use GOOGLE_DRIVE_FOLDER_ID from .env
  google_drive_folder_id: ""
```

**Note**: Leaving values empty tells the system to use environment variables from `.env`.

---

## Part 5: Test Locally

**⏱️ Time**: 10 minutes

Let's test the system on your local machine before deploying to the cloud.

### Step 5.1: Install Dependencies

```bash
# Make sure you're in the project root
cd Job-Finder-

# Install all required packages
pip install -r requirements.txt
```

This will install:
- google-cloud-aiplatform (for AI)
- google-cloud-firestore (for database)
- google-cloud-storage (for files)
- And many more...

### Step 5.2: Run a Test

```bash
# Run the main orchestrator
python main.py
```

### What to Expect

The system will:
1. ✅ Load your configuration
2. ✅ Read your resume from `data/master_resume.json`
3. ✅ Search job sites (this takes 30-60 seconds)
4. ✅ Analyze jobs with AI
5. ✅ Customize resumes for matches
6. ✅ Generate PDF files (saved to `output/`)
7. ✅ Send email (if configured)
8. ✅ Upload to Drive (if configured)

### Check the Output

```bash
# View generated resumes
ls -la output/

# You should see PDF files and modification reports
```

### Common First-Run Issues

**"No module named 'google'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**"Authentication error"**
```bash
# Solution: Check your .env file
# Make sure GOOGLE_CLOUD_PROJECT and API keys are correct
```

**"No jobs found"**
- This is normal if there are no new matches today
- Try adjusting `min_match_percentage` lower in `config.yaml`

---

## Part 6: Deploy to Google Cloud

**⏱️ Time**: 20-30 minutes

Now let's deploy to Google Cloud so it runs automatically every day!

### Step 6.1: Install Google Cloud SDK

If you haven't already:
- Download from [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
- Follow installation instructions for your OS
- Verify: `gcloud --version`

### Step 6.2: Login to Google Cloud

```bash
# Authenticate with your Google account
gcloud auth login

# This will open a browser window
# Sign in with the same Google account you used for Cloud Console
```

### Step 6.3: Set Your Project

```bash
# Set the project ID from Part 2
gcloud config set project your-project-id

# Verify it's set correctly
gcloud config get-value project
```

### Step 6.4: Enable Required APIs

```bash
# Enable all required Google Cloud APIs
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  drive.googleapis.com \
  gmail.googleapis.com
```

This may take 2-3 minutes.

### Step 6.5: Create Firestore Database

```bash
# Create a Firestore database in Native mode
gcloud firestore databases create \
  --region=us-central1
```

Choose "us-central1" (or your preferred region).

### Step 6.6: Create Service Account

```bash
# Create a service account
gcloud iam service-accounts create job-finder-sa \
  --display-name="Job Finder Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:job-finder-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/owner"

# Create and download key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=job-finder-sa@your-project-id.iam.gserviceaccount.com
```

**Important**: This creates `service-account-key.json` in your project root. This file is already in `.gitignore`.

### Step 6.7: Share Google Drive Folder

1. Open the Google Drive folder you created earlier
2. Click "Share" button
3. Add your service account email:
   ```
   job-finder-sa@your-project-id.iam.gserviceaccount.com
   ```
4. Give it "Editor" permissions
5. Click "Share"

This allows the Cloud Function to upload files to your Drive.

### Step 6.8: Run the Deployment Script

```bash
# Navigate to deploy directory
cd deploy

# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### What the Deployment Does

The script will:
1. ✅ Copy source files from root to deploy/
2. ✅ Copy your .env file temporarily
3. ✅ Deploy to Cloud Functions (Gen 2)
4. ✅ Configure environment variables
5. ✅ Set memory to 2GB, timeout to 9 minutes
6. ✅ Ask if you want to set up Cloud Scheduler

### Deployment Output

You should see:
```
Deploying function (may take a while)...
✓ Function deployed successfully
✓ Function URL: https://us-central1-your-project-id.cloudfunctions.net/job-finder
```

**Save this URL** - you'll need it for testing and scheduling.

---

## Part 7: Set Up Automation

**⏱️ Time**: 5 minutes

Now let's set up automatic daily runs with Cloud Scheduler.

### Option A: During Deployment

When deploy.sh asks:
```
Do you want to set up Cloud Scheduler? (y/n)
```

Answer `y` and it will:
- Create a scheduler job
- Set it to run at your configured time (from config.yaml)
- Use your configured timezone

### Option B: Manual Setup

```bash
# Create a Cloud Scheduler job
gcloud scheduler jobs create http job-finder-daily \
  --location=us-central1 \
  --schedule="0 8 * * *" \
  --time-zone="America/New_York" \
  --uri="YOUR_FUNCTION_URL" \
  --http-method=POST \
  --headers="Content-Type=application/json"
```

Replace:
- `0 8 * * *` with your preferred schedule (cron format)
- `America/New_York` with your timezone
- `YOUR_FUNCTION_URL` with the URL from deployment

### Cron Schedule Examples

- `0 8 * * *` = Every day at 8 AM
- `0 9 * * 1-5` = Weekdays at 9 AM
- `0 */6 * * *` = Every 6 hours
- `0 8,14 * * *` = 8 AM and 2 PM daily

### Step 7.2: Test the Scheduler

```bash
# Trigger manually to test
gcloud scheduler jobs run job-finder-daily --location=us-central1
```

### Step 7.3: View Logs

```bash
# View Cloud Function logs
gcloud functions logs read job-finder \
  --region=us-central1 \
  --limit=50
```

---

## Troubleshooting

### Common Issues

#### "Permission denied" errors
- Make sure service account has correct roles
- Check that Drive folder is shared with service account
- Verify Firestore database is created

#### "API not enabled" errors
```bash
# Enable missing APIs
gcloud services enable <api-name>.googleapis.com
```

#### Email not sending
- Verify Gmail app password is correct (16 chars, no spaces)
- Check that 2FA is enabled on Google account
- Test with local run first: `python main.py`

#### No jobs found
- Lower `min_match_percentage` in config.yaml
- Check that job_search titles and locations are reasonable
- Verify API keys are valid (Adzuna, JSearch)

#### Deployment fails
- Check that all APIs are enabled
- Verify project billing is enabled
- Ensure service account key exists
- Check deploy.sh has correct permissions: `chmod +x deploy.sh`

### Getting Help

1. **Check logs**: `gcloud functions logs read job-finder --region=us-central1`
2. **Test locally**: `python main.py` to see detailed errors
3. **Verify config**: Make sure .env and config.yaml are correct
4. **Check quotas**: Ensure you haven't exceeded free tier limits

---

## Next Steps

Congratulations! Your Job Finder is now set up and running. Here's what happens next:

### Daily Operation

Every day at your scheduled time:
1. ✅ Cloud Scheduler triggers your Cloud Function
2. ✅ Function searches all enabled job sources
3. ✅ AI analyzes and matches jobs
4. ✅ Customizes resumes for top matches
5. ✅ Generates PDFs and interview prep guides
6. ✅ Uploads to Google Drive
7. ✅ Sends you an email with everything
8. ✅ Updates Firestore to prevent duplicates

### Monitoring Your System

```bash
# View recent logs
gcloud functions logs read job-finder --region=us-central1 --limit=100

# Check scheduler jobs
gcloud scheduler jobs list --location=us-central1

# View Firestore data (in Cloud Console)
# https://console.cloud.google.com/firestore
```

### Updating Your System

When you make changes:

```bash
# Update your master resume
python tools/resume_converter.py

# Or edit config.yaml to change job preferences
# Then redeploy:
cd deploy
./deploy.sh
```

### Cost Monitoring

This project should stay **FREE** under normal usage:
- Vertex AI: Free tier includes 50 requests/day
- Cloud Functions: Free tier includes 2M invocations/month
- Firestore: Free tier includes 50K reads/day
- Cloud Scheduler: Free tier includes 3 jobs

**Monitor costs**: [https://console.cloud.google.com/billing](https://console.cloud.google.com/billing)

### Customization Ideas

- Add more job sources (extend scrapers/)
- Adjust matching algorithm (modify src/matcher/)
- Create custom email templates (src/notifier/)
- Add Slack/Discord notifications
- Build a web dashboard

### Further Reading

- [FEATURES.md](FEATURES.md) - Detailed feature documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [COPILOT_GUIDE.md](COPILOT_GUIDE.md) - For AI assistants
- [tools/README.md](tools/README.md) - Resume converter details

---

## Summary Checklist

Before you're fully set up, make sure you've completed:

- [ ] Converted resume to JSON using `tools/resume_converter.py`
- [ ] Got all API keys (Adzuna, JSearch, Gmail, Drive)
- [ ] Created and filled `.env` file
- [ ] Customized `config.yaml` with job preferences
- [ ] Tested locally with `python main.py`
- [ ] Created Google Cloud project
- [ ] Enabled all required APIs
- [ ] Created Firestore database
- [ ] Created service account and downloaded key
- [ ] Shared Drive folder with service account
- [ ] Deployed to Cloud Functions with `./deploy.sh`
- [ ] Set up Cloud Scheduler for daily runs
- [ ] Tested scheduler with manual trigger
- [ ] Received first email with jobs!

**You're all set!** Your personal AI job finder is now working for you 24/7.

---

**Need help?** Check the troubleshooting section above or open an issue on GitHub.
