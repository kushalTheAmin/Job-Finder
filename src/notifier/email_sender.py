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
