#!/usr/bin/env python3
"""
Standalone test to verify what data we actually get from each scraper.
Tests each scraper independently to see description quality.

Run this WITHOUT needing the full project setup.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def analyze_description(description, source):
    """Analyze description quality."""
    if not description:
        return {
            'quality': 'EMPTY',
            'word_count': 0,
            'has_sections': False,
            'tech_count': 0
        }

    word_count = len(description.split())

    # Check for key sections
    key_sections = ['responsibilities', 'requirements', 'qualifications',
                   'experience', 'skills', 'required', 'preferred']
    has_sections = any(s in description.lower() for s in key_sections)

    # Count tech keywords
    tech_keywords = ['python', 'java', 'javascript', 'react', 'node', 'aws',
                    'docker', 'kubernetes', 'sql', 'api', 'cloud', 'git']
    tech_count = sum(1 for t in tech_keywords if t in description.lower())

    # Determine quality
    if word_count < 50:
        quality = 'SNIPPET'
    elif word_count < 200:
        quality = 'PARTIAL'
    else:
        quality = 'FULL'

    return {
        'quality': quality,
        'word_count': word_count,
        'has_sections': has_sections,
        'tech_count': tech_count
    }

def test_adzuna():
    """Test Adzuna API to see what descriptions we get."""
    print_header("TESTING ADZUNA API")

    app_id = os.getenv('ADZUNA_APP_ID')
    app_key = os.getenv('ADZUNA_APP_KEY')

    if not app_id or not app_key:
        print_error("Adzuna credentials not found in .env file")
        print_warning("Set ADZUNA_APP_ID and ADZUNA_APP_KEY")
        return None

    try:
        url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'what': 'software engineer',
            'where': 'new york',
            'results_per_page': 5
        }

        print(f"Fetching from: {url}")
        print(f"Query: software engineer in new york")

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        jobs = data.get('results', [])

        print_success(f"Got {len(jobs)} jobs from Adzuna")

        # Analyze first 3 jobs
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{Colors.BOLD}Job {i}: {job.get('title', 'N/A')}{Colors.END}")
            print(f"Company: {job.get('company', {}).get('display_name', 'N/A')}")

            description = job.get('description', '')
            analysis = analyze_description(description, 'Adzuna')

            print(f"Description quality: {Colors.YELLOW}{analysis['quality']}{Colors.END}")
            print(f"Word count: {analysis['word_count']}")
            print(f"Has key sections: {analysis['has_sections']}")
            print(f"Tech keywords found: {analysis['tech_count']}")

            # Print first 200 chars of description
            print(f"\nDescription preview:")
            print(f"{Colors.BLUE}{description[:200]}...{Colors.END}")

            # Check if redirect_url exists
            redirect_url = job.get('redirect_url', '')
            if redirect_url:
                print(f"\nRedirect URL available: {Colors.GREEN}YES{Colors.END}")
                print(f"URL: {redirect_url[:80]}...")
            else:
                print(f"\nRedirect URL available: {Colors.RED}NO{Colors.END}")

        return {
            'source': 'Adzuna',
            'jobs_found': len(jobs),
            'avg_word_count': sum(analyze_description(j.get('description', ''), 'Adzuna')['word_count'] for j in jobs[:3]) / 3,
            'has_redirect_urls': all(j.get('redirect_url') for j in jobs[:3])
        }

    except Exception as e:
        print_error(f"Adzuna test failed: {str(e)}")
        return None

def test_jsearch():
    """Test JSearch API to see what descriptions we get."""
    print_header("TESTING JSEARCH API")

    api_key = os.getenv('JSEARCH_API_KEY')

    if not api_key:
        print_error("JSearch API key not found in .env file")
        print_warning("Set JSEARCH_API_KEY")
        return None

    try:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }
        params = {
            'query': 'software engineer in new york',
            'num_pages': 1
        }

        print(f"Fetching from: {url}")
        print(f"Query: software engineer in new york")

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        jobs = data.get('data', [])

        print_success(f"Got {len(jobs)} jobs from JSearch")

        # Analyze first 3 jobs
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{Colors.BOLD}Job {i}: {job.get('job_title', 'N/A')}{Colors.END}")
            print(f"Company: {job.get('employer_name', 'N/A')}")

            description = job.get('job_description', '')
            analysis = analyze_description(description, 'JSearch')

            print(f"Description quality: {Colors.YELLOW}{analysis['quality']}{Colors.END}")
            print(f"Word count: {analysis['word_count']}")
            print(f"Has key sections: {analysis['has_sections']}")
            print(f"Tech keywords found: {analysis['tech_count']}")

            # Print first 200 chars of description
            print(f"\nDescription preview:")
            print(f"{Colors.BLUE}{description[:200]}...{Colors.END}")

            # Check if job_id exists for detail endpoint
            job_id = job.get('job_id', '')
            if job_id:
                print(f"\nJob ID available: {Colors.GREEN}YES{Colors.END}")
                print(f"Job ID: {job_id}")
                print(f"Could fetch details from: /job-details?job_id={job_id}")
            else:
                print(f"\nJob ID available: {Colors.RED}NO{Colors.END}")

        return {
            'source': 'JSearch',
            'jobs_found': len(jobs),
            'avg_word_count': sum(analyze_description(j.get('job_description', ''), 'JSearch')['word_count'] for j in jobs[:3]) / 3,
            'has_job_ids': all(j.get('job_id') for j in jobs[:3])
        }

    except Exception as e:
        print_error(f"JSearch test failed: {str(e)}")
        return None

def test_jsearch_job_details():
    """Test JSearch Job Details endpoint to see if it gives more data."""
    print_header("TESTING JSEARCH JOB DETAILS ENDPOINT")

    api_key = os.getenv('JSEARCH_API_KEY')

    if not api_key:
        print_error("JSearch API key not found")
        return None

    try:
        # First get a job ID from search
        search_url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }
        params = {
            'query': 'software engineer in new york',
            'num_pages': 1
        }

        response = requests.get(search_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        jobs = data.get('data', [])

        if not jobs:
            print_error("No jobs found to test details endpoint")
            return None

        # Get first job ID
        job_id = jobs[0].get('job_id')
        if not job_id:
            print_error("No job_id in search results")
            return None

        print(f"Testing with job_id: {job_id}")

        # Now fetch job details
        details_url = "https://jsearch.p.rapidapi.com/job-details"
        params = {'job_id': job_id}

        print(f"Fetching from: {details_url}")

        response = requests.get(details_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        details_data = response.json()
        job_details = details_data.get('data', [])

        if job_details:
            job = job_details[0]
            print_success("Got job details from Job Details endpoint")

            print(f"\n{Colors.BOLD}Job: {job.get('job_title', 'N/A')}{Colors.END}")
            print(f"Company: {job.get('employer_name', 'N/A')}")

            description = job.get('job_description', '')
            analysis = analyze_description(description, 'JSearch Details')

            print(f"\nDescription quality: {Colors.YELLOW}{analysis['quality']}{Colors.END}")
            print(f"Word count: {analysis['word_count']}")
            print(f"Has key sections: {analysis['has_sections']}")
            print(f"Tech keywords found: {analysis['tech_count']}")

            # Compare with search endpoint
            search_desc = jobs[0].get('job_description', '')
            search_analysis = analyze_description(search_desc, 'JSearch Search')

            print(f"\n{Colors.BOLD}COMPARISON:{Colors.END}")
            print(f"Search endpoint: {search_analysis['word_count']} words")
            print(f"Details endpoint: {analysis['word_count']} words")

            if analysis['word_count'] > search_analysis['word_count']:
                print_success("Details endpoint has MORE content!")
            elif analysis['word_count'] == search_analysis['word_count']:
                print_warning("Same content from both endpoints")
            else:
                print_error("Details endpoint has LESS content? (unexpected)")

            return {
                'search_words': search_analysis['word_count'],
                'details_words': analysis['word_count'],
                'difference': analysis['word_count'] - search_analysis['word_count']
            }
        else:
            print_error("No data in job details response")
            return None

    except Exception as e:
        print_error(f"JSearch details test failed: {str(e)}")
        return None

def main():
    """Run all tests and provide summary."""
    print(f"\n{Colors.BOLD}JOB SCRAPER DATA QUALITY TEST{Colors.END}")
    print(f"{Colors.BOLD}Testing what data we actually get from each source{Colors.END}\n")

    results = []

    # Test Adzuna
    adzuna_result = test_adzuna()
    if adzuna_result:
        results.append(adzuna_result)

    # Test JSearch
    jsearch_result = test_jsearch()
    if jsearch_result:
        results.append(jsearch_result)

    # Test JSearch Details endpoint
    jsearch_details = test_jsearch_job_details()

    # Summary
    print_header("SUMMARY")

    for result in results:
        print(f"\n{Colors.BOLD}{result['source']}:{Colors.END}")
        print(f"  Jobs found: {result['jobs_found']}")
        print(f"  Avg word count: {result['avg_word_count']:.0f}")

        if result['avg_word_count'] < 100:
            print(f"  Quality: {Colors.RED}SNIPPET - Need to fetch full pages{Colors.END}")
        elif result['avg_word_count'] < 300:
            print(f"  Quality: {Colors.YELLOW}PARTIAL - May need full pages{Colors.END}")
        else:
            print(f"  Quality: {Colors.GREEN}FULL - Looks good!{Colors.END}")

    if jsearch_details:
        print(f"\n{Colors.BOLD}JSearch Endpoints Comparison:{Colors.END}")
        print(f"  Search endpoint: {jsearch_details['search_words']} words")
        print(f"  Details endpoint: {jsearch_details['details_words']} words")
        print(f"  Difference: {jsearch_details['difference']:+d} words")

    print_header("RECOMMENDATIONS")

    for result in results:
        source = result['source']
        avg_words = result['avg_word_count']

        if avg_words < 100:
            print_error(f"{source}: NEEDS FIX - Currently getting snippets only")
            if source == 'Adzuna' and result.get('has_redirect_urls'):
                print(f"  → Fetch redirect_url to get full job page")
            if source == 'JSearch' and result.get('has_job_ids'):
                print(f"  → Use /job-details endpoint with job_id")
        elif avg_words < 300:
            print_warning(f"{source}: SHOULD FIX - Partial descriptions")
        else:
            print_success(f"{source}: OK - Getting full descriptions")

    print("\n")

if __name__ == '__main__':
    main()
