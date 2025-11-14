"""
AI DOCX Layout Analyzer - Intelligently analyzes resume JSON and creates flexible rendering plans.

This module uses AI to:
1. Identify all sections in resume JSON (standard and custom)
2. Determine best section ordering for each job
3. Handle field name variations (title vs position, bullets vs responsibilities)
4. Extract data from any format (objects, arrays, strings)
5. Create structured layout plans for the doc generator

The AI adapts to ANY JSON structure while the doc generator enforces styling rules.
"""

import logging
import json
from typing import Dict, Any, List
import vertexai
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class AIDOCXLayoutAnalyzer:
    """
    AI-powered layout analyzer that creates flexible rendering plans
    for any resume JSON structure.
    """

    def __init__(self, config: Any):
        """Initialize AI layout analyzer."""
        self.config = config

        # Initialize Vertex AI
        vertexai.init(
            project=config.project_id,
            location=config.vertex_location
        )

        self.model = GenerativeModel(config.vertex_model)
        logger.info(f"Initialized AIDOCXLayoutAnalyzer with {config.vertex_model}")

    def analyze_and_create_layout(
        self,
        resume_data: Dict[str, Any],
        job: Dict[str, Any],
        match_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume JSON and create intelligent layout plan.

        Args:
            resume_data: Resume JSON (any structure)
            job: Job posting details
            match_analysis: Optional match analysis for prioritization

        Returns:
            Layout plan with structured sections ready for rendering
        """
        try:
            job_title = job.get('title', 'Unknown')
            job_company = job.get('company', 'Unknown')
            logger.info("=" * 70)
            logger.info(f"🤖 AI LAYOUT ANALYZER - Starting analysis for: {job_company} - {job_title}")
            logger.info("=" * 70)

            # Log resume structure
            logger.info(f"📄 Input resume structure: {list(resume_data.keys())}")

            # Count sections in input
            section_counts = {}
            for key, value in resume_data.items():
                if isinstance(value, list):
                    section_counts[key] = f"list[{len(value)}]"
                elif isinstance(value, dict):
                    section_counts[key] = f"dict[{len(value)}]"
                else:
                    section_counts[key] = type(value).__name__
            logger.info(f"📊 Section details: {section_counts}")

            # Build AI prompt
            logger.info("🔨 Building AI analysis prompt...")
            prompt = self._build_analysis_prompt(resume_data, job, match_analysis)

            # Get AI analysis
            logger.info("🚀 Calling Vertex AI Gemini for intelligent layout analysis...")
            logger.info(f"   Model: {self.config.vertex_model}")
            logger.info(f"   Temperature: 0.3 (consistent, predictable)")
            logger.info(f"   Max tokens: 4000")

            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,
                    'max_output_tokens': 4000
                }
            )

            logger.info("✅ AI response received, parsing layout plan...")

            # Parse AI response
            layout_plan = self._parse_ai_response(response.text)

            # Log what AI discovered
            sections = layout_plan.get('sections', [])
            logger.info("=" * 70)
            logger.info(f"✨ AI DISCOVERED {len(sections)} SECTIONS:")
            for idx, section in enumerate(sections, 1):
                section_type = section.get('type', 'unknown')
                section_title = section.get('title', section.get('type', 'N/A'))

                # Count items in section
                item_count = ""
                if 'items' in section:
                    item_count = f" ({len(section['items'])} items)"
                elif 'categories' in section:
                    item_count = f" ({len(section['categories'])} categories)"
                elif 'content' in section:
                    content_len = len(str(section['content']))
                    item_count = f" ({content_len} chars)"

                logger.info(f"   {idx}. [{section_type}] {section_title}{item_count}")

            logger.info("=" * 70)
            logger.info("✅ Layout plan ready for Smart DOCX Renderer")

            return layout_plan

        except Exception as e:
            logger.error("=" * 70)
            logger.error(f"❌ ERROR in AI layout analysis: {str(e)}")
            logger.error("🔄 Falling back to basic structure extraction...")
            logger.error("=" * 70)
            # Fallback to basic structure
            return self._create_fallback_layout(resume_data)

    def _build_analysis_prompt(
        self,
        resume_data: Dict[str, Any],
        job: Dict[str, Any],
        match_analysis: Dict[str, Any] = None
    ) -> str:
        """Build AI prompt for layout analysis."""

        job_title = job.get('title', 'Software Engineer')
        job_company = job.get('company', 'Company')
        job_description = job.get('description', '')[:500]  # Truncate for token efficiency

        prompt = f"""You are an expert resume formatter. Analyze this resume JSON structure and create an intelligent layout plan for a DOCX document.

JOB APPLYING FOR:
Title: {job_title}
Company: {job_company}
Description excerpt: {job_description}

RESUME JSON TO ANALYZE:
{json.dumps(resume_data, indent=2)}

YOUR TASK:
1. Identify ALL sections in the resume (personal_info, summary, skills, experience, education, certifications, projects, publications, awards, etc.)
2. Handle field name variations intelligently:
   - "title" or "position" for job titles
   - "bullets" or "responsibilities" or "achievements" for experience items
   - "school" or "institution" for education
3. Extract data from ANY format:
   - Certifications might be [{{objects}}] → extract to ["string list"]
   - Projects might be [{{objects}}] → format appropriately
   - Handle nested structures
4. Order sections by relevance to THIS job
5. For each section, specify rendering type and clean data

OUTPUT THIS JSON STRUCTURE (and ONLY this JSON, no explanations):
{{
  "sections": [
    {{
      "type": "header",
      "data": {{
        "name": "extracted name",
        "email": "extracted email",
        "phone": "extracted phone",
        "linkedin": "extracted linkedin",
        "location": "extracted location"
      }}
    }},
    {{
      "type": "text_block",
      "title": "PROFESSIONAL SUMMARY",
      "content": "summary text"
    }},
    {{
      "type": "skills_dict",
      "title": "TECHNICAL SKILLS",
      "categories": {{
        "Category1": ["skill1", "skill2"],
        "Category2": ["skill3", "skill4"]
      }}
    }},
    {{
      "type": "experience_list",
      "title": "PROFESSIONAL EXPERIENCE",
      "items": [
        {{
          "company": "Company Name",
          "title": "Job Title",
          "location": "Location",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM or Present",
          "bullets": ["bullet1", "bullet2"],
          "context": "optional context line"
        }}
      ]
    }},
    {{
      "type": "education_list",
      "title": "EDUCATION",
      "items": [
        {{
          "degree": "Degree Name",
          "school": "School Name",
          "location": "Location",
          "graduation_date": "YYYY-MM",
          "gpa": "optional GPA"
        }}
      ]
    }},
    {{
      "type": "simple_list",
      "title": "CERTIFICATIONS",
      "format": "pipe_separated",
      "items": ["Cert 1 (Date)", "Cert 2 (Date)"]
    }},
    {{
      "type": "project_list",
      "title": "PROJECTS",
      "items": [
        {{
          "name": "Project Name",
          "description": "Brief description",
          "technologies": ["Tech1", "Tech2"],
          "link": "optional link"
        }}
      ]
    }},
    {{
      "type": "simple_list",
      "title": "PUBLICATIONS",
      "format": "bulleted",
      "items": ["Publication 1", "Publication 2"]
    }}
  ]
}}

SECTION TYPES YOU CAN USE:
- "header": Personal information (name, email, phone, linkedin, location)
- "text_block": Any text section (summary, objective, etc.)
- "skills_dict": Skills organized by categories (dict of arrays)
- "experience_list": Work experience with bullets
- "education_list": Educational background
- "simple_list": Any simple list (certifications, awards, languages, etc.)
- "project_list": Projects with descriptions and tech

FORMAT OPTIONS FOR simple_list:
- "pipe_separated": Items joined with " | " (for certifications, awards)
- "bulleted": Items with bullet points (for publications, achievements)

CRITICAL RULES:
1. Extract ALL sections present in the JSON - don't skip anything
2. If certifications are objects with {{name, issuer, date}}, extract to: ["Name (Date)", "Name2 (Date2)"]
3. If projects are objects, keep the structure with name, description, technologies
4. Order sections by relevance to job (put most relevant first after header)
5. Standard order suggestion: header → summary → skills → experience → education → certifications → projects → other
6. Return ONLY valid JSON, no markdown, no explanations

Output JSON:"""

        return prompt

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract layout plan."""
        try:
            # Remove code blocks if present
            response_text = response_text.strip()
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            # Parse JSON
            layout_plan = json.loads(response_text)

            # Validate structure
            if 'sections' not in layout_plan:
                raise ValueError("Missing 'sections' in layout plan")

            return layout_plan

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI layout response: {str(e)}")
            logger.error(f"Response preview: {response_text[:500]}")
            raise RuntimeError("AI returned invalid layout plan")

    def _create_fallback_layout(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a basic fallback layout if AI fails.
        Uses simple heuristics to extract common sections.
        """
        logger.warning("=" * 70)
        logger.warning("⚠️  FALLBACK MODE: Creating basic layout without AI")
        logger.warning("=" * 70)

        sections = []
        fallback_sections_created = 0

        # Header (required)
        personal_info = resume_data.get('personal_info', {})
        sections.append({
            'type': 'header',
            'data': {
                'name': personal_info.get('name', resume_data.get('name', 'Resume')),
                'email': personal_info.get('email', resume_data.get('email', '')),
                'phone': personal_info.get('phone', resume_data.get('phone', '')),
                'linkedin': personal_info.get('linkedin', resume_data.get('linkedin', '')),
                'location': personal_info.get('location', resume_data.get('location', ''))
            }
        })

        # Summary
        if 'summary' in resume_data and resume_data['summary']:
            sections.append({
                'type': 'text_block',
                'title': 'PROFESSIONAL SUMMARY',
                'content': resume_data['summary']
            })

        # Skills
        skills = resume_data.get('technical_skills', resume_data.get('skills', {}))
        if skills:
            sections.append({
                'type': 'skills_dict',
                'title': 'TECHNICAL SKILLS',
                'categories': skills if isinstance(skills, dict) else {'Skills': skills}
            })

        # Experience
        if 'experience' in resume_data:
            sections.append({
                'type': 'experience_list',
                'title': 'PROFESSIONAL EXPERIENCE',
                'items': resume_data['experience']
            })

        # Education
        if 'education' in resume_data:
            sections.append({
                'type': 'education_list',
                'title': 'EDUCATION',
                'items': resume_data['education']
            })

        # Certifications (handle both formats)
        if 'certifications' in resume_data:
            certs = resume_data['certifications']
            if isinstance(certs, list) and len(certs) > 0:
                if isinstance(certs[0], dict):
                    # Extract from objects
                    cert_strings = [f"{c.get('name', '')} ({c.get('date', '')})" for c in certs]
                else:
                    cert_strings = certs

                sections.append({
                    'type': 'simple_list',
                    'title': 'CERTIFICATIONS',
                    'format': 'pipe_separated',
                    'items': cert_strings
                })

        # Projects
        if 'projects' in resume_data:
            sections.append({
                'type': 'project_list',
                'title': 'PROJECTS',
                'items': resume_data['projects']
            })

        return {'sections': sections}
