"""Utility functions for Job Finder application."""

import logging
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )

    return logging.getLogger('job_finder')


def generate_job_id(job: Dict[str, Any]) -> str:
    """Generate unique ID for a job posting."""
    # Use company name + job title + location as unique identifier
    unique_string = f"{job.get('company', '')}_{job.get('title', '')}_{job.get('location', '')}"
    return hashlib.md5(unique_string.encode()).hexdigest()


def normalize_job_data(job: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Normalize job data from different sources to a standard format."""
    return {
        'id': generate_job_id(job),
        'title': job.get('title', ''),
        'company': job.get('company', ''),
        'location': job.get('location', ''),
        'description': job.get('description', ''),
        'url': job.get('url', ''),
        'posted_date': job.get('posted_date', datetime.now().isoformat()),
        'salary': job.get('salary', ''),
        'job_type': job.get('job_type', ''),
        'remote': job.get('remote', False),
        'source': source,
        'retrieved_at': datetime.now().isoformat(),
        'raw_data': job
    }


def extract_skills_from_text(text: str, skill_keywords: List[str]) -> List[str]:
    """Extract mentioned skills from text."""
    text_lower = text.lower()
    found_skills = []

    for skill in skill_keywords:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: str) -> None:
    """Save data to JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def format_date(date_str: str) -> str:
    """Format date string to readable format."""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%B %d, %Y')
    except:
        return date_str


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'


def safe_get(dictionary: Dict, *keys, default=None):
    """Safely get nested dictionary value."""
    value = dictionary
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        if value is None:
            return default
    return value
