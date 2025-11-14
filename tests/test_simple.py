#!/usr/bin/env python3
"""
Simple standalone test for AI-driven DOCX generation system.
Tests the new AI Layout Analyzer + Smart DOCX Generator.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.resume.ai_docx_layout_analyzer import AIDOCXLayoutAnalyzer
from src.resume.smart_doc_generator import SmartDOCXGenerator
from src.config import get_config
from src.utils import setup_logging


def test_doc_generation():
    """Test AI-driven DOCX generation with sample data."""
    print("=" * 70)
    print("TESTING AI-DRIVEN DOCX GENERATION")
    print("=" * 70)

    # Create sample resume data
    sample_resume = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe",
        "summary": "Senior Full-Stack Engineer with **8+ years** building **React/TypeScript** applications and **C#/.NET** backends. Currently leading frontend development at **Tech Corp**, driving UI modernization and **AI integration** for analytics platforms. Strong hands-on experience with cloud infrastructure (GCP, AWS), testing frameworks, and establishing team development standards.",
        "skills": {
            "Frontend": ["React", "Next.js", "TypeScript", "Redux", "HTML5", "CSS3", "SASS"],
            "Backend": ["C#/.NET Core", "Python", "Node.js", "RESTful APIs", "Microservices"],
            "Cloud/Data": ["GCP", "AWS", "Azure DevOps", "Redis", "PostgreSQL", "MongoDB"],
            "Tools": ["Git", "Docker", "Jest", "SonarQube", "Webpack", "JIRA", "GitHub Copilot"]
        },
        "experience": [
            {
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "position": "Senior Full-Stack Engineer",
                "start_date": "August 2021",
                "end_date": "Present",
                "context": "Building analytics platform, an AI-powered solution for data-driven decision making.",
                "responsibilities": [
                    "Lead frontend development for **8-person team**—conduct code reviews, establish **React/TypeScript standards**, and mentor **3 junior developers**.",
                    "Drove UI modernization migrating **5+ legacy apps** from jQuery/AngularJS to **React/Next.js with TypeScript**. Reduced page load times from **~6s to ~3.5s** through code splitting and lazy loading.",
                    "Built component library (**50+ components**) with design system and Storybook docs—reduced development time by **30%** as developers scaffold UIs in hours instead of days.",
                    "Integrated **AI messaging system** using **Google Gemini API** with prompt engineering architecture. Generates **~10K personalized messages daily**. Solved output inconsistency by implementing structured prompts.",
                    "Resolved critical production incident: diagnosed **Redis connection exhaustion** (**500+ connections** causing degradation), implemented connection pooling with circuit breaker pattern, reduced to **~50 connections**.",
                    "Established **CI/CD pipelines** in Azure DevOps with automated testing (**Jest**) and code quality gates (**SonarQube**). Improved code coverage from ~60% to **85%+** and SonarQube rating from C to **A**.",
                    "Optimized frontend build process: reduced bundle size from **~2MB to ~700KB** through code splitting (**React.lazy**), tree shaking, and lazy loading of charts. Improved Lighthouse performance score by **40%**.",
                    "Worked with UI Architect to establish **React/Redux patterns** for **20+ developers** across company. Created comprehensive documentation and conducted training sessions on state management."
                ],
                "technologies": ["React", "Next.js", "TypeScript", "Redux", "C#/.NET Core", "GCP", "BigQuery", "Azure DevOps", "Redis", "PostgreSQL", "Jest", "SonarQube", "Docker", "GitHub Copilot"]
            },
            {
                "company": "Innovation Labs",
                "location": "New York, NY",
                "position": "Full-Stack Developer",
                "start_date": "June 2018",
                "end_date": "July 2021",
                "context": "Built e-commerce platform, a scalable solution for online retail operations.",
                "responsibilities": [
                    "Developed responsive frontend using **React** and **Redux** for state management, serving **50K+ daily active users**.",
                    "Built **RESTful APIs** with **Node.js** and **Express**, integrating with **MongoDB** for data persistence and **Redis** for caching.",
                    "Implemented **JWT authentication** and role-based access control (RBAC) securing **100K+ user accounts**.",
                    "Collaborated with **12-person engineering team** using agile methodologies, participating in sprint planning and retrospectives.",
                    "Achieved **90%+ test coverage** using **Jest** and **Enzyme** for unit and integration testing.",
                    "Deployed applications to **AWS** using **Docker** containers orchestrated with **ECS**, reducing deployment time by **50%**."
                ],
                "technologies": ["React", "Redux", "Node.js", "Express", "MongoDB", "Redis", "JWT", "AWS", "Docker", "ECS", "Jest", "Enzyme"]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of California, Berkeley",
                "year": "2018"
            }
        ]
    }

    # Create sample job
    sample_job = {
        "title": "Senior Full-Stack Engineer",
        "company": "Amazing Tech Company",
        "location": "Remote"
    }

    # Load configuration
    print("\n1. Loading configuration...")
    try:
        config = get_config("config.yaml")
        setup_logging(config.log_level, config.log_file)
        print("   ✓ Configuration loaded")
    except Exception as e:
        print(f"   ✗ Error loading config: {e}")
        print("   Make sure config.yaml exists")
        return None

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
        return None

    # Generate using AI-driven two-phase system
    print("\n3. Generating DOCX (AI analysis + rendering)...")
    try:
        # Phase 1: AI analyzes resume structure
        print("   Analyzing resume structure with AI...")
        layout_plan = layout_analyzer.analyze_and_create_layout(sample_resume, sample_job)

        # Phase 2: Smart renderer creates DOCX
        print("   Rendering DOCX from AI layout plan...")
        output_path = doc_generator.generate(sample_resume, sample_job, layout_plan)

        print(f"\n✓ SUCCESS!")
        print(f"\n   Generated: {output_path}")
        print(f"   Location:  {Path(output_path).absolute()}")
        print(f"   File size: {Path(output_path).stat().st_size / 1024:.1f} KB")

        print("\n4. What to check in the DOCX:")
        print("   ✓ AI-discovered sections:")
        print("     - All sections from resume JSON identified")
        print("     - Sections ordered by relevance to job")
        print("     - Field name variations handled (title vs position)")
        print("\n   ✓ Formatting (enforced by Smart Generator):")
        print("     - Font: Calibri 10.5pt")
        print("     - Name: 18pt bold dark blue")
        print("     - Section headers: 12pt bold dark blue")
        print("     - Context lines: 10pt italic gray")
        print("     - Spacing: Pt(0) after paragraphs, line_spacing=1.0")
        print("     - Margins: 0.5\" top/bottom, 0.6\" left/right")
        print("\n   ✓ Structure:")
        print("     - Professional summary")
        print("     - Technical skills by category")
        print("     - Experience with context lines and tech stacks")
        print("     - Education")

        return output_path

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test AI-driven DOCX generation
    doc_path = test_doc_generation()

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    if doc_path:
        print(f"\nOpen the generated file to review:")
        print(f"  open '{doc_path}'")
        print("\nOr use the command:")
        print(f"  open {Path(doc_path).parent}")
    else:
        print("\n✗ Test failed - see errors above")
