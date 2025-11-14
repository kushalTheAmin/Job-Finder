"""Adzuna API job scraper."""

import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
import re
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
        stats = {
            'full_fetched': 0,
            'fallback_used': 0,
            'fetch_errors': 0,
            'skipped_quality': 0,
            'kept_high_quality': 0,
            'kept_good': 0,
            'kept_acceptable': 0
        }

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

            # Validate description quality - skip jobs that don't meet threshold
            quality_score, word_count, sections = self._validate_description_quality(description)

            if quality_score < 3:
                # Skip this job due to poor quality
                skip_reason = self._get_skip_reason(word_count, sections, quality_score)
                self.logger.warning(f"⊘ Skipping low-quality job - {skip_reason}: {title}")
                stats['skipped_quality'] += 1
                continue  # Skip to next result

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
        total_kept = stats['kept_high_quality'] + stats['kept_good'] + stats['kept_acceptable']
        total_processed = total_kept + stats['skipped_quality']

        success_rate = (stats['full_fetched'] / total_attempts * 100) if total_attempts > 0 else 0
        retention_rate = (total_kept / total_processed * 100) if total_processed > 0 else 0

        self.logger.info(f"\n📊 Adzuna Quality Summary:")
        self.logger.info(f"   Jobs processed: {total_processed}")
        self.logger.info(f"   ✓ Kept (high quality): {total_kept} ({retention_rate:.1f}%)")
        self.logger.info(f"   ⊘ Skipped (low quality): {stats['skipped_quality']} ({100-retention_rate:.1f}%)")
        self.logger.info(f"")
        self.logger.info(f"   Quality Breakdown:")
        self.logger.info(f"     ⭐ Excellent (7+ score): {stats['kept_high_quality']} jobs")
        self.logger.info(f"     ✓ Good (5-6 score): {stats['kept_good']} jobs")
        self.logger.info(f"     ~ Acceptable (3-4 score): {stats['kept_acceptable']} jobs")
        self.logger.info(f"")
        self.logger.info(f"   Fetch Statistics:")
        self.logger.info(f"     ✓ Full descriptions fetched: {stats['full_fetched']}/{total_attempts} ({success_rate:.1f}%)")
        self.logger.info(f"     ✗ Fetch errors: {stats['fetch_errors']}")
        self.logger.info(f"\n   Final result: {len(jobs)} high-quality jobs returned")

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

            # Get final URL after redirects and detect site type
            final_url = response.url
            site_type = self._detect_site_type(final_url)
            self.logger.debug(f"Redirect destination: {site_type} ({final_url[:60]}...)")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract using site-specific selectors (no generic fallback)
            description = self._extract_with_site_selectors(soup, site_type, final_url, job_title)

            if description and len(description) > 100:
                word_count = len(description.split())
                self.logger.info(f"✓ Got full description ({word_count} words, {site_type}) for: {job_title}")
                return self._clean_description(description)
            else:
                self.logger.warning(f"✗ Could not extract description from {site_type} site for: {job_title}")
                return ""

        except Exception as e:
            self.logger.warning(f"✗ Error fetching redirect URL for {job_title}: {str(e)}")
            return ""

    def _detect_site_type(self, url: str) -> str:
        """
        Detect job board type from URL.

        Args:
            url: The final URL after redirects

        Returns:
            Site type string: 'indeed', 'glassdoor', 'linkedin', 'lever',
                            'greenhouse', 'ziprecruiter', or 'generic'
        """
        url_lower = url.lower()

        if 'indeed.com' in url_lower:
            return 'indeed'
        elif 'glassdoor.com' in url_lower or 'glassdoor.co' in url_lower:
            return 'glassdoor'
        elif 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'lever.co' in url_lower or 'jobs.lever.co' in url_lower:
            return 'lever'
        elif 'greenhouse.io' in url_lower or 'boards.greenhouse.io' in url_lower:
            return 'greenhouse'
        elif 'ziprecruiter.com' in url_lower:
            return 'ziprecruiter'
        else:
            return 'generic'

    def _extract_with_site_selectors(self, soup, site_type: str, url: str, job_title: str) -> str:
        """
        Extract job description using site-specific selectors.

        Each job board has different HTML structure. This method tries
        selectors specific to each platform.

        Args:
            soup: BeautifulSoup object
            site_type: Detected site type
            url: Full URL for logging
            job_title: Job title for logging

        Returns:
            Extracted description or empty string if extraction fails
        """
        description = None

        # Get site-specific selectors
        if site_type == 'indeed':
            self.logger.debug(f"Using Indeed-specific selectors for: {job_title}")
            selectors = [
                ('div', {'id': 'jobDescriptionText'}),
                ('div', {'class': re.compile(r'jobsearch-jobDescriptionText')}),
                ('div', {'class': re.compile(r'jobsearch-JobComponent-description')}),
            ]
        elif site_type == 'glassdoor':
            self.logger.debug(f"Using Glassdoor-specific selectors for: {job_title}")
            selectors = [
                ('div', {'class': 'jobDescriptionContent'}),
                ('div', {'class': re.compile(r'JobDetails_jobDescription')}),
                ('div', {'id': 'JobDescriptionContainer'}),
            ]
        elif site_type == 'linkedin':
            self.logger.debug(f"Using LinkedIn-specific selectors for: {job_title}")
            selectors = [
                ('div', {'class': 'show-more-less-html__markup'}),
                ('div', {'class': 'description__text'}),
                ('section', {'class': 'description'}),
            ]
        elif site_type == 'lever':
            self.logger.debug(f"Using Lever-specific selectors for: {job_title}")
            selectors = [
                ('div', {'class': 'content'}),
                ('div', {'class': 'posting-description'}),
                ('div', {'class': 'section-wrapper'}),
            ]
        elif site_type == 'greenhouse':
            self.logger.debug(f"Using Greenhouse-specific selectors for: {job_title}")
            selectors = [
                ('div', {'id': 'content'}),
                ('div', {'class': 'application'}),
                ('div', {'class': 'job-post'}),
            ]
        elif site_type == 'ziprecruiter':
            self.logger.debug(f"Using ZipRecruiter-specific selectors for: {job_title}")
            selectors = [
                ('div', {'class': 'job-description'}),
                ('div', {'class': 'jobDescriptionSection'}),
            ]
        else:  # generic
            self.logger.debug(f"Using generic selectors for: {job_title}")
            selectors = [
                ('div', {'class': 'job-description'}),
                ('section', {'class': 'job-details'}),
                ('div', {'id': 'job-description'}),
                ('div', {'class': 'description'}),
                ('article', {'class': 'job-content'}),
            ]

        # Try selectors
        for tag, attrs in selectors:
            desc_elem = soup.find(tag, attrs)
            if desc_elem:
                description = desc_elem.get_text(separator='\n', strip=True)
                if len(description) > 100:
                    selector_name = f"{tag}.{attrs.get('class', attrs.get('id', 'unknown'))}"
                    self.logger.debug(f"Found description using {site_type} selector: {selector_name}")
                    break

        # NO fallback - if site-specific selectors fail, return empty
        if not description or len(description) < 100:
            self.logger.warning(f"⊘ No matching {site_type} selectors found for: {job_title}")
            return ""

        return description

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
