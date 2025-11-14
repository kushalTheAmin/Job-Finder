#!/usr/bin/env python3
"""
Test with real resume data to match the reference PDF.
Uses the new AI-driven DOCX generation system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.resume.ai_docx_layout_analyzer import AIDOCXLayoutAnalyzer
from src.resume.smart_doc_generator import SmartDOCXGenerator
from src.config import get_config
from src.utils import setup_logging

# Real resume data from the PDF
resume_data = {
    "name": "KUSHAL DHIRENDRAKUMAR",
    "email": "kushalamin0@gmail.com",
    "phone": "(845)-400-6147",
    "linkedin": "linkedin.com/in/kushalamin39",
    "summary": "Senior Full-Stack Engineer with **8+ years** building **React/TypeScript** applications and **C#/.NET** backends. Currently leading frontend development at **S&P Global**, driving UI modernization and **AI integration** for automotive analytics. Strong hands-on experience with cloud infrastructure (GCP), testing frameworks, and establishing team development standards.",
    "skills": {
        "Frontend": ["React", "Next.js", "TypeScript", "Redux", "HTML5", "CSS3", "SASS", "styled-components"],
        "Backend": ["C#/.NET Core", "Python", "Node.js", "RESTful APIs", "Microservices"],
        "Cloud/Data": ["GCP (BigQuery, Cloud Storage)", "Azure DevOps", "Redis", "PostgreSQL", "MongoDB"],
        "Tools": ["Git", "Docker", "Jest", "SonarCloud", "Webpack", "JIRA", "GitHub Copilot", "N8n"]
    },
    "experience": [
        {
            "company": "S&P Global",
            "location": "New York, NY",
            "position": "Senior Software Engineer",
            "start_date": "August 2021",
            "end_date": "Present",
            "context": "Building Fritz Analytics, an AI-powered platform for automotive dealerships.",
            "responsibilities": [
                "Lead frontend development for 8-person team—conduct code reviews, make architecture decisions, establish React/TypeScript standards, and mentor 3 junior developers.",
                "Drove UI modernization migrating 5+ legacy apps from jQuery/AngularJS to React/Next.js with TypeScript. Reduced page load times from ~6s to ~3.5s through code splitting and lazy loading.",
                "Built enterprise component library (50+ components) with design system and Storybook docs—reduced new feature development time by 30% as developers now scaffold UIs in hours instead of days.",
                "Integrated AI messaging system using Google Gemini API with prompt engineering architecture (few-shot learning, response validation). Generates ~10K personalized messages daily. Solved output inconsistency by implementing structured prompts with constraints.",
                "Developed multiple real-time dashboards (D3.js, Chart.js) for dealership metrics and Command Center for AI system monitoring. Product uses these daily for client demos.",
                "Resolved critical production incident: diagnosed Redis connection exhaustion (500+ connections causing degradation), implemented connection pooling with circuit breaker pattern, reduced to ~50 connections.",
                "Established testing standards achieving 85%+ coverage for SonarCloud compliance. Created reusable Jest utilities and CI/CD automation—regression bugs dropped 60%.",
                "Integrated AI dev tools (GitHub Copilot, ChatGPT) into team workflow with best practices. Team now completes ~30% more story points per sprint while maintaining quality."
            ],
            "technologies": ["React", "Next.js", "TypeScript", "C#/.NET", "GCP", "Redis", "Gemini API", "D3.js", "SonarCloud", "Docker"]
        },
        {
            "company": "Bank of America",
            "location": "New Jersey",
            "position": "React Developer",
            "start_date": "January 2020",
            "end_date": "July 2021",
            "context": "Built financial forecasting application for analysts.",
            "responsibilities": [
                "Developed React/Redux app with complex validation and real-time calculations. Optimized re-renders using React.memo and useCallback—reduced unnecessary renders by 40%.",
                "Built analytics dashboard tracking user behavior and feature adoption. Used insights to identify UX friction and implement changes that improved form completion rates.",
                "Created RESTful API layer with JWT auth, token refresh, and retry logic with exponential backoff. Built error handling that surfaces actionable messages instead of generic errors.",
                "Designed responsive component library with SASS/BEM. Ensured cross-browser compatibility (Chrome, Firefox, Safari, Edge) and mobile support down to 320px.",
                "Established Jest testing practices reaching 80%+ coverage on core modules. Created testing utilities and patterns adopted by team.",
                "Optimized performance through code splitting (React.lazy) and bundle analysis—reduced initial bundle from ~2MB to ~700KB, significantly improving Time to Interactive."
            ],
            "technologies": ["React", "Redux", "JavaScript (ES6+)", "SASS", "Jest", "Webpack", "JWT"]
        },
        {
            "company": "Express Scripts (Cigna)",
            "location": "Franklin Lakes, NJ",
            "position": "React Developer",
            "start_date": "September 2018",
            "end_date": "December 2019",
            "context": "Developed Health Connect platform for patient engagement and care coordination.",
            "responsibilities": [
                "Worked with UI Architect to establish React/Redux patterns for 20+ developers. Evaluated state management options (Context API, MobX, Redux) and created coding standards documentation.",
                "Implemented presentational/container pattern with HOCs for cross-cutting concerns (auth, error boundaries). Improved code reusability by 40% by reducing duplicated logic.",
                "Built D3.js visualizations (packed circles, trend graphs) for population health analytics. Collaborated with UX designer to ensure WCAG 2.1 accessibility compliance.",
                "Integrated SonarQube into CI/CD for automated quality checks. Refactored technical debt—improved maintainability index from C to A rating over 6 months.",
                "Created component library (50+ components) documented in Storybook. Became foundation for consistent UI, reduced feature dev time 25%.",
                "Designed Redux architecture with normalized data (normalizr), memoized selectors (reselect), and redux-saga for side effects. Scaled to 50+ reducers."
            ],
            "technologies": ["React", "Redux", "D3.js", "SonarQube", "JavaScript (ES6+)", "Storybook"]
        }
    ]
}

job = {
    "title": "Senior Full-Stack Engineer",
    "company": "Test_Company",
    "location": "Remote"
}

print("=" * 70)
print("GENERATING RESUME WITH REAL DATA (AI-DRIVEN SYSTEM)")
print("=" * 70)
print()

# Load configuration
print("1. Loading configuration...")
config = get_config("config.yaml")
setup_logging(config.log_level, config.log_file)
print("   ✓ Configuration loaded")

# Initialize AI-driven system
print("\n2. Initializing AI-driven DOCX generation system...")
try:
    layout_analyzer = AIDOCXLayoutAnalyzer(config)
    doc_generator = SmartDOCXGenerator()
    print("   ✓ AI Layout Analyzer initialized")
    print("   ✓ Smart DOCX Generator initialized")
except Exception as e:
    print(f"   ✗ Error initializing AI system: {e}")
    print("   Make sure Vertex AI credentials are configured")
    sys.exit(1)

# Generate resume using AI-driven two-phase system
print("\n3. Generating resume (AI analysis + DOCX rendering)...")
try:
    # Phase 1: AI analyzes resume structure and creates layout plan
    layout_plan = layout_analyzer.analyze_and_create_layout(resume_data, job)

    # Phase 2: Smart renderer creates DOCX from layout plan
    output_path = doc_generator.generate(resume_data, job, layout_plan, output_dir="output/test")

    print(f"\n✓ Generated: {output_path}")
    print(f"  Location: {Path(output_path).absolute()}")
    print()
    print("Compare this output with:")
    print("  /Users/kushal/Downloads/Kushal_Dhirendrakumar_Resume_2025.docx.pdf")
    print()
    print("To open:")
    print(f"  open '{output_path}'")
except Exception as e:
    print(f"\n✗ Error generating resume: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
