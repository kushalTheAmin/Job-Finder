"""
DOC Resume Generator - Creates professional DOCX resumes.
Optimized for ATS compatibility with strategic highlighting.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)


class DOCResumeGenerator:
    """Generates ATS-optimized DOCX resumes with strategic highlighting."""

    # Color scheme - Professional dark blue
    COLOR_HEADER = RGBColor(0, 51, 102)  # Dark blue for headers and company names
    COLOR_BODY = RGBColor(0, 0, 0)  # Black for body text
    COLOR_CONTEXT = RGBColor(60, 60, 60)  # Gray for context lines

    def __init__(self):
        """Initialize generator."""
        logger.info("Initialized DOCResumeGenerator")

    def generate(self, resume_data: Dict, job: Dict) -> str:
        """
        Generate DOCX resume.

        Args:
            resume_data: Resume data dict
            job: Job posting dict

        Returns:
            Path to generated DOCX file
        """
        try:
            doc = Document()

            # Set margins
            for section in doc.sections:
                section.top_margin = Inches(0.5)
                section.bottom_margin = Inches(0.5)
                section.left_margin = Inches(0.7)
                section.right_margin = Inches(0.7)

            # Add content sections
            self._add_header(doc, resume_data)
            self._add_technical_skills(doc, resume_data)
            self._add_experience(doc, resume_data)
            self._add_education(doc, resume_data)
            self._add_certifications(doc, resume_data)

            # Save file
            output_dir = Path('output/resumes')
            output_dir.mkdir(parents=True, exist_ok=True)

            company_name = job.get('company', 'Company').replace(' ', '_').replace('/', '_')
            timestamp = job.get('timestamp', '').replace(':', '').replace('-', '').replace(' ', '_')[:15]
            filename = f"{resume_data.get('name', 'Resume').replace(' ', '_')}_{company_name}_{timestamp}.docx"
            output_path = output_dir / filename

            doc.save(str(output_path))
            logger.info(f"Generated DOCX resume: {output_path}")

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating DOCX: {str(e)}")
            raise

    @staticmethod
    def _add_header(doc: Document, resume_data: Dict):
        """Add header with name, title, contact info - all in ONE paragraph with line breaks."""
        # Single paragraph for entire header to avoid paragraph spacing
        header_para = doc.add_paragraph()
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_para.space_after = Pt(0)
        header_para.line_spacing = 1.0

        # Get personal info (handle both nested and flat structures)
        personal_info = resume_data.get("personal_info", {})
        name = personal_info.get("name") or resume_data.get("name", "")
        email = personal_info.get("email") or resume_data.get("email", "")
        phone = personal_info.get("phone") or resume_data.get("phone", "")
        linkedin = personal_info.get("linkedin") or resume_data.get("linkedin", "")
        location = personal_info.get("location") or resume_data.get("location", "")

        # Name (18pt, bold, dark blue)
        name_run = header_para.add_run(name)
        name_run.font.size = Pt(18)
        name_run.font.bold = True
        name_run.font.name = 'Calibri'
        name_run.font.color.rgb = DOCResumeGenerator.COLOR_HEADER

        # Line break (not new paragraph!)
        header_para.add_run('\n')

        # Contact info (10pt, pipe-separated)
        contact_parts = []
        if email:
            contact_parts.append(email)
        if phone:
            contact_parts.append(phone)
        if linkedin:
            contact_parts.append(linkedin)
        if location:
            contact_parts.append(location)

        if contact_parts:
            contact_run = header_para.add_run(" | ".join(contact_parts))
            contact_run.font.size = Pt(10)
            contact_run.font.name = 'Calibri'
            contact_run.font.color.rgb = DOCResumeGenerator.COLOR_BODY

    @staticmethod
    def _add_section_header(doc: Document, title: str):
        """Add section header with formatting."""
        header_para = doc.add_paragraph()
        header_run = header_para.add_run(title)
        header_run.font.size = Pt(12)
        header_run.font.bold = True
        header_run.font.name = 'Calibri'
        header_run.font.color.rgb = DOCResumeGenerator.COLOR_HEADER

        header_para.space_before = Pt(0)
        header_para.space_after = Pt(0)
        header_para.line_spacing = 1.0

    @staticmethod
    def _add_technical_skills(doc: Document, resume_data: Dict):
        """Add technical skills - all in ONE paragraph with line breaks."""
        skills = resume_data.get("technical_skills", resume_data.get("skills", {}))
        if not skills:
            return

        DOCResumeGenerator._add_section_header(doc, "TECHNICAL SKILLS")

        if isinstance(skills, dict):
            # Single paragraph for all skills to avoid spacing between categories
            skills_para = doc.add_paragraph()
            skills_para.space_after = Pt(0)
            skills_para.line_spacing = 1.0

            for idx, (category, tech_list) in enumerate(skills.items()):
                # Add line break before each category (except first)
                if idx > 0:
                    skills_para.add_run('\n')

                # Category name (bold)
                category_run = skills_para.add_run(f"{category}: ")
                category_run.font.bold = True
                category_run.font.size = Pt(10.5)
                category_run.font.name = 'Calibri'

                # Technologies (not bold)
                if isinstance(tech_list, list):
                    tech_text = ", ".join(tech_list)
                else:
                    tech_text = str(tech_list)

                tech_run = skills_para.add_run(tech_text)
                tech_run.font.size = Pt(10.5)
                tech_run.font.name = 'Calibri'
                tech_run.font.color.rgb = DOCResumeGenerator.COLOR_BODY

        elif isinstance(skills, list):
            skills_para = doc.add_paragraph()
            skills_para.space_after = Pt(0)
            skills_para.line_spacing = 1.0
            skills_run = skills_para.add_run(", ".join(skills))
            skills_run.font.size = Pt(10.5)
            skills_run.font.name = 'Calibri'

    @staticmethod
    def _add_experience(doc: Document, resume_data: Dict):
        """Add work experience with company/position in blue, bullets in ONE paragraph."""
        experience = resume_data.get("experience", [])
        if not experience:
            return

        DOCResumeGenerator._add_section_header(doc, "PROFESSIONAL EXPERIENCE")

        for idx, job in enumerate(experience):
            # Company and title in single paragraph to avoid spacing
            job_header_para = doc.add_paragraph()
            job_header_para.space_after = Pt(0)
            job_header_para.space_before = Pt(6) if idx > 0 else Pt(0)  # Add space above company name (except first)
            job_header_para.line_spacing = 1.0

            # Company name and location - larger font, blue color to stand out
            company_run = job_header_para.add_run(job.get("company", ""))
            company_run.font.bold = True
            company_run.font.size = Pt(12)  # Larger to stand out
            company_run.font.name = 'Calibri'
            company_run.font.color.rgb = DOCResumeGenerator.COLOR_HEADER  # Blue color

            if "location" in job:
                location_run = job_header_para.add_run(f" | {job['location']}")
                location_run.font.size = Pt(11)
                location_run.font.name = 'Calibri'
                location_run.font.color.rgb = DOCResumeGenerator.COLOR_HEADER  # Blue color

            # Line break (not new paragraph!)
            job_header_para.add_run('\n')

            # Job title and dates (same paragraph, new line) - larger font, blue color to stand out
            title_run = job_header_para.add_run(job.get("position", job.get("title", "")))
            title_run.font.italic = True
            title_run.font.size = Pt(11)  # Larger to stand out
            title_run.font.name = 'Calibri'
            title_run.font.color.rgb = DOCResumeGenerator.COLOR_HEADER  # Blue color

            if "start_date" in job:
                end_date = job.get("end_date", "Present")
                dates_run = job_header_para.add_run(f" | {job['start_date']} – {end_date}")
                dates_run.font.italic = True
                dates_run.font.size = Pt(11)
                dates_run.font.name = 'Calibri'
                dates_run.font.color.rgb = DOCResumeGenerator.COLOR_HEADER  # Blue color

            # Context line (if present) - add to same paragraph with line break
            if "context" in job:
                job_header_para.add_run('\n')
                context_run = job_header_para.add_run(job["context"])
                context_run.font.italic = True
                context_run.font.size = Pt(10)
                context_run.font.name = 'Calibri'
                context_run.font.color.rgb = DOCResumeGenerator.COLOR_CONTEXT

            # Bullets with strategic highlighting - single paragraph to avoid spacing
            bullets = job.get("responsibilities", job.get("achievements", job.get("bullets", [])))
            if bullets:
                bullets_para = doc.add_paragraph()
                bullets_para.space_after = Pt(0)
                bullets_para.line_spacing = 1.0

                for bullet_idx, bullet_text in enumerate(bullets):
                    # Add line break before each bullet (except first)
                    if bullet_idx > 0:
                        bullets_para.add_run('\n')

                    # Add bullet symbol
                    bullet_symbol = bullets_para.add_run('• ')
                    bullet_symbol.font.size = Pt(10.5)
                    bullet_symbol.font.name = 'Calibri'

                    # Apply strategic highlighting to bullet text
                    StrategicHighlighter.apply_strategic_highlighting(bullets_para, bullet_text)

                    # Format all runs that don't have explicit formatting
                    for run in bullets_para.runs:
                        if run.font.size is None:
                            run.font.size = Pt(10.5)
                        if run.font.name is None:
                            run.font.name = 'Calibri'
                        if not run.font.bold and run.font.color.rgb is None:
                            run.font.color.rgb = DOCResumeGenerator.COLOR_BODY

    @staticmethod
    def _add_education(doc: Document, resume_data: Dict):
        """Add education section."""
        education = resume_data.get("education", [])
        if not education:
            return

        DOCResumeGenerator._add_section_header(doc, "EDUCATION")

        for edu in education:
            edu_para = doc.add_paragraph()
            edu_para.space_after = Pt(0)
            edu_para.line_spacing = 1.0

            # Degree
            degree_run = edu_para.add_run(edu.get("degree", ""))
            degree_run.font.bold = True
            degree_run.font.size = Pt(10.5)
            degree_run.font.name = 'Calibri'

            # School and date
            school_text = f" | {edu.get('school', '')}"
            if "graduation_date" in edu:
                school_text += f" | {edu['graduation_date']}"

            school_run = edu_para.add_run(school_text)
            school_run.font.size = Pt(10.5)
            school_run.font.name = 'Calibri'

    @staticmethod
    def _add_certifications(doc: Document, resume_data: Dict):
        """Add certifications section."""
        certs = resume_data.get("certifications", [])
        if not certs:
            return

        DOCResumeGenerator._add_section_header(doc, "CERTIFICATIONS")

        cert_para = doc.add_paragraph()
        cert_para.space_after = Pt(0)
        cert_para.line_spacing = 1.0

        if isinstance(certs, list):
            cert_text = " | ".join(certs)
        else:
            cert_text = str(certs)

        cert_run = cert_para.add_run(cert_text)
        cert_run.font.size = Pt(10.5)
        cert_run.font.name = 'Calibri'


class StrategicHighlighter:
    """Applies strategic bold highlighting to resume bullets."""

    # Patterns to highlight (numbers, percentages, key tech, achievements)
    HIGHLIGHT_PATTERNS = [
        r'\b\d+[%+]?\b',  # Numbers and percentages
        r'\b\d+[KMB]\+?\b',  # 10K, 5M, 1B
        r'\b(React|Node\.js|Python|AWS|Docker|Kubernetes|TypeScript|JavaScript|Java|Go|Rust|SQL|PostgreSQL|MongoDB|Redis|GraphQL|REST|API|CI/CD|Git|Jenkins|Terraform|Lambda)\b',  # Tech keywords
        r'\b(increased|reduced|improved|optimized|automated|implemented|launched|designed|developed|built|created|led|managed)\b',  # Action verbs
    ]

    @staticmethod
    def apply_strategic_highlighting(paragraph, text: str):
        """Apply bold highlighting to key parts of text."""
        # Collect ALL matches from ALL patterns first
        all_matches = []
        for pattern in StrategicHighlighter.HIGHLIGHT_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                all_matches.append((match.start(), match.end()))

        # Sort by start position
        all_matches.sort(key=lambda x: x[0])

        # Merge overlapping matches
        merged_matches = []
        for start, end in all_matches:
            if merged_matches and start <= merged_matches[-1][1]:
                # Overlapping - extend the previous match
                merged_matches[-1] = (merged_matches[-1][0], max(merged_matches[-1][1], end))
            else:
                # Non-overlapping - add new match
                merged_matches.append((start, end))

        # Add runs in a single pass through the text
        position = 0
        for start, end in merged_matches:
            # Add normal text before match
            if position < start:
                normal_run = paragraph.add_run(text[position:start])
                normal_run.font.size = Pt(10.5)
                normal_run.font.name = 'Calibri'

            # Add bold match
            bold_run = paragraph.add_run(text[start:end])
            bold_run.font.bold = True
            bold_run.font.size = Pt(10.5)
            bold_run.font.name = 'Calibri'

            position = end

        # Add remaining text
        if position < len(text):
            final_run = paragraph.add_run(text[position:])
            final_run.font.size = Pt(10.5)
            final_run.font.name = 'Calibri'
