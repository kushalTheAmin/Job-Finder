"""LinkedIn job scraper using web scraping."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import re
from . import BaseScraper


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn job listings."""

    BASE_URL = "https://www.linkedin.com/jobs/search"

    def __init__(self, config: Any):
        """Initialize LinkedIn scraper."""
        super().__init__(config)
        self.delay = config.get('sources', 'scraping', 'delay_between_requests', default=2)
        self.max_pages = config.get('sources', 'scraping', 'max_pages', default=3)
        self.cookies = self._load_cookies(config)

    def _load_cookies(self, config) -> dict:
        """
        Load LinkedIn cookies from config for authentication.

        Returns:
            dict: Cookie dictionary for requests
        """
        try:
            linkedin_cookies = config.get('sources', 'scraping', 'linkedin_cookies', default={})

            if not linkedin_cookies or not linkedin_cookies.get('li_at'):
                self.logger.warning("⚠️ LinkedIn cookies not configured - expect lower success rate (~20-40%)")
                self.logger.info("   To improve: Add cookies from browser to config.yaml (see docs)")
                return {}

            # Build cookie dict
            cookies = {}
            if linkedin_cookies.get('li_at'):
                cookies['li_at'] = linkedin_cookies['li_at']
            if linkedin_cookies.get('JSESSIONID'):
                cookies['JSESSIONID'] = linkedin_cookies['JSESSIONID']
            if linkedin_cookies.get('bcookie'):
                cookies['bcookie'] = linkedin_cookies['bcookie']

            self.logger.info(f"✓ Loaded {len(cookies)} LinkedIn authentication cookie(s)")
            return cookies

        except Exception as e:
            self.logger.warning(f"Error loading LinkedIn cookies: {str(e)}")
            return {}

    def search(self, title: str, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for jobs on LinkedIn."""
        try:
            jobs = []

            # Build search parameters
            params = {
                'keywords': title,
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'position': 1,
                'pageNum': 0
            }

            # Set headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }

            self.logger.info(f"Searching LinkedIn for '{title}' in '{location}'")

            # Scrape multiple pages
            for page in range(self.max_pages):
                params['start'] = page * 25

                try:
                    response = requests.get(
                        self.BASE_URL,
                        params=params,
                        headers=headers,
                        cookies=self.cookies,
                        timeout=30
                    )
                    response.raise_for_status()

                    page_jobs = self._parse_page(response.text)
                    jobs.extend(page_jobs)

                    # Respect rate limiting
                    if page < self.max_pages - 1:
                        time.sleep(self.delay)

                except Exception as e:
                    self.logger.error(f"Error scraping LinkedIn page {page}: {str(e)}")
                    break

            # Log summary statistics
            if hasattr(self, 'stats'):
                total_attempts = self.stats['full_fetched'] + self.stats['fallback_used']
                total_kept = self.stats['kept_high_quality'] + self.stats['kept_good'] + self.stats['kept_acceptable']
                total_processed = total_kept + self.stats['skipped_quality']

                success_rate = (self.stats['full_fetched'] / total_attempts * 100) if total_attempts > 0 else 0
                retention_rate = (total_kept / total_processed * 100) if total_processed > 0 else 0

                self.logger.info(f"\n📊 LinkedIn Quality Summary:")
                self.logger.info(f"   Jobs processed: {total_processed}")
                self.logger.info(f"   ✓ Kept (high quality): {total_kept} ({retention_rate:.1f}%)")
                self.logger.info(f"   ⊘ Skipped (low quality): {self.stats['skipped_quality']} ({100-retention_rate:.1f}%)")
                self.logger.info(f"")
                self.logger.info(f"   Quality Breakdown:")
                self.logger.info(f"     ⭐ Excellent (7+ score): {self.stats['kept_high_quality']} jobs")
                self.logger.info(f"     ✓ Good (5-6 score): {self.stats['kept_good']} jobs")
                self.logger.info(f"     ~ Acceptable (3-4 score): {self.stats['kept_acceptable']} jobs")
                self.logger.info(f"")
                self.logger.info(f"   Fetch Statistics:")
                self.logger.info(f"     ✓ Full descriptions fetched: {self.stats['full_fetched']}/{total_attempts} ({success_rate:.1f}%)")
                self.logger.info(f"     🔒 Auth blocked: {self.stats['auth_blocked']}")
                self.logger.info(f"     ✗ Fetch errors: {self.stats['fetch_errors']}")
                self.logger.info(f"\n   Final result: {len(jobs)} high-quality jobs returned")
            else:
                self.logger.info(f"Found {len(jobs)} jobs from LinkedIn")

            return jobs

        except Exception as e:
            self.logger.error(f"Unexpected error in LinkedIn scraper: {str(e)}")
            return []

    def _parse_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse LinkedIn search results page."""
        jobs = []
        soup = BeautifulSoup(html, 'html.parser')

        # Find job cards
        job_cards = soup.find_all('div', class_='base-card')

        # Track statistics
        if not hasattr(self, 'stats'):
            self.stats = {
                'full_fetched': 0,
                'fallback_used': 0,
                'auth_blocked': 0,
                'fetch_errors': 0,
                'skipped_quality': 0,
                'kept_high_quality': 0,
                'kept_good': 0,
                'kept_acceptable': 0
            }

        self.logger.debug(f"Found {len(job_cards)} job cards on page")

        for card in job_cards:
            try:
                job = self._parse_job_card(card)
                if job and self._is_valid_job(job):
                    jobs.append(job)
            except Exception as e:
                self.logger.debug(f"Error parsing job card: {str(e)}")
                continue

        return jobs

    def _parse_job_card(self, card) -> Dict[str, Any]:
        """Parse individual job card."""
        # Extract title
        title_elem = card.find('h3', class_='base-search-card__title')
        title = title_elem.text.strip() if title_elem else ''

        # Extract company
        company_elem = card.find('h4', class_='base-search-card__subtitle')
        company = company_elem.text.strip() if company_elem else ''

        # Extract location
        location_elem = card.find('span', class_='job-search-card__location')
        location = location_elem.text.strip() if location_elem else ''

        # Extract URL
        link_elem = card.find('a', class_='base-card__full-link')
        url = link_elem.get('href', '') if link_elem else ''

        # Extract posted date
        date_elem = card.find('time')
        posted_date = date_elem.get('datetime', '') if date_elem else ''

        # Default description (fallback)
        description = f"LinkedIn job posting for {title} at {company}"

        # Fetch full job description from job page
        if url:
            self.logger.debug(f"Fetching full description for: {title} at {company}")
            try:
                details = self.get_job_details(url)
                if details.get('description'):
                    description = details['description']
                    word_count = len(description.split())
                    self.logger.info(f"✓ Got full description ({word_count} words) for: {title}")
                    self.stats['full_fetched'] += 1
                elif details.get('auth_required'):
                    self.logger.warning(f"✗ Auth required for: {title}, using placeholder")
                    self.stats['auth_blocked'] += 1
                    self.stats['fallback_used'] += 1
                else:
                    self.logger.warning(f"✗ Could not fetch full description for: {title}, using placeholder")
                    self.stats['fetch_errors'] += 1
                    self.stats['fallback_used'] += 1

                # Rate limiting: delay between detail fetches to avoid blocking
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"✗ Error fetching description for {title}: {str(e)}, using placeholder")
                self.stats['fetch_errors'] += 1
                self.stats['fallback_used'] += 1

        # Validate description quality - skip jobs that don't meet threshold
        quality_score, word_count, sections = self._validate_description_quality(description)

        if quality_score < 3:
            # Skip this job due to poor quality
            skip_reason = self._get_skip_reason(word_count, sections, quality_score)
            self.logger.warning(f"⊘ Skipping low-quality job - {skip_reason}: {title}")
            self.stats['skipped_quality'] += 1
            return None

        # Track quality tier for kept jobs
        if quality_score >= 7:
            self.stats['kept_high_quality'] += 1
            quality_tier = "excellent"
        elif quality_score >= 5:
            self.stats['kept_good'] += 1
            quality_tier = "good"
        else:
            self.stats['kept_acceptable'] += 1
            quality_tier = "acceptable"

        self.logger.info(f"✓ Kept job ({quality_tier}, quality {quality_score}/10, {word_count} words, {sections} sections): {title}")

        # Create job object
        job = {
            'title': title,
            'company': company,
            'location': location,
            'description': description,
            'url': url,
            'posted_date': posted_date,
            'salary': '',
            'job_type': 'Full-time',
            'remote': 'remote' in location.lower(),
        }

        return job

    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        Get detailed job description from job URL.
        Note: LinkedIn often requires authentication - success rate may be 20-40%.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.linkedin.com/jobs/search',
            }

            response = requests.get(job_url, headers=headers, cookies=self.cookies, timeout=30)
            response.raise_for_status()

            # Check if we got redirected to login/authwall page
            if 'authwall' in response.url or 'login' in response.url or '/uas/login' in response.url:
                self.logger.warning("LinkedIn requires authentication for this job (authwall detected)")
                return {'auth_required': True}

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple selectors (LinkedIn changes these frequently)
            description = None
            selectors = [
                ('div', {'class': 'show-more-less-html__markup'}),
                ('div', {'class': 'description__text'}),
                ('section', {'class': 'description'}),
                ('div', {'class': 'jobs-description'}),
                ('div', {'class': 'jobs-description__content'}),
                ('article', {'class': 'jobs-description__container'}),
            ]

            for tag, attrs in selectors:
                desc_elem = soup.find(tag, attrs)
                if desc_elem:
                    description = desc_elem.get_text(separator='\n', strip=True)
                    if len(description) > 100:  # Ensure we got real content, not just headers
                        self.logger.debug(f"Found description using selector: {tag}.{attrs}")
                        break

            # Fallback: Find largest text block if selectors fail
            if not description or len(description) < 100:
                self.logger.debug("Selectors failed, trying fallback: largest text block")
                all_divs = soup.find_all('div')
                texts = [(div.get_text(separator='\n', strip=True), div) for div in all_divs]
                texts.sort(key=lambda x: len(x[0]), reverse=True)

                # Get the largest text block that looks like a job description (> 200 chars)
                for text, div in texts[:5]:  # Check top 5 largest
                    if len(text) > 200 and 'responsibilities' in text.lower() or 'requirements' in text.lower() or 'experience' in text.lower():
                        description = text
                        self.logger.debug(f"Found description using fallback ({len(text)} chars)")
                        break

            if description and len(description) > 100:
                return {'description': self._clean_description(description)}
            else:
                self.logger.warning("Could not extract job description (no content found)")
                return {}

        except Exception as e:
            self.logger.warning(f"Could not get job details: {str(e)}")
            return {}
