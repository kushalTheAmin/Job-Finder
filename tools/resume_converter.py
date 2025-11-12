#!/usr/bin/env python3
"""
Resume Converter - Convert your existing resume to JSON format
Supports: PDF, DOCX, TXT, or manual input
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    from google.cloud import aiplatform
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def print_banner():
    """Print welcome banner."""
    print("=" * 70)
    print("📄 RESUME CONVERTER - Convert Your Resume to JSON Format")
    print("=" * 70)
    print()


def read_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        print("❌ PyPDF2 not installed. Install with: pip install PyPDF2")
        return None

    try:
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        print(f"❌ Error reading PDF: {str(e)}")
        return None


def read_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        print("❌ python-docx not installed. Install with: pip install python-docx")
        return None

    try:
        doc = docx.Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        print(f"❌ Error reading DOCX: {str(e)}")
        return None


def read_text_file(file_path: str) -> str:
    """Read plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return None


def manual_input() -> str:
    """Get resume text through manual input."""
    print("\n📝 Paste your resume text below (Ctrl+D or Ctrl+Z when done):")
    print("-" * 70)

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return '\n'.join(lines)


def convert_with_ai(resume_text: str, project_id: str = None) -> dict:
    """Convert resume text to JSON using Vertex AI."""
    if not VERTEX_AVAILABLE:
        print("❌ Vertex AI not available. Install: pip install google-cloud-aiplatform")
        return None

    if not project_id:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            print("❌ Google Cloud Project ID not set.")
            print("   Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id")
            return None

    try:
        print("\n🤖 Converting resume using AI...")

        # Initialize Vertex AI
        vertexai.init(project=project_id, location='us-central1')
        model = GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""You are an expert resume parser. Convert this resume to JSON format.

RESUME TEXT:
{resume_text}

OUTPUT FORMAT (JSON):
{{
  "personal_info": {{
    "name": "Full Name",
    "title": "Current Job Title",
    "email": "email@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "portfolio": "website.com"
  }},
  "summary": "Professional summary paragraph (2-3 sentences)",
  "skills": {{
    "programming_languages": ["list", "of", "languages"],
    "frontend": ["list", "of", "frontend", "technologies"],
    "backend": ["list", "of", "backend", "technologies"],
    "databases": ["list"],
    "cloud_devops": ["list"],
    "ai_ml": ["list if applicable"],
    "tools": ["list"]
  }},
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title",
      "location": "City, State",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "responsibilities": [
        "Achievement/responsibility with metrics",
        "Another achievement with impact"
      ],
      "technologies": ["Tech", "Stack", "Used"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "location": "City, State",
      "graduation_date": "YYYY-MM",
      "gpa": "X.X/4.0",
      "relevant_courses": ["Course 1", "Course 2"]
    }}
  ],
  "certifications": [
    {{
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date": "YYYY-MM"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Tech", "Stack"],
      "link": "github.com/user/project"
    }}
  ]
}}

IMPORTANT:
- Extract ALL information from the resume
- For experience, convert bullet points to achievement-focused statements
- Include metrics and numbers wherever present
- Group skills into appropriate categories
- Use "Present" for current positions
- Output ONLY valid JSON, no additional text

Provide ONLY the JSON output, nothing else.
"""

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Extract JSON from response
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()

        # Parse JSON
        resume_json = json.loads(response_text)

        print("✅ Resume converted successfully!")
        return resume_json

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing AI response as JSON: {str(e)}")
        print("\nAI Response:")
        print(response_text[:500])
        return None
    except Exception as e:
        print(f"❌ Error converting resume: {str(e)}")
        return None


def save_json(resume_json: dict, output_path: str = None):
    """Save JSON to file."""
    if not output_path:
        output_path = 'data/master_resume.json'

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(resume_json, f, indent=2)

    print(f"\n✅ Resume saved to: {output_file}")
    print(f"\n📝 Next steps:")
    print(f"   1. Review and edit: {output_file}")
    print(f"   2. Update personal info (email, phone, etc.)")
    print(f"   3. Verify all experience and achievements are accurate")
    print(f"   4. Run the Job Finder: python main.py")


def main():
    """Main function."""
    print_banner()

    print("How would you like to provide your resume?\n")
    print("1. Upload PDF file")
    print("2. Upload DOCX file")
    print("3. Upload TXT file")
    print("4. Paste text manually")
    print()

    choice = input("Enter your choice (1-4): ").strip()

    resume_text = None

    if choice == '1':
        file_path = input("\nEnter path to PDF file: ").strip()
        resume_text = read_pdf(file_path)

    elif choice == '2':
        file_path = input("\nEnter path to DOCX file: ").strip()
        resume_text = read_docx(file_path)

    elif choice == '3':
        file_path = input("\nEnter path to TXT file: ").strip()
        resume_text = read_text_file(file_path)

    elif choice == '4':
        resume_text = manual_input()

    else:
        print("❌ Invalid choice")
        return

    if not resume_text:
        print("❌ Could not read resume text")
        return

    print(f"\n✅ Resume text extracted ({len(resume_text)} characters)")

    # Option to use AI or manual JSON creation
    print("\nConversion method:")
    print("1. AI-powered conversion (requires Vertex AI setup)")
    print("2. Manual JSON template (I'll create a template for you)")

    method = input("\nEnter your choice (1-2): ").strip()

    if method == '1':
        project_id = input("\nEnter Google Cloud Project ID (or press Enter to use env var): ").strip()
        if not project_id:
            project_id = None

        resume_json = convert_with_ai(resume_text, project_id)

        if resume_json:
            # Preview
            print("\n" + "=" * 70)
            print("📋 PREVIEW OF CONVERTED RESUME")
            print("=" * 70)
            print(json.dumps(resume_json, indent=2)[:1000] + "...")

            save = input("\n\nSave this resume? (y/n): ").strip().lower()
            if save == 'y':
                output_path = input("Output path (press Enter for data/master_resume.json): ").strip()
                save_json(resume_json, output_path if output_path else None)

    elif method == '2':
        print("\n📝 Creating manual template...")
        template = {
            "personal_info": {
                "name": "Your Name",
                "title": "Your Job Title",
                "email": "your.email@example.com",
                "phone": "+1 (555) 123-4567",
                "location": "City, State",
                "linkedin": "linkedin.com/in/yourusername",
                "github": "github.com/yourusername",
                "portfolio": "yourwebsite.com"
            },
            "summary": "Your professional summary here (2-3 sentences about your experience and expertise)",
            "skills": {
                "programming_languages": ["Python", "JavaScript", "Java"],
                "frontend": ["React", "Vue.js", "HTML/CSS"],
                "backend": ["Node.js", "Django", "Express"],
                "databases": ["PostgreSQL", "MongoDB", "Redis"],
                "cloud_devops": ["AWS", "Docker", "Kubernetes"],
                "tools": ["Git", "VS Code", "Jira"]
            },
            "experience": [
                {
                    "company": "Company Name",
                    "position": "Your Job Title",
                    "location": "City, State",
                    "start_date": "2021-01",
                    "end_date": "Present",
                    "responsibilities": [
                        "Achievement with specific metric (e.g., Increased performance by 50%)",
                        "Another achievement with impact and numbers"
                    ],
                    "technologies": ["Tech1", "Tech2", "Tech3"]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University Name",
                    "location": "City, State",
                    "graduation_date": "2020-05",
                    "gpa": "3.8/4.0"
                }
            ]
        }

        output_path = 'data/master_resume_template.json'
        save_json(template, output_path)

        print(f"\n📝 Template created!")
        print(f"\nNext steps:")
        print(f"   1. Open: {output_path}")
        print(f"   2. Fill in your actual information")
        print(f"   3. Use the resume text I extracted as reference")
        print(f"   4. Save as: data/master_resume.json")

    print("\n" + "=" * 70)
    print("✅ Done! Your resume is ready for the Job Finder system.")
    print("=" * 70)


if __name__ == "__main__":
    main()
