# 🏗️ Architecture Documentation - Job Finder

This document explains the system architecture, data flow, and project structure of Job Finder.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Data Flow](#data-flow)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Cloud Infrastructure](#cloud-infrastructure)
7. [Data Models](#data-models)
8. [Technology Stack](#technology-stack)

---

## System Overview

Job Finder is a **serverless, AI-powered job search automation system** built on Google Cloud Platform. It combines web scraping, AI analysis, and intelligent resume customization to automatically find and apply to relevant job opportunities.

### Key Characteristics

- **Serverless**: Runs on Cloud Functions, scales automatically
- **AI-Powered**: Uses Vertex AI Gemini for intelligent matching and customization
- **Event-Driven**: Triggered by Cloud Scheduler
- **Stateless**: Each run is independent
- **Data-Persistent**: Uses Firestore for state and history

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER SETUP                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Resume (PDF) │→│Resume Convert│→│master_resume  │          │
│  │ DOCX, TXT    │  │ (AI-powered) │  │   .json      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     CLOUD SCHEDULER                              │
│            Triggers Cloud Function Daily at 8 AM                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD FUNCTION (main.py)                      │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    ORCHESTRATOR                             │ │
│  │  Coordinates all components and manages workflow           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               1. JOB SEARCH (Parallel)                     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │  │
│  │  │LinkedIn  │ │ Indeed   │ │ Adzuna   │ │ JSearch  │    │  │
│  │  │ Scraper  │ │ Scraper  │ │   API    │ │   API    │    │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │  │
│  │                      ↓                                     │  │
│  │              Aggregator & Deduplicator                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            2. CHECK FIRESTORE FOR DUPLICATES              │  │
│  │               Filter out previously seen jobs             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         3. JOB MATCHING (Vertex AI Gemini)                │  │
│  │  • Dual-brain analysis (ATS + Human)                      │  │
│  │  • Calculate match percentage                             │  │
│  │  • Identify skill gaps                                    │  │
│  │  • Prioritize skills (CRITICAL/IMPORTANT/NICE)            │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          4. FILTER BY MATCH THRESHOLD                     │  │
│  │          Keep only jobs >= min_match_percentage           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │      5. SMART RESUME CUSTOMIZATION (Vertex AI)            │  │
│  │  • Story-based modifications                              │  │
│  │  • Coherence validation                                   │  │
│  │  • Confidence scoring                                     │  │
│  │  • ATS optimization                                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          6. GENERATE DOCUMENTS                            │  │
│  │  • DOCX resumes (python-docx) - ATS-optimized            │  │
│  │  • Interview prep guides (Markdown)                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              7. UPLOAD TO GOOGLE DRIVE                    │  │
│  │         Organized by date in shared folder                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            8. SEND EMAIL NOTIFICATION                     │  │
│  │  • HTML email with job cards                              │  │
│  │  • Attached resumes and prep guides                       │  │
│  │  • Match analysis and recommendations                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          9. UPDATE FIRESTORE DATABASE                     │  │
│  │  • Mark jobs as sent                                      │  │
│  │  • Save run history                                       │  │
│  │  • Store modifications                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         USER INBOX                               │
│   Receives email with jobs and customized resumes               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Input Phase

```
User Resume (PDF/DOCX)
    ↓
Resume Converter Tool (AI parsing)
    ↓
master_resume.json (Structured data)
    ↓
Loaded by Orchestrator
```

### 2. Search Phase

```
Job Search Criteria (config.yaml)
    ↓
4 Scrapers execute in parallel
    ↓
Raw job listings (15-50 jobs)
    ↓
Aggregator normalizes data
    ↓
Deduplicator removes duplicates
    ↓
Unique job listings (10-30 jobs)
```

### 3. Filtering Phase

```
Unique Jobs
    ↓
Check Firestore (applied_jobs collection)
    ↓
Filter out previously seen jobs
    ↓
New jobs only (5-15 jobs)
```

### 4. Matching Phase

```
New Jobs + Master Resume
    ↓
Vertex AI Gemini Analysis
    ↓
Match Score (0-100%)
    ↓
Filter by min_match_percentage
    ↓
Qualified jobs (2-10 jobs)
```

### 5. Customization Phase

```
Qualified Job + Master Resume
    ↓
Smart Customizer (AI-powered)
    ↓
Modified Resume JSON
    ↓
Coherence Validator
    ↓
Confidence Scorer
    ↓
Final Customized Resume
```

### 6. Generation Phase

```
Customized Resume JSON
    ↓
PDF Generator (WeasyPrint)
    ↓
DOCX Generator (python-docx)
    ↓
Interview Prep Generator
    ↓
Files (PDF, DOCX, MD)
```

### 7. Distribution Phase

```
Generated Files
    ├─→ Google Drive Upload
    ├─→ Email Attachment
    └─→ Firestore Metadata
```

---

## Project Structure

### Why Two Folders?

The project has two main directories:

#### `/ (Root)` - Development Environment
- **Purpose**: Local development and testing
- **Entry Point**: `main.py`
- **Contains**: Source of truth for code
- **Usage**: `python main.py` for local testing

#### `/deploy` - Cloud Deployment Package
- **Purpose**: Cloud Functions deployment
- **Entry Point**: `main.py` (different from root)
- **Contains**: Cloud-specific orchestrator
- **Usage**: `./deploy.sh` to deploy to Google Cloud

### Directory Tree

```
Job-Finder-/
│
├── src/                        # Source code (SINGLE SOURCE OF TRUTH)
│   ├── __init__.py
│   ├── config.py              # Configuration loader
│   ├── utils.py               # Shared utilities
│   │
│   ├── scrapers/              # Job search modules
│   │   ├── __init__.py
│   │   ├── aggregator.py     # Coordinates all scrapers
│   │   ├── linkedin_scraper.py
│   │   ├── indeed_scraper.py
│   │   ├── adzuna_scraper.py
│   │   └── jsearch_scraper.py
│   │
│   ├── matcher/               # Job matching
│   │   ├── __init__.py
│   │   └── job_matcher.py    # AI-powered matching
│   │
│   ├── resume/                # Resume operations
│   │   ├── __init__.py
│   │   ├── resume_customizer.py   # Legacy customizer
│   │   ├── smart_customizer.py    # New story-based customizer
│   │   ├── story_builder.py       # Story templates
│   │   ├── ats_optimizer.py       # ATS optimization
│   │   ├── interview_prep.py      # Prep guide generator
│   │   ├── pdf_generator.py       # PDF generation
│   │   ├── doc_generator.py       # DOCX generation
│   │   ├── resume_modifier.py     # Modification applier
│   │   └── resume_validator.py    # Validation logic
│   │
│   ├── notifier/              # Notifications
│   │   ├── __init__.py
│   │   └── email_sender.py   # Email with Gmail
│   │
│   └── storage/               # Data persistence
│       ├── __init__.py
│       ├── firestore_db.py   # Firestore operations
│       └── gdrive.py          # Google Drive uploads
│
├── tools/                      # Utility tools
│   ├── resume_converter.py   # PDF/DOCX → JSON converter
│   └── README.md              # Converter documentation
│
├── data/                       # User data
│   └── master_resume.json    # Your resume (JSON format)
│
├── tests/                      # Test files
│   ├── test_simple.py
│   ├── test_resume_modifier.py
│   ├── test_resume_generation.py
│   └── test_with_real_data.py
│
├── deploy/                     # Cloud deployment
│   ├── main.py                # Cloud Function entry point
│   ├── orchestrator.py        # Cloud orchestrator (21KB)
│   ├── deploy.sh              # Deployment script
│   └── requirements.txt       # Cloud dependencies
│
├── main.py                     # Local entry point
├── config.yaml                 # Configuration file
├── requirements.txt            # Local dependencies
├── .env                        # Environment variables (not committed)
├── .env.template              # Environment template
├── .gitignore                 # Git ignore rules
│
├── README.md                   # Main documentation
├── SETUP_GUIDE.md             # Complete setup guide
├── FEATURES.md                # Feature documentation
├── ARCHITECTURE.md            # This file
└── COPILOT_GUIDE.md           # AI assistant guide
```

### Key Files

| File | Purpose | Important? |
|------|---------|------------|
| `main.py` (root) | Local testing entry point | Testing only |
| `deploy/main.py` | Cloud Function handler | Production |
| `deploy/orchestrator.py` | Cloud workflow coordinator | Production |
| `src/**/*.py` | All business logic | Core |
| `config.yaml` | User configuration | Critical |
| `.env` | Secrets and credentials | Critical (never commit) |
| `data/master_resume.json` | Your resume data | Critical |
| `deploy.sh` | Deployment automation | Deployment |

---

## Core Components

### 1. Orchestrator
**File**: `deploy/orchestrator.py` (21KB)
**Purpose**: Coordinates entire workflow

```python
class JobFinderOrchestrator:
    def run(self):
        # 1. Initialize
        self.load_config()
        self.load_resume()

        # 2. Search
        jobs = self.search_jobs()

        # 3. Filter duplicates
        new_jobs = self.filter_seen_jobs(jobs)

        # 4. Match
        matched_jobs = self.match_jobs(new_jobs)

        # 5. Customize
        for job in matched_jobs:
            resume = self.customize_resume(job)
            files = self.generate_files(resume, job)
            self.upload_files(files)

        # 6. Notify
        self.send_email(matched_jobs)

        # 7. Update database
        self.update_firestore(matched_jobs)
```

### 2. Scrapers
**Location**: `src/scrapers/`
**Pattern**: Strategy Pattern - each scraper implements common interface

```python
class BaseScraper(ABC):
    @abstractmethod
    def search(self, title, location) -> List[Job]:
        pass

    @abstractmethod
    def parse_job(self, raw_data) -> Job:
        pass
```

### 3. Matcher
**Location**: `src/matcher/job_matcher.py`
**Pattern**: Analyzer Pattern - delegates to AI

```python
class JobMatcher:
    def __init__(self, vertex_ai_client):
        self.ai = vertex_ai_client

    def analyze_job(self, job, resume) -> MatchResult:
        # Dual-brain analysis using AI
        ats_analysis = self.analyze_ats_perspective(job, resume)
        human_analysis = self.analyze_human_perspective(job, resume)

        # Calculate match score
        score = self.calculate_match_score(ats_analysis, human_analysis)

        return MatchResult(score, ats_analysis, human_analysis)
```

### 4. Smart Customizer
**Location**: `src/resume/smart_customizer.py`
**Pattern**: Builder Pattern - constructs modified resume

```python
class SmartCustomizer:
    def customize(self, resume, job_analysis) -> CustomizedResume:
        # Find opportunities
        opportunities = self.find_customization_opportunities(
            resume,
            job_analysis.missing_skills
        )

        # Build stories
        modifications = []
        for opp in opportunities:
            if opp.confidence >= self.min_confidence:
                story = self.story_builder.build_story(opp)
                modifications.append(story)

        # Apply and validate
        modified_resume = self.apply_modifications(resume, modifications)
        self.validator.validate_coherence(modified_resume)

        return modified_resume
```

---

## Cloud Infrastructure

### Google Cloud Services Used

#### 1. Cloud Functions (Gen 2)
- **Purpose**: Serverless compute
- **Trigger**: HTTP (from Cloud Scheduler)
- **Runtime**: Python 3.11
- **Memory**: 2GB
- **Timeout**: 540s (9 minutes)
- **Region**: us-central1

#### 2. Cloud Scheduler
- **Purpose**: Cron-based triggering
- **Schedule**: Daily at configured time
- **Payload**: HTTP POST to Cloud Function
- **Timezone**: Configurable

#### 3. Firestore
- **Purpose**: NoSQL database
- **Mode**: Native
- **Collections**:
  - `applied_jobs`: Job tracking
  - `job_history`: Run summaries
- **Region**: us-central1

#### 4. Vertex AI
- **Purpose**: AI/ML processing
- **Model**: gemini-2.5-flash
- **Usage**:
  - Job matching analysis
  - Resume customization
  - Interview prep generation
- **Region**: us-central1

#### 5. Cloud Storage (via Drive API)
- **Purpose**: File storage
- **Method**: Google Drive API
- **Structure**: Folders by date

#### 6. Gmail API
- **Purpose**: Email sending
- **Method**: SMTP with app password
- **Content**: HTML emails with attachments

### Infrastructure as Code

```bash
# Deployment creates:
gcloud functions deploy job-finder \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --memory=2GB \
  --timeout=540s \
  --set-env-vars=$(cat .env) \
  --allow-unauthenticated

# Scheduler setup:
gcloud scheduler jobs create http job-finder-daily \
  --location=us-central1 \
  --schedule="0 8 * * *" \
  --uri=FUNCTION_URL \
  --http-method=POST
```

---

## Data Models

### Job Model
```python
@dataclass
class Job:
    id: str              # Hash of title+company+location
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str          # linkedin, indeed, adzuna, jsearch
    posted_date: datetime
    salary_min: Optional[int]
    salary_max: Optional[int]
    job_type: str        # Full-time, Contract, etc.
    experience_level: str  # Entry, Mid, Senior, etc.
```

### Resume Model
```python
@dataclass
class Resume:
    personal_info: PersonalInfo
    summary: str
    skills: Skills
    experience: List[Experience]
    education: List[Education]
    certifications: List[Certification]
    projects: List[Project]
    achievements: List[str]
```

### Match Result Model
```python
@dataclass
class MatchResult:
    job_id: str
    match_percentage: int  # 0-100
    matched_skills: Dict[str, List[str]]  # critical, important, nice
    missing_skills: Dict[str, List[str]]
    ats_perspective: ATSAnalysis
    recruiter_perspective: RecruiterAnalysis
    recommendations: List[str]
```

### Customization Model
```python
@dataclass
class Customization:
    experience_id: str
    modification_type: str  # add, modify, emphasize
    original_text: str
    modified_text: str
    skill_added: str
    confidence: int  # 0-100
    story_template: str
    prep_time_hours: int
```

---

## Technology Stack

### Core Technologies
- **Language**: Python 3.11
- **AI**: Google Vertex AI (Gemini 2.5 Flash)
- **Database**: Google Firestore
- **Compute**: Google Cloud Functions Gen 2
- **Scheduler**: Google Cloud Scheduler

### Key Libraries

#### Web Scraping
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `selenium` - Browser automation (if needed)

#### AI & ML
- `google-cloud-aiplatform` - Vertex AI
- `google-generativeai` - Gemini API

#### Data Processing
- `pandas` - Data manipulation (if needed)
- `python-dateutil` - Date parsing

#### Document Generation
- `WeasyPrint` - PDF generation
- `python-docx` - DOCX generation
- `jinja2` - Template rendering

#### Resume Conversion
- `PyPDF2` - PDF reading
- `python-docx` - DOCX reading

#### Cloud Services
- `google-cloud-firestore` - Firestore
- `google-cloud-storage` - Cloud Storage
- `google-auth` - Authentication

#### Email
- `smtplib` - Email sending (built-in)
- `email` - Email formatting (built-in)

#### Utilities
- `pyyaml` - YAML parsing
- `python-dotenv` - Environment variables
- `hashlib` - Hashing (built-in)

### Development Tools
- `pytest` - Testing
- `black` - Code formatting
- `pylint` - Code linting

---

## Design Patterns Used

1. **Strategy Pattern**: Scrapers (interchangeable implementations)
2. **Factory Pattern**: Job creation from different sources
3. **Builder Pattern**: Resume customization
4. **Observer Pattern**: Event logging
5. **Singleton Pattern**: Configuration loader
6. **Template Method**: Document generation
7. **Facade Pattern**: Orchestrator (simplifies complex system)

---

## Performance Considerations

### Parallel Processing
- Scrapers run concurrently (ThreadPoolExecutor)
- Each scraper has independent rate limiting
- Maximum 4 concurrent scraper threads

### Caching
- Firestore acts as job cache
- Resume loaded once per run
- Configuration loaded once per run

### Rate Limiting
- Scraper delays: 2 seconds between requests
- API quotas respected
- Exponential backoff on failures

### Memory Management
- Cloud Function: 2GB memory
- Large objects cleaned up after use
- Streaming for file uploads

### Timeouts
- Cloud Function timeout: 9 minutes
- Individual scraper timeout: 30 seconds
- AI request timeout: 60 seconds
- Email send timeout: 30 seconds

---

## Security Considerations

### Secrets Management
- All secrets in `.env` file (never committed)
- Service account key stored securely
- Environment variables in Cloud Functions
- No hardcoded credentials

### API Key Protection
- Keys stored in environment variables
- Separate keys for dev/prod
- Regular rotation recommended
- Least privilege access

### Data Privacy
- No PII stored in logs
- Firestore security rules
- Drive folder permissions
- Email encryption (TLS)

---

## Monitoring & Observability

### Logging
```python
import logging

logging.info("Job search started")
logging.warning("API rate limit approaching")
logging.error("Failed to send email", exc_info=True)
```

### Metrics
- Jobs found per run
- Match percentages
- Customization confidence scores
- Runtime duration
- Error rates

### Alerts
- Cloud Function failures
- API quota warnings
- Email delivery failures

### Debugging
```bash
# View logs
gcloud functions logs read job-finder --region=us-central1

# Check Firestore data
# Visit: https://console.cloud.google.com/firestore

# Monitor costs
# Visit: https://console.cloud.google.com/billing
```

---

## Scalability

### Current Limits
- 4 job sources
- ~50 jobs per search
- ~10 matched jobs per run
- 1 run per day

### Scaling Considerations
- Add more scrapers (horizontal scaling)
- Increase Cloud Function memory
- Use Cloud Run for longer timeouts
- Implement batch processing
- Add caching layer (Redis)

---

## Future Architecture Enhancements

### Potential Improvements
1. **Web Dashboard**: Real-time status and history
2. **Mobile App**: Push notifications
3. **API**: Public API for integrations
4. **ML Pipeline**: Custom matching model
5. **A/B Testing**: Test different strategies
6. **Analytics**: Detailed insights and trends
7. **Multi-User**: Support multiple users
8. **Kubernetes**: For complex workloads

---

**For setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**
**For feature details, see [FEATURES.md](FEATURES.md)**
