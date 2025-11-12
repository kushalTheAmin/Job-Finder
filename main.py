#!/usr/bin/env python3
"""
Job Finder - Automated Job Search and Resume Customization System
Main orchestrator script that runs the entire pipeline.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_config
from src.utils import setup_logging, load_json_file
from src.scrapers.aggregator import JobAggregator
from src.matcher.job_matcher import JobMatcher
from src.resume.smart_customizer import SmartResumeCustomizer
from src.resume.interview_prep import InterviewPrepGenerator
from src.resume.pdf_generator import PDFResumeGenerator
from src.storage.firestore_db import FirestoreDB
from src.storage.gdrive import GoogleDriveUploader
from src.notifier.email_sender import EmailSender


logger = logging.getLogger(__name__)


class JobFinderOrchestrator:
    """Main orchestrator for the job finding system."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the orchestrator."""
        # Load configuration
        self.config = get_config(config_path)

        # Set up logging
        setup_logging(self.config.log_level, self.config.log_file)
        logger.info("=" * 60)
        logger.info("Job Finder - Starting New Run")
        logger.info("=" * 60)

        # Load master resume
        logger.info(f"Loading master resume from: {self.config.master_resume_path}")
        self.master_resume = load_json_file(self.config.master_resume_path)

        # Initialize components
        self.job_aggregator = JobAggregator(self.config)
        self.job_matcher = JobMatcher(self.config, self.master_resume)
        self.resume_customizer = SmartResumeCustomizer(self.config, self.master_resume)
        self.interview_prep_gen = InterviewPrepGenerator()
        self.pdf_generator = PDFResumeGenerator()
        self.firestore = FirestoreDB(self.config)
        self.drive_uploader = GoogleDriveUploader(
            self.config.google_drive_folder_id
        ) if self.config.upload_to_drive else None
        self.email_sender = EmailSender(self.config) if self.config.send_email else None

        logger.info("All components initialized successfully")
        logger.info("Using Smart Resume Customizer with coherence validation")

    def run(self) -> Dict[str, Any]:
        """Execute the main job finding pipeline."""
        try:
            # Step 1: Search for jobs
            logger.info("\n" + "=" * 60)
            logger.info("STEP 1: Searching for Jobs")
            logger.info("=" * 60)
            all_jobs = self._search_jobs()

            if not all_jobs:
                logger.warning("No jobs found. Exiting.")
                return self._create_run_summary(0, 0, 0, [])

            # Step 2: Filter out already applied jobs
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Filtering New Jobs")
            logger.info("=" * 60)
            new_jobs = self.firestore.filter_new_jobs(all_jobs)

            if not new_jobs:
                logger.info("No new jobs to process. All jobs have been seen before.")
                return self._create_run_summary(len(all_jobs), 0, 0, [])

            # Step 3: Match jobs with resume
            logger.info("\n" + "=" * 60)
            logger.info("STEP 3: Matching Jobs with Resume")
            logger.info("=" * 60)
            matched_jobs = self.job_matcher.match_jobs(new_jobs)

            if not matched_jobs:
                logger.warning("No jobs matched the threshold. Exiting.")
                return self._create_run_summary(len(all_jobs), 0, 0, [])

            # Step 4: Rank and limit jobs
            logger.info("\n" + "=" * 60)
            logger.info("STEP 4: Ranking Jobs")
            logger.info("=" * 60)
            top_jobs = self.job_matcher.rank_jobs(matched_jobs)

            # Step 5: Customize resumes for each job (with interview prep)
            logger.info("\n" + "=" * 60)
            logger.info("STEP 5: Customizing Resumes & Generating Interview Prep")
            logger.info("=" * 60)
            resume_files, prep_guides = self._customize_resumes(top_jobs)

            # Step 6: Upload to Google Drive
            if self.drive_uploader and self.config.upload_to_drive:
                logger.info("\n" + "=" * 60)
                logger.info("STEP 6: Uploading to Google Drive")
                logger.info("=" * 60)
                self._upload_to_drive(resume_files)

            # Step 7: Send email notification with prep guides
            if self.email_sender and self.config.send_email:
                logger.info("\n" + "=" * 60)
                logger.info("STEP 7: Sending Email Notification")
                logger.info("=" * 60)
                self._send_email(top_jobs, resume_files, prep_guides)

            # Step 8: Mark jobs as applied
            logger.info("\n" + "=" * 60)
            logger.info("STEP 8: Updating Database")
            logger.info("=" * 60)
            for job in top_jobs:
                self.firestore.mark_job_applied(job)

            # Save run summary
            run_summary = self._create_run_summary(
                len(all_jobs),
                len(matched_jobs),
                len(top_jobs),
                top_jobs
            )
            self.firestore.save_daily_run(run_summary)

            logger.info("\n" + "=" * 60)
            logger.info("✅ Job Finder Run Completed Successfully")
            logger.info("=" * 60)
            self._print_summary(run_summary)

            return run_summary

        except Exception as e:
            logger.error(f"Error in job finder pipeline: {str(e)}", exc_info=True)
            # Save error to history
            error_summary = {
                'status': 'error',
                'error': str(e),
                'jobs_found': 0,
                'jobs_matched': 0,
                'jobs_applied': 0
            }
            self.firestore.save_daily_run(error_summary)
            raise

    def _search_jobs(self) -> List[Dict[str, Any]]:
        """Search for jobs across all sources."""
        jobs = self.job_aggregator.search_all(
            self.config.job_titles,
            self.config.locations
        )
        logger.info(f"Found {len(jobs)} total jobs")
        return jobs

    def _customize_resumes(self, jobs: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Customize resumes for each job and generate PDFs with interview prep."""
        resume_files = []
        prep_guides = []

        for i, job in enumerate(jobs):
            try:
                logger.info(f"\nCustomizing resume {i+1}/{len(jobs)} for: {job.get('title')} at {job.get('company')}")

                # Smart customization with coherence validation
                customized_resume, customization_report = self.resume_customizer.customize_for_job(job)

                # Log customization details
                logger.info(f"  Coherence Score: {customization_report.get('coherence_score', 0)}%")
                logger.info(f"  Changes Made: {customization_report.get('total_changes', 0)}")
                logger.info(f"  Interview Readiness: {customization_report.get('interview_readiness', 0)}%")

                # Generate interview prep guide
                if self.config.get('resume_customization', 'generate_interview_prep', default=True):
                    prep_guide = self.interview_prep_gen.generate_prep_guide(customization_report, job)
                    prep_guides.append(prep_guide)

                    # Save prep guide as text file
                    prep_text = self.interview_prep_gen.format_as_text(prep_guide)
                    prep_file_path = Path('output/prep_guides') / f"prep_{job.get('company', 'job')}_{i}.txt"
                    prep_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(prep_file_path, 'w') as f:
                        f.write(prep_text)
                    logger.info(f"  Generated interview prep guide: {prep_file_path.name}")

                # Generate PDF
                pdf_path = self.pdf_generator.generate(customized_resume, job)
                resume_files.append(pdf_path)

                logger.info(f"✓ Generated resume: {Path(pdf_path).name}")

            except Exception as e:
                logger.error(f"Error customizing resume for job: {str(e)}")
                continue

        return resume_files

    def _upload_to_drive(self, resume_files: List[str]) -> None:
        """Upload resume files to Google Drive."""
        for file_path in resume_files:
            try:
                file_id = self.drive_uploader.upload_file(file_path)
                if file_id:
                    logger.info(f"✓ Uploaded to Drive: {Path(file_path).name}")
            except Exception as e:
                logger.error(f"Error uploading file: {str(e)}")

    def _send_email(
        self,
        jobs: List[Dict[str, Any]],
        resume_files: List[str],
        prep_guides: List[Dict[str, Any]]
    ) -> None:
        """Send email notification with jobs, resumes, and interview prep guides."""
        stats = {
            'jobs_found': len(jobs),
            'avg_match_score': sum(j.get('match_score', 0) for j in jobs) / len(jobs) if jobs else 0
        }

        success = self.email_sender.send_daily_report(jobs, resume_files, stats, prep_guides)
        if success:
            logger.info(f"✓ Sent email to {self.config.email_to}")
        else:
            logger.error("Failed to send email")

    def _create_run_summary(
        self,
        jobs_found: int,
        jobs_matched: int,
        jobs_applied: int,
        jobs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create summary of the run."""
        sources_used = self.config.enabled_sources

        top_companies = list(set(
            job.get('company', 'Unknown')
            for job in jobs[:10]
        ))

        avg_match_score = (
            sum(job.get('match_score', 0) for job in jobs) / len(jobs)
            if jobs else 0
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'jobs_found': jobs_found,
            'jobs_matched': jobs_matched,
            'jobs_applied': jobs_applied,
            'sources_used': sources_used,
            'avg_match_score': round(avg_match_score, 2),
            'top_companies': top_companies,
            'status': 'success'
        }

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print run summary to console."""
        logger.info("\n📊 Run Summary:")
        logger.info(f"   Jobs Found: {summary['jobs_found']}")
        logger.info(f"   Jobs Matched: {summary['jobs_matched']}")
        logger.info(f"   Jobs Applied: {summary['jobs_applied']}")
        logger.info(f"   Avg Match Score: {summary['avg_match_score']}%")
        logger.info(f"   Sources Used: {', '.join(summary['sources_used'])}")
        if summary.get('top_companies'):
            logger.info(f"   Top Companies: {', '.join(summary['top_companies'][:5])}")


def main():
    """Main entry point."""
    try:
        orchestrator = JobFinderOrchestrator()
        orchestrator.run()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\n\nJob Finder interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
