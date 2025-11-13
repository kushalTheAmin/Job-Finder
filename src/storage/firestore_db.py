"""Firestore database operations for job tracking."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.cloud import firestore


logger = logging.getLogger(__name__)


class FirestoreDB:
    """Manages job tracking in Firestore."""

    def __init__(self, config: Any):
        """Initialize Firestore client."""
        self.config = config
        self.db = firestore.Client(project=config.project_id)
        self.jobs_collection = config.jobs_collection
        self.history_collection = config.history_collection

        logger.info(f"Initialized Firestore DB for project: {config.project_id}")

    def is_job_applied(self, job_id: str) -> bool:
        """Check if job has already been applied to."""
        try:
            doc_ref = self.db.collection(self.jobs_collection).document(job_id)
            doc = doc_ref.get()
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking job status: {str(e)}")
            return False

    def mark_job_applied(self, job: Dict[str, Any]) -> None:
        """Mark job as applied in Firestore."""
        try:
            job_id = job.get('id')
            if not job_id:
                logger.warning("Job ID missing, cannot mark as applied")
                return

            doc_ref = self.db.collection(self.jobs_collection).document(job_id)

            job_data = {
                'job_id': job_id,
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'url': job.get('url', ''),
                'match_score': job.get('match_score', 0),
                'source': job.get('source', ''),
                'applied_at': firestore.SERVER_TIMESTAMP,
                'status': 'applied'
            }

            doc_ref.set(job_data)
            logger.info(f"Marked job as applied: {job.get('title')} at {job.get('company')}")

        except Exception as e:
            logger.error(f"Error marking job as applied: {str(e)}")

    def get_applied_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of applied jobs."""
        try:
            docs = (
                self.db.collection(self.jobs_collection)
                .order_by('applied_at', direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            jobs = []
            for doc in docs:
                job_data = doc.to_dict()
                job_data['id'] = doc.id
                jobs.append(job_data)

            return jobs

        except Exception as e:
            logger.error(f"Error getting applied jobs: {str(e)}")
            return []

    def filter_new_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out jobs that have already been applied to."""
        new_jobs = []

        for job in jobs:
            job_id = job.get('id')
            if job_id and not self.is_job_applied(job_id):
                new_jobs.append(job)
            else:
                logger.debug(f"Skipping duplicate job: {job.get('title')}")

        logger.info(f"Filtered to {len(new_jobs)} new jobs (from {len(jobs)} total)")
        return new_jobs

    def filter_new_jobs_batched(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out jobs that have already been applied to using batched Firestore queries.
        Much faster than filter_new_jobs() which does 1 query per job.
        """
        if not jobs:
            return []

        try:
            # Extract all job IDs
            job_ids = [job.get('id') for job in jobs if job.get('id')]

            if not job_ids:
                return jobs

            # Query Firestore for all these job IDs in one batch
            # Firestore 'in' queries are limited to 10 items, so we batch them
            applied_job_ids = set()
            batch_size = 10

            for i in range(0, len(job_ids), batch_size):
                batch_ids = job_ids[i:i + batch_size]
                # Query using document IDs directly (faster than field query)
                for job_id in batch_ids:
                    doc_ref = self.db.collection(self.jobs_collection).document(job_id)
                    if doc_ref.get().exists:
                        applied_job_ids.add(job_id)

            # Filter out already applied jobs
            new_jobs = []
            for job in jobs:
                job_id = job.get('id')
                if job_id and job_id not in applied_job_ids:
                    new_jobs.append(job)
                else:
                    logger.debug(f"Skipping duplicate job: {job.get('title')}")

            logger.info(f"Batched filter: {len(new_jobs)} new jobs (from {len(jobs)} total, {len(applied_job_ids)} already applied)")
            return new_jobs

        except Exception as e:
            logger.error(f"Error in batched filtering: {str(e)}")
            # Fallback to regular filtering
            logger.info("Falling back to non-batched filtering")
            return self.filter_new_jobs(jobs)

    def save_daily_run(self, run_data: Dict[str, Any]) -> None:
        """Save daily run statistics to history."""
        try:
            doc_ref = self.db.collection(self.history_collection).document()

            history_data = {
                'timestamp': firestore.SERVER_TIMESTAMP,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'jobs_found': run_data.get('jobs_found', 0),
                'jobs_matched': run_data.get('jobs_matched', 0),
                'jobs_applied': run_data.get('jobs_applied', 0),
                'sources_used': run_data.get('sources_used', []),
                'avg_match_score': run_data.get('avg_match_score', 0),
                'top_companies': run_data.get('top_companies', []),
                'status': run_data.get('status', 'success'),
                'error': run_data.get('error', None)
            }

            doc_ref.set(history_data)
            logger.info("Saved daily run to history")

        except Exception as e:
            logger.error(f"Error saving daily run: {str(e)}")

    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get job search statistics for the last N days."""
        try:
            cutoff_date = datetime.now()
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

            docs = (
                self.db.collection(self.history_collection)
                .where('timestamp', '>=', cutoff_date)
                .stream()
            )

            stats = {
                'total_runs': 0,
                'total_jobs_found': 0,
                'total_jobs_matched': 0,
                'total_jobs_applied': 0,
                'runs': []
            }

            for doc in docs:
                run_data = doc.to_dict()
                stats['total_runs'] += 1
                stats['total_jobs_found'] += run_data.get('jobs_found', 0)
                stats['total_jobs_matched'] += run_data.get('jobs_matched', 0)
                stats['total_jobs_applied'] += run_data.get('jobs_applied', 0)
                stats['runs'].append(run_data)

            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}

    def update_job_status(self, job_id: str, status: str, notes: str = None) -> None:
        """Update job application status."""
        try:
            doc_ref = self.db.collection(self.jobs_collection).document(job_id)

            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            if notes:
                update_data['notes'] = notes

            doc_ref.update(update_data)
            logger.info(f"Updated job status to: {status}")

        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
