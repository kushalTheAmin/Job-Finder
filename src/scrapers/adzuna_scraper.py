"""Adzuna API job scraper."""

import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
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
        """Parse Adzuna API response and fetch full descriptions."""
        jobs = []

        # Track statistics
        stats = {'full_fetched': 0, 'fallback_used': 0, 'fetch_errors': 0}

        results = data.get('results', [])
        total_results = len(results)

        self.logger.debug(f"Processing {total_results} results from Adzuna API")

        for idx, result in enumerate(results, 1):
            title = result.get('title', '')
            company = result.get('company', {}).get('display_name', '')
            redirect_url = result.get('redirect_url', '')

            # API returns snippet (50-100 words), fetch full description from redirect_url
            snippet_description = self._clean_description(result.get('description', ''))
            full_description = self._fetch_full_description_from_redirect(redirect_url, title)

            # Use full description if available, otherwise fallback to snippet
            description = full_description if full_description else snippet_description

            if full_description:
                stats['full_fetched'] += 1
            else:
                snippet_words = len(snippet_description.split())
                self.logger.warning(f"Using snippet ({snippet_words} words) for: {title}")
                stats['fallback_used'] += 1
                stats['fetch_errors'] += 1

            job = {
                'title': title,
                'company': company,
                'location': result.get('location', {}).get('display_name', ''),
                'description': description,
                'url': redirect_url,
                'posted_date': result.get('created', ''),
                'salary': self._format_salary(result),
                'job_type': result.get('contract_time', ''),
                'remote': 'remote' in description.lower(),
            }

            if self._is_valid_job(job):
                jobs.append(job)

            # Rate limiting: delay between fetches to avoid blocking
            # Skip delay for last job
            if idx < total_results:
                time.sleep(1)

        # Log summary statistics
        total_attempts = stats['full_fetched'] + stats['fallback_used']
        success_rate = (stats['full_fetched'] / total_attempts * 100) if total_attempts > 0 else 0
        self.logger.info(f"📊 Adzuna Summary: {stats['full_fetched']}/{total_attempts} full descriptions ({success_rate:.1f}% success)")
        self.logger.info(f"   ✓ Full fetched: {stats['full_fetched']}")
        self.logger.info(f"   ⚠️ Fallback used: {stats['fallback_used']}")
        self.logger.info(f"   ✗ Fetch errors: {stats['fetch_errors']}")

        return jobs

    def _fetch_full_description_from_redirect(self, redirect_url: str, job_title: str) -> str:
        """
        Fetch full job description from Adzuna redirect URL.

        The API only returns snippets (~50-100 words), but the redirect_url
        contains the full job posting.
        """
        if not redirect_url:
            return ""

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            self.logger.debug(f"Fetching full description from: {redirect_url[:80]}...")

            response = requests.get(redirect_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple selectors for job description
            # Adzuna pages may have different structures depending on the source
            description = None

            # Try common job description selectors
            selectors = [
                ('div', {'class': 'job-description'}),
                ('section', {'class': 'job-details'}),
                ('div', {'id': 'job-description'}),
                ('div', {'class': 'description'}),
                ('article', {'class': 'job-content'}),
            ]

            for tag, attrs in selectors:
                desc_elem = soup.find(tag, attrs)
                if desc_elem:
                    description = desc_elem.get_text(separator='\n', strip=True)
                    if len(description) > 100:  # Ensure we got substantial content
                        break

            # Fallback: look for any large text block if specific selectors fail
            if not description or len(description) < 100:
                # Find all paragraphs and concatenate
                paragraphs = soup.find_all('p')
                description = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)

            if description and len(description) > 100:
                word_count = len(description.split())
                self.logger.info(f"✓ Got full description ({word_count} words) for: {job_title}")
                return self._clean_description(description)
            else:
                self.logger.warning(f"✗ Could not extract full description from redirect for: {job_title}")
                return ""

        except Exception as e:
            self.logger.warning(f"✗ Error fetching redirect URL for {job_title}: {str(e)}")
            return ""

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
