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

        # Track statistics
        stats = {
            'details_fetched': 0,
            'search_used': 0,
            'details_better': 0,
            'fetch_errors': 0,
            'skipped_quality': 0,
            'kept_high_quality': 0,
            'kept_good': 0,
            'kept_acceptable': 0
        }

        results = data.get('data', [])
        total_results = len(results)

        self.logger.debug(f"Processing {total_results} results from JSearch API")

        for idx, result in enumerate(results, 1):
            title = result.get('job_title', '')
            job_id = result.get('job_id', '')

            # Get description from search endpoint
            search_description = self._clean_description(result.get('job_description', ''))

            # Try to fetch fuller description from job-details endpoint
            full_description = self._fetch_job_details(job_id, title) if job_id else ""

            # Quality-based selection: choose description with better quality score
            search_quality_score, search_words, search_sections = self._validate_description_quality(search_description)
            full_quality_score, full_words, full_sections = self._validate_description_quality(full_description) if full_description else (0, 0, 0)

            # Use the higher quality description
            if full_quality_score > search_quality_score:
                description = full_description
                stats['details_fetched'] += 1
                stats['details_better'] += 1
                self.logger.debug(f"Using details endpoint (better quality: {full_quality_score} vs {search_quality_score}): {title}")
            elif search_quality_score >= 3:
                description = search_description
                stats['search_used'] += 1
                self.logger.debug(f"Using search description (quality: {search_quality_score}): {title}")
            elif full_quality_score >= 3:
                description = full_description
                stats['details_fetched'] += 1
                self.logger.debug(f"Using details endpoint (only source meeting quality): {title}")
            else:
                # Neither meets quality threshold - skip job
                self.logger.warning(f"⊘ Skipping job - both sources below quality threshold (details: {full_quality_score}, search: {search_quality_score}): {title}")
                stats['skipped_quality'] += 1
                continue

            # Validate final description quality
            quality_score, word_count, sections = self._validate_description_quality(description)

            # Track quality tier for kept jobs
            if quality_score >= 7:
                stats['kept_high_quality'] += 1
                quality_tier = "excellent"
            elif quality_score >= 5:
                stats['kept_good'] += 1
                quality_tier = "good"
            else:
                stats['kept_acceptable'] += 1
                quality_tier = "acceptable"

            self.logger.info(f"✓ Kept job ({quality_tier}, quality {quality_score}/10, {word_count} words, {sections} sections): {title}")

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

        # Log summary statistics
        total_attempts = stats['details_fetched'] + stats['search_used']
        total_kept = stats['kept_high_quality'] + stats['kept_good'] + stats['kept_acceptable']
        total_processed = total_kept + stats['skipped_quality']

        success_rate = (stats['details_fetched'] / total_attempts * 100) if total_attempts > 0 else 0
        retention_rate = (total_kept / total_processed * 100) if total_processed > 0 else 0

        self.logger.info(f"\n📊 JSearch Quality Summary:")
        self.logger.info(f"   Jobs processed: {total_processed}")
        self.logger.info(f"   ✓ Kept (high quality): {total_kept} ({retention_rate:.1f}%)")
        self.logger.info(f"   ⊘ Skipped (low quality): {stats['skipped_quality']} ({100-retention_rate:.1f}%)")
        self.logger.info(f"")
        self.logger.info(f"   Quality Breakdown:")
        self.logger.info(f"     ⭐ Excellent (7+ score): {stats['kept_high_quality']} jobs")
        self.logger.info(f"     ✓ Good (5-6 score): {stats['kept_good']} jobs")
        self.logger.info(f"     ~ Acceptable (3-4 score): {stats['kept_acceptable']} jobs")
        self.logger.info(f"")
        self.logger.info(f"   Source Statistics:")
        self.logger.info(f"     ✓ Details endpoint used: {stats['details_fetched']}/{total_attempts} ({success_rate:.1f}%)")
        self.logger.info(f"     📈 Details had better quality: {stats['details_better']}")
        self.logger.info(f"     🔍 Search endpoint used: {stats['search_used']}")
        self.logger.info(f"\n   Final result: {len(jobs)} high-quality jobs returned")

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
