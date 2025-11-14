"""JSearch (RapidAPI) job scraper."""

import requests
import time
from typing import List, Dict, Any
from . import BaseScraper


class JSearchScraper(BaseScraper):
    """Scraper for JSearch API via RapidAPI."""

    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def __init__(self, config: Any):
        """Initialize JSearch scraper."""
        super().__init__(config)
        self.api_key = config.get('sources', 'jsearch', 'api_key')
        self.has_details_endpoint = None  # Will verify on first use

        if not self.api_key:
            self.logger.warning("JSearch API key not configured")
        else:
            # Verify endpoint availability on initialization
            self._verify_details_endpoint()

    def search(self, title: str, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for jobs using JSearch API."""
        if not self.api_key:
            self.logger.warning("JSearch API key missing, skipping")
            return []

        try:
            # Build query
            query = f"{title} in {location}"

            # Build headers
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            }

            # Build parameters
            params = {
                'query': query,
                'page': '1',
                'num_pages': '1',
                'date_posted': 'week'  # Recent jobs
            }

            # Add optional filters
            if kwargs.get('employment_types'):
                params['employment_types'] = kwargs['employment_types']

            self.logger.info(f"Searching JSearch for '{title}' in '{location}'")
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            jobs = self._parse_response(data)

            self.logger.info(f"Found {len(jobs)} jobs from JSearch")
            return jobs

        except requests.exceptions.RequestException as e:
            self.logger.error(f"JSearch API error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error in JSearch scraper: {str(e)}")
            return []

    def _parse_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse JSearch API response and fetch full job details."""
        jobs = []

        results = data.get('data', [])
        total_results = len(results)

        for idx, result in enumerate(results, 1):
            title = result.get('job_title', '')
            job_id = result.get('job_id', '')

            # Get description from search endpoint
            search_description = self._clean_description(result.get('job_description', ''))

            # Try to fetch fuller description from job-details endpoint
            full_description = self._fetch_job_details(job_id, title) if job_id else ""

            # Use the longer/better description
            description = full_description if full_description else search_description

            # Log which source we used
            if full_description:
                full_words = len(full_description.split())
                search_words = len(search_description.split())
                if full_words > search_words:
                    self.logger.info(f"✓ Details endpoint has more content ({full_words} vs {search_words} words) for: {title}")
                else:
                    self.logger.debug(f"Details endpoint similar length for: {title}")
            else:
                search_words = len(search_description.split())
                self.logger.warning(f"Using search description ({search_words} words) for: {title}")

            job = {
                'title': title,
                'company': result.get('employer_name', ''),
                'location': self._format_location(result),
                'description': description,
                'url': result.get('job_apply_link', ''),
                'posted_date': result.get('job_posted_at_datetime_utc', ''),
                'salary': self._format_salary(result),
                'job_type': result.get('job_employment_type', ''),
                'remote': result.get('job_is_remote', False),
            }

            if self._is_valid_job(job):
                jobs.append(job)

            # Rate limiting: delay between API calls
            # Skip delay for last job
            if idx < total_results:
                time.sleep(0.5)

        return jobs

    def _verify_details_endpoint(self):
        """
        Verify if JSearch /job-details endpoint exists and is accessible.

        Sets self.has_details_endpoint to True/False based on availability.
        If endpoint doesn't exist or returns errors, we'll use search descriptions only.
        """
        if not self.api_key:
            self.has_details_endpoint = False
            return

        try:
            url = "https://jsearch.p.rapidapi.com/job-details"
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            }
            # Use a test job_id - endpoint should return 400 (bad job_id) not 404 (not found)
            params = {'job_id': 'test_verification'}

            self.logger.debug("Verifying JSearch /job-details endpoint availability...")

            response = requests.get(url, headers=headers, params=params, timeout=10)

            # 404 = endpoint doesn't exist
            # 400 = endpoint exists but bad job_id (expected)
            # 200 = endpoint exists and working
            if response.status_code == 404:
                self.has_details_endpoint = False
                self.logger.warning("⚠️ JSearch /job-details endpoint NOT available (404) - will use search descriptions only")
            elif response.status_code in [400, 200]:
                self.has_details_endpoint = True
                self.logger.info("✓ JSearch /job-details endpoint available")
            else:
                # Other errors - assume endpoint might not be available
                self.has_details_endpoint = False
                self.logger.warning(f"⚠️ JSearch /job-details endpoint verification unclear (HTTP {response.status_code}) - will use search descriptions only")

        except Exception as e:
            self.has_details_endpoint = False
            self.logger.warning(f"⚠️ Could not verify JSearch /job-details endpoint: {str(e)} - will use search descriptions only")

    def _fetch_job_details(self, job_id: str, job_title: str) -> str:
        """
        Fetch full job details from JSearch /job-details endpoint.

        The search endpoint may return shorter descriptions, while the
        job-details endpoint provides complete job postings.
        Note: Endpoint availability verified at initialization.
        """
        if not job_id or not self.api_key:
            return ""

        # Skip if endpoint not available
        if self.has_details_endpoint is False:
            return ""

        try:
            url = "https://jsearch.p.rapidapi.com/job-details"
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            }
            params = {'job_id': job_id}

            self.logger.debug(f"Fetching details for job ID: {job_id}")

            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            details = data.get('data', [])

            if details and len(details) > 0:
                detail = details[0]
                description = detail.get('job_description', '')
                if description:
                    return self._clean_description(description)

            return ""

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Endpoint doesn't exist, mark it for future calls
                self.has_details_endpoint = False
                self.logger.warning(f"⚠️ JSearch /job-details endpoint not found (404) - disabling for future calls")
            else:
                self.logger.warning(f"✗ HTTP error fetching details for {job_title}: {str(e)}")
            return ""
        except Exception as e:
            self.logger.warning(f"✗ Could not fetch details for {job_title}: {str(e)}")
            return ""

    def _format_location(self, result: Dict[str, Any]) -> str:
        """Format location information."""
        city = result.get('job_city', '')
        state = result.get('job_state', '')
        country = result.get('job_country', '')

        parts = [p for p in [city, state, country] if p]
        return ', '.join(parts) if parts else 'Not specified'

    def _format_salary(self, result: Dict[str, Any]) -> str:
        """Format salary information."""
        salary_min = result.get('job_min_salary')
        salary_max = result.get('job_max_salary')

        if salary_min and salary_max:
            return f"${salary_min:,.0f} - ${salary_max:,.0f}"
        elif salary_min:
            return f"${salary_min:,.0f}+"
        elif salary_max:
            return f"Up to ${salary_max:,.0f}"
        else:
            return ""
