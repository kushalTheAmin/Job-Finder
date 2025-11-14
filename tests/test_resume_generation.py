#!/usr/bin/env python3
"""
Test script for resume generation with transformation guide.
Tests the new AI-driven DOCX generation system and ATS optimization locally.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.resume.ai_docx_layout_analyzer import AIDOCXLayoutAnalyzer
from src.resume.smart_doc_generator import SmartDOCXGenerator
from src.resume.ats_optimizer import ATSOptimizer
from src.resume.resume_validator import ResumeValidator
from src.config import get_config
from src.utils import setup_logging, load_json_file
import vertexai
from vertexai.generative_models import GenerativeModel


def test_resume_generation():
    """Test resume generation with transformation guide."""

    print("=" * 70)
    print("TESTING RESUME GENERATION WITH TRANSFORMATION GUIDE")
    print("=" * 70)

    # 1. Load configuration
    print("\n1. Loading configuration...")
    config = get_config("config.yaml")
    setup_logging(config.log_level, config.log_file)
    print("✓ Configuration loaded")

    # 2. Initialize Vertex AI
    print("\n2. Initializing Vertex AI...")
    try:
        vertexai.init(
            project=config.gcp_project_id,
            location=config.gcp_region
        )
        ai_model = GenerativeModel(config.ai_model_name)
        print(f"✓ Initialized {config.ai_model_name}")
    except Exception as e:
        print(f"✗ Error initializing Vertex AI: {e}")
        print("  Continuing with limited functionality...")
        ai_model = None

    # 3. Load master resume
    print("\n3. Loading master resume...")
    try:
        master_resume = load_json_file("data/master_resume.json")
        print(f"✓ Loaded resume for {master_resume.get('name', 'Unknown')}")
        print(f"  Experience entries: {len(master_resume.get('experience', []))}")
    except Exception as e:
        print(f"✗ Error loading resume: {e}")
        return

    # 4. Create sample job posting
    print("\n4. Creating sample job posting...")
    sample_job = {
        "title": "Senior Full-Stack Engineer",
        "company": "Tech Innovations Inc",
        "location": "San Francisco, CA",
        "description": """
        We're looking for a Senior Full-Stack Engineer with 5+ years of experience
        building modern web applications. You'll work with React, TypeScript, Next.js
        on the frontend and Python, Django, PostgreSQL on the backend. Experience with
        AWS, Docker, Kubernetes is required. You'll lead a team of 6 developers,
        mentor juniors, and drive technical decisions. Strong communication skills
        and experience with agile methodologies required.

        Required Skills:
        - React, TypeScript, Next.js (5+ years)
        - Python, Django, FastAPI
        - PostgreSQL, Redis
        - AWS (EC2, S3, Lambda)
        - Docker, Kubernetes
        - CI/CD pipelines
        - Team leadership and mentoring
        """,
        "salary": "$150,000 - $200,000",
        "posted_date": "2024-01-15"
    }
    print(f"✓ Sample job: {sample_job['title']} at {sample_job['company']}")

    # 5. Test AI-driven DOCX generation system
    print("\n5. Testing AI-driven DOCX generation...")
    try:
        # Initialize AI-driven system
        layout_analyzer = AIDOCXLayoutAnalyzer(config)
        doc_generator = SmartDOCXGenerator()
        print("  ✓ AI Layout Analyzer initialized")
        print("  ✓ Smart DOCX Generator initialized")

        # Generate using two-phase AI process
        print("  Analyzing resume structure with AI...")
        layout_plan = layout_analyzer.analyze_and_create_layout(master_resume, sample_job)

        print("  Rendering DOCX from layout plan...")
        basic_doc_path = doc_generator.generate(master_resume, sample_job, layout_plan, output_dir="output/test")

        print(f"✓ Generated AI-driven DOCX: {basic_doc_path}")
        print(f"  Location: {Path(basic_doc_path).absolute()}")
    except Exception as e:
        print(f"✗ Error generating DOC: {e}")
        import traceback
        traceback.print_exc()

    # 6. Test with AI optimization (if available)
    if ai_model:
        print("\n6. Testing AI-powered optimization...")
        try:
            # Initialize optimizer
            ats_optimizer = ATSOptimizer(config, ai_model)

            # Create minimal match analysis
            match_analysis = {
                'match_score': 85,
                'matched_skills': ['React', 'TypeScript', 'Python'],
                'missing_skills': ['AWS', 'Docker', 'Kubernetes']
            }

            print("  Running ATS optimization (this may take 2-4 minutes)...")
            print("  - Generating professional summary (40-50 words)")
            print("  - Extracting skills from job description")
            print("  - Rewriting bullets with 4-part framework")
            print("  - Adding context lines and tech stacks")
            print("  - Applying strategic highlighting")

            optimization_result = ats_optimizer.optimize_resume(
                master_resume.copy(),
                sample_job,
                match_analysis
            )

            print(f"\n  ✓ Optimization complete!")
            print(f"    Coverage: {optimization_result.get('coverage_before', 0)}% → {optimization_result.get('coverage_after', 0)}%")
            print(f"    Bullets modified: {optimization_result.get('total_changes', 0)}")

            # Get optimized resume
            optimized_resume = optimization_result.get('optimized_resume', master_resume)

            # Show sample of new summary
            new_summary = optimized_resume.get('summary', '')
            if new_summary:
                print(f"\n  New Summary ({len(new_summary.split())} words):")
                print(f"  '{new_summary[:200]}...'")

            # Generate optimized DOCX using AI-driven system
            print("\n7. Generating optimized DOCX with AI layout analysis...")
            print("  Analyzing optimized resume structure...")
            optimized_layout_plan = layout_analyzer.analyze_and_create_layout(
                optimized_resume,
                sample_job,
                match_analysis
            )

            print("  Rendering optimized DOCX...")
            optimized_doc_path = doc_generator.generate(
                optimized_resume,
                sample_job,
                optimized_layout_plan,
                output_dir="output/test"
            )
            print(f"  ✓ Generated optimized DOCX: {optimized_doc_path}")
            print(f"    Location: {Path(optimized_doc_path).absolute()}")

            # Test validator
            print("\n8. Running transformation guide validation...")
            validator = ResumeValidator(config, ai_model)
            validation_result = validator.validate_transformation_guide(optimized_resume)

            print(f"  Validation: {'✓ PASSED' if validation_result['passed'] else '✗ FAILED'}")
            print(f"  Summary:")
            summary = validation_result['summary']
            print(f"    - Summary word count: {summary['summary_word_count']} (target: 40-50)")
            print(f"    - Buzzwords found: {summary['buzzwords_count']}")
            print(f"    - Vague terms found: {summary['vague_terms_count']}")
            print(f"    - Total bullets: {summary['total_bullets']}")
            print(f"    - Collaborative bullets: {summary['collaborative_bullets']} ({summary['collaboration_percentage']}%)")

            if validation_result['issues']:
                print(f"\n  Issues ({len(validation_result['issues'])}):")
                for issue in validation_result['issues']:
                    print(f"    ✗ [{issue['category']}] {issue['message']}")

            if validation_result['warnings']:
                print(f"\n  Warnings ({len(validation_result['warnings'])}):")
                for warning in validation_result['warnings'][:3]:
                    print(f"    ⚠ [{warning['category']}] {warning['message']}")

        except Exception as e:
            print(f"  ✗ Error during AI optimization: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n6. Skipping AI optimization (Vertex AI not available)")

    # Summary
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  1. Basic DOCX: output/test/")
    if ai_model:
        print(f"  2. Optimized DOCX: output/test/")
    print("\nNext steps:")
    print("  1. Open the generated DOCX files to review formatting")
    print("  2. Check strategic highlighting (metrics/tech should be bold)")
    print("  3. Verify 4-part bullet structure (WHAT + HOW + TECH + IMPACT)")
    print("  4. Confirm summary is 40-50 words with key terms bolded")
    print("  5. Review context lines and tech stacks for each job")
    print("\nYou can convert the DOCX to PDF using Word or another tool.")


if __name__ == "__main__":
    test_resume_generation()
