# Resume Converter Tool

This tool helps you convert your existing resume (PDF, DOCX, or text) into the JSON format required by the Job Finder system.

## Quick Start

```bash
# Install dependencies (if needed)
pip install PyPDF2 python-docx google-cloud-aiplatform

# Run the converter
python tools/resume_converter.py
```

## Usage Options

### Option 1: AI-Powered Conversion (Recommended)

**Requirements:**
- Google Cloud account with Vertex AI enabled
- GOOGLE_CLOUD_PROJECT environment variable set

**Steps:**
1. Run: `python tools/resume_converter.py`
2. Choose your resume format (PDF, DOCX, TXT, or paste)
3. Select "AI-powered conversion"
4. AI will parse and convert to JSON
5. Review and save

**Example:**
```bash
$ python tools/resume_converter.py

How would you like to provide your resume?
1. Upload PDF file
2. Upload DOCX file
3. Upload TXT file
4. Paste text manually

Enter your choice (1-4): 1
Enter path to PDF file: ~/Downloads/my_resume.pdf

✅ Resume text extracted (3450 characters)

Conversion method:
1. AI-powered conversion
2. Manual JSON template

Enter your choice (1-2): 1

🤖 Converting resume using AI...
✅ Resume converted successfully!

📋 PREVIEW OF CONVERTED RESUME
...

Save this resume? (y/n): y
✅ Resume saved to: data/master_resume.json
```

### Option 2: Manual Template

If you don't have Vertex AI set up:

1. Run: `python tools/resume_converter.py`
2. Provide your resume text
3. Select "Manual JSON template"
4. Edit the generated template file
5. Copy your info from extracted text

## Output Format

The tool creates a JSON file with this structure:

```json
{
  "personal_info": {
    "name": "Your Name",
    "title": "Your Job Title",
    "email": "email@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username"
  },
  "summary": "Professional summary...",
  "skills": {
    "programming_languages": ["Python", "JavaScript"],
    "frontend": ["React", "Vue.js"],
    "backend": ["Node.js", "Django"],
    "databases": ["PostgreSQL", "MongoDB"],
    "cloud_devops": ["AWS", "Docker"],
    "tools": ["Git", "VS Code"]
  },
  "experience": [
    {
      "company": "Company Name",
      "position": "Job Title",
      "location": "City, State",
      "start_date": "2021-01",
      "end_date": "Present",
      "responsibilities": [
        "Built feature X, improving metric by Y%",
        "Led team of Z developers"
      ],
      "technologies": ["React", "Node.js", "AWS"]
    }
  ],
  "education": [...],
  "certifications": [...],
  "projects": [...]
}
```

## Tips for Best Results

### Writing Achievements

**Bad (vague):**
- "Worked on frontend development"
- "Responsible for API creation"

**Good (specific with metrics):**
- "Built customer dashboard using React, serving 50K daily users"
- "Created REST API handling 100K requests/day with 99.9% uptime"

### Technology Specificity

**Bad:**
- "Web development"
- "Cloud technologies"

**Good:**
- "React, Next.js, TypeScript"
- "AWS (Lambda, S3, RDS), Docker, Kubernetes"

### Date Formats

Use YYYY-MM format for dates:
- ✅ "2021-03"
- ✅ "Present"
- ❌ "March 2021"
- ❌ "2021"

## Troubleshooting

### PDF Not Reading Correctly

```bash
# Install PDF library
pip install PyPDF2

# If still having issues, try converting to text first
# Then use Option 3 or 4
```

### Vertex AI Errors

```bash
# Set project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### Manual Editing

If AI conversion doesn't work perfectly:

1. It will save to `data/master_resume.json`
2. Open the file in any text editor
3. Fix any incorrect information
4. Ensure JSON is valid (use jsonlint.com to check)

## After Conversion

Once you have `data/master_resume.json`:

1. **Review carefully** - ensure all info is accurate
2. **Update personal info** - email, phone, links
3. **Verify achievements** - check metrics and dates
4. **Test the system** - run `python main.py` to test
5. **Make it your master** - this becomes your source resume

## Alternative: Use Sample Resume

If you want to test first:

```bash
# The system includes a sample resume
cp data/master_resume.json data/master_resume_backup.json

# Edit the sample with your info
nano data/master_resume.json

# Or just use it to understand the format
```

## Need Help?

Check the main README.md for full system documentation.

For Vertex AI setup: `deploy/setup_guide.md`
