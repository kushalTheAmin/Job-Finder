"""Job scrapers package."""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all job scrapers."""

    def __init__(self, config: Any):
        """Initialize scraper with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def search(self, title: str, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for jobs. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement search method")

    def _clean_description(self, description: str) -> str:
        """Clean and normalize job description."""
        if not description:
            return ""

        # Remove excessive whitespace
        description = " ".join(description.split())

        return description

    def _is_valid_job(self, job: Dict[str, Any]) -> bool:
        """Validate job data."""
        required_fields = ['title', 'company', 'description']
        return all(job.get(field) for field in required_fields)
