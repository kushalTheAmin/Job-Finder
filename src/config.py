"""Configuration loader for Job Finder application."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration from YAML file and environment variables."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment variables
        self._apply_env_overrides(config)
        return config

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Override configuration with environment variables."""
        # Google Cloud
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            config['google_cloud']['project_id'] = os.getenv('GOOGLE_CLOUD_PROJECT')

        # Adzuna
        if os.getenv('ADZUNA_APP_ID'):
            config['sources']['adzuna']['app_id'] = os.getenv('ADZUNA_APP_ID')
        if os.getenv('ADZUNA_APP_KEY'):
            config['sources']['adzuna']['app_key'] = os.getenv('ADZUNA_APP_KEY')

        # JSearch
        if os.getenv('JSEARCH_API_KEY'):
            config['sources']['jsearch']['api_key'] = os.getenv('JSEARCH_API_KEY')

        # Email
        if os.getenv('GMAIL_USER'):
            config['notifications']['email_to'] = os.getenv('GMAIL_USER')

        # Google Drive
        if os.getenv('GOOGLE_DRIVE_FOLDER_ID'):
            config['notifications']['google_drive_folder_id'] = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

    def _validate_config(self) -> None:
        """Validate required configuration fields."""
        required_fields = [
            ('job_search', 'default_titles'),
            ('job_search', 'default_locations'),
            ('matching', 'min_match_percentage'),
            ('matching', 'max_jobs_per_day'),
            ('resume', 'master_resume_path'),
            ('google_cloud', 'project_id'),
        ]

        for *path, field in required_fields:
            config_section = self.config
            for key in path:
                config_section = config_section.get(key, {})
            if not config_section.get(field):
                raise ValueError(f"Missing required configuration: {'.'.join(path)}.{field}")

    @property
    def job_titles(self) -> List[str]:
        """Get job titles to search for."""
        return self.config['job_search']['default_titles']

    @property
    def locations(self) -> List[str]:
        """Get locations to search in."""
        return self.config['job_search']['default_locations']

    @property
    def experience_level(self) -> str:
        """Get experience level."""
        return self.config['job_search'].get('experience_level', 'Senior')

    @property
    def job_types(self) -> List[str]:
        """Get job types."""
        return self.config['job_search'].get('job_types', ['Full-time'])

    @property
    def remote_ok(self) -> bool:
        """Check if remote jobs are acceptable."""
        return self.config['job_search'].get('remote_ok', True)

    @property
    def required_skills(self) -> List[str]:
        """Get required skills."""
        return self.config['job_search'].get('required_skills', [])

    @property
    def preferred_skills(self) -> List[str]:
        """Get preferred skills."""
        return self.config['job_search'].get('preferred_skills', [])

    @property
    def min_match_percentage(self) -> int:
        """Get minimum match percentage."""
        return self.config['matching']['min_match_percentage']

    @property
    def max_jobs_per_day(self) -> int:
        """Get maximum jobs per day."""
        return self.config['matching']['max_jobs_per_day']

    @property
    def master_resume_path(self) -> str:
        """Get master resume path."""
        return self.config['resume']['master_resume_path']

    @property
    def output_format(self) -> str:
        """Get output format for resumes."""
        return self.config['resume'].get('output_format', 'pdf')

    @property
    def customize_sections(self) -> List[str]:
        """Get sections to customize in resume."""
        return self.config['resume'].get('customize_sections', ['summary', 'skills', 'experience'])

    @property
    def email_to(self) -> str:
        """Get recipient email address."""
        return self.config['notifications']['email_to']

    @property
    def send_email(self) -> bool:
        """Check if email notifications are enabled."""
        return self.config['notifications'].get('send_email', True)

    @property
    def upload_to_drive(self) -> bool:
        """Check if Google Drive upload is enabled."""
        return self.config['notifications'].get('upload_to_drive', True)

    @property
    def google_drive_folder_id(self) -> str:
        """Get Google Drive folder ID."""
        return self.config['notifications'].get('google_drive_folder_id', '')

    @property
    def enabled_sources(self) -> List[str]:
        """Get enabled job sources."""
        return self.config['sources'].get('enabled', [])

    @property
    def project_id(self) -> str:
        """Get Google Cloud project ID."""
        return self.config['google_cloud']['project_id']

    @property
    def vertex_location(self) -> str:
        """Get Vertex AI location."""
        return self.config['google_cloud']['vertex_ai']['location']

    @property
    def vertex_model(self) -> str:
        """Get Vertex AI model name."""
        return self.config['google_cloud']['vertex_ai']['model']

    @property
    def jobs_collection(self) -> str:
        """Get Firestore jobs collection name."""
        return self.config['google_cloud']['firestore']['jobs_collection']

    @property
    def history_collection(self) -> str:
        """Get Firestore history collection name."""
        return self.config['google_cloud']['firestore']['history_collection']

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.config['logging'].get('level', 'INFO')

    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.config['logging'].get('log_file', 'logs/job_finder.log')

    def get(self, *keys, default=None):
        """Get nested configuration value."""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value


# Global config instance
_config = None


def get_config(config_path: str = "config.yaml") -> Config:
    """Get or create global configuration instance."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
