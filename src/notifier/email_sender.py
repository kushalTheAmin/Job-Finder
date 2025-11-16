"""Email notification system."""

import logging
import os
from typing import List, Dict, Any
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib


logger = logging.getLogger(__name__)


class EmailSender:
    """Sends email notifications with job listings and resumes."""

    def __init__(self, config: Any):
        """Initialize email sender."""
        self.config = config
        self.from_email = os.getenv('GMAIL_USER')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        self.to_email = config.email_to

        if not self.from_email or not self.app_password:
            logger.warning("Gmail credentials not configured")

    def send_daily_report(
        self,
        jobs: List[Dict[str, Any]],
        resume_files: List[str] = None,
        stats: Dict[str, Any] = None
    ) -> bool:
        """Send daily job report email."""
        if not self.from_email or not self.app_password:
            logger.error("Email credentials missing")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._create_subject(len(jobs))
            msg['From'] = self.from_email
            msg['To'] = self.to_email

            # Create HTML body
            html_body = self._create_html_body(jobs, stats)

            # Attach HTML
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Attach resume PDFs
            if resume_files:
                for file_path in resume_files:
                    self._attach_file(msg, file_path)

            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.from_email, self.app_password)
                server.send_message(msg)

            logger.info(f"Sent email report to {self.to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def _create_subject(self, job_count: int) -> str:
        """Create email subject line."""
        from datetime import datetime
        date_str = datetime.now().strftime('%B %d, %Y')

        if job_count == 0:
            return f"Job Finder - No New Jobs ({date_str})"
        elif job_count == 1:
            return f"Job Finder - 1 New Matching Job ({date_str})"
        else:
            return f"Job Finder - {job_count} New Matching Jobs ({date_str})"

    def _create_html_body(self, jobs: List[Dict[str, Any]], stats: Dict[str, Any] = None) -> str:
        """Create HTML email body."""
        from datetime import datetime

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats {{
            background: #f7f9fc;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .job-card {{
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }}
        .job-title {{
            font-size: 20px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 0 0 5px 0;
        }}
        .company {{
            font-size: 16px;
            color: #667eea;
            margin: 0;
        }}
        .match-badge {{
            background: #10b981;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        .job-details {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 14px;
            color: #666;
        }}
        .job-detail {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .description {{
            color: #333;
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        .highlights {{
            background: #f0f9ff;
            border-left: 3px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        .highlights-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }}
        .highlights ul {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        .highlights li {{
            margin-bottom: 5px;
        }}
        .modifications {{
            background: #fff9e6;
            border-left: 3px solid #f59e0b;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        .modifications-title {{
            font-weight: bold;
            color: #f59e0b;
            margin-bottom: 12px;
            font-size: 16px;
        }}
        .modification-section {{
            margin-bottom: 12px;
        }}
        .modification-label {{
            font-weight: bold;
            color: #666;
            font-size: 13px;
            margin-bottom: 4px;
        }}
        .modification-content {{
            color: #333;
            font-size: 14px;
            padding-left: 8px;
        }}
        .score-bar {{
            background: #e5e7eb;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 4px;
        }}
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            transition: width 0.3s ease;
        }}
        .score-text {{
            font-size: 12px;
            color: #666;
            margin-top: 2px;
        }}
        .bullet-change {{
            background: #f0fdf4;
            border: 1px solid #d1fae5;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        .bullet-before {{
            color: #ef4444;
            text-decoration: line-through;
            margin-bottom: 4px;
        }}
        .bullet-after {{
            color: #10b981;
            font-weight: 500;
        }}
        .keywords-added {{
            background: #dbeafe;
            color: #1e40af;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            display: inline-block;
            margin: 2px;
        }}
        .apply-button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
        }}
        .apply-button:hover {{
            background: #5568d3;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e8ed;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .no-jobs {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Your Daily Job Matches</h1>
        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
    </div>
"""

        # Add statistics if provided
        if stats:
            html += f"""
    <div class="stats">
        <div class="stat">
            <div class="stat-number">{stats.get('jobs_found', 0)}</div>
            <div class="stat-label">Jobs Searched</div>
        </div>
        <div class="stat">
            <div class="stat-number">{len(jobs)}</div>
            <div class="stat-label">Matches Found</div>
        </div>
        <div class="stat">
            <div class="stat-number">{stats.get('avg_match_score', 0):.0f}%</div>
            <div class="stat-label">Avg Match Score</div>
        </div>
    </div>
"""

        # Add job cards
        if jobs:
            for job in jobs:
                match_score = job.get('match_score', 0)
                analysis = job.get('match_analysis', {})

                html += f"""
    <div class="job-card">
        <div class="job-header">
            <div>
                <h2 class="job-title">{job.get('title', 'Unknown Title')}</h2>
                <p class="company">{job.get('company', 'Unknown Company')}</p>
            </div>
            <div class="match-badge">{match_score}% Match</div>
        </div>

        <div class="job-details">
            <div class="job-detail">📍 {job.get('location', 'N/A')}</div>
            {f'<div class="job-detail">💰 {job.get("salary", "Not specified")}</div>' if job.get('salary') else ''}
            <div class="job-detail">🏢 {job.get('job_type', 'Full-time')}</div>
            {f'<div class="job-detail">🏠 Remote</div>' if job.get('remote') else ''}
        </div>

        <div class="description">
            {job.get('description', '')[:300]}...
        </div>
"""

                # Add highlights from AI analysis
                if analysis.get('key_highlights'):
                    html += """
        <div class="highlights">
            <div class="highlights-title">✨ Why You're a Great Match:</div>
            <ul>
"""
                    for highlight in analysis.get('key_highlights', [])[:3]:
                        html += f"                <li>{highlight}</li>\n"

                    html += """
            </ul>
        </div>
"""

                # Add matching skills
                if analysis.get('matching_skills'):
                    skills_text = ', '.join(analysis.get('matching_skills', [])[:8])
                    html += f"""
        <div class="highlights">
            <div class="highlights-title">🎯 Matching Skills:</div>
            <p>{skills_text}</p>
        </div>
"""

                # Add resume modifications report
                customization = job.get('customization_report', {})
                if customization:
                    html += self._create_modifications_report(customization)

                html += f"""
        <a href="{job.get('url', '#')}" class="apply-button" target="_blank">View Job & Apply →</a>
    </div>
"""
        else:
            html += """
    <div class="no-jobs">
        <h2>No new jobs found today</h2>
        <p>We'll keep searching and notify you when we find matching opportunities!</p>
    </div>
"""

        html += """
    <div class="footer">
        <p>📎 Your customized resumes are attached to this email and uploaded to Google Drive.</p>
        <p>This is an automated email from your Job Finder system.</p>
    </div>
</body>
</html>
"""

        return html

    def _create_modifications_report(self, customization: Dict[str, Any]) -> str:
        """Create HTML for resume modifications report."""
        coverage_before = customization.get('coverage_before', 0)
        coverage_after = customization.get('coverage_after', 0)
        total_changes = customization.get('total_changes', 0)
        modifications = customization.get('modifications', [])
        role_analysis = customization.get('role_analysis', {})

        html = """
        <div class="modifications">
            <div class="modifications-title">📝 Resume Customization Report</div>
"""

        # ATS Coverage improvement
        if coverage_before > 0 or coverage_after > 0:
            improvement = coverage_after - coverage_before
            improvement_text = f"+{improvement}%" if improvement > 0 else f"{improvement}%"

            html += f"""
            <div class="modification-section">
                <div class="modification-label">ATS Match Score:</div>
                <div class="modification-content">
                    {coverage_before}% → {coverage_after}% <span style="color: #10b981; font-weight: bold;">({improvement_text})</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {coverage_after}%;"></div>
                    </div>
                </div>
            </div>
"""

        # Domain/Role repositioning
        domain_shift = role_analysis.get('repositioning_strategy', {}).get('domain_context_shift', '')
        if domain_shift:
            html += f"""
            <div class="modification-section">
                <div class="modification-label">Domain Repositioning:</div>
                <div class="modification-content">{domain_shift}</div>
            </div>
"""

        # Total changes summary
        if total_changes > 0:
            html += f"""
            <div class="modification-section">
                <div class="modification-label">Changes Made:</div>
                <div class="modification-content">
                    ✏️ Modified {total_changes} experience bullet{'s' if total_changes != 1 else ''}
"""

            # Count skills added
            all_keywords = []
            for mod in modifications[:3]:  # Top 3 modifications
                if isinstance(mod, dict):
                    keywords = mod.get('keywords_added', [])
                    if isinstance(keywords, list):
                        all_keywords.extend(keywords)

            if all_keywords:
                unique_keywords = list(set(all_keywords))
                html += f"""
                    <br>🎯 Added {len(unique_keywords)} new keyword{'s' if len(unique_keywords) != 1 else ''}: """
                for keyword in unique_keywords[:10]:
                    html += f'<span class="keywords-added">{keyword}</span>'
                if len(unique_keywords) > 10:
                    html += f' <span style="color: #666;">+{len(unique_keywords) - 10} more</span>'

            html += """
                </div>
            </div>
"""

        # Show top 3 bullet modifications with before/after
        if modifications:
            html += """
            <div class="modification-section">
                <div class="modification-label">Top Changes (Bullet Examples):</div>
"""
            for i, mod in enumerate(modifications[:3], 1):
                if not isinstance(mod, dict):
                    continue

                original = mod.get('original', '')
                modified = mod.get('modified', '')
                keywords = mod.get('keywords_added', [])
                if not isinstance(keywords, list):
                    keywords = []

                if original and modified and original != modified:
                    # Truncate for readability
                    original_short = original[:120] + '...' if len(original) > 120 else original
                    modified_short = modified[:120] + '...' if len(modified) > 120 else modified

                    html += f"""
                <div class="bullet-change">
                    <div class="bullet-before">Before: {original_short}</div>
                    <div class="bullet-after">After: {modified_short}</div>"""

                    if keywords:
                        html += f"""
                    <div style="margin-top: 4px; font-size: 11px; color: #666;">
                        Added: {', '.join(keywords)}
                    </div>"""

                    html += """
                </div>
"""

            html += """
            </div>
"""

        # Professional Summary change indicator
        role_summary_rewrite = role_analysis.get('repositioning_strategy', {}).get('summary_rewrite', '')
        if role_summary_rewrite:
            summary_preview = role_summary_rewrite[:150] + '...' if len(role_summary_rewrite) > 150 else role_summary_rewrite
            html += f"""
            <div class="modification-section">
                <div class="modification-label">Professional Summary:</div>
                <div class="modification-content" style="font-style: italic;">
                    ✅ Completely rewritten to match job focus<br>
                    <span style="font-size: 12px; color: #666;">"{summary_preview}"</span>
                </div>
            </div>
"""

        # Validation scores if available
        validation_score = customization.get('validation_score', 0)
        authenticity_score = customization.get('authenticity_score', 0)

        if validation_score > 0 or authenticity_score > 0:
            html += """
            <div class="modification-section">
                <div class="modification-label">Quality Scores:</div>
                <div class="modification-content">
"""
            if validation_score > 0:
                html += f"""
                    <div>Overall Quality: {validation_score}%</div>
                    <div class="score-bar" style="max-width: 200px;">
                        <div class="score-fill" style="width: {validation_score}%;"></div>
                    </div>
"""
            if authenticity_score > 0:
                html += f"""
                    <div style="margin-top: 4px;">Authenticity: {authenticity_score}%</div>
                    <div class="score-bar" style="max-width: 200px;">
                        <div class="score-fill" style="width: {authenticity_score}%;"></div>
                    </div>
"""
            html += """
                </div>
            </div>
"""

        html += """
        </div>
"""

        return html

    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach file to email."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"File not found for attachment: {file_path}")
                return

            with open(file_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='pdf')
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=file_path.name
                )
                msg.attach(attachment)

            logger.debug(f"Attached file: {file_path.name}")

        except Exception as e:
            logger.error(f"Error attaching file: {str(e)}")
