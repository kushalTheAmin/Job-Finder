"""
Cloud Function entry point for Job Finder.
This is the entry point when deployed to Google Cloud Functions.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def job_finder_handler(request=None):
    """
    Cloud Function handler.
    Can be triggered by Cloud Scheduler or HTTP request.
    """
    try:
        # Import here to ensure path is set
        from orchestrator import JobFinderOrchestrator

        orchestrator = JobFinderOrchestrator()
        result = orchestrator.run()

        return {
            'statusCode': 200,
            'body': result
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error: {str(e)}")
        print(f"Traceback: {error_details}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


# For Cloud Functions / Cloud Run
def job_finder_http(request):
    """HTTP entry point."""
    return job_finder_handler(request)

def main(request):
    """Alternative HTTP entry point for Cloud Run."""
    return job_finder_handler(request)
