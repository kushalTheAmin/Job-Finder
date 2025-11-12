"""Adzuna API job scraper."""

import requests
from typing import List, Dict, Any
from . import BaseScraper


class AdzunaScraper(BaseScraper):
    """Scraper for Adzuna API."""

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(self, config: Any):
        """Initialize Adzuna scraper."""
        super().__init__(config)
        self.app_id = config.get('sources', 'adzuna', 'app_id')
        self.app_key = config.get('sources', 'adzuna', 'app_key')

        if not self.app_id or not self.app_key:
            self.logger.warning("Adzuna API credentials not configured")

    def search(self, title: str, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for jobs using Adzuna API."""
        if not self.app_id or not self.app_key:
            self.logger.warning("Adzuna API credentials missing, skipping")
            return []

        try:
            # Parse location to get country code (default to US)
            country = self._parse_country(location)

            # Build API URL
            url = f"{self.BASE_URL}/{country}/search/1"

            # Build query parameters
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'what': title,
                'where': location,
                'results_per_page': 50,
                'content-type': 'application/json'
            }

            # Add optional parameters
            if kwargs.get('max_days_old'):
                params['max_days_old'] = kwargs['max_days_old']

            self.logger.info(f"Searching Adzuna for '{title}' in '{location}'")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            jobs = self._parse_response(data)

            self.logger.info(f"Found {len(jobs)} jobs from Adzuna")
            return jobs

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Adzuna API error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in Adzuna scraper: {str(e)}")
            return []

    def _parse_country(self, location: str) -> str:
        """Parse country code from location string."""
        location_lower = location.lower()

        # Map common locations to country codes
        if 'uk' in location_lower or 'united kingdom' in location_lower:
            return 'gb'
        elif 'canada' in location_lower:
            return 'ca'
        elif 'australia' in location_lower:
            return 'au'
        else:
            return 'us'  # Default to US

    def _parse_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Adzuna API response."""
        jobs = []

        for result in data.get('results', []):
            job = {
                'title': result.get('title', ''),
                'company': result.get('company', {}).get('display_name', ''),
                'location': result.get('location', {}).get('display_name', ''),
                'description': self._clean_description(result.get('description', '')),
                'url': result.get('redirect_url', ''),
                'posted_date': result.get('created', ''),
                'salary': self._format_salary(result),
                'job_type': result.get('contract_time', ''),
                'remote': 'remote' in result.get('description', '').lower(),
            }

            if self._is_valid_job(job):
                jobs.append(job)

        return jobs

    def _format_salary(self, result: Dict[str, Any]) -> str:
        """Format salary information."""
        salary_min = result.get('salary_min')
        salary_max = result.get('salary_max')

        if salary_min and salary_max:
            return f"${salary_min:,.0f} - ${salary_max:,.0f}"
        elif salary_min:
            return f"${salary_min:,.0f}+"
        elif salary_max:
            return f"Up to ${salary_max:,.0f}"
        else:
            return ""
