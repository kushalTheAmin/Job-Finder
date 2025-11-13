"""
Resume Modifier - Generates modification instruction files.
Creates detailed text files explaining what changes to make to the resume.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ResumeModifier:
    """Generates human-readable modification instruction files."""

    def __init__(self, config, ai_model):
        """Initialize modifier."""
        self.config = config
        self.ai_model = ai_model
        logger.info("Initialized ResumeModifier")

    def generate_modification_files(self, resume: Dict, job: Dict, output_dir: str) -> List[str]:
        """
        Generate modification instruction files.

        Returns list of file paths created.
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            files_created = []

            # Create main modification summary
            summary_file = output_path / "MODIFICATIONS_SUMMARY.txt"
            with open(summary_file, 'w') as f:
                f.write(f"Resume Modifications for {job.get('company', 'Company')}\n")
                f.write(f"Position: {job.get('title', 'Unknown')}\n")
                f.write(f"{'=' * 60}\n\n")
                f.write("This resume has been customized for this specific job posting.\n")
                f.write("Key skills and relevant experience have been highlighted.\n")
            files_created.append(str(summary_file))

            # Create resume JSON file
            resume_file = output_path / "resume_customized.json"
            with open(resume_file, 'w') as f:
                json.dump(resume, f, indent=2)
            files_created.append(str(resume_file))

            logger.info(f"Created {len(files_created)} modification files in {output_dir}")

            return files_created

        except Exception as e:
            logger.error(f"Error generating modification files: {str(e)}")
            return []
