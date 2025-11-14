# AI Resume Converter Tools

**Convert your resume (PDF/DOCX/TXT) to JSON format using AI - in 5 minutes!**

We provide **TWO** converter tools depending on your setup:

| Tool | Best For | Authentication | Setup Time |
|------|----------|----------------|------------|
| **`convert_resume_vertex.py`** | Users with Google Cloud project | Service Account (already configured) | **0 min** ✅ |
| **`ai_resume_converter.py`** | Users without Google Cloud | Free Gemini API key | 2 min |

---

## 🚀 Option 1: Vertex AI Converter (Recommended if you have GCP)

**Use this if you already have:**
- Google Cloud project configured
- `service-account-key.json` file
- `GOOGLE_CLOUD_PROJECT` in your `.env`

### Quick Start

```bash
# Just run it - no additional setup needed!
python tools/convert_resume_vertex.py /path/to/your/resume.pdf
```

That's it! The converter uses your existing Google Cloud credentials.

### How It Works

1. Uses **Vertex AI** with your service account
2. Automatically reads `GOOGLE_CLOUD_PROJECT` from `.env`
3. No need for additional API keys
4. Same AI-powered conversion as Option 2

---

## Option 2: Gemini API Converter (For users without GCP)

This tool uses Google's Gemini AI to read your resume and create a structured JSON file. The AI validates itself and fixes any issues automatically.

---

## Quick Start (3 Steps)

### Step 1: Get Your Free Gemini API Key (2 minutes)

1. Go to: **https://ai.google.dev/**
2. Click "**Get API Key**"
3. Click "**Create API Key**"
4. Copy the key (looks like: `AIzaSy...`)

### Step 2: Install Dependencies (1 minute)

```bash
# Install the resume converter dependencies
pip install -r requirements-local.txt
```

This installs:
- `google-generativeai` - Google AI SDK (for Gemini)
- `PyPDF2` - PDF reader
- `python-docx` - DOCX reader
- Other utilities

### Step 3: Add API Key to .env File (30 seconds)

```bash
# Create .env file if you don't have one
cp .env.template .env

# Open .env file and add your key:
GEMINI_API_KEY=AIzaSy...your-actual-key-here
```

---

## How to Convert Your Resume

### Run the Converter

```bash
python tools/ai_resume_converter.py
```

### Follow the Prompts

```
🤖 AI-POWERED RESUME CONVERTER
==============================================================

Enter path to your resume file: /path/to/your/resume.pdf
```

### What Happens Next

1. **AI reads your resume** (extracts text from PDF/DOCX)
2. **AI converts to JSON** (structures all information)
3. **AI validates** (checks if everything looks good)
4. **AI fixes issues** (if any problems found)
5. **You review** (preview the JSON)
6. **Saves to** `data/master_resume.json`

**The AI tries up to 3 times to get it perfect!**

---

## Example Run

```bash
$ python tools/ai_resume_converter.py

==============================================================
🤖 AI-POWERED RESUME CONVERTER
==============================================================

This tool converts your resume (PDF/DOCX/TXT) to JSON format.
The AI will read your resume and create a structured JSON file.

Enter path to your resume file: ~/Downloads/my_resume.pdf

🔄 Converting resume: ~/Downloads/my_resume.pdf
✓ Extracted 3450 characters

🤖 AI Conversion - Attempt 1/3
🔍 AI validating its own output...
✅ Validation passed!

==============================================================
📋 PREVIEW OF CONVERTED RESUME
==============================================================
{
  "personal_info": {
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1 (555) 123-4567",
    ...
  },
  "summary": "Experienced software engineer with 8 years...",
  ...
}

==============================================================
📊 CONVERSION STATISTICS
==============================================================
✓ AI attempts used: 1/3
✓ Name: John Smith
✓ Experience entries: 3
✓ Skills categories: 6
✓ Education entries: 1

==============================================================
Save this resume to data/master_resume.json? (y/n): y

✅ Resume saved to: data/master_resume.json

📝 Next steps:
   1. Review and edit: data/master_resume.json
   2. Make sure all information is correct
   3. Update config.yaml with your job preferences
   4. Deploy to cloud: cd deploy && ./deploy.sh
```

---

## Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **PDF** | `.pdf` | Must be text-based (not scanned image) |
| **Word** | `.docx` | Microsoft Word documents |
| **Text** | `.txt` | Plain text files |

**File size limit:** 10 MB

---

## What the AI Does

### 1. Intelligent Extraction
- Reads your resume text
- Understands structure (sections, dates, companies)
- Extracts personal info, experience, skills, education
- Recognizes different resume formats

### 2. Self-Validation
- Checks if email is valid
- Verifies dates are in correct format
- Ensures required fields exist
- Detects placeholder text

### 3. Auto-Fixing
- If validation finds issues → AI fixes them
- Tries up to 3 times to get it perfect
- You see the final, validated result

---

## Output JSON Structure

The AI creates this JSON structure:

```json
{
  "personal_info": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "portfolio": "yourwebsite.com"
  },
  "summary": "Professional summary (2-3 sentences)",
  "skills": {
    "programming_languages": ["Python", "JavaScript", "Java"],
    "frontend": ["React", "Vue.js", "Angular"],
    "backend": ["Node.js", "Django", "FastAPI"],
    "databases": ["PostgreSQL", "MongoDB", "Redis"],
    "cloud_devops": ["AWS", "Docker", "Kubernetes"],
    "tools": ["Git", "VS Code", "Jira"]
  },
  "experience": [
    {
      "company": "Company Name",
      "title": "Job Title",
      "location": "City, State",
      "start_date": "2021-03",
      "end_date": "Present",
      "bullets": [
        "Achievement with metrics (e.g., Improved performance by 40%)",
        "Another achievement with impact"
      ],
      "technologies": ["React", "Node.js", "AWS"]
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "school": "University Name",
      "location": "City, State",
      "graduation_date": "2020-05",
      "gpa": "3.8/4.0"
    }
  ],
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2023-06"
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Python", "React"],
      "link": "github.com/user/project"
    }
  ]
}
```

---

## After Conversion - What to Do

### 1. Review the JSON (5 minutes)

Open `data/master_resume.json` and check:
- ✅ Personal info is correct
- ✅ All jobs are listed
- ✅ Skills are categorized properly
- ✅ Dates are in YYYY-MM format
- ✅ No placeholder text

### 2. Manual Edits (if needed)

You can edit the JSON file directly:
```bash
# Use any text editor
nano data/master_resume.json
# or
code data/master_resume.json
```

**Important**: Keep it valid JSON! Use a JSON validator if unsure: https://jsonlint.com/

### 3. Test Locally

```bash
# Test the system with your resume
python main.py
```

### 4. Deploy to Cloud

```bash
# Once you're happy, deploy
cd deploy
./deploy.sh
```

---

## Troubleshooting

### ❌ "GEMINI_API_KEY not found"

**Problem**: API key not set

**Solution**:
```bash
# 1. Get key from: https://ai.google.dev/
# 2. Add to .env file:
echo "GEMINI_API_KEY=your-key-here" >> .env
```

### ❌ "Cannot read PDF"

**Problem**: PDF is scanned image or corrupted

**Solutions**:
1. Try converting PDF to DOCX first
2. Or copy-paste text into a .txt file
3. Make sure PDF is text-based (not image)

### ❌ "AI conversion failed"

**Problem**: AI couldn't parse resume

**Solutions**:
1. Check resume file isn't corrupted
2. Try with a simpler format (TXT file)
3. Manually create JSON using the template above
4. Ensure resume has clear sections (Experience, Education, etc.)

### ❌ "File too large"

**Problem**: Resume file > 10MB

**Solution**:
1. Compress the PDF
2. Remove images/graphics
3. Or copy text to .txt file

### ❌ "Validation found issues"

**Problem**: AI detected problems in generated JSON

**What happens**:
- AI will automatically try to fix (up to 3 attempts)
- If it can't fix, you'll see what's wrong
- You can manually edit the JSON file

**Example**:
```
⚠️  Validation found 2 issues:
   - Missing email in personal_info
   - Date format wrong in experience[0]

🔧 AI will fix these issues...

🤖 AI Conversion - Attempt 2/3
✅ Validation passed!
```

---

## Tips for Best Results

### ✅ DO:
- Use a clean, well-formatted resume
- Have clear section headings (Experience, Education, Skills)
- Use consistent date formats in your original resume
- Include metrics in achievements ("Improved X by 40%")

### ❌ DON'T:
- Use scanned PDFs (AI can't read images)
- Have complex tables or graphics
- Use unusual resume formats
- Skip important sections

---

## Why Use This Instead of Manual JSON?

| Manual JSON | AI Converter |
|-------------|--------------|
| 30-60 minutes | 5 minutes |
| Error-prone | Auto-validated |
| Need to understand JSON | Just run the tool |
| Manual formatting | AI formats perfectly |
| Easy to make mistakes | AI catches issues |

---

## Differences from Old Converter

### Old Tool (`resume_converter.py`):
- ❌ Required Vertex AI (cloud setup)
- ❌ Needed service account
- ❌ Complex authentication
- ❌ Only worked with cloud access

### New Tool (`ai_resume_converter.py`):
- ✅ Uses simple Gemini API (FREE!)
- ✅ Works on any computer
- ✅ Just needs API key
- ✅ No cloud setup required
- ✅ AI validates and fixes itself

---

## Security & Privacy

### Your Data:
- ✅ Resume text sent to Google Gemini API
- ✅ Used ONLY for conversion
- ✅ Not stored by Google after processing
- ✅ JSON file stays on your computer

### API Key:
- ✅ Stored in `.env` file (not committed to git)
- ✅ Only used for AI conversion
- ✅ Can be regenerated anytime
- ✅ Free tier: 60 requests/minute

---

## FAQ

**Q: Is Gemini API free?**
A: Yes! Free tier includes 60 requests/minute. You'll only use 1-3 requests per conversion.

**Q: Do I need Google Cloud for this?**
A: No! This tool uses simple Gemini API, not Vertex AI. No cloud setup needed.

**Q: Will this work on Windows/Mac/Linux?**
A: Yes! Works on all platforms.

**Q: Can I convert multiple resumes?**
A: Yes, run the tool multiple times. Each run creates/overwrites `data/master_resume.json`.

**Q: What if the AI makes mistakes?**
A: You can manually edit the JSON file after conversion. The AI is usually 95%+ accurate.

**Q: Can I use this without internet?**
A: No, it needs internet to call Gemini API.

---

## Need Help?

1. **Check error messages** - They tell you exactly what's wrong
2. **Read troubleshooting section** above
3. **Try with a different file format** (PDF → DOCX → TXT)
4. **Check main README.md** for full system setup
5. **Manually create JSON** using the template if all else fails

---

## What's Next?

After successfully converting your resume:

1. ✅ Review `data/master_resume.json`
2. ✅ Update `config.yaml` with job preferences
3. ✅ Test locally: `python main.py`
4. ✅ Deploy to cloud: `cd deploy && ./deploy.sh`
5. ✅ Get daily job matches with custom resumes!

**Good luck with your job search!** 🚀
