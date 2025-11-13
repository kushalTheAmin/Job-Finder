#!/usr/bin/env python3
"""
PDF to JSON Resume Converter
Uses Google Gemini AI to extract structured resume data from PDF
"""

import sys
import json
import argparse
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from PDF file."""
    print(f"📄 Reading PDF: {pdf_path}")

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text += page.extract_text()
            print(f"   Extracted page {page_num}/{len(pdf_reader.pages)}")

    return text


def convert_to_json(pdf_text: str, project_id: str = "job-finder-1762921964") -> dict:
    """Use Gemini AI to convert resume text to structured JSON."""
    print("\n🤖 Converting to JSON using Gemini AI...")

    # Initialize Vertex AI
    vertexai.init(project=project_id, location="us-central1")
    model = GenerativeModel("gemini-2.0-flash-exp")

    prompt = f"""You are a resume data extraction expert. Convert this resume into a structured JSON format.

RESUME TEXT:
{pdf_text}

INSTRUCTIONS:
1. Extract ALL information accurately from the resume
2. Preserve exact wording, dates, company names, job titles
3. Keep all bullet points and achievements exactly as written
4. Extract contact information (name, email, phone, linkedin, location)
5. Structure experience with: company, position, location, start_date, end_date, context (if present), responsibilities, technologies

OUTPUT FORMAT (JSON only, no markdown):
{{
  "personal_info": {{
    "name": "Full Name",
    "title": "Professional Title",
    "email": "email@example.com",
    "phone": "(xxx)-xxx-xxxx",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "",
    "portfolio": ""
  }},
  "summary": "Professional summary text exactly as written in resume",
  "technical_skills": {{
    "Frontend": ["skill1", "skill2"],
    "Backend": ["skill1", "skill2"],
    "Cloud/Data": ["skill1", "skill2"],
    "Tools": ["skill1", "skill2"]
  }},
  "skills": {{
    "Frontend": ["skill1", "skill2"],
    "Backend": ["skill1", "skill2"],
    "Cloud/Data": ["skill1", "skill2"],
    "Tools": ["skill1", "skill2"]
  }},
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title",
      "location": "City, State",
      "start_date": "Month Year",
      "end_date": "Month Year or Present",
      "context": "One-line context about the role or product (if present in resume)",
      "responsibilities": [
        "Exact bullet point 1",
        "Exact bullet point 2"
      ],
      "technologies": ["Tech1", "Tech2"]
    }}
  ]
}}

CRITICAL RULES:
- Return ONLY valid JSON, no markdown code blocks, no explanations
- Copy ALL text exactly as written (don't paraphrase or summarize)
- Preserve ALL bullet points from each job
- Keep exact dates, company names, job titles
- If a field is not in the resume, use empty string ""
- For technical skills, organize by category as shown in resume"""

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    # Clean markdown formatting if present
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()

    # Parse JSON
    try:
        resume_data = json.loads(response_text)
        print("✅ Successfully converted to JSON")

        # Clean spacing artifacts from PDF extraction
        resume_data = clean_spacing_artifacts(resume_data)
        print("✅ Cleaned spacing artifacts")

        return resume_data
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        print(f"Response text:\n{response_text[:500]}")
        raise


def clean_spacing_artifacts(data):
    """Remove spacing artifacts from PDF text extraction."""
    import re

    def clean_text(text):
        if not isinstance(text, str):
            return text

        # Remove newlines and extra spaces
        text = re.sub(r'\s*\n\s*', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Fix split words pattern: remove space when lowercase letter is followed by space and lowercase letter
        # This handles cases like "developmen t" -> "development"
        text = re.sub(r'([a-z])\s+([a-z])', r'\1\2', text)

        # Fix specific known issues that the pattern might miss
        text = text.replace('Full-St ack', 'Full-Stack')
        text = text.replace('C #', 'C#')

        # Fix name formatting (KUSHAL AMIN -> Kushal Amin)
        if text == 'KUSHAL AMIN':
            text = 'Kushal Amin'

        return text

    # Recursively clean all strings
    if isinstance(data, dict):
        return {k: clean_spacing_artifacts(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_spacing_artifacts(item) for item in data]
    elif isinstance(data, str):
        return clean_text(data)
    return data


def main():
    parser = argparse.ArgumentParser(description="Convert resume PDF to JSON")
    parser.add_argument("pdf_path", help="Path to resume PDF file")
    parser.add_argument("-o", "--output", help="Output JSON file path", default=None)
    parser.add_argument("-p", "--project", help="GCP Project ID", default="job-finder-1762921964")

    args = parser.parse_args()

    # Validate PDF path
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    # Set output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("data/master_resume.json")

    # Extract text from PDF
    pdf_text = extract_text_from_pdf(str(pdf_path))

    if not pdf_text.strip():
        print("❌ Error: No text extracted from PDF")
        sys.exit(1)

    print(f"   Extracted {len(pdf_text)} characters")

    # Convert to JSON using AI
    resume_data = convert_to_json(pdf_text, args.project)

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(resume_data, f, indent=2)

    print(f"\n✅ Resume JSON saved to: {output_path}")
    print(f"\nSummary:")
    print(f"  Name: {resume_data.get('personal_info', {}).get('name', 'N/A')}")
    print(f"  Email: {resume_data.get('personal_info', {}).get('email', 'N/A')}")
    print(f"  Phone: {resume_data.get('personal_info', {}).get('phone', 'N/A')}")
    print(f"  Experience: {len(resume_data.get('experience', []))} jobs")


if __name__ == "__main__":
    main()
