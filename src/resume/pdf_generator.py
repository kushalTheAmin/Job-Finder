"""PDF resume generator."""

import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


logger = logging.getLogger(__name__)


class PDFResumeGenerator:
    """Generates professional PDF resumes from JSON data."""

    def __init__(self, output_dir: str = "output/resumes"):
        """Initialize PDF generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Name style
        self.styles.add(ParagraphStyle(
            name='Name',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))

        # Title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12,
            borderWidth=0,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=0,
            leftIndent=0
        ))

        # Company/Position style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))

        # Date style
        self.styles.add(ParagraphStyle(
            name='Date',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6
        ))

        # Bullet style
        self.styles.add(ParagraphStyle(
            name='Bullet',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceAfter=4,
            bulletIndent=10
        ))

    def generate(self, resume: Dict[str, Any], job: Dict[str, Any] = None) -> str:
        """Generate PDF resume and return file path."""
        try:
            # Generate filename
            name = resume.get('personal_info', {}).get('name', 'resume').replace(' ', '_')
            company = job.get('company', 'general').replace(' ', '_') if job else 'general'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{company}_{timestamp}.pdf"
            filepath = self.output_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )

            # Build content
            story = []
            story.extend(self._build_header(resume))
            story.extend(self._build_summary(resume))
            story.extend(self._build_skills(resume))
            story.extend(self._build_experience(resume))
            story.extend(self._build_education(resume))

            # Add certifications if present
            if resume.get('certifications'):
                story.extend(self._build_certifications(resume))

            # Add projects if present
            if resume.get('projects'):
                story.extend(self._build_projects(resume))

            # Build PDF
            doc.build(story)

            logger.info(f"Generated PDF resume: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _build_header(self, resume: Dict[str, Any]) -> list:
        """Build header section with contact info."""
        elements = []
        info = resume.get('personal_info', {})

        # Name
        name = info.get('name', '')
        elements.append(Paragraph(name, self.styles['Name']))

        # Title
        title = info.get('title', '')
        elements.append(Paragraph(title, self.styles['JobTitle']))

        # Contact info
        contact_parts = []
        if info.get('email'):
            contact_parts.append(info['email'])
        if info.get('phone'):
            contact_parts.append(info['phone'])
        if info.get('location'):
            contact_parts.append(info['location'])

        contact_line = ' • '.join(contact_parts)
        elements.append(Paragraph(
            contact_line,
            ParagraphStyle('Contact', parent=self.styles['Normal'], fontSize=9, alignment=TA_CENTER, spaceAfter=6)
        ))

        # Links
        link_parts = []
        if info.get('linkedin'):
            link_parts.append(f"LinkedIn: {info['linkedin']}")
        if info.get('github'):
            link_parts.append(f"GitHub: {info['github']}")
        if info.get('portfolio'):
            link_parts.append(f"Portfolio: {info['portfolio']}")

        if link_parts:
            links_line = ' • '.join(link_parts)
            elements.append(Paragraph(
                links_line,
                ParagraphStyle('Links', parent=self.styles['Normal'], fontSize=8, alignment=TA_CENTER, spaceAfter=12)
            ))

        elements.append(Spacer(1, 0.1*inch))
        return elements

    def _build_summary(self, resume: Dict[str, Any]) -> list:
        """Build professional summary section."""
        elements = []
        summary = resume.get('summary', '')

        if summary:
            elements.append(Paragraph('PROFESSIONAL SUMMARY', self.styles['SectionHeading']))
            # Add horizontal line
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph(summary, self.styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))

        return elements

    def _build_skills(self, resume: Dict[str, Any]) -> list:
        """Build skills section."""
        elements = []
        skills = resume.get('skills', {})

        if skills:
            elements.append(Paragraph('TECHNICAL SKILLS', self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.05*inch))

            for category, skill_list in skills.items():
                if skill_list:
                    # Format category name
                    category_name = category.replace('_', ' ').title()
                    skills_text = ', '.join(skill_list[:15])  # Limit to 15 skills per category

                    skill_para = Paragraph(
                        f"<b>{category_name}:</b> {skills_text}",
                        self.styles['Normal']
                    )
                    elements.append(skill_para)
                    elements.append(Spacer(1, 0.08*inch))

            elements.append(Spacer(1, 0.1*inch))

        return elements

    def _build_experience(self, resume: Dict[str, Any]) -> list:
        """Build experience section."""
        elements = []
        experiences = resume.get('experience', [])

        if experiences:
            elements.append(Paragraph('PROFESSIONAL EXPERIENCE', self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.05*inch))

            for exp in experiences:
                # Company and position
                position = exp.get('position', '')
                company = exp.get('company', '')
                location = exp.get('location', '')

                elements.append(Paragraph(
                    f"<b>{position}</b> • {company}",
                    self.styles['Company']
                ))

                # Date and location
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', 'Present')
                date_str = f"{start_date} - {end_date}"
                if location:
                    date_str += f" • {location}"

                elements.append(Paragraph(date_str, self.styles['Date']))

                # Responsibilities
                responsibilities = exp.get('responsibilities', [])
                for resp in responsibilities:
                    bullet_text = f"• {resp}"
                    elements.append(Paragraph(bullet_text, self.styles['Bullet']))

                elements.append(Spacer(1, 0.15*inch))

        return elements

    def _build_education(self, resume: Dict[str, Any]) -> list:
        """Build education section."""
        elements = []
        education = resume.get('education', [])

        if education:
            elements.append(Paragraph('EDUCATION', self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.05*inch))

            for edu in education:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                graduation_date = edu.get('graduation_date', '')
                gpa = edu.get('gpa', '')

                elements.append(Paragraph(
                    f"<b>{degree}</b>",
                    self.styles['Company']
                ))

                date_line = institution
                if graduation_date:
                    date_line += f" • Graduated: {graduation_date}"
                if gpa:
                    date_line += f" • GPA: {gpa}"

                elements.append(Paragraph(date_line, self.styles['Date']))
                elements.append(Spacer(1, 0.1*inch))

        return elements

    def _build_certifications(self, resume: Dict[str, Any]) -> list:
        """Build certifications section."""
        elements = []
        certifications = resume.get('certifications', [])

        if certifications:
            elements.append(Paragraph('CERTIFICATIONS', self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.05*inch))

            for cert in certifications:
                name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                date = cert.get('date', '')

                cert_text = f"• <b>{name}</b> - {issuer}"
                if date:
                    cert_text += f" ({date})"

                elements.append(Paragraph(cert_text, self.styles['Normal']))
                elements.append(Spacer(1, 0.05*inch))

            elements.append(Spacer(1, 0.1*inch))

        return elements

    def _build_projects(self, resume: Dict[str, Any]) -> list:
        """Build projects section."""
        elements = []
        projects = resume.get('projects', [])

        if projects:
            elements.append(Paragraph('KEY PROJECTS', self.styles['SectionHeading']))
            elements.append(Spacer(1, 0.05*inch))

            for proj in projects:
                name = proj.get('name', '')
                description = proj.get('description', '')
                technologies = proj.get('technologies', [])

                elements.append(Paragraph(f"<b>{name}</b>", self.styles['Company']))

                if description:
                    elements.append(Paragraph(description, self.styles['Normal']))

                if technologies:
                    tech_text = f"Technologies: {', '.join(technologies)}"
                    elements.append(Paragraph(tech_text, self.styles['Date']))

                elements.append(Spacer(1, 0.1*inch))

        return elements
