"""Indeed job scraper using web scraping."""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import re
from urllib.parse import urljoin
from . import BaseScraper


class IndeedScraper(BaseScraper):
    """Scraper for Indeed job listings."""

    BASE_URL = "https://www.indeed.com/jobs"

    def __init__(self, config: Any):
        """Initialize Indeed scraper."""
        super().__init__(config)
        self.delay = config.get('sources', 'scraping', 'delay_between_requests', default=2)
        self.max_pages = config.get('sources', 'scraping', 'max_pages', default=3)

    def search(self, title: str, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for jobs on Indeed."""
        try:
            jobs = []

            # Build search parameters
            params = {
                'q': title,
                'l': location,
                'fromage': 7,  # Last 7 days
                'sort': 'date'
            }

            # Set headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            self.logger.info(f"Searching Indeed for '{title}' in '{location}'")

            # Scrape multiple pages
            for page in range(self.max_pages):
                params['start'] = page * 10

                try:
                    response = requests.get(
                        self.BASE_URL,
                        params=params,
                        headers=headers,
                        timeout=30
                    )
                    response.raise_for_status()

                    page_jobs = self._parse_page(response.text)
                    jobs.extend(page_jobs)

                    # Respect rate limiting
                    if page < self.max_pages - 1:
                        time.sleep(self.delay)

                except Exception as e:
                    self.logger.error(f"Error scraping Indeed page {page}: {str(e)}")
                    break

            self.logger.info(f"Found {len(jobs)} jobs from Indeed")
            return jobs

        except Exception as e:
            self.logger.error(f"Unexpected error in Indeed scraper: {str(e)}")
            return []

    def _parse_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse Indeed search results page."""
        jobs = []
        soup = BeautifulSoup(html, 'html.parser')

        # Find job cards (Indeed frequently changes their class names)
        # Try multiple selectors
        job_cards = (
            soup.find_all('div', class_=re.compile(r'job_seen_beacon')) or
            soup.find_all('div', class_=re.compile(r'resultContent')) or
            soup.find_all('td', class_='resultContent')
        )

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
        title_elem = card.find('h2', class_=re.compile(r'jobTitle'))
        if not title_elem:
            title_elem = card.find('a', class_=re.compile(r'jcs-JobTitle'))

        title = ''
        if title_elem:
            # Title might be in a nested span or the element itself
            title_span = title_elem.find('span')
            title = title_span.text.strip() if title_span else title_elem.text.strip()

        # Extract company
        company_elem = card.find('span', {'data-testid': 'company-name'})
        if not company_elem:
            company_elem = card.find('span', class_=re.compile(r'companyName'))
        company = company_elem.text.strip() if company_elem else ''

        # Extract location
        location_elem = card.find('div', {'data-testid': 'text-location'})
        if not location_elem:
            location_elem = card.find('div', class_=re.compile(r'companyLocation'))
        location = location_elem.text.strip() if location_elem else ''

        # Extract URL
        link_elem = title_elem.find('a') if title_elem else None
        if not link_elem:
            link_elem = card.find('a', class_=re.compile(r'jcs-JobTitle'))
        url = urljoin('https://www.indeed.com', link_elem.get('href', '')) if link_elem else ''

        # Extract salary
        salary_elem = card.find('div', class_=re.compile(r'salary-snippet'))
        salary = salary_elem.text.strip() if salary_elem else ''

        # Extract snippet/description (fallback)
        snippet_elem = card.find('div', class_=re.compile(r'job-snippet'))
        if not snippet_elem:
            snippet_elem = card.find('div', {'data-testid': 'job-snippet'})
        snippet_description = snippet_elem.text.strip() if snippet_elem else f"{title} position at {company}"

        # Extract job type
        metadata = card.find('div', class_=re.compile(r'metadata'))
        job_type = 'Full-time'
        if metadata and 'part-time' in metadata.text.lower():
            job_type = 'Part-time'
        elif metadata and 'contract' in metadata.text.lower():
            job_type = 'Contract'

        # Fetch full description from job page
        description = snippet_description
        if url:
            job_id = self._extract_job_id(url)
            if job_id:
                full_description = self._fetch_full_description(job_id, title)
                if full_description:
                    description = full_description
                else:
                    snippet_words = len(snippet_description.split())
                    self.logger.warning(f"Using snippet ({snippet_words} words) for: {title}")

        # Create job object
        job = {
            'title': title,
            'company': company,
            'location': location,
            'description': self._clean_description(description),
            'url': url,
            'posted_date': '',
            'salary': salary,
            'job_type': job_type,
            'remote': 'remote' in location.lower() or 'remote' in description.lower(),
        }

        return job

    def _extract_job_id(self, url: str) -> str:
        """Extract job ID from Indeed URL."""
        match = re.search(r'jk=([a-zA-Z0-9]+)', url)
        return match.group(1) if match else ""

    def _fetch_full_description(self, job_id: str, job_title: str) -> str:
        """
        Fetch full job description from Indeed viewjob page.

        Search results only show snippets (~20-50 words), but the viewjob
        endpoint contains the full job description.
        Note: Indeed has aggressive anti-scraping - success rate may be 30-50%.
        """
        if not job_id:
            return ""

        try:
            # Construct viewjob URL
            url = f"https://www.indeed.com/viewjob?viewtype=embedded&jk={job_id}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.indeed.com/jobs',
                'Connection': 'keep-alive',
            }

            self.logger.debug(f"Fetching full description for job ID: {job_id}")

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Check for blocking/captcha pages
            response_text = response.text.lower()
            if 'captcha' in response_text or 'blocked' in response_text or 'access denied' in response_text:
                self.logger.warning(f"✗ Indeed blocking detected for job {job_id} (captcha/blocked)")
                return ""

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try multiple selectors (Indeed changes these frequently)
            description = None
            selectors = [
                ('div', {'id': 'jobDescriptionText'}),
                ('div', {'class': re.compile(r'jobsearch-jobDescriptionText')}),
                ('div', {'class': re.compile(r'jobsearch-JobComponent-description')}),
                ('div', {'data-testid': 'jobDescriptionText'}),
                ('section', {'class': re.compile(r'jobDescriptionSection')}),
            ]

            for tag, attrs in selectors:
                if isinstance(attrs, dict) and 'id' in attrs:
                    desc_elem = soup.find(tag, attrs)
                elif isinstance(attrs, dict) and 'data-testid' in attrs:
                    desc_elem = soup.find(tag, attrs)
                else:
                    desc_elem = soup.find(tag, attrs)

                if desc_elem:
                    description = desc_elem.get_text(separator='\n', strip=True)
                    if len(description) > 100:
                        self.logger.debug(f"Found description using selector: {tag}")
                        break

            if description and len(description) > 100:
                word_count = len(description.split())
                self.logger.info(f"✓ Got full description ({word_count} words) for: {job_title}")

                # Rate limiting: delay after successful fetch
                time.sleep(1)

                return description
            else:
                self.logger.warning(f"✗ Could not extract description for: {job_title} (no content found)")
                return ""

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 or e.response.status_code == 429:
                self.logger.warning(f"✗ Indeed blocking/rate limiting for job {job_id} (HTTP {e.response.status_code})")
            else:
                self.logger.warning(f"✗ HTTP error fetching job {job_id}: {str(e)}")
            return ""
        except Exception as e:
            self.logger.warning(f"✗ Error fetching job {job_id}: {str(e)}")
            return ""
