#!/usr/bin/env python3
"""
Test the new Resume Modifier approach.

Instead of generating the final document, this creates detailed modification files
showing exactly what changes to make for a specific job posting.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.resume.resume_modifier import ResumeModifier
from src.utils import load_json_file

def test_resume_modifier():
    """Test resume modifier with sample job posting."""

    print("=" * 70)
    print("TESTING RESUME MODIFICATION FILE GENERATION")
    print("=" * 70)
    print()

    # 1. Load master resume
    print("1. Loading master resume...")
    try:
        master_resume = load_json_file("data/master_resume.json")
        print(f"✓ Loaded resume for {master_resume.get('name', 'Unknown')}")
        print(f"  Experience entries: {len(master_resume.get('experience', []))}")
        print(f"  Total bullets: {sum(len(job.get('responsibilities', [])) for job in master_resume.get('experience', []))}")
    except Exception as e:
        print(f"✗ Error loading resume: {e}")
        return

    # 2. Create sample job posting
    print("\n2. Creating sample job posting...")
    sample_job = {
        "title": "Senior Full-Stack Engineer",
        "company": "TechCorp Industries",
        "location": "San Francisco, CA (Remote)",
        "salary": "$160,000 - $220,000",
        "posted_date": "2024-01-15",
        "description": """
About the Role:
We're looking for a Senior Full-Stack Engineer with 5+ years of experience building
modern web applications. You'll work on our customer-facing platform serving 100K+
daily users, leading technical initiatives and mentoring junior developers.

Required Skills:
- React and TypeScript (5+ years)
- Node.js and Python backend development
- PostgreSQL or MongoDB experience
- AWS or GCP cloud infrastructure
- CI/CD pipelines (GitHub Actions, Jenkins)
- Strong understanding of system design and architecture

Responsibilities:
- Lead development of new features for our analytics platform
- Mentor 2-3 junior engineers
- Participate in architecture decisions and code reviews
- Work with product team to translate requirements into technical solutions
- Improve performance and scalability of existing systems
- Establish best practices for testing and code quality

Nice to Have:
- Experience with Next.js
- GraphQL API development
- Docker and Kubernetes
- Experience in fintech or financial services
- Open source contributions

We offer:
- Competitive salary and equity
- Remote-first culture
- Health, dental, vision insurance
- 401k matching
- Unlimited PTO
        """,
        "requirements": [
            "5+ years of professional software development experience",
            "Strong proficiency in React and TypeScript",
            "Experience with Node.js and Python",
            "Database experience (PostgreSQL or MongoDB)",
            "Cloud platform experience (AWS or GCP)",
            "Excellent communication and collaboration skills"
        ]
    }
    print(f"✓ Created sample job: {sample_job['title']} at {sample_job['company']}")

    # 3. Generate modification files
    print("\n3. Generating modification files...")
    print("   This will create 9-10 detailed files with instructions...")

    try:
        modifier = ResumeModifier()
        files_created = modifier.generate_modification_files(
            master_resume,
            sample_job,
            output_dir="modifications"
        )

        print(f"\n✓ Generated {len(files_created)} modification files!")
        print("\nFiles created:")
        for file_type, filepath in files_created.items():
            file_path = Path(filepath)
            file_size = file_path.stat().st_size
            print(f"   {file_type:15} → {filepath}")
            print(f"                     ({file_size:,} bytes, {file_size // 1024}KB)")

        print("\n" + "=" * 70)
        print("SUCCESS! Modification files generated")
        print("=" * 70)

        print("\n📁 Output Directory:")
        print(f"   {Path('modifications').absolute()}")

        print("\n📋 What's in these files:")
        print("   01_overview          - Summary of all modifications needed")
        print("   02_job_analysis      - Detailed analysis of job requirements")
        print("   03_summary_rewrite   - Professional summary customization")
        print("   04_skills_emphasis   - How to reorder technical skills")
        print("   05_bullet_rewrites   - Detailed bullet point transformations")
        print("   06_context_lines     - Context lines for each job")
        print("   07_tech_stacks       - Tech stack lines for each role")
        print("   08_highlighting      - Strategic highlighting guide")
        print("   09_quality_checklist - Final quality verification")

        print("\n📖 How to use:")
        print("   1. Start with 01_overview.md to understand the scope")
        print("   2. Read 02_job_analysis.md to see what job needs")
        print("   3. Work through files 03-07 to customize your resume")
        print("   4. Apply strategic highlighting from 08")
        print("   5. Verify with 09_quality_checklist.md before submitting")

        print("\n🔍 Key Principles Applied:")
        print("   ✓ 4-part bullet framework: [WHAT] + [HOW] + [TECH] + [IMPACT]")
        print("   ✓ Strategic highlighting: Metrics, tech, achievements (NOT verbs)")
        print("   ✓ Human voice: No buzzwords, ~approximate numbers")
        print("   ✓ 40-50 word summary with strategic bold")
        print("   ✓ Collaboration balance: 60% individual / 40% team")

        print("\n💡 What's Different:")
        print("   OLD approach: Generate final DOCX directly")
        print("   NEW approach: Generate detailed modification instructions")
        print("   ➜ More control, transparency, and understanding of changes")

        print("\n🚀 Next Steps:")
        print("   1. Review the modification files in 'modifications/' directory")
        print("   2. Apply suggested changes to your resume")
        print("   3. Generate final DOCX with your preferred tool")
        print("   4. Compare before/after to see improvements")

        # Show sample of overview file
        print("\n" + "=" * 70)
        print("SAMPLE: Overview File (first 50 lines)")
        print("=" * 70)

        overview_path = Path(files_created['overview'])
        if overview_path.exists():
            lines = overview_path.read_text().split('\n')[:50]
            for line in lines:
                print(line)
            if len(overview_path.read_text().split('\n')) > 50:
                print("\n... (see full file for more)")

    except Exception as e:
        print(f"✗ Error generating modification files: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_resume_modifier()
