# 🔍 API Verification Guide
## Test What Data We're Actually Getting (Without Running Full Project)

Before implementing fixes, let's verify what quality of data we're actually receiving from each API.

---

## 🎯 Goal

Answer these questions:
1. ✅ Does Adzuna return full descriptions or just snippets?
2. ✅ Does JSearch return full descriptions or just snippets?
3. ✅ What's the average word count per description?
4. ✅ Do we need to fetch additional endpoints to get full data?

---

## 📊 Three Ways to Test

### Option 1: Python Test Script (Recommended)

**Best for:** Complete analysis with quality metrics

```bash
# From Job-Finder directory
python tests/verify_scrapers.py
```

**What it does:**
- Tests Adzuna API (gets 5 jobs)
- Tests JSearch API (gets 10 jobs)
- Tests JSearch /job-details endpoint
- Analyzes description quality (word count, sections, tech keywords)
- Compares endpoints (search vs details)
- Provides recommendations

**Requirements:**
- Python 3.x
- `requests` library: `pip install requests python-dotenv`
- API keys in `.env` file

**Output example:**
```
==================================================================
TESTING ADZUNA API
==================================================================

✓ Got 5 jobs from Adzuna

Job 1: Senior Software Engineer
Company: TechCorp
Description quality: SNIPPET
Word count: 45
Has key sections: False
Tech keywords found: 3

Redirect URL available: YES

==================================================================
SUMMARY
==================================================================

Adzuna:
  Jobs found: 5
  Avg word count: 47
  Quality: SNIPPET - Need to fetch full pages

==================================================================
RECOMMENDATIONS
==================================================================

✗ Adzuna: NEEDS FIX - Currently getting snippets only
  → Fetch redirect_url to get full job page
```

---

### Option 2: Bash Script (Quick Test)

**Best for:** Quick verification with curl

```bash
# From tests directory
cd tests
./manual_api_test.sh
```

**What it does:**
- Uses curl to test APIs
- Shows first job from each source
- Counts words in descriptions
- Saves full responses to /tmp

**Requirements:**
- bash, curl, jq
- API keys in `.env` file

**Output example:**
```
==================================================================
TEST 1: ADZUNA API
==================================================================

✓ Request successful
Jobs returned: 3

Title: Backend Engineer
Company: StartupCo
Description word count: 52
Quality: SNIPPET - Only getting short summary
→ Need to fetch redirect_url for full description

Redirect URL available: YES
URL: https://www.adzuna.com/land/ad/...
```

---

### Option 3: Manual curl Commands

**Best for:** Testing without any scripts

#### Test Adzuna:
```bash
# Replace YOUR_APP_ID and YOUR_APP_KEY
curl "https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=YOUR_APP_ID&app_key=YOUR_APP_KEY&what=software%20engineer&where=new%20york&results_per_page=3" | jq .
```

**Look for:**
- `.results[0].description` - How long is it?
- `.results[0].redirect_url` - Can we fetch full page?

#### Test JSearch:
```bash
# Replace YOUR_RAPIDAPI_KEY
curl -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
     -H "X-RapidAPI-Host: jsearch.p.rapidapi.com" \
     "https://jsearch.p.rapidapi.com/search?query=software%20engineer%20in%20new%20york&num_pages=1" | jq .
```

**Look for:**
- `.data[0].job_description` - How long is it?
- `.data[0].job_id` - Can we fetch details?

#### Test JSearch Job Details:
```bash
# First get a job_id from search above, then:
curl -H "X-RapidAPI-Key: YOUR_RAPIDAPI_KEY" \
     -H "X-RapidAPI-Host: jsearch.p.rapidapi.com" \
     "https://jsearch.p.rapidapi.com/job-details?job_id=THE_JOB_ID" | jq .
```

**Compare:**
- Is `.data[0].job_description` longer than from search endpoint?

---

## 📋 Prerequisites

### Get API Keys (Free!)

#### Adzuna API
1. Go to https://developer.adzuna.com/
2. Click "Sign Up"
3. Create account and get App ID + App Key
4. Free tier: 100 calls/month

#### JSearch API
1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
2. Sign up for RapidAPI
3. Subscribe to JSearch (FREE tier available)
4. Copy API key from dashboard
5. Free tier: 5,000 requests/month

### Setup .env File

```bash
# Copy template
cp .env.template .env

# Edit .env and add your keys:
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
JSEARCH_API_KEY=your_rapidapi_key_here
```

---

## 📊 Interpreting Results

### Word Count Guide

| Word Count | Quality Level | Meaning |
|-----------|--------------|---------|
| < 50 words | **SNIPPET** | Only 1-2 sentences, basically useless |
| 50-100 words | **SHORT SNIPPET** | Short summary, missing 90% of details |
| 100-300 words | **PARTIAL** | Some details but incomplete |
| 300+ words | **FULL** | Complete job description |

### What We Need

**Target:** 300+ words per job description

**Why?** To extract 30-50 skills instead of 2-5

**Current hypothesis:**
- Adzuna: Probably < 100 words (snippet)
- JSearch: Unknown (need to test)

---

## 🔍 What to Look For

### In Adzuna Response

```json
{
  "results": [
    {
      "title": "Software Engineer",
      "description": "...",  // ← How long is this?
      "redirect_url": "https://..."  // ← Can we fetch this?
    }
  ]
}
```

**Questions:**
1. How many words in `description`?
2. Does `redirect_url` exist?
3. If we fetch `redirect_url`, do we get full HTML page?

### In JSearch Response

```json
{
  "data": [
    {
      "job_title": "Software Engineer",
      "job_description": "...",  // ← How long is this?
      "job_id": "abc123"  // ← Can we use this for /job-details?
    }
  ]
}
```

**Questions:**
1. How many words in `job_description`?
2. Does `job_id` exist?
3. Does `/job-details` endpoint give more data?

---

## 🎯 Expected Findings

### Scenario A: Both APIs Return Snippets
```
Adzuna: 45 words average
JSearch: 75 words average
```
**Action:** Fix ALL 4 scrapers (LinkedIn, Indeed, Adzuna, JSearch)

### Scenario B: JSearch OK, Adzuna Snippets
```
Adzuna: 45 words average
JSearch: 350 words average
```
**Action:** Fix 3 scrapers (LinkedIn, Indeed, Adzuna)

### Scenario C: Both APIs OK
```
Adzuna: 400 words average
JSearch: 350 words average
```
**Action:** Only fix web scrapers (LinkedIn, Indeed)

---

## 🚀 After Testing

### If Results Show Snippets:

1. **Update Implementation Plan**
   - Add fixes for Adzuna (fetch redirect_url)
   - Add fixes for JSearch (use /job-details endpoint)
   - Update timeline estimates

2. **Prioritize by Impact**
   - Fix your primary source first (Adzuna if most jobs come from there)
   - Fix others in order of usage

3. **Implement Systematically**
   - Follow updated plan
   - Test after each fix
   - Validate improvements

### Example Decision Tree:

```
Test Results → Adzuna: 50 words (SNIPPET)
            → JSearch: 300 words (FULL)

Decision:
  Priority 1: Fix Adzuna (primary source)
  Priority 2: Fix LinkedIn (secondary source)
  Priority 3: Fix Indeed (additional source)
  Skip: JSearch (already working)
```

---

## 💡 Tips

### Viewing JSON Responses

**Pretty print:**
```bash
cat /tmp/adzuna_response.json | jq .
```

**Get just descriptions:**
```bash
cat /tmp/adzuna_response.json | jq '.results[].description'
```

**Count words in first description:**
```bash
cat /tmp/adzuna_response.json | jq -r '.results[0].description' | wc -w
```

### Debugging

**See full request:**
```bash
curl -v "https://api.adzuna.com/..." 2>&1 | grep ">"
```

**Save response:**
```bash
curl "..." > response.json
cat response.json | jq .
```

**Test with different queries:**
```bash
# Try different job titles
what=backend%20engineer
what=python%20developer
what=senior%20software%20engineer
```

---

## 📝 Document Your Findings

Create a file: `tests/VERIFICATION_RESULTS.md`

```markdown
# API Verification Results

Date: 2025-11-14

## Adzuna
- Average word count: 47 words
- Quality: SNIPPET
- Has redirect_url: YES
- Recommendation: NEEDS FIX - fetch redirect_url

## JSearch
- Search endpoint: 85 words
- Details endpoint: 420 words
- Quality: Details endpoint = FULL
- Recommendation: USE /job-details endpoint

## Conclusion
- Adzuna: Fix required (fetch redirect_url)
- JSearch: Fix required (use /job-details instead of search)
- LinkedIn: Fix required (already known)
- Indeed: Fix required (already known)

All 4 scrapers need fixes!
```

---

## ❓ Questions This Answers

✅ "Are we getting full job descriptions?" → Test will show
✅ "Which scrapers need fixes?" → Test will identify
✅ "What's the actual data quality?" → Test will measure
✅ "Should we use different endpoints?" → Test will recommend

---

## 🎬 Ready to Test?

**Choose your method:**

1. **Quick test (5 min):** Run `./tests/manual_api_test.sh`
2. **Detailed test (10 min):** Run `python tests/verify_scrapers.py`
3. **Manual test (15 min):** Use curl commands above

**Then:**
1. Document your findings
2. Update implementation plan based on results
3. Start fixes with confidence!

---

**No assumptions, just facts. Let's see what we're actually getting!** 🔍
