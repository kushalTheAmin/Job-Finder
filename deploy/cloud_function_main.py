"""
Cloud Function entry point for Job Finder.
This is the entry point when deployed to Google Cloud Functions.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import JobFinderOrchestrator


def job_finder_handler(request=None):
    """
    Cloud Function handler.
    Can be triggered by Cloud Scheduler or HTTP request.
    """
    try:
        orchestrator = JobFinderOrchestrator()
        result = orchestrator.run()

        return {
            'statusCode': 200,
            'body': result
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


# For Cloud Run
def main(request):
    """HTTP entry point for Cloud Run."""
    return job_finder_handler(request)
