# Job Finder - Quick Start Guide
## Get Started in 15 Minutes!

This guide will help you set up Job Finder step by step in simple language.

---

## What You'll Need

- [ ] Your resume (PDF, DOCX, or TXT file)
- [ ] 15 minutes of your time
- [ ] Internet connection

---

## Part 1: Local Setup (Convert Your Resume) - 10 minutes

This runs ONCE on your computer to convert your resume to JSON format.

### Step 1: Get Free Gemini API Key (3 minutes)

1. Open https://ai.google.dev/ in your browser
2. Click the blue "**Get API Key**" button
3. Click "**Create API Key in new project**"
4. Copy the key (starts with `AIzaSy...`)

### Step 2: Install Local Dependencies (2 minutes)

Open terminal and run:

```bash
cd Job-Finder
pip install -r requirements-local.txt
```

This installs the AI tools needed to read your resume.

### Step 3: Add API Key (1 minute)

```bash
# Copy the template
cp .env.template .env

# Open .env file and add your API key
# Find this line and replace with your actual key:
GEMINI_API_KEY=AIzaSy...your-actual-key-here
```

### Step 4: Convert Your Resume (4 minutes)

```bash
python tools/ai_resume_converter.py
```

When it asks for your resume path, enter the full path:
```
Enter path to your resume file: /Users/yourname/Downloads/resume.pdf
```

The AI will:
- Read your resume
- Convert to JSON
- Validate automatically
- Fix any issues

When it shows the preview, type `y` to save.

**Done!** Your resume is now at `data/master_resume.json`

---

## Part 2: Cloud Setup (Deploy to Google Cloud) - 5 minutes

This makes the system run automatically every day at 8 AM.

### Step 1: Review Your Config (1 minute)

Open `config.yaml` and update:

```yaml
job_search:
  default_titles:
    - "Senior Software Engineer"  # ← Change to your desired job title

  default_locations:
    - "New York, NY"  # ← Change to your location
    - "Remote"
```

### Step 2: Get Other API Keys (3 minutes)

You need a few more free API keys for job searching:

**Adzuna** (FREE - 1000 calls/month):
1. Go to: https://developer.adzuna.com/
2. Sign up → Get App ID and App Key
3. Add to `.env` file:
   ```
   ADZUNA_APP_ID=your-app-id
   ADZUNA_APP_KEY=your-app-key
   ```

**Gmail App Password**:
1. Go to: https://myaccount.google.com/apppasswords
2. Generate app password for "Mail"
3. Add to `.env`:
   ```
   GMAIL_USER=your.email@gmail.com
   GMAIL_APP_PASSWORD=your-16-char-password
   ```

### Step 3: Deploy to Cloud (1 minute)

```bash
cd deploy
./deploy.sh
```

Follow the prompts. The script will:
- Set up Google Cloud
- Deploy your code
- Schedule daily runs at 8 AM

**Done!** ✅

---

## What Happens Next?

### Every Day at 8 AM:

1. **Cloud finds jobs** matching your criteria
2. **AI customizes your resume** for each job (6-stage AI pipeline!)
3. **Generates DOCX resumes** with perfect spacing
4. **Emails you** the jobs + resumes
5. **Uploads to Google Drive** for easy access

### You Get an Email Like This:

```
Subject: 🎯 Found 5 Matching Jobs - 87% Average Match

Jobs Found:
1. Senior Engineer at Google (92% match) - Resume attached
2. Staff Engineer at Meta (88% match) - Resume attached
3. Lead Engineer at Amazon (85% match) - Resume attached
...
```

### What You Do:

1. Check your email every morning
2. Review the jobs and resumes
3. Apply to ones you like
4. That's it!

---

## Testing Before Cloud Deployment

Want to test locally first?

```bash
# Run once manually to see how it works
python main.py
```

This will:
- Search for jobs
- Match them to your resume
- Generate customized DOCXs
- Show you the results

**No email sent** - just shows you what would happen.

---

## File Structure (What Everything Does)

```
Job-Finder/
├── .env                          ← Your API keys (NEVER commit this!)
├── config.yaml                   ← Your job preferences (EDIT THIS!)
├── data/
│   └── master_resume.json       ← Your resume (AI created this!)
│
├── tools/
│   └── ai_resume_converter.py   ← Run ONCE to convert resume
│
├── requirements-local.txt       ← Local dependencies (for converter)
├── requirements.txt            ← Cloud dependencies (for daily runs)
│
└── main.py                      ← Main script (runs daily in cloud)
```

---

## Common Questions

**Q: Do I need to run the converter every time?**
A: No! Run it ONCE to create your master resume JSON. That's it.

**Q: Where does resume customization happen?**
A: All customization runs in the cloud, on JSON. DOCX is just the final output.

**Q: Why two different AI setups?**
A:
- **Local** (converter): Uses simple Gemini API with just an API key
- **Cloud** (daily runs): Uses Vertex AI (already set up in cloud)

**Q: How much does this cost?**
A:
- Gemini API: FREE (60 requests/minute)
- Google Cloud: ~$5-15/month (free tier available)
- Job APIs: FREE tiers available

**Q: Can I change job preferences later?**
A: Yes! Just edit `config.yaml` and redeploy.

**Q: Will it automatically apply to jobs?**
A: NO! It finds jobs and creates resumes. YOU decide which ones to apply to.

**Q: Why DOCX only, no PDF?**
A: DOCX is more ATS-friendly and easier to customize. You can convert to PDF anytime.

---

## Troubleshooting

### ❌ "GEMINI_API_KEY not found"
```bash
# Make sure you added it to .env file
cat .env | grep GEMINI_API_KEY
# Should show: GEMINI_API_KEY=AIzaSy...
```

### ❌ "Cannot read PDF"
- Make sure PDF is text-based (not scanned image)
- Try converting to DOCX first
- Or copy text to .txt file

### ❌ "No jobs found"
- Check your internet connection
- Verify API keys in `.env`
- Try broader job titles in `config.yaml`

### ❌ "Permission denied" (during deployment)
```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project your-project-id
```

---

## Next Steps

After your first successful run:

1. ✅ Check your email for job matches
2. ✅ Review the DOCX resumes in Google Drive
3. ✅ Apply to jobs you like
4. ✅ Adjust `config.yaml` if needed (more/fewer jobs, different titles)
5. ✅ Relax - the system runs automatically every day!

---

## Getting Help

1. **Error messages** - Read them carefully, they tell you what's wrong
2. **tools/README.md** - Detailed converter guide
3. **SETUP_GUIDE.md** - Full cloud setup guide
4. **README.md** - Complete system documentation

---

## Summary

### Local (Run ONCE):
1. Get Gemini API key
2. Install `requirements-local.txt`
3. Run `python tools/ai_resume_converter.py`
4. Save JSON

### Cloud (Deploy ONCE, Runs Daily):
1. Update `config.yaml`
2. Get other API keys
3. Run `./deploy/deploy.sh`
4. Receive daily emails!

**Total setup time**: ~15 minutes
**Daily time investment**: 5 minutes to review emails
**Value**: Customized job matches every single day! 🚀

**Good luck with your job search!**
