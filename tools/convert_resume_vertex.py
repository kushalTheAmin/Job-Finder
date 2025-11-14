#!/usr/bin/env python3
"""
Resume Converter using Vertex AI (uses service-account-key.json)
Converts PDF/DOCX → JSON using your existing Google Cloud credentials
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Vertex AI
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("❌ Vertex AI not installed!")
    print("   Run: pip install vertexai")
    sys.exit(1)

# PDF/DOCX reading libraries
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

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VertexAIResumeConverter:
    """AI-powered resume converter using Vertex AI."""

    def __init__(self):
        """Initialize with Vertex AI using service account."""
        # Get GCP project from env
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.region = os.getenv('GCP_REGION', 'us-central1')

        if not self.project_id:
            raise ValueError(
                "\n❌ GOOGLE_CLOUD_PROJECT not found in .env!\n"
                "   Please add: GOOGLE_CLOUD_PROJECT=your-project-id\n"
            )

        # Initialize Vertex AI
        print(f"🔧 Initializing Vertex AI...")
        print(f"   Project: {self.project_id}")
        print(f"   Region: {self.region}")

        vertexai.init(project=self.project_id, location=self.region)
        self.model = GenerativeModel('gemini-2.5-flash')

        print("✅ AI Converter initialized (using Vertex AI with service account)")

    def convert(self, file_path: str) -> Tuple[Dict, int]:
        """
        Convert resume file to JSON.

        Args:
            file_path: Path to PDF or DOCX file

        Returns:
            (resume_json, attempts_used)
        """
        print(f"\n🔄 Converting resume: {file_path}")

        # Step 1: Extract text from file
        text = self._extract_text(file_path)
        print(f"✓ Extracted {len(text)} characters")

        # Step 2: AI converts to JSON (with self-validation)
        resume_json, attempts = self._ai_convert_with_validation(text)

        return resume_json, attempts

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 10:
            raise ValueError(f"❌ File too large: {size_mb:.1f}MB (max 10MB)")

        # Extract based on extension
        ext = path.suffix.lower()

        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        elif ext == '.txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"❌ Unsupported file type: {ext}\n   Supported: .pdf, .docx, .txt")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""
        if not PDF_AVAILABLE:
            raise ImportError(
                "❌ PyPDF2 not installed!\n"
                "   Run: pip install PyPDF2"
            )

        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                if len(pdf_reader.pages) == 0:
                    raise ValueError("PDF has no pages")

                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            if not text:
                raise ValueError("No text found in PDF")

            return '\n'.join(text)

        except Exception as e:
            raise RuntimeError(
                f"❌ Cannot read PDF: {str(e)}\n"
                f"   Make sure it's a text-based PDF (not a scanned image)"
            )

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX."""
        if not DOCX_AVAILABLE:
            raise ImportError(
                "❌ python-docx not installed!\n"
                "   Run: pip install python-docx"
            )

        try:
            doc = docx.Document(file_path)
            text = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)

            if not text:
                raise ValueError("No text found in DOCX")

            return '\n'.join(text)

        except Exception as e:
            raise RuntimeError(f"❌ Cannot read DOCX: {str(e)}")

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            if not text.strip():
                raise ValueError("Text file is empty")

            return text

        except Exception as e:
            raise RuntimeError(f"❌ Cannot read TXT: {str(e)}")

    def _ai_convert_with_validation(self, resume_text: str) -> Tuple[Dict, int]:
        """Convert resume text to JSON using AI with self-validation."""

        prompt = f"""You are a resume parsing AI. Convert this resume into structured JSON format.

IMPORTANT: Return ONLY valid JSON, no markdown, no explanations.

Required JSON structure:
{{
  "personal_info": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "City, State",
    "linkedin": "LinkedIn URL (optional)",
    "github": "GitHub URL (optional)",
    "website": "Personal website (optional)",
    "portfolio": "Portfolio URL (optional)"
  }},
  "summary": "Professional summary paragraph",
  "skills": {{
    "Category1": ["skill1", "skill2"],
    "Category2": ["skill1", "skill2"]
  }},
  "experience": [
    {{
      "company": "Company Name",
      "location": "City, State",
      "position": "Job Title",
      "start_date": "Month Year",
      "end_date": "Month Year or Present",
      "context": "One-line context about the company/project",
      "responsibilities": [
        "Achievement or responsibility with **bold** for numbers/tech",
        "Another achievement"
      ],
      "technologies": ["Tech1", "Tech2"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "year": "Graduation Year",
      "gpa": "GPA (optional)",
      "honors": "Honors (optional)"
    }}
  ],
  "certifications": ["Certification 1", "Certification 2"],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Tech1", "Tech2"],
      "url": "Project URL (optional)"
    }}
  ],
  "achievements": ["Achievement 1", "Achievement 2"]
}}

Resume text:
{resume_text}

Return ONLY the JSON object, nothing else."""

        print("🤖 Sending to Vertex AI for conversion...")

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            print(f"\n   Attempt {attempt}/{max_attempts}...")

            try:
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()

                # Remove markdown code blocks if present
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                    response_text = response_text.strip()

                # Parse JSON
                resume_json = json.loads(response_text)

                # Validate
                if self._validate_resume_json(resume_json):
                    print(f"✅ Successfully converted and validated!")
                    return resume_json, attempt
                else:
                    print(f"⚠️  JSON validation failed, retrying...")

            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing error: {e}")
                if attempt == max_attempts:
                    raise RuntimeError("Failed to get valid JSON after 3 attempts")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                if attempt == max_attempts:
                    raise

        raise RuntimeError("Failed to convert resume after maximum attempts")

    def _validate_resume_json(self, resume_json: Dict) -> bool:
        """Validate the resume JSON structure."""
        required_fields = ['personal_info', 'summary', 'skills', 'experience', 'education']

        for field in required_fields:
            if field not in resume_json:
                print(f"   Missing required field: {field}")
                return False

        # Validate personal_info
        if 'name' not in resume_json['personal_info'] or 'email' not in resume_json['personal_info']:
            print(f"   Missing name or email in personal_info")
            return False

        return True

    def save_json(self, resume_json: Dict, output_path: str = None):
        """Save resume JSON to file."""
        if output_path is None:
            output_path = "data/master_resume.json"

        # Create directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resume_json, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved to: {output_path}")


def main():
    """Main function."""
    print("=" * 70)
    print("RESUME CONVERTER - Using Vertex AI")
    print("=" * 70)

    # Get file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("\n📄 Enter path to your resume file (PDF/DOCX/TXT): ").strip()
        # Remove quotes if present
        file_path = file_path.strip('"').strip("'")

    try:
        # Initialize converter
        converter = VertexAIResumeConverter()

        # Convert
        resume_json, attempts = converter.convert(file_path)

        print("\n" + "=" * 70)
        print("CONVERSION SUCCESSFUL!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   Name: {resume_json['personal_info'].get('name', 'N/A')}")
        print(f"   Email: {resume_json['personal_info'].get('email', 'N/A')}")
        print(f"   Experience: {len(resume_json.get('experience', []))} positions")
        print(f"   Education: {len(resume_json.get('education', []))} degrees")
        print(f"   Skills: {len(resume_json.get('skills', {}))} categories")
        print(f"   Attempts: {attempts}")

        # Preview
        print("\n" + "=" * 70)
        print("PREVIEW (first 500 characters):")
        print("=" * 70)
        preview = json.dumps(resume_json, indent=2)[:500]
        print(preview + "...")

        # Ask to save
        save = input("\n💾 Save this to data/master_resume.json? (y/n): ").lower()

        if save == 'y':
            converter.save_json(resume_json)
            print("\n✅ Done! You can now use this resume with the Job Finder system.")
        else:
            print("\n❌ Not saved. Run again when ready.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
