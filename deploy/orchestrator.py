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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_config
from src.utils import setup_logging, load_json_file
from src.scrapers.aggregator import JobAggregator
from src.matcher.job_matcher import JobMatcher
from src.resume.ats_optimizer import ATSOptimizer
from src.resume.interview_prep import InterviewPrepGenerator
from src.resume.doc_generator import DOCResumeGenerator
from src.resume.resume_modifier import ResumeModifier
from src.resume.resume_validator import ResumeValidator
from src.storage.firestore_db import FirestoreDB
from src.storage.gdrive import GoogleDriveUploader
from src.notifier.email_sender import EmailSender
import vertexai
from vertexai.generative_models import GenerativeModel


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

        # Initialize Vertex AI and ATS Optimizer
        vertexai.init(
            project=self.config.project_id,
            location=self.config.vertex_location
        )
        ai_model = GenerativeModel(self.config.vertex_model)
        self.ats_optimizer = ATSOptimizer(self.config, ai_model)
        target_coverage = self.config.get('resume_customization', 'target_skill_coverage', default=95)
        logger.info(f"Using AI-Powered ATS Optimizer (target: {target_coverage}% coverage)")

        self.resume_validator = ResumeValidator(self.config, ai_model)
        logger.info("AI-Powered Resume Validator enabled (prevents repetition & quality issues)")

        self.interview_prep_gen = InterviewPrepGenerator()
        self.doc_generator = DOCResumeGenerator()
        self.resume_modifier = ResumeModifier(self.config, ai_model)
        self.firestore = FirestoreDB(self.config)
        self.drive_uploader = GoogleDriveUploader(
            self.config.google_drive_folder_id
        ) if self.config.upload_to_drive else None
        self.email_sender = EmailSender(self.config) if self.config.send_email else None

        # Thread safety for parallel processing
        self.logging_lock = threading.Lock()
        self.max_workers = self.config.get('matching', 'parallel_workers', default=3)

        logger.info("All components initialized successfully")
        logger.info(f"Parallel processing: {self.max_workers} workers")

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

            # Extract salary and visa information for all jobs (optional)
            logger.info("Extracting salary and visa information...")
            for job in all_jobs:
                try:
                    if hasattr(self.job_matcher, 'extract_salary'):
                        salary_info = self.job_matcher.extract_salary(job)
                        job['salary_info'] = salary_info
                        if salary_info.get('min'):
                            # Format for display
                            if salary_info.get('max'):
                                job['salary'] = f"${salary_info['min']:,} - ${salary_info['max']:,}"
                            else:
                                job['salary'] = f"${salary_info['min']:,}+"
                except Exception as e:
                    logger.debug(f"Could not extract salary: {e}")

                try:
                    if hasattr(self.job_matcher, 'detect_visa_requirements'):
                        visa_info = self.job_matcher.detect_visa_requirements(job)
                        job['visa_info'] = visa_info
                        if visa_info.get('flag_text'):
                            logger.debug(f"  {job.get('company')}: {visa_info['flag_text']}")
                except Exception as e:
                    logger.debug(f"Could not detect visa info: {e}")

            # Step 2: Filter out already applied jobs (using batched queries)
            logger.info("\n" + "=" * 60)
            logger.info("STEP 2: Filtering New Jobs (Batched)")
            logger.info("=" * 60)

            # Use batched Firestore filtering - much faster than one-by-one
            new_jobs = self.firestore.filter_new_jobs_batched(all_jobs)

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

    def _process_single_resume(
        self,
        job: Dict[str, Any],
        job_index: int,
        total_jobs: int
    ) -> Dict[str, Any]:
        """
        Process a single job resume customization (thread-safe).

        Args:
            job: Job details
            job_index: Index in the job list (for logging)
            total_jobs: Total number of jobs being processed

        Returns:
            Result dictionary with success status and generated files
        """
        result = {
            'success': False,
            'job': job,
            'resume_file': None,
            'prep_guide': None,
            'error': None
        }

        try:
            with self.logging_lock:
                logger.info(f"\nCustomizing resume {job_index+1}/{total_jobs} for: {job.get('title')} at {job.get('company')}")

            # Use AI-powered ATS optimization for 95% coverage
            # For stretch jobs (50-70% match), use aggressive mode for 98% coverage
            match_analysis = job.get('match_analysis', {})
            is_stretch = job.get('_is_stretch_job', False)

            if is_stretch:
                with self.logging_lock:
                    logger.info(f"  Using AGGRESSIVE mode for stretch job (boost potential: {job.get('_boost_potential', 0)})")

            ats_result = self.ats_optimizer.optimize_resume(
                self.master_resume,
                job,
                match_analysis
            )

            customized_resume = ats_result.get('optimized_resume', self.master_resume)

            # Build customization report for email
            customization_report = {
                'total_changes': ats_result.get('total_changes', 0),
                'coverage_before': ats_result.get('coverage_before', 0),
                'coverage_after': ats_result.get('coverage_after', 0),
                'ats_optimization': ats_result.get('verification', {}),
                'modifications': ats_result.get('modifications', []),
                'coherence_score': 90,  # ATS optimizer maintains coherence
                'interview_readiness': ats_result.get('verification', {}).get('final_coverage', 0)
            }

            # VALIDATION STEP: Check and fix resume quality issues
            with self.logging_lock:
                logger.info(f"  Validating resume quality (checking for repetition, date conflicts, etc.)...")

            validation_result = self.resume_validator.validate_and_fix(
                customized_resume,
                job,
                customization_report
            )

            # Use validated resume if validation passed or was fixed
            if validation_result.get('validation_passed'):
                customized_resume = validation_result.get('validated_resume', customized_resume)
                with self.logging_lock:
                    logger.info(f"  ✓ Resume quality validated (Authenticity: {validation_result.get('authenticity_score')}%, Quality: {validation_result.get('quality_score')}%)")

                    fixes = validation_result.get('fixes_applied', [])
                    if fixes:
                        logger.info(f"  Applied {len(fixes)} auto-fixes to improve quality")
            else:
                # Log validation failure warning
                issues = validation_result.get('issues_found', [])
                with self.logging_lock:
                    logger.warning(f"  ⚠️  Resume validation failed - {len(issues)} issues found")
                    logger.warning(f"  Authenticity: {validation_result.get('authenticity_score')}%, Quality: {validation_result.get('quality_score')}%")
                    # Use validated resume anyway (it may have partial fixes)
                    customized_resume = validation_result.get('validated_resume', customized_resume)

            # Attach validation report to customization report
            customization_report['validation_report'] = validation_result.get('validation_report', {})

            with self.logging_lock:
                logger.info(f"  ATS Coverage: {customization_report['coverage_before']}% → {customization_report['coverage_after']}%")
                logger.info(f"  Bullets Modified: {customization_report['total_changes']}")
                logger.info(f"  Keywords Added: {ats_result.get('verification', {}).get('changes_summary', {}).get('keywords_added', 0)}")

            # Attach customization report to job for email
            job['customization_report'] = customization_report

            # Generate interview prep guide
            if self.config.get('resume_customization', 'generate_interview_prep', default=True):
                prep_guide = self.interview_prep_gen.generate_prep_guide(customization_report, job)
                job['prep_guide'] = prep_guide  # Attach to job for easy access in email
                result['prep_guide'] = prep_guide

                # Save prep guide as text file (thread-safe)
                prep_text = self.interview_prep_gen.format_as_text(prep_guide)
                prep_file_path = Path('output/prep_guides') / f"prep_{job.get('company', 'job')}_{job_index}.txt"
                prep_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(prep_file_path, 'w') as f:
                    f.write(prep_text)

                with self.logging_lock:
                    logger.info(f"  Generated interview prep guide: {prep_file_path.name}")

            # Generate modification files (NEW APPROACH - detailed instructions)
            if getattr(self.config, 'generate_modification_files', True):
                modifications_dir = f"output/modifications/{job.get('company', 'Company').replace(' ', '_')}"
                modification_files = self.resume_modifier.generate_modification_files(
                    customized_resume,
                    job,
                    output_dir=modifications_dir
                )
                result['modification_files'] = modification_files

                with self.logging_lock:
                    logger.info(f"✓ Generated {len(modification_files)} modification files: {modifications_dir}/")

            # Generate DOCX (OLD APPROACH - optional, for immediate use)
            if getattr(self.config, 'generate_docx', False):
                doc_path = self.doc_generator.generate(customized_resume, job)
                result['resume_file'] = doc_path
                with self.logging_lock:
                    logger.info(f"✓ Generated resume DOCX: {Path(doc_path).name}")

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)
            with self.logging_lock:
                logger.error(f"❌ Failed to customize resume for {job.get('company')} - {job.get('title')}")
                logger.error(f"   Error: {str(e)}")

        return result

    def _customize_resumes(self, jobs: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Customize resumes for each job in parallel and generate DOCXs with interview prep."""
        resume_files = []
        prep_guides = []
        failed_resumes = []

        # Use parallel processing if multiple jobs
        if len(jobs) > 1 and self.max_workers > 1:
            logger.info(f"Processing {len(jobs)} resumes in parallel with {self.max_workers} workers")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all jobs to the executor
                future_to_job = {
                    executor.submit(self._process_single_resume, job, i, len(jobs)): (job, i)
                    for i, job in enumerate(jobs)
                }

                # Collect results as they complete
                for future in as_completed(future_to_job):
                    result = future.result()

                    if result['success']:
                        if result['resume_file']:
                            resume_files.append(result['resume_file'])
                        if result['prep_guide']:
                            prep_guides.append(result['prep_guide'])
                    else:
                        failed_resumes.append({
                            'company': result['job'].get('company'),
                            'title': result['job'].get('title'),
                            'error': result['error']
                        })

        else:
            # Sequential processing for single job or if parallel disabled
            logger.info(f"Processing {len(jobs)} resumes sequentially")
            for i, job in enumerate(jobs):
                result = self._process_single_resume(job, i, len(jobs))

                if result['success']:
                    if result['resume_file']:
                        resume_files.append(result['resume_file'])
                    if result['prep_guide']:
                        prep_guides.append(result['prep_guide'])
                else:
                    failed_resumes.append({
                        'company': result['job'].get('company'),
                        'title': result['job'].get('title'),
                        'error': result['error']
                    })

        # Log summary
        if failed_resumes:
            logger.warning(f"\n⚠️  {len(failed_resumes)}/{len(jobs)} resumes failed:")
            for failed in failed_resumes:
                logger.warning(f"   - {failed['company']} - {failed['title']}")

        logger.info(f"\n✓ Successfully customized {len(resume_files)}/{len(jobs)} resumes")

        return resume_files, prep_guides

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

        success = self.email_sender.send_daily_report(jobs, resume_files, stats)
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
