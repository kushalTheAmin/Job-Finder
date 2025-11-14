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

    def _validate_description_quality(self, description: str) -> tuple:
        """
        Validate job description quality.

        Returns:
            tuple: (quality_score, word_count, sections_found)
                - quality_score: 0-10 (3+ to keep, <3 to skip)
                - word_count: number of words
                - sections_found: number of key sections detected
        """
        if not description:
            return 0, 0, 0

        score = 0
        word_count = len(description.split())

        # Word count scoring (max 3 points)
        if word_count >= 300:
            score += 3
        elif word_count >= 200:
            score += 2
        elif word_count >= 150:
            score += 1

        # Section detection - look for key job description sections
        quality_keywords = {
            'responsibilities': ['responsibilities', 'duties', 'you will', 'role includes', 'day to day', 'what you\'ll do'],
            'requirements': ['requirements', 'qualifications', 'required', 'must have', 'you have', 'you should have'],
            'experience': ['experience', 'years', 'background', 'proven track record'],
            'skills': ['skills', 'proficiency', 'knowledge of', 'familiar with', 'expertise in'],
            'benefits': ['benefits', 'we offer', 'compensation', 'salary', 'perks', 'package'],
            'about': ['about us', 'about the company', 'our team', 'who we are', 'our mission']
        }

        sections_found = 0
        desc_lower = description.lower()
        for section, keywords in quality_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                sections_found += 1

        # Section scoring (1 point per section, max 4 points)
        score += min(sections_found, 4)

        self.logger.debug(f"Quality validation: {word_count} words, {sections_found} sections, score {score}/10")

        return score, word_count, sections_found

    def _get_skip_reason(self, word_count: int, sections: int, quality_score: int) -> str:
        """
        Get human-readable reason for skipping a job.

        Args:
            word_count: Number of words in description
            sections: Number of key sections found
            quality_score: Overall quality score (0-10)

        Returns:
            String describing why job was skipped
        """
        reasons = []

        if word_count < 150:
            reasons.append(f"too short ({word_count} words)")
        elif word_count < 200:
            reasons.append(f"insufficient words ({word_count} < 200)")

        if sections < 2:
            reasons.append(f"missing sections ({sections} found, need 2+)")

        if quality_score < 3:
            reasons.append(f"low quality score ({quality_score}/10)")

        return ", ".join(reasons) if reasons else "quality threshold not met"
