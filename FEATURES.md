# 📋 Features Documentation - Job Finder

This document provides detailed explanations of all Job Finder features, how they work, and how to configure them.

---

## Table of Contents

1. [Resume Converter Tool](#1-resume-converter-tool)
2. [Job Search & Scraping](#2-job-search--scraping)
3. [Intelligent Job Matching](#3-intelligent-job-matching)
4. [Smart Resume Customization](#4-smart-resume-customization)
5. [Interview Preparation Generator](#5-interview-preparation-generator)
6. [Document Generation](#6-document-generation)
7. [Email Notifications](#7-email-notifications)
8. [Duplicate Detection & Storage](#8-duplicate-detection--storage)
9. [Google Drive Integration](#9-google-drive-integration)
10. [Configuration System](#10-configuration-system)

---

## 1. Resume Converter Tool

**Location**: `tools/ai_resume_converter.py`
**Purpose**: Convert your existing resume (PDF/DOCX/TXT) into the JSON format required by Job Finder

### How It Works

The resume converter is an AI-powered tool that:
1. Accepts multiple input formats (PDF, DOCX, TXT)
2. Uses Google Gemini API to intelligently parse your resume
3. Extracts and structures all information into JSON
4. AI validates and fixes its own output automatically
5. Saves to `data/master_resume.json`

### Two Conversion Methods

#### AI-Powered Conversion (Recommended)
- Uses Google's Gemini AI to understand resume context
- Automatically categorizes skills by type
- Extracts metrics and achievements
- Preserves formatting and structure
- **Accuracy**: ~95% with minimal manual correction needed

#### Manual Template
- Creates a blank JSON template
- You fill in all fields manually
- Useful if you prefer full control
- Good for understanding the expected structure

### Input Formats Supported

| Format | Requirements | Notes |
|--------|-------------|-------|
| **PDF** | Requires PyPDF2 | Text-based PDFs only (not scanned images) |
| **DOCX** | Requires python-docx | Microsoft Word documents |
| **TXT** | Built-in | Plain text files |
| **Paste** | Built-in | Copy-paste from anywhere |

### JSON Structure

```json
{
  "personal_info": {
    "name": "string",
    "title": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "links": {
      "linkedin": "url",
      "github": "url",
      "portfolio": "url"
    }
  },
  "summary": "2-3 sentence professional summary",
  "skills": {
    "programming_languages": ["Python", "JavaScript"],
    "frontend": ["React", "Vue.js"],
    "backend": ["Django", "Node.js"],
    "databases": ["PostgreSQL", "MongoDB"],
    "cloud_devops": ["AWS", "Docker", "Kubernetes"],
    "ai_ml": ["TensorFlow", "PyTorch"],
    "tools": ["Git", "CI/CD"]
  },
  "experience": [
    {
      "company": "string",
      "position": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or 'present'",
      "location": "string",
      "responsibilities": [
        "Action verb + context + metrics + technologies"
      ],
      "technologies": ["list", "of", "tech"]
    }
  ],
  "education": [...],
  "certifications": [...],
  "projects": [...],
  "achievements": [...]
}
```

### Usage

```bash
# Install local dependencies (one-time)
pip install -r requirements-local.txt

# Add your free Gemini API key to .env
# Get it from: https://ai.google.dev/

# Run converter
python tools/ai_resume_converter.py

# Follow prompts - AI will validate and fix automatically!
```

### When to Use

- **Initial Setup**: Convert your resume when first setting up Job Finder
- **Resume Updates**: After changing jobs, adding skills, or completing projects
- **Testing**: To understand the expected JSON format
- **Migration**: When moving from another resume format

### AI Self-Validation

The converter uses a 3-attempt validation loop:
1. AI converts your resume to JSON
2. AI validates its own output
3. If issues found, AI fixes them automatically
4. Repeats up to 3 times for perfect results

No manual validation needed - the AI checks and corrects itself!

---

## 2. Job Search & Scraping

**Location**: `src/scrapers/`
**Purpose**: Search multiple job boards simultaneously for matching positions

### Supported Job Sources

#### 1. LinkedIn Scraper
- **File**: `linkedin_scraper.py`
- **Method**: Web scraping
- **Coverage**: Largest professional network
- **Rate Limits**: Respectful delays between requests
- **Returns**: Company, title, location, description, posted date

#### 2. Indeed Scraper
- **File**: `indeed_scraper.py`
- **Method**: Web scraping
- **Coverage**: Broad job market
- **Rate Limits**: 2-second delays between requests
- **Returns**: Full job details including salary (when available)

#### 3. Adzuna API
- **File**: `adzuna_scraper.py`
- **Method**: Official API
- **Requires**: Free API key (1000 calls/month)
- **Coverage**: Aggregates from multiple sources
- **Returns**: Comprehensive job data with salary ranges

#### 4. JSearch API (RapidAPI)
- **File**: `jsearch_scraper.py`
- **Method**: Official API via RapidAPI
- **Requires**: Free API key (100 calls/month)
- **Coverage**: Global job listings
- **Returns**: Detailed job information with apply links

### Aggregator

**File**: `aggregator.py`

The aggregator:
1. Runs all enabled scrapers in parallel (ThreadPoolExecutor)
2. Normalizes data from different sources
3. Deduplicates based on unique ID (hash of title + company + location)
4. Filters by experience level and job type
5. Returns unified job list

### How Scraping Works

```python
# Parallel execution
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(linkedin_scraper.search, ...): "linkedin",
        executor.submit(indeed_scraper.search, ...): "indeed",
        executor.submit(adzuna_scraper.search, ...): "adzuna",
        executor.submit(jsearch_scraper.search, ...): "jsearch",
    }

# Gather results
for future in as_completed(futures):
    source = futures[future]
    jobs = future.result()
    all_jobs.extend(jobs)

# Deduplicate
unique_jobs = deduplicate_jobs(all_jobs)
```

### Data Normalization

All scrapers return jobs in a consistent format:
```python
{
    "id": "unique-hash",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "New York, NY",
    "description": "Full job description...",
    "url": "https://apply-url.com",
    "source": "linkedin",
    "posted_date": "2025-11-13",
    "salary_min": 120000,  # Optional
    "salary_max": 180000,  # Optional
    "job_type": "Full-time",
    "experience_level": "Senior"
}
```

### Configuration

In `config.yaml`:
```yaml
sources:
  # Enable/disable sources
  enabled:
    - "linkedin"
    - "indeed"
    - "adzuna"
    - "jsearch"

  # API keys
  adzuna:
    app_id: "from-env"
    app_key: "from-env"

  jsearch:
    api_key: "from-env"

  # Scraping settings
  scraping:
    use_proxy: false
    max_pages: 3  # Per source
    delay_between_requests: 2  # seconds
```

### Anti-Scraping Measures

The scrapers respect websites by:
- Using reasonable delays (2+ seconds)
- Limiting pages per search (default: 3)
- Using proper user agents
- Honoring robots.txt
- Rotating requests across sources

---

## 3. Intelligent Job Matching

**Location**: `src/matcher/job_matcher.py`
**Purpose**: AI-powered analysis to determine how well you match each job

### Dual-Brain Analysis

The matcher analyzes jobs from two perspectives:

#### 1. ATS Scanner Perspective
- Looks for exact keyword matches
- Counts skill mentions (CRITICAL: 3+, IMPORTANT: 2-3, NICE: 1)
- Checks required vs preferred sections
- Validates experience level match
- **Purpose**: Ensure you pass automated filters

#### 2. Human Recruiter Perspective
- Understands context and semantics
- Recognizes equivalent skills (e.g., "React" covers "React.js")
- Evaluates domain expertise
- Assesses cultural fit indicators
- **Purpose**: Ensure you're a good human match

### Match Score Calculation

```python
# Scoring algorithm
base_score = 0

# Critical skills (mentioned 3+ times or in "Required")
critical_matched = count_matched_critical_skills()
critical_missing = count_missing_critical_skills()
base_score += (critical_matched / total_critical) * 40  # 40% weight

# Important skills (mentioned 2-3 times)
important_matched = count_matched_important_skills()
base_score += (important_matched / total_important) * 30  # 30% weight

# Nice-to-have skills (mentioned once)
nice_matched = count_matched_nice_skills()
base_score += (nice_matched / total_nice) * 15  # 15% weight

# Experience level match
if experience_matches:
    base_score += 10  # 10% weight

# Domain expertise
if domain_matches:
    base_score += 5  # 5% weight

# Final score (0-100%)
match_percentage = min(100, base_score)
```

### Skill Priority Categorization

| Priority | Criteria | Weight | Impact |
|----------|----------|--------|--------|
| **CRITICAL** | Mentioned 3+ times OR in "Required" section | 40% | Must have or no match |
| **IMPORTANT** | Mentioned 2-3 times OR in "Preferred" section | 30% | Strongly recommended |
| **NICE_TO_HAVE** | Mentioned once OR in "Optional" section | 15% | Bonus points |

### AI-Powered Deep Analysis

Uses Vertex AI Gemini to:
1. Extract all skills from job description
2. Identify implicit requirements (e.g., "startup experience" implies adaptability)
3. Understand domain-specific terminology
4. Recognize skill equivalencies
5. Assess cultural fit indicators

### Example Output

```json
{
  "job_id": "abc123",
  "match_percentage": 78,
  "matched_skills": {
    "critical": ["Python", "React", "PostgreSQL"],
    "important": ["Docker", "AWS", "CI/CD"],
    "nice_to_have": ["Kubernetes", "GraphQL"]
  },
  "missing_skills": {
    "critical": [],
    "important": ["Terraform"],
    "nice_to_have": ["Go"]
  },
  "ats_perspective": {
    "keyword_density": 0.85,
    "section_coverage": 0.90,
    "experience_match": true
  },
  "recruiter_perspective": {
    "domain_fit": "excellent",
    "culture_indicators": ["team collaboration", "agile"],
    "growth_potential": "high"
  },
  "recommendations": [
    "Highlight Python experience in multiple projects",
    "Emphasize React expertise with specific examples",
    "Consider adding Terraform to study list"
  ]
}
```

### Configuration

```yaml
matching:
  # Minimum match to consider
  min_match_percentage: 60

  # Maximum jobs per day
  max_jobs_per_day: 10

  # Sort by match score
  sort_by_match: true

  # AI model for analysis
  model: "gemini-2.5-flash"
```

---

## 4. Smart Resume Customization

**Location**: `src/resume/smart_customizer.py`
**Purpose**: Authentically customize your resume for each job using story-based approach

### Philosophy: Story-Based, Not Keyword Stuffing

Traditional approach (BAD):
```
❌ "Used Python, React, AWS, Docker, Kubernetes"
   (Just keywords - obvious to recruiters)
```

Smart approach (GOOD):
```
✅ "Built microservices architecture using Python FastAPI and Docker,
    deployed on AWS EKS with Kubernetes orchestration, serving 1M+ users"
   (Natural story - technologies in context)
```

### Key Principles

#### 1. The 2-3 Mention Rule
Technologies must appear 2-3 times across your resume for credibility.

**Example**:
```
Experience #1: "Built React dashboard..."
Experience #2: "Maintained React component library..."
Skills section: "React, Redux, React Native"
```

#### 2. Timeline Intelligence
Never adds technologies that didn't exist at the time:
- Won't add "Kubernetes" to 2013 experience
- Won't add "ChatGPT" before 2022
- Validates tech release dates automatically

#### 3. Coherence Validation
Every change is validated for:
- Technical feasibility
- Contextual fit
- Natural language flow
- Metric consistency

#### 4. Confidence Scoring
Each modification receives a confidence score:
- **80-100%**: Very confident (direct experience)
- **65-79%**: Confident (transferable skills)
- **50-64%**: Moderate (requires study)
- **<50%**: Low (not recommended)

### Story Templates

Located in `story_builder.py`, includes:

#### Multi-App Integration Story
```
"Integrated {tech1} with {tech2} to create unified {system_type},
 reducing {metric} by {improvement}% across {number} applications"
```

#### Migration Story
```
"Migrated legacy {old_tech} system to modern {new_tech} architecture,
 improving {metric} by {improvement}% while maintaining zero downtime"
```

#### Performance Optimization Story
```
"Optimized {component} using {tech} and {optimization_technique},
 achieving {metric} improvement of {percentage}% for {users} users"
```

#### Hybrid Cloud Story
```
"Designed hybrid cloud architecture using {cloud_provider} and on-premise
 {tech}, balancing cost and performance for {use_case}"
```

### Customization Process

```python
# 1. Analyze job requirements
job_analysis = matcher.analyze_job(job_description)

# 2. Identify gaps
missing_skills = job_analysis.missing_skills.critical + important

# 3. Find customization opportunities
opportunities = []
for experience in resume.experiences:
    for skill in missing_skills:
        if can_add_authentically(experience, skill):
            opportunities.append({
                'experience': experience,
                'skill': skill,
                'confidence': calculate_confidence(experience, skill),
                'story_template': select_best_template(experience, skill)
            })

# 4. Apply modifications (high confidence only)
for opp in opportunities:
    if opp.confidence >= min_confidence_score:
        apply_story(opp)

# 5. Validate coherence
validate_modified_resume(modified_resume)

# 6. Generate interview prep for added skills
prep_guide = generate_prep_guide(modifications)
```

### ATS Optimization

**File**: `ats_optimizer.py`

Ensures resumes pass Applicant Tracking Systems:
1. **Keyword Density**: Optimal mentions without stuffing
2. **Section Ordering**: Standard ATS-friendly structure
3. **Formatting**: Machine-readable (no tables, columns, images)
4. **File Format**: Both PDF and DOCX generated
5. **Metadata**: Proper document properties

### Configuration

```yaml
resume_customization:
  # Balance (70 = 70% authentic, 30% keywords)
  authenticity_balance: 70

  # Aggressiveness
  modification_level: moderate  # conservative, moderate, aggressive

  # Max skills to add
  max_skills_to_add: 5

  # Don't modify old experience
  max_experience_age_years: 5

  # Minimum confidence to proceed
  min_confidence_score: 65

  # Writing style
  style: action_focused  # action_focused, corporate, technical

  # Generate interview prep
  generate_interview_prep: true
```

### Customization Levels

| Level | Changes/Job | Confidence Threshold | Risk |
|-------|-------------|---------------------|------|
| **Conservative** | 2-3 | 80% | Very Low |
| **Moderate** | 3-5 | 65% | Low |
| **Aggressive** | 5-8 | 50% | Medium |

---

## 5. Interview Preparation Generator

**Location**: `src/resume/interview_prep.py`
**Purpose**: Auto-generate study guides for skills added to your resume

### What It Creates

For each job, generates a comprehensive prep guide with:

1. **Summary**
   - Total prep time estimate
   - Confidence level
   - Number of changes made

2. **Skills Study Plan**
   For each added/emphasized skill:
   - Why it was added
   - Your current level
   - Target level
   - Study time estimate
   - **Sample interview questions**
   - **Suggested answers**
   - **Resource links**

3. **Experience Discussion Points**
   - How to discuss modifications
   - Authentic talking points
   - Related experiences to mention

4. **Confidence Builder**
   - Skills you can discuss confidently (80%+)
   - Skills needing light prep (65-79%)
   - Skills requiring study (50-64%)

### Example Output

```markdown
# Interview Prep Guide
## TechCorp - Senior Full Stack Engineer

### Summary
- Total Prep Time: 6-8 hours
- Overall Confidence: 78%
- Changes Made: 4 modifications

### Skills to Study

#### Terraform (Confidence: 68%)
**Why Added**: Job requires infrastructure as code experience
**Current Level**: Basic knowledge
**Target Level**: Intermediate
**Prep Time**: 3-4 hours

**Sample Questions**:
1. "Tell me about your experience with Terraform"
   - **Your Answer**: "I've used Terraform to manage AWS infrastructure,
     including EC2, RDS, and S3 resources. In my recent project, I
     created modules for repeatable deployments..."

2. "How do you handle Terraform state management?"
   - **Your Answer**: "I use remote state with S3 backend and state
     locking via DynamoDB to prevent conflicts..."

**Resources**:
- Terraform Tutorial: https://learn.hashicorp.com/terraform
- AWS + Terraform Guide: https://...
- Practice Projects: https://...

**Real Experience Connection**:
Your experience with CloudFormation and Infrastructure as Code
principles transfers directly to Terraform.

---

#### GraphQL (Confidence: 72%)
... similar structure ...
```

### Prep Time Estimates

Based on confidence levels:
- **80-100%**: 0-1 hour (just review)
- **70-79%**: 2-3 hours (moderate study)
- **60-69%**: 4-6 hours (focused learning)
- **50-59%**: 8-12 hours (significant study)

### Generated Files

```
output/
├── TechCorp_Senior_Engineer_resume.docx
├── TechCorp_Senior_Engineer_prep_guide.md
└── TechCorp_Senior_Engineer_modifications.json
```

### Configuration

```yaml
resume_customization:
  # Enable prep guides
  generate_interview_prep: true

  # Detail level
  interview_prep_detail: moderate  # minimal, moderate, detailed

  # Minimal: Just topics
  # Moderate: Topics + resources
  # Detailed: Topics + resources + questions + answers
```

---

## 6. Document Generation

**Location**: `src/resume/doc_generator.py`

### DOCX Generation

Uses **python-docx** to generate ATS-optimized Word documents.

#### Why DOCX Only?

- **Best ATS compatibility**: ATS systems parse DOCX more reliably than PDF
- **Recruiter-friendly**: Easily editable by recruiters
- **Standard format**: Universally accepted for job applications
- **Preserves structure**: Maintains formatting across all systems
- **No rendering issues**: Text-based format ensures consistency

#### Features

- Clean, professional design
- ATS-friendly formatting (no columns, tables, images)
- Proper spacing (Pt(0), line_spacing=1.0)
- Standard margins (0.5-0.7 inches)
- Semantic structure (header, sections, bullets)
- Single paragraphs with line breaks for perfect spacing

#### Spacing Style Guide

The generator uses strict spacing rules for professional appearance:
```python
# All paragraphs use:
paragraph.space_after = Pt(0)  # No extra spacing
paragraph.line_spacing = 1.0   # Single spacing

# Use ONE paragraph with \n line breaks
# NOT multiple paragraphs (prevents extra spacing)
header_para.add_run(name)
header_para.add_run('\n')  # Line break
header_para.add_run(contact_info)
```

### File Naming

```
{Company}_{Position}_{Date}_resume.docx

Examples:
TechCorp_Senior_Engineer_20251113_resume.docx
Startup_Lead_Developer_20251113_resume.docx
```

### What Happened to PDF?

PDF generation was removed in favor of DOCX-only approach:
- Better ATS parsing accuracy
- Easier for recruiters to customize
- More reliable formatting
- Can convert to PDF anytime if needed

---

## 7. Email Notifications

**Location**: `src/notifier/email_sender.py`
**Purpose**: Send beautiful HTML emails with job matches and resumes

### Email Contents

#### Subject Line
```
🎯 Job Finder: {num_jobs} New Matches ({avg_match}% avg match)
```

#### Email Structure

1. **Summary Section**
   - Total jobs found
   - Average match percentage
   - Date range
   - Sources searched

2. **Job Cards**
   Each job includes:
   - Company logo (if available)
   - Job title and company
   - Location and salary (if available)
   - Match percentage with visual indicator
   - **Why You're a Great Fit** (AI-generated)
   - Missing skills to study
   - ATS metrics (keyword density, etc.)
   - Interview prep summary
   - "Apply Now" button

3. **Attachments**
   - Customized DOCX resume for each job
   - Interview prep guide (markdown)
   - Modification report (JSON)

### HTML Template

```html
<div class="email-container">
  <header>
    <h1>🎯 Your Job Matches for {date}</h1>
    <div class="summary">
      {num_jobs} jobs found | {avg_match}% average match
    </div>
  </header>

  <div class="jobs">
    <div class="job-card">
      <div class="job-header">
        <h2>{company} - {title}</h2>
        <div class="match-badge">{match}% Match</div>
      </div>

      <div class="job-details">
        <p>📍 {location}</p>
        <p>💰 {salary}</p>
        <p>🔗 Source: {source}</p>
      </div>

      <div class="match-analysis">
        <h3>Why You're a Great Fit:</h3>
        <ul>
          <li>{reason 1}</li>
          <li>{reason 2}</li>
        </ul>
      </div>

      <div class="missing-skills">
        <h3>Skills to Highlight:</h3>
        <span class="skill-tag">{skill 1}</span>
        <span class="skill-tag">{skill 2}</span>
      </div>

      <div class="attachments">
        <p>📄 Customized DOCX resume attached</p>
        <p>📚 Interview prep guide attached</p>
      </div>

      <a href="{apply_url}" class="apply-button">Apply Now →</a>
    </div>
  </div>

  <footer>
    <p>Generated by Job Finder | {timestamp}</p>
  </footer>
</div>
```

### Email Delivery

Uses Gmail SMTP with app-specific password:
```python
smtp_server = "smtp.gmail.com"
smtp_port = 587
from_email = os.getenv("GMAIL_USER")
password = os.getenv("GMAIL_APP_PASSWORD")
```

### Configuration

```yaml
notifications:
  # Recipient email
  email_to: ""  # Uses GMAIL_USER from .env if empty

  # Enable/disable emails
  send_email: true

  # Include attachments
  attach_resumes: true
  attach_prep_guides: true
```

---

## 8. Duplicate Detection & Storage

**Location**: `src/storage/firestore_db.py`
**Purpose**: Track all jobs to prevent duplicates and maintain history

### Firestore Collections

#### 1. `applied_jobs`
Tracks every job ever seen:
```python
{
  "job_id": "unique-hash",
  "title": "Senior Engineer",
  "company": "TechCorp",
  "status": "sent",  # sent, applied, rejected, interviewing
  "match_percentage": 78,
  "date_found": "2025-11-13",
  "date_sent": "2025-11-13",
  "resume_version": "v1.2.3",
  "customizations": [...],
  "source": "linkedin"
}
```

#### 2. `job_history`
Daily run summaries:
```python
{
  "run_date": "2025-11-13",
  "jobs_found": 15,
  "jobs_matched": 8,
  "jobs_sent": 5,
  "avg_match": 72,
  "sources_searched": ["linkedin", "indeed"],
  "errors": [],
  "runtime_seconds": 120
}
```

### Duplicate Detection

```python
def is_duplicate(job):
    # Generate unique ID
    job_id = hashlib.md5(
        f"{job.title}-{job.company}-{job.location}".encode()
    ).hexdigest()

    # Check Firestore
    doc = db.collection('applied_jobs').document(job_id).get()

    return doc.exists
```

### Benefits

1. **Never see same job twice**
2. **Track application status**
3. **Historical data for analysis**
4. **Resume version control**
5. **Performance metrics**

---

## 9. Google Drive Integration

**Location**: `src/storage/gdrive.py`
**Purpose**: Automatically upload resumes and prep guides to Google Drive

### Folder Structure

```
Job Finder Resumes/
├── 2025-11-13/
│   ├── TechCorp_Senior_Engineer_resume.docx
│   ├── TechCorp_Senior_Engineer_prep.md
│   ├── Startup_Lead_Dev_resume.docx
│   └── Startup_Lead_Dev_prep.md
├── 2025-11-12/
│   └── ...
└── metadata.json
```

### Features

- Automatic daily folder creation
- Metadata tracking
- Duplicate handling
- Shareable links
- Access from anywhere

### Configuration

```yaml
notifications:
  # Enable Drive upload
  upload_to_drive: true

  # Folder ID (from Drive URL)
  google_drive_folder_id: ""  # Uses env var if empty
```

---

## 10. Configuration System

**Location**: `config.yaml`
**Purpose**: Central configuration for all system behavior

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed configuration examples.

### Key Configuration Areas

1. **Job Search**: Titles, locations, skills
2. **Matching**: Thresholds, limits
3. **Customization**: Aggressiveness, confidence
4. **Schedule**: Run time, timezone, days
5. **Resume**: Format, sections
6. **Notifications**: Email, Drive
7. **Sources**: Enable/disable scrapers

### Environment Variables

Sensitive data in `.env`:
- API keys
- Credentials
- Project IDs
- Folder IDs

### Best Practices

1. Keep `.env` file secure (never commit)
2. Use `.env.template` for sharing setup
3. Document custom configurations
4. Test locally before deploying
5. Monitor costs and quotas

---

**For setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**
**For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)**
