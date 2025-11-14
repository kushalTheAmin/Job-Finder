"""
Smart DOCX Resume Generator - AI-driven with enforced styling rules.

This generator:
1. Accepts flexible layout plans from AI Layout Analyzer
2. Renders ANY section type discovered by AI
3. ALWAYS enforces user's perfected styling rules (Pt(0), line_spacing=1.0, single paragraphs)
4. Handles all field name variations gracefully
5. Future-proof to any JSON structure changes
"""

import logging
import html
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)


class SmartDOCXGenerator:
    """
    AI-driven DOCX generator that adapts to any resume structure
    while religiously enforcing styling rules.
    """

    # STYLING RULES - NEVER CHANGE THESE!
    # These are the user's perfected rules from many iterations
    STYLE_SPACE_AFTER = Pt(0)  # No extra spacing between paragraphs
    STYLE_LINE_SPACING = 1.0  # Single line spacing
    STYLE_USE_SINGLE_PARAGRAPH = True  # Use ONE paragraph with \n breaks
    STYLE_MARGINS = (0.5, 0.7)  # Top/bottom, left/right in inches
    STYLE_FONT = 'Calibri'

    # Color scheme - Professional dark blue
    COLOR_HEADER = RGBColor(0, 51, 102)  # Dark blue for headers and company names
    COLOR_BODY = RGBColor(0, 0, 0)  # Black for body text
    COLOR_CONTEXT = RGBColor(60, 60, 60)  # Gray for context lines

    def __init__(self):
        """Initialize smart generator."""
        logger.info("Initialized SmartDOCXGenerator")

    def generate(
        self,
        resume_data: Dict,
        job: Dict,
        layout_plan: Optional[Dict] = None
    ) -> str:
        """
        Generate DOCX resume from layout plan.

        Args:
            resume_data: Resume data dict (fallback if no layout_plan)
            job: Job posting dict
            layout_plan: AI-generated layout plan (optional)

        Returns:
            Path to generated DOCX file
        """
        try:
            job_company = job.get('company', 'Unknown')
            job_title = job.get('title', 'Unknown')

            logger.info("=" * 70)
            logger.info(f"📝 SMART DOCX GENERATOR - Starting for: {job_company} - {job_title}")
            logger.info("=" * 70)

            doc = Document()

            # Set margins (user's rule)
            logger.info("📐 Setting document margins (user's perfected rules)")
            logger.info(f"   Margins: {self.STYLE_MARGINS[0]}\" top/bottom, {self.STYLE_MARGINS[1]}\" left/right")
            self._set_margins(doc)

            # Render sections from layout plan
            if layout_plan and 'sections' in layout_plan:
                logger.info(f"✅ Layout plan received with {len(layout_plan['sections'])} sections")
                logger.info("🎨 Rendering resume with AI-discovered structure...")
                logger.info("   STYLING RULES ENFORCED:")
                logger.info(f"   • space_after = {self.STYLE_SPACE_AFTER} (no extra spacing)")
                logger.info(f"   • line_spacing = {self.STYLE_LINE_SPACING} (single spacing)")
                logger.info(f"   • Font = {self.STYLE_FONT}")
                logger.info(f"   • Single paragraphs with \\n line breaks")
                logger.info("-" * 70)

                self._render_from_layout_plan(doc, layout_plan, resume_data)
            else:
                # Fallback: shouldn't happen with AI analyzer
                logger.warning("❌ No layout plan provided! Using emergency fallback")
                self._render_fallback(doc, resume_data)

            # Save file
            output_path = self._save_document(doc, resume_data, job)

            logger.info("=" * 70)
            logger.info(f"✅ DOCX GENERATION COMPLETE: {output_path.name}")
            logger.info("=" * 70)

            return str(output_path)

        except Exception as e:
            logger.error("=" * 70)
            logger.error(f"❌ ERROR generating DOCX: {str(e)}")
            logger.error("=" * 70)
            raise

    def _set_margins(self, doc: Document):
        """Set document margins (user's styling rule)."""
        top_bottom, left_right = self.STYLE_MARGINS
        for section in doc.sections:
            section.top_margin = Inches(top_bottom)
            section.bottom_margin = Inches(top_bottom)
            section.left_margin = Inches(left_right)
            section.right_margin = Inches(left_right)

    def _render_from_layout_plan(self, doc: Document, layout_plan: Dict, resume_data: Dict):
        """Render document from AI layout plan."""
        sections = layout_plan.get('sections', [])

        for section in sections:
            section_type = section.get('type')

            if section_type == 'header':
                self._render_header(doc, section.get('data', {}))

            elif section_type == 'text_block':
                self._render_text_block(doc, section)

            elif section_type == 'skills_dict':
                self._render_skills_dict(doc, section)

            elif section_type == 'experience_list':
                self._render_experience_list(doc, section)

            elif section_type == 'education_list':
                self._render_education_list(doc, section)

            elif section_type == 'simple_list':
                self._render_simple_list(doc, section)

            elif section_type == 'project_list':
                self._render_project_list(doc, section)

            else:
                logger.warning(f"Unknown section type: {section_type}, skipping")

    def _render_header(self, doc: Document, data: Dict):
        """
        Render header section (name, contact info).
        STYLING RULE: Single paragraph with line breaks.
        """
        header_para = doc.add_paragraph()
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
        header_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

        # Name (18pt, bold, dark blue)
        name = data.get('name', '')
        if name:
            name_run = header_para.add_run(name)
            name_run.font.size = Pt(18)
            name_run.font.bold = True
            name_run.font.name = self.STYLE_FONT
            name_run.font.color.rgb = self.COLOR_HEADER

            # Line break (not new paragraph!)
            header_para.add_run('\n')

        # Contact info (10pt, pipe-separated)
        contact_parts = []
        for field in ['email', 'phone', 'linkedin', 'location']:
            if data.get(field):
                contact_parts.append(data[field])

        if contact_parts:
            contact_run = header_para.add_run(" | ".join(contact_parts))
            contact_run.font.size = Pt(10)
            contact_run.font.name = self.STYLE_FONT
            contact_run.font.color.rgb = self.COLOR_BODY

    def _render_text_block(self, doc: Document, section: Dict):
        """
        Render text block section (summary, objective, etc.).
        STYLING RULE: Single paragraph with Pt(0) spacing.
        """
        title = section.get('title', '')
        content = section.get('content', '')

        if not content:
            return

        # Section header
        self._add_section_header(doc, title)

        # Content paragraph
        content_para = doc.add_paragraph()
        content_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
        content_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

        content_run = content_para.add_run(content)
        content_run.font.size = Pt(10.5)
        content_run.font.name = self.STYLE_FONT
        content_run.font.color.rgb = self.COLOR_BODY

    def _render_skills_dict(self, doc: Document, section: Dict):
        """
        Render skills dictionary section.
        STYLING RULE: Single paragraph with line breaks between categories.
        """
        title = section.get('title', 'TECHNICAL SKILLS')
        categories = section.get('categories', {})

        if not categories:
            return

        # Section header
        self._add_section_header(doc, title)

        # Single paragraph for all skills (user's rule!)
        skills_para = doc.add_paragraph()
        skills_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
        skills_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

        for idx, (category, tech_list) in enumerate(categories.items()):
            # Add line break before each category (except first)
            if idx > 0:
                skills_para.add_run('\n')

            # Category name (bold)
            category_run = skills_para.add_run(f"{category}: ")
            category_run.font.bold = True
            category_run.font.size = Pt(10.5)
            category_run.font.name = self.STYLE_FONT

            # Technologies (not bold)
            if isinstance(tech_list, list):
                tech_text = ", ".join(str(t) for t in tech_list)
            else:
                tech_text = str(tech_list)

            tech_run = skills_para.add_run(tech_text)
            tech_run.font.size = Pt(10.5)
            tech_run.font.name = self.STYLE_FONT
            tech_run.font.color.rgb = self.COLOR_BODY

    def _render_experience_list(self, doc: Document, section: Dict):
        """
        Render experience list section.
        STYLING RULE: Company/title in ONE paragraph, bullets in another.
        """
        title = section.get('title', 'PROFESSIONAL EXPERIENCE')
        items = section.get('items', [])

        if not items:
            return

        # Section header
        self._add_section_header(doc, title)

        for idx, job in enumerate(items):
            # Company and title in single paragraph (user's rule!)
            job_header_para = doc.add_paragraph()
            job_header_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
            job_header_para.space_before = Pt(6) if idx > 0 else Pt(0)
            job_header_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

            # Company name and location
            company = job.get('company', '')
            if company:
                company_run = job_header_para.add_run(company)
                company_run.font.bold = True
                company_run.font.size = Pt(12)
                company_run.font.name = self.STYLE_FONT
                company_run.font.color.rgb = self.COLOR_HEADER

            location = job.get('location', '')
            if location:
                location_run = job_header_para.add_run(f" | {location}")
                location_run.font.size = Pt(11)
                location_run.font.name = self.STYLE_FONT
                location_run.font.color.rgb = self.COLOR_HEADER

            # Line break (not new paragraph!)
            job_header_para.add_run('\n')

            # Job title and dates
            title = job.get('title', '')
            if title:
                title_run = job_header_para.add_run(title)
                title_run.font.italic = True
                title_run.font.size = Pt(11)
                title_run.font.name = self.STYLE_FONT
                title_run.font.color.rgb = self.COLOR_HEADER

            start_date = job.get('start_date', '')
            if start_date:
                end_date = job.get('end_date', 'Present')
                dates_run = job_header_para.add_run(f" | {start_date} – {end_date}")
                dates_run.font.italic = True
                dates_run.font.size = Pt(11)
                dates_run.font.name = self.STYLE_FONT
                dates_run.font.color.rgb = self.COLOR_HEADER

            # Context line (if present)
            context = job.get('context', '')
            if context:
                job_header_para.add_run('\n')
                context_run = job_header_para.add_run(context)
                context_run.font.italic = True
                context_run.font.size = Pt(10)
                context_run.font.name = self.STYLE_FONT
                context_run.font.color.rgb = self.COLOR_CONTEXT

            # Bullets in single paragraph (user's rule!)
            bullets = job.get('bullets', [])
            if bullets:
                bullets_para = doc.add_paragraph()
                bullets_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
                bullets_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

                for bullet_idx, bullet_text in enumerate(bullets):
                    # Add line break before each bullet (except first)
                    if bullet_idx > 0:
                        bullets_para.add_run('\n')

                    # Add bullet symbol
                    bullet_symbol = bullets_para.add_run('• ')
                    bullet_symbol.font.size = Pt(10.5)
                    bullet_symbol.font.name = self.STYLE_FONT

                    # Decode HTML entities
                    clean_bullet_text = html.unescape(str(bullet_text))

                    # Apply strategic highlighting
                    StrategicHighlighter.apply_strategic_highlighting(bullets_para, clean_bullet_text)

                    # Format all runs
                    for run in bullets_para.runs:
                        if run.font.size is None:
                            run.font.size = Pt(10.5)
                        if run.font.name is None:
                            run.font.name = self.STYLE_FONT
                        if not run.font.bold and run.font.color.rgb is None:
                            run.font.color.rgb = self.COLOR_BODY

    def _render_education_list(self, doc: Document, section: Dict):
        """
        Render education list section.
        STYLING RULE: Each item in one paragraph.
        """
        title = section.get('title', 'EDUCATION')
        items = section.get('items', [])

        if not items:
            return

        # Section header
        self._add_section_header(doc, title)

        for edu in items:
            edu_para = doc.add_paragraph()
            edu_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
            edu_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

            # Degree (bold)
            degree = edu.get('degree', '')
            if degree:
                degree_run = edu_para.add_run(degree)
                degree_run.font.bold = True
                degree_run.font.size = Pt(10.5)
                degree_run.font.name = self.STYLE_FONT

            # School and date
            school = edu.get('school', '')
            graduation_date = edu.get('graduation_date', '')

            school_parts = []
            if school:
                school_parts.append(school)
            if graduation_date:
                school_parts.append(graduation_date)

            if school_parts:
                school_text = " | ".join(school_parts)
                school_run = edu_para.add_run(f" | {school_text}")
                school_run.font.size = Pt(10.5)
                school_run.font.name = self.STYLE_FONT

    def _render_simple_list(self, doc: Document, section: Dict):
        """
        Render simple list section (certifications, awards, etc.).
        STYLING RULE: Single paragraph with chosen format.
        """
        title = section.get('title', '')
        items = section.get('items', [])
        format_type = section.get('format', 'pipe_separated')

        if not items:
            return

        # Section header
        self._add_section_header(doc, title)

        # Single paragraph (user's rule!)
        list_para = doc.add_paragraph()
        list_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
        list_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

        # Format items based on type
        if format_type == 'pipe_separated':
            # Join with pipes (for certifications, awards)
            text = " | ".join(str(item) for item in items)
        else:  # 'bulleted' or default
            # Join with newlines and bullets (for publications, achievements)
            text = "\n".join(f"• {item}" for item in items)

        list_run = list_para.add_run(text)
        list_run.font.size = Pt(10.5)
        list_run.font.name = self.STYLE_FONT
        list_run.font.color.rgb = self.COLOR_BODY

    def _render_project_list(self, doc: Document, section: Dict):
        """
        Render project list section.
        STYLING RULE: Each project in paragraphs with Pt(0) spacing.
        """
        title = section.get('title', 'PROJECTS')
        items = section.get('items', [])

        if not items:
            return

        # Section header
        self._add_section_header(doc, title)

        for project in items:
            project_para = doc.add_paragraph()
            project_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
            project_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

            # Project name (bold)
            name = project.get('name', '')
            if name:
                name_run = project_para.add_run(name)
                name_run.font.bold = True
                name_run.font.size = Pt(10.5)
                name_run.font.name = self.STYLE_FONT

            # Description
            description = project.get('description', '')
            if description:
                project_para.add_run(f" - {description}")

            # Technologies
            technologies = project.get('technologies', [])
            if technologies:
                tech_text = ", ".join(str(t) for t in technologies)
                tech_run = project_para.add_run(f" ({tech_text})")
                tech_run.font.italic = True

            # Format all runs
            for run in project_para.runs:
                if run.font.size is None:
                    run.font.size = Pt(10.5)
                if run.font.name is None:
                    run.font.name = self.STYLE_FONT
                if not run.font.bold and not run.font.italic and run.font.color.rgb is None:
                    run.font.color.rgb = self.COLOR_BODY

    def _add_section_header(self, doc: Document, title: str):
        """
        Add section header with formatting.
        STYLING RULE: Pt(0) spacing.
        """
        header_para = doc.add_paragraph()
        header_run = header_para.add_run(title)
        header_run.font.size = Pt(12)
        header_run.font.bold = True
        header_run.font.name = self.STYLE_FONT
        header_run.font.color.rgb = self.COLOR_HEADER

        header_para.space_before = self.STYLE_SPACE_AFTER  # Pt(0)
        header_para.space_after = self.STYLE_SPACE_AFTER  # Pt(0)
        header_para.line_spacing = self.STYLE_LINE_SPACING  # 1.0

    def _render_fallback(self, doc: Document, resume_data: Dict):
        """
        Fallback rendering if no layout plan.
        Creates basic structure from resume_data.
        """
        logger.error("NO LAYOUT PLAN PROVIDED! This should never happen with AI analyzer.")
        logger.error("Creating emergency fallback structure...")

        # Emergency fallback - render basic sections
        # Header
        if 'personal_info' in resume_data or 'name' in resume_data:
            personal_info = resume_data.get('personal_info', {})
            header_data = {
                'name': personal_info.get('name', resume_data.get('name', '')),
                'email': personal_info.get('email', resume_data.get('email', '')),
                'phone': personal_info.get('phone', resume_data.get('phone', '')),
                'linkedin': personal_info.get('linkedin', resume_data.get('linkedin', '')),
                'location': personal_info.get('location', resume_data.get('location', ''))
            }
            self._render_header(doc, header_data)
            logger.warning("Fallback: Rendered header")

        # Skills
        skills = resume_data.get('technical_skills', resume_data.get('skills', {}))
        if skills and isinstance(skills, dict):
            self._render_skills_dict(doc, {'title': 'TECHNICAL SKILLS', 'categories': skills})
            logger.warning("Fallback: Rendered skills")

        # Experience
        if 'experience' in resume_data:
            self._render_experience_list(doc, {'title': 'PROFESSIONAL EXPERIENCE', 'items': resume_data['experience']})
            logger.warning("Fallback: Rendered experience")

        # Education
        if 'education' in resume_data:
            self._render_education_list(doc, {'title': 'EDUCATION', 'items': resume_data['education']})
            logger.warning("Fallback: Rendered education")

        logger.error("Fallback rendering complete - but AI Layout Analyzer should be used!")

    def _save_document(self, doc: Document, resume_data: Dict, job: Dict) -> Path:
        """Save document and return path."""
        output_dir = Path('output/resumes')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get name from various possible locations
        name = resume_data.get('name')
        if not name and 'personal_info' in resume_data:
            name = resume_data['personal_info'].get('name')
        if not name:
            name = 'Resume'

        company_name = job.get('company', 'Company').replace(' ', '_').replace('/', '_')
        timestamp = job.get('timestamp', '').replace(':', '').replace('-', '').replace(' ', '_')[:15]
        filename = f"{name.replace(' ', '_')}_{company_name}_{timestamp}.docx"
        output_path = output_dir / filename

        doc.save(str(output_path))
        return output_path

def _parse_markdown_bold(text: str) -> list:
    """
    Parse markdown bold syntax (**text**) and return segments with bold flags.

    Args:
        text: Text that may contain **bold** markdown syntax

    Returns:
        List of (text, is_bold) tuples

    Example:
        "Hello **world** test" -> [("Hello ", False), ("world", True), (" test", False)]
    """
    segments = []
    current_pos = 0

    # Find all **text** patterns
    pattern = r'\*\*([^*]+)\*\*'
    matches = list(re.finditer(pattern, text))

    for match in matches:
        # Add text before the bold section
        if current_pos < match.start():
            segments.append((text[current_pos:match.start()], False))

        # Add the bold text (without the ** markers)
        segments.append((match.group(1), True))
        current_pos = match.end()

    # Add remaining text
    if current_pos < len(text):
        segments.append((text[current_pos:], False))

    return segments if segments else [(text, False)]


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
        """
        Apply bold highlighting to key parts of text.
        Handles both markdown bold syntax (**text**) and strategic highlighting patterns.
        """
        # Step 1: Parse markdown bold syntax first
        markdown_segments = _parse_markdown_bold(text)

        # Step 2: Process each markdown segment
        for segment_text, is_markdown_bold in markdown_segments:
            if not segment_text:
                continue

            # Find strategic highlighting matches within this segment
            strategic_matches = []
            for pattern in StrategicHighlighter.HIGHLIGHT_PATTERNS:
                for match in re.finditer(pattern, segment_text, re.IGNORECASE):
                    strategic_matches.append((match.start(), match.end()))

            # Sort and merge strategic matches
            strategic_matches.sort(key=lambda x: x[0])
            merged_matches = []
            for start, end in strategic_matches:
                if merged_matches and start <= merged_matches[-1][1]:
                    merged_matches[-1] = (merged_matches[-1][0], max(merged_matches[-1][1], end))
                else:
                    merged_matches.append((start, end))

            # Step 3: Create runs for this segment
            if not merged_matches:
                # No strategic matches - just add the segment with markdown bold if applicable
                run = paragraph.add_run(segment_text)
                run.font.bold = is_markdown_bold
                run.font.size = Pt(10.5)
                run.font.name = 'Calibri'
            else:
                # Has strategic matches - interleave normal and strategic-bold text
                position = 0
                for start, end in merged_matches:
                    # Add text before strategic match
                    if position < start:
                        run = paragraph.add_run(segment_text[position:start])
                        run.font.bold = is_markdown_bold  # Respect markdown bold
                        run.font.size = Pt(10.5)
                        run.font.name = 'Calibri'

                    # Add strategic match (always bold, even if not markdown bold)
                    bold_run = paragraph.add_run(segment_text[start:end])
                    bold_run.font.bold = True
                    bold_run.font.size = Pt(10.5)
                    bold_run.font.name = 'Calibri'

                    position = end

                # Add remaining text in segment
                if position < len(segment_text):
                    run = paragraph.add_run(segment_text[position:])
                    run.font.bold = is_markdown_bold  # Respect markdown bold
                    run.font.size = Pt(10.5)
                    run.font.name = 'Calibri'
