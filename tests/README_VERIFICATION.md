# Scraper Verification Tests

## Quick Test to See What Data We're Actually Getting

This test script checks what quality of job descriptions we actually receive from each API/scraper.

## Run the Test

```bash
# From the Job-Finder directory
python tests/verify_scrapers.py
```

## What It Tests

### 1. Adzuna API
- Fetches 5 jobs using your API credentials
- Analyzes description quality (word count, sections, tech terms)
- Shows first 200 characters of each description
- Checks if `redirect_url` is available for fetching full page

### 2. JSearch API
- Fetches jobs from search endpoint
- Analyzes description quality
- Checks if `job_id` is available for details endpoint
- Tests the `/job-details` endpoint to compare

### 3. Comparison
- Shows average word counts
- Identifies if we're getting snippets vs full descriptions
- Provides recommendations for fixes

## Expected Output

```
==================================================================
TESTING ADZUNA API
==================================================================

Fetching from: https://api.adzuna.com/v1/api/jobs/us/search/1
Query: software engineer in new york
✓ Got 5 jobs from Adzuna

Job 1: Senior Software Engineer
Company: TechCorp
Description quality: SNIPPET
Word count: 45
Has key sections: False
Tech keywords found: 3

Description preview:
Looking for experienced software engineer with Python...

Redirect URL available: YES
URL: https://www.adzuna.com/land/ad/...

==================================================================
SUMMARY
==================================================================

Adzuna:
  Jobs found: 5
  Avg word count: 47
  Quality: SNIPPET - Need to fetch full pages

JSearch:
  Jobs found: 10
  Avg word count: 285
  Quality: PARTIAL - May need full pages

==================================================================
RECOMMENDATIONS
==================================================================

✗ Adzuna: NEEDS FIX - Currently getting snippets only
  → Fetch redirect_url to get full job page
⚠ JSearch: SHOULD FIX - Partial descriptions
  → Use /job-details endpoint with job_id
```

## What This Tells Us

### If Average Word Count is:
- **< 100 words**: SNIPPET - We're only getting search result summaries
- **100-300 words**: PARTIAL - Getting some details but not complete
- **> 300 words**: FULL - Getting complete job descriptions

### Key Indicators:
- **Has key sections**: Does description include "requirements", "responsibilities", etc?
- **Tech count**: How many technology keywords are mentioned?
- **redirect_url / job_id**: Can we fetch more detailed data?

## Prerequisites

Make sure your `.env` file has:
```bash
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
JSEARCH_API_KEY=your_rapidapi_key
```

## No API Keys?

If you don't have API keys yet:
- **Adzuna**: https://developer.adzuna.com/
- **JSearch**: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

Both have free tiers!

## Understanding the Results

### Example 1: Adzuna Returns Snippet
```
Word count: 45
Has key sections: False
```
**Means**: We're only getting 1-2 sentences from search results. Need to fetch `redirect_url` to get full job posting.

### Example 2: JSearch Search vs Details
```
Search endpoint: 150 words
Details endpoint: 450 words
Difference: +300 words
```
**Means**: The Details endpoint has 3x more content! We should use that instead of just search.

## Next Steps Based on Results

### If Adzuna shows < 100 words:
→ We need to implement fetching `redirect_url` in the scraper

### If JSearch shows difference between endpoints:
→ We need to call `/job-details` endpoint after getting search results

### If both return < 100 words:
→ All 4 scrapers need fixes (LinkedIn, Indeed, Adzuna, JSearch)

## Running Without .env File

You can also test with hardcoded API keys (for quick testing only):

```python
# Edit verify_scrapers.py temporarily
# Replace:
app_id = os.getenv('ADZUNA_APP_ID')
# With:
app_id = 'your_actual_app_id_here'
```

## Interpreting Colors

- 🟢 **Green (✓)**: Good quality, working correctly
- 🟡 **Yellow (⚠)**: Partial quality, might need improvement
- 🔴 **Red (✗)**: Poor quality, definitely needs fixing

## Troubleshooting

### "Adzuna credentials not found"
→ Check your `.env` file has `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`

### "JSearch API key not found"
→ Check your `.env` file has `JSEARCH_API_KEY`

### "Request failed"
→ Check internet connection and API key validity

### Rate limit errors
→ Wait a few minutes, free tiers have limits

## What We Learn From This

This test answers:
1. ✅ Are we getting full descriptions or just snippets?
2. ✅ Which scrapers need fixes?
3. ✅ What endpoints should we use?
4. ✅ What's the actual data quality?

No need to run the entire job search system just to verify this!
