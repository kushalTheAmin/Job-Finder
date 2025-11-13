# 🎯 Job Finder - Automated Job Search & Resume Customizer

**Your personal AI assistant that finds matching jobs and creates custom resumes automatically - every single day!**

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete step-by-step setup guide (start here!)
- **[FEATURES.md](FEATURES.md)** - Detailed feature explanations and configuration
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and project structure
- **[COPILOT_GUIDE.md](COPILOT_GUIDE.md)** - Guide for AI coding assistants
- **[tools/README.md](tools/README.md)** - Resume converter tool documentation

## What Does This Do?

Imagine waking up every morning to an email with:
- 📧 A list of jobs that match YOUR skills and preferences (60%+ match)
- 📄 Custom resumes already created for each job
- ☁️ All resumes uploaded to your Google Drive
- 🎯 Everything ranked by how well they match your profile

That's exactly what this system does - **completely automatically**!

## How It Works (Simple Version)

```
Every Day at 8 AM:
1. 🔍 Searches LinkedIn, Indeed, Adzuna, and other job sites
2. 🤖 AI analyzes each job and compares it to YOUR resume
3. ✅ Only picks jobs that match at least 60% (you can change this!)
4. ✏️ AI rewrites your resume for EACH job
   - Changes "Vertex AI" to "OpenAI" if job wants OpenAI
   - Highlights relevant skills
   - Keeps your achievements authentic
5. 📧 Emails you the jobs + customized resumes
6. ☁️ Uploads everything to Google Drive
7. 💾 Remembers which jobs it already found (no duplicates!)
```

## Features

### 🧠 **NEW: Intelligent Story-Based Customization**
- **Thinks holistically** about your resume, not just bullet-by-bullet
- **2-3 mention rule**: Technologies appear multiple times with coherent context
- **Timeline intelligence**: Never adds tech that didn't exist in that time period
- **Coherence validation**: Ensures resume sounds authentic, not keyword-stuffed
- **Confidence scoring**: Tells you which changes need interview prep
- **Interview prep guides**: Auto-generated study plans for added skills

### ✨ Smart Job Matching
- **Dual-brain analysis**: ATS Scanner + Human Recruiter perspective
- Searches multiple job sites at once
- AI calculates match percentage for each job
- Only shows you jobs above your threshold (default: 60%)
- Ranks jobs by best match first
- Identifies CRITICAL vs NICE-TO-HAVE skills

### 🎨 AI-Powered Resume Customization
- **Story templates**: Multiple apps, migration, integration, hybrid cloud
- Reads the job description from both ATS and human perspectives
- Identifies required skills and technologies with priority levels
- Intelligently modifies your resume to match while staying authentic
- Changes tech stack mentions (e.g., Vertex AI → OpenAI) only when coherent
- Highlights relevant experience with specific metrics
- **Keeps your core achievements and metrics unchanged**
- **70% authentic / 30% keywords balance** (configurable)

### 🚫 No Duplicates
- Tracks every job in Firestore database
- Never shows you the same job twice
- Maintains history of all applications

### 📧 Email Notifications
- Beautiful HTML emails with job details
- Match percentages for each job
- Why you're a great fit for each position
- Resumes attached as PDFs

### ☁️ Cloud Storage
- Automatically uploads to Google Drive
- Organized by job and date
- Easy to access from anywhere

### 📚 Interview Preparation
- **Auto-generated prep guides** for each job
- Study plans with estimated time (e.g., "6 hours total")
- Sample interview questions and suggested answers
- Resource links for each technology
- Confidence assessment per change made

### ⚙️ Fully Configurable
- Change job search criteria anytime
- Adjust match threshold and authenticity balance
- Choose which job sites to search
- Set modification aggressiveness (conservative/moderate/aggressive)
- Configure minimum confidence scores
- Set your own schedule

## Quick Start (For Beginners)

### What You Need

1. **A Google Cloud account** (free tier is fine!)
2. **Gmail account** (for sending emails)
3. **Your resume** in JSON format (we'll help you convert it)
4. **30 minutes** to set everything up

### Step 1: Get Your Master Resume Ready

Your resume needs to be in JSON format. We've included a sample in `data/master_resume.json`.

**Option A**: Edit the sample file with your info

**Option B**: Use our converter tool - converts PDF/DOCX/TXT to JSON automatically!

```bash
# Install converter dependencies
pip install PyPDF2 python-docx

# Run the interactive converter
python tools/resume_converter.py

# It will:
# 1. Ask for your resume (PDF, DOCX, TXT, or paste text)
# 2. Extract the text
# 3. Convert to JSON using AI (or provide a template)
# 4. Save to data/master_resume.json
```

See `tools/README.md` for detailed converter documentation.

### Step 2: Get API Keys (All Free!)

You need a few free API keys:

#### Adzuna (Job Search)
1. Go to https://developer.adzuna.com/
2. Click "Sign Up"
3. Get your App ID and App Key
4. Copy them to your `.env` file

#### JSearch/RapidAPI (Job Search)
1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Sign up for free
3. Click "Subscribe to Test" (FREE tier)
4. Copy API key to your `.env` file

#### Gmail (For Email Notifications)
1. Go to https://myaccount.google.com/security
2. Turn on "2-Step Verification"
3. Search for "App Passwords"
4. Create one for "Mail"
5. Copy the password to your `.env` file

#### Google Drive (For Storing Resumes)
1. Go to https://drive.google.com
2. Create a folder called "Job Finder Resumes"
3. Open it and look at the URL
4. Copy the folder ID (the long string after `/folders/`)
5. Put it in your `.env` file

### Step 3: Install on Your Computer (Local Testing)

```bash
# 1. Clone this repository
git clone <your-repo-url>
cd Job-Finder-

# 2. Install Python packages
pip install -r requirements.txt

# 3. Copy the template environment file
cp .env.template .env

# 4. Edit .env with your API keys
# Use any text editor to fill in your keys
# See .env.template for detailed instructions on getting each key

# 5. Edit config.yaml with your preferences
# Set your job titles, locations, etc.

# 6. Update your resume
# Edit data/master_resume.json with your information

# 7. Test it!
python main.py
```

### Step 4: Deploy to Google Cloud (Run Automatically)

This is the magic part - it will run automatically every day!

```bash
# 1. Make sure you have gcloud installed
# Download from: https://cloud.google.com/sdk/docs/install

# 2. Login to Google Cloud
gcloud auth login

# 3. Create a new project (or use existing)
gcloud projects create job-finder-project
gcloud config set project job-finder-project

# 4. Run the deployment script
cd deploy
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Deploy everything to Google Cloud
- Set up automatic daily runs at 8 AM
- Give you a URL to trigger it manually

**That's it!** You're done! 🎉

## Configuration Guide

### config.yaml - Main Settings

```yaml
# Change these to match what you're looking for
job_search:
  default_titles:
    - "Senior Full Stack Software Engineer"  # Your desired job title
    - "Lead Full Stack Developer"            # Add more titles

  default_locations:
    - "New York, NY"     # Where you want to work
    - "Remote"           # Include remote jobs

  experience_level: "Senior"  # Entry, Mid, Senior

matching:
  min_match_percentage: 60  # Minimum match score (0-100)
  max_jobs_per_day: 10      # How many jobs max per day

schedule:
  run_time: "08:00"         # When to run (24-hour format)
  timezone: "America/New_York"
```

### .env - Your Secret Keys

```bash
# Never share this file! It has your passwords!

GOOGLE_CLOUD_PROJECT=your-project-id
ADZUNA_APP_ID=your-app-id
ADZUNA_APP_KEY=your-app-key
JSEARCH_API_KEY=your-rapidapi-key
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
```

## Understanding the Resume Customization

### What Gets Changed?
- **Technology names**: "Vertex AI" → "OpenAI" if job wants OpenAI
- **Skill emphasis**: Highlights skills mentioned in job description
- **Summary**: Rewritten to focus on relevant experience
- **Keywords**: Adds important keywords for ATS systems

### What NEVER Changes?
- Your actual work experience dates
- Achievement numbers and metrics
- Core responsibilities
- Education details
- Company names

### Example

**Original Resume:**
```
"Created AI chatbot using Vertex AI and LangChain, handling 10K+ queries daily"
```

**Job Wants OpenAI:**
```
"Created AI chatbot using OpenAI and LangChain, handling 10K+ queries daily"
```

**The AI keeps the achievement (10K+ queries) but changes the technology to match!**

## Common Questions

### Q: Will this automatically apply to jobs?
**A**: No! It finds jobs and creates resumes, but YOU decide when to apply. You get an email every day with the jobs and resumes attached.

### Q: How much does this cost?
**A**: About $5-15/month on Google Cloud (they have a free tier too!)
- Vertex AI: ~$3-8/month
- Cloud Functions: ~$2-5/month
- Storage: <$1/month

### Q: What if I want to change my job search?
**A**: Just edit `config.yaml` and redeploy! Takes 2 minutes.

### Q: Can I run this on my computer instead of the cloud?
**A**: Yes! Just run `python main.py` whenever you want. But cloud is better because it runs automatically.

### Q: Is my resume data safe?
**A**: Yes! Everything stays in YOUR Google Cloud account. The code runs in your own cloud space.

### Q: How do I stop it?
**A**: Delete the Cloud Scheduler job in Google Cloud Console, or delete the whole Cloud Function.

### Q: Can I test it before deploying?
**A**: Absolutely! Just run `python main.py` on your computer first.

## File Structure

```
Job-Finder/
├── config.yaml              # Your job search settings (edit this!)
├── .env                     # Your API keys (keep secret!)
├── main.py                  # Main script that runs everything
├── requirements.txt         # Python packages needed
│
├── data/
│   └── master_resume.json  # Your resume (edit this!)
│
├── src/                    # All the code
│   ├── scrapers/          # Gets jobs from websites
│   ├── matcher/           # AI that matches jobs
│   ├── resume/            # AI that customizes resumes
│   ├── storage/           # Saves to Drive & database
│   └── notifier/          # Sends emails
│
└── deploy/                # Cloud deployment files
    ├── deploy.sh          # Run this to deploy
    └── setup_guide.md     # Detailed deployment guide
```

## Troubleshooting

### "No jobs found"
- Check your internet connection
- Verify API keys are correct in `.env`
- Try broader job search terms in `config.yaml`

### "Email not sending"
- Make sure Gmail App Password is correct
- Check that 2-Step Verification is ON in Gmail
- Verify GMAIL_USER and GMAIL_APP_PASSWORD in `.env`

### "Permission denied" errors
- Make sure you're logged into Google Cloud: `gcloud auth login`
- Check that all APIs are enabled (see deploy/setup_guide.md)

### "Import errors" when running
- Make sure you installed all packages: `pip install -r requirements.txt`
- Check you're in the right directory

### Jobs not matching well
- Lower the `min_match_percentage` in `config.yaml` (try 50%)
- Add more job titles to search for
- Broaden your location criteria

## Advanced Features

### Custom Scrapers
Want to add more job sites? Edit `src/scrapers/` files.

### Different AI Models
Want to use a different AI? Edit `config.yaml`:
```yaml
google_cloud:
  vertex_ai:
    model: "gemini-2.0-flash-exp"  # Change this
```

### Custom Email Templates
Edit `src/notifier/email_sender.py` to change email format.

### API Usage
Run manually via HTTP:
```bash
curl https://your-function-url.cloudfunctions.net
```

## What's Next?

Some ideas for enhancements:
- [ ] Add more job sources
- [ ] Create a web dashboard to view history
- [ ] Add cover letter generation
- [ ] LinkedIn auto-apply integration
- [ ] Salary negotiation insights
- [ ] Interview preparation tips

## Getting Help

1. Check the logs: `gcloud functions logs read job-finder`
2. Read the detailed setup guide: `deploy/setup_guide.md`
3. Test locally first: `python main.py`
4. Check your configuration files

## Credits

Built with:
- Google Cloud Platform (Vertex AI, Firestore, Cloud Functions)
- Python & Beautiful Libraries
- Love for automation ❤️

---

## 🚀 Ready to Start?

1. Get your API keys (15 minutes)
2. Update your resume JSON (10 minutes)
3. Deploy to Google Cloud (5 minutes)
4. **Receive job matches every day!** ✨

**Good luck with your job search!** 🎉
