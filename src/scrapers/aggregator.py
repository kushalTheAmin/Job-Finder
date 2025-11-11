"""Job aggregator to combine results from all scrapers."""

from typing import List, Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .adzuna_scraper import AdzunaScraper
from .jsearch_scraper import JSearchScraper
from .linkedin_scraper import LinkedInScraper
from .indeed_scraper import IndeedScraper
from ..utils import normalize_job_data, generate_job_id


logger = logging.getLogger(__name__)


class JobAggregator:
    """Aggregates jobs from multiple sources."""

    def __init__(self, config: Any):
        """Initialize job aggregator."""
        self.config = config
        self.enabled_sources = config.enabled_sources

        # Initialize scrapers
        self.scrapers = {}
        if 'adzuna' in self.enabled_sources:
            self.scrapers['adzuna'] = AdzunaScraper(config)
        if 'jsearch' in self.enabled_sources:
            self.scrapers['jsearch'] = JSearchScraper(config)
        if 'linkedin' in self.enabled_sources:
            self.scrapers['linkedin'] = LinkedInScraper(config)
        if 'indeed' in self.enabled_sources:
            self.scrapers['indeed'] = IndeedScraper(config)

        logger.info(f"Initialized {len(self.scrapers)} job scrapers")

    def search_all(self, titles: List[str], locations: List[str]) -> List[Dict[str, Any]]:
        """Search all enabled sources for jobs."""
        all_jobs = []
        seen_ids = set()

        # Search for each title-location combination
        for title in titles:
            for location in locations:
                logger.info(f"Searching for '{title}' in '{location}'")

                # Search all sources concurrently
                with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
                    # Submit all search tasks
                    future_to_source = {
                        executor.submit(scraper.search, title, location): source
                        for source, scraper in self.scrapers.items()
                    }

                    # Collect results as they complete
                    for future in as_completed(future_to_source):
                        source = future_to_source[future]
                        try:
                            jobs = future.result()
                            logger.info(f"Got {len(jobs)} jobs from {source}")

                            # Normalize and deduplicate jobs
                            for job in jobs:
                                normalized = normalize_job_data(job, source)
                                job_id = normalized['id']

                                if job_id not in seen_ids:
                                    seen_ids.add(job_id)
                                    all_jobs.append(normalized)

                        except Exception as e:
                            logger.error(f"Error getting jobs from {source}: {str(e)}")

        logger.info(f"Total unique jobs found: {len(all_jobs)}")
        return all_jobs

    def search_source(self, source: str, title: str, location: str) -> List[Dict[str, Any]]:
        """Search a specific source."""
        if source not in self.scrapers:
            logger.warning(f"Source '{source}' not available")
            return []

        try:
            jobs = self.scrapers[source].search(title, location)
            return [normalize_job_data(job, source) for job in jobs]
        except Exception as e:
            logger.error(f"Error searching {source}: {str(e)}")
            return []
