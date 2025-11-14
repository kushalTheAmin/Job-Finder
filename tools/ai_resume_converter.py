#!/usr/bin/env python3
"""
AI-Powered Resume Converter (Local Tool)
Converts PDF/DOCX/TXT → JSON using Google AI (Gemini)
Run this ONCE to create your master resume JSON.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Google AI SDK (NOT Vertex AI - this is for local use)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ Google AI SDK not installed!")
    print("   Run: pip install google-generativeai")
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


class AIResumeConverter:
    """AI-powered resume converter for LOCAL use."""

    def __init__(self, api_key: str = None):
        """Initialize with Gemini API key."""
        # Get API key from env or parameter
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "\n❌ GEMINI_API_KEY not found!\n\n"
                "   How to fix:\n"
                "   1. Get free API key from: https://ai.google.dev/\n"
                "   2. Click 'Get API Key' → Create new key → Copy it\n"
                "   3. Add to .env file:\n"
                "      GEMINI_API_KEY=your-api-key-here\n"
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        print("✅ AI Converter initialized (using Gemini 2.0 Flash)")

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
            text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]

            if not text:
                raise ValueError("No text found in DOCX")

            return '\n'.join(text)

        except Exception as e:
            raise RuntimeError(f"❌ Cannot read DOCX: {str(e)}")

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
                raise ValueError("File is empty")

            return text

        except Exception as e:
            raise RuntimeError(f"❌ Cannot read TXT: {str(e)}")

    def _ai_convert_with_validation(self, text: str) -> Tuple[Dict, int]:
        """
        AI converts to JSON with self-validation loop.
        Max 3 attempts: convert → validate → fix → repeat

        Returns:
            (resume_json, attempts_used)
        """
        resume_json = None
        validation_result = None

        for attempt in range(1, 4):  # 3 attempts max
            print(f"\n🤖 AI Conversion - Attempt {attempt}/3")

            # Step 1: AI converts to JSON
            if attempt == 1:
                resume_json = self._ai_convert_to_json(text)
            else:
                # AI fixes previous attempt
                resume_json = self._ai_fix_json(resume_json, validation_result)

            # Step 2: AI validates its own JSON
            print("🔍 AI validating its own output...")
            validation_result = self._ai_validate_json(resume_json)

            if validation_result['is_valid']:
                print("✅ Validation passed!")
                return resume_json, attempt
            else:
                print(f"⚠️  Validation found {len(validation_result['issues'])} issues:")
                for issue in validation_result['issues'][:3]:  # Show first 3
                    print(f"   - {issue}")

                if attempt < 3:
                    print("🔧 AI will fix these issues...")
                else:
                    print("⚠️  Max attempts reached. Using best available version.")
                    print("   Please review the JSON manually.")

        return resume_json, 3

    def _ai_convert_to_json(self, text: str) -> Dict:
        """AI converts resume text to JSON."""

        prompt = f"""You are an expert resume parser. Convert this resume to JSON format.

RESUME TEXT:
{text}

OUTPUT EXACTLY THIS JSON STRUCTURE:
{{
  "personal_info": {{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1 (555) 123-4567",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "portfolio": "website.com"
  }},
  "summary": "Professional summary (2-3 sentences, 50-200 words)",
  "skills": {{
    "programming_languages": ["Python", "JavaScript", "..."],
    "frontend": ["React", "Vue.js", "..."],
    "backend": ["Node.js", "Django", "..."],
    "databases": ["PostgreSQL", "MongoDB", "..."],
    "cloud_devops": ["AWS", "Docker", "..."],
    "tools": ["Git", "VS Code", "..."]
  }},
  "experience": [
    {{
      "company": "Company Name",
      "title": "Job Title",
      "location": "City, State",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "bullets": [
        "Achievement with metrics (e.g., Improved performance by 40%)",
        "Another achievement"
      ],
      "technologies": ["Tech1", "Tech2"]
    }}
  ],
  "education": [
    {{
      "degree": "Bachelor of Science in Computer Science",
      "school": "University Name",
      "location": "City, State",
      "graduation_date": "YYYY-MM",
      "gpa": "3.8/4.0"
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
      "technologies": ["Tech1", "Tech2"],
      "link": "github.com/user/project"
    }}
  ]
}}

CRITICAL RULES:
1. Extract ALL information from the resume
2. Use "school" not "institution" for education
3. Use "bullets" not "responsibilities" for experience
4. Use "title" not "position" for job titles
5. Dates in YYYY-MM format, use "Present" for current jobs
6. DO NOT add placeholder text - extract actual data from resume
7. If a field is not in resume, omit it (don't use "N/A" or empty strings)
8. Return ONLY valid JSON, no explanations or markdown

Output JSON:"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': 8000
                }
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove code blocks if present
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
            return resume_json

        except json.JSONDecodeError as e:
            print(f"⚠️  AI returned invalid JSON: {str(e)}")
            print(f"Response preview: {response_text[:200]}...")
            raise RuntimeError("AI conversion failed - invalid JSON format")
        except Exception as e:
            print(f"❌ AI conversion failed: {str(e)}")
            raise

    def _ai_validate_json(self, resume_json: Dict) -> Dict:
        """AI validates the resume JSON it created."""

        prompt = f"""You are a resume quality validator. Check if this resume JSON is valid and complete.

RESUME JSON TO VALIDATE:
{json.dumps(resume_json, indent=2)}

CHECK THESE REQUIREMENTS:
1. personal_info must have: name, email
2. email must contain @ symbol
3. summary should be 50-300 characters
4. experience array must have at least 1 entry
5. Each experience must have: company, title, start_date, bullets
6. Dates must be in YYYY-MM format (or "Present")
7. NO placeholder text like "Your Name", "Company Name", "your.email@example.com"
8. skills should have at least 3 categories with real tech names

OUTPUT THIS JSON:
{{
  "is_valid": true or false,
  "issues": [
    "List of specific issues found (or empty array if valid)"
  ]
}}

Return ONLY the JSON, no explanations."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.1, 'max_output_tokens': 1000}
            )

            response_text = response.text.strip()

            # Extract JSON
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            validation_result = json.loads(response_text)
            return validation_result

        except Exception as e:
            print(f"⚠️  Validation failed, assuming valid: {str(e)}")
            return {'is_valid': True, 'issues': []}

    def _ai_fix_json(self, resume_json: Dict, validation_result: Dict) -> Dict:
        """AI fixes the issues in its JSON."""

        issues = validation_result.get('issues', [])
        issues_text = '\n'.join(f"- {issue}" for issue in issues)

        prompt = f"""You created this resume JSON but it has validation issues. Fix them.

ORIGINAL JSON:
{json.dumps(resume_json, indent=2)}

ISSUES TO FIX:
{issues_text}

Fix these issues and return the corrected JSON.
Use the same structure as before.
Return ONLY valid JSON, no explanations."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={'temperature': 0.2, 'max_output_tokens': 8000}
            )

            response_text = response.text.strip()

            # Extract JSON
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            fixed_json = json.loads(response_text)
            return fixed_json

        except Exception as e:
            print(f"⚠️  Fix attempt failed: {str(e)}")
            return resume_json  # Return original if fix fails


def main():
    """Main function for interactive use."""
    print("=" * 70)
    print("🤖 AI-POWERED RESUME CONVERTER")
    print("=" * 70)
    print()
    print("This tool converts your resume (PDF/DOCX/TXT) to JSON format.")
    print("The AI will read your resume and create a structured JSON file.")
    print()

    # Get file path
    file_path = input("Enter path to your resume file: ").strip()

    # Remove quotes if user added them
    file_path = file_path.strip('"').strip("'")

    try:
        # Initialize converter
        converter = AIResumeConverter()

        # Convert
        resume_json, attempts = converter.convert(file_path)

        # Preview
        print("\n" + "=" * 70)
        print("📋 PREVIEW OF CONVERTED RESUME")
        print("=" * 70)
        preview = json.dumps(resume_json, indent=2)
        if len(preview) > 1500:
            print(preview[:1500])
            print("...")
            print(f"\n(Showing first 1500 characters of {len(preview)} total)")
        else:
            print(preview)
        print()

        # Statistics
        print("=" * 70)
        print("📊 CONVERSION STATISTICS")
        print("=" * 70)
        print(f"✓ AI attempts used: {attempts}/3")
        print(f"✓ Name: {resume_json.get('personal_info', {}).get('name', 'N/A')}")
        print(f"✓ Experience entries: {len(resume_json.get('experience', []))}")
        print(f"✓ Skills categories: {len(resume_json.get('skills', {}))}")
        print(f"✓ Education entries: {len(resume_json.get('education', []))}")
        print()

        # Save
        print("=" * 70)
        save = input("Save this resume to data/master_resume.json? (y/n): ").lower().strip()

        if save == 'y':
            output_path = Path('data/master_resume.json')
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(resume_json, f, indent=2)

            print(f"\n✅ Resume saved to: {output_path}")
            print(f"\n📝 Next steps:")
            print(f"   1. Review and edit: {output_path}")
            print(f"   2. Make sure all information is correct")
            print(f"   3. Update config.yaml with your job preferences")
            print(f"   4. Deploy to cloud: cd deploy && ./deploy.sh")
            print()
        else:
            print("\n✓ Resume not saved. You can run this tool again anytime.")
            print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  - Make sure your file path is correct")
        print("  - Check that GEMINI_API_KEY is set in .env file")
        print("  - Verify your resume file is not corrupted")
        print("  - Try with a different file format (PDF, DOCX, or TXT)")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
