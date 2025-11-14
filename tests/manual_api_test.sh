#!/bin/bash
# Manual API testing script
# Test Adzuna and JSearch APIs with curl to see response structure

echo "======================================================================"
echo "MANUAL API VERIFICATION TEST"
echo "======================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo -e "${YELLOW}⚠ No .env file found. Creating from template...${NC}"
    echo ""
    echo "Please add your API keys to .env file:"
    echo "  ADZUNA_APP_ID=your_app_id"
    echo "  ADZUNA_APP_KEY=your_app_key"
    echo "  JSEARCH_API_KEY=your_rapidapi_key"
    echo ""
    exit 1
fi

# Load .env file
source ../.env

echo "======================================================================"
echo "TEST 1: ADZUNA API"
echo "======================================================================"
echo ""

if [ -z "$ADZUNA_APP_ID" ] || [ -z "$ADZUNA_APP_KEY" ]; then
    echo -e "${RED}✗ Adzuna credentials not found in .env${NC}"
    echo "Set ADZUNA_APP_ID and ADZUNA_APP_KEY"
    echo ""
else
    echo "Testing Adzuna API..."
    echo "Query: software engineer in new york"
    echo ""

    ADZUNA_URL="https://api.adzuna.com/v1/api/jobs/us/search/1"
    ADZUNA_PARAMS="app_id=${ADZUNA_APP_ID}&app_key=${ADZUNA_APP_KEY}&what=software%20engineer&where=new%20york&results_per_page=3"

    echo "Fetching: ${ADZUNA_URL}?${ADZUNA_PARAMS}"
    echo ""

    # Make request and save to file
    curl -s "${ADZUNA_URL}?${ADZUNA_PARAMS}" > /tmp/adzuna_response.json

    # Check if successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Request successful${NC}"
        echo ""

        # Count jobs
        JOB_COUNT=$(jq '.results | length' /tmp/adzuna_response.json 2>/dev/null || echo "0")
        echo "Jobs returned: $JOB_COUNT"
        echo ""

        if [ "$JOB_COUNT" -gt 0 ]; then
            echo "Analyzing first job:"
            echo ""

            # Extract first job details
            TITLE=$(jq -r '.results[0].title' /tmp/adzuna_response.json 2>/dev/null || echo "N/A")
            COMPANY=$(jq -r '.results[0].company.display_name' /tmp/adzuna_response.json 2>/dev/null || echo "N/A")
            DESCRIPTION=$(jq -r '.results[0].description' /tmp/adzuna_response.json 2>/dev/null || echo "N/A")
            REDIRECT_URL=$(jq -r '.results[0].redirect_url' /tmp/adzuna_response.json 2>/dev/null || echo "N/A")

            echo "Title: $TITLE"
            echo "Company: $COMPANY"
            echo ""
            echo "Description (first 200 chars):"
            echo -e "${BLUE}${DESCRIPTION:0:200}...${NC}"
            echo ""

            # Count words in description
            WORD_COUNT=$(echo "$DESCRIPTION" | wc -w)
            echo "Description word count: $WORD_COUNT"

            if [ "$WORD_COUNT" -lt 100 ]; then
                echo -e "${RED}Quality: SNIPPET - Only getting short summary${NC}"
                echo -e "${YELLOW}→ Need to fetch redirect_url for full description${NC}"
            elif [ "$WORD_COUNT" -lt 300 ]; then
                echo -e "${YELLOW}Quality: PARTIAL - Getting some content${NC}"
            else
                echo -e "${GREEN}Quality: FULL - Getting complete description${NC}"
            fi

            echo ""
            echo "Redirect URL available: $([ "$REDIRECT_URL" != "N/A" ] && echo -e "${GREEN}YES${NC}" || echo -e "${RED}NO${NC}")"
            if [ "$REDIRECT_URL" != "N/A" ]; then
                echo "URL: ${REDIRECT_URL:0:80}..."
            fi
        fi
    else
        echo -e "${RED}✗ Request failed${NC}"
    fi

    echo ""
fi

echo "======================================================================"
echo "TEST 2: JSEARCH API"
echo "======================================================================"
echo ""

if [ -z "$JSEARCH_API_KEY" ]; then
    echo -e "${RED}✗ JSearch API key not found in .env${NC}"
    echo "Set JSEARCH_API_KEY"
    echo ""
else
    echo "Testing JSearch API (Search endpoint)..."
    echo "Query: software engineer in new york"
    echo ""

    JSEARCH_URL="https://jsearch.p.rapidapi.com/search"

    # Make request
    curl -s \
        -H "X-RapidAPI-Key: ${JSEARCH_API_KEY}" \
        -H "X-RapidAPI-Host: jsearch.p.rapidapi.com" \
        "${JSEARCH_URL}?query=software%20engineer%20in%20new%20york&num_pages=1" \
        > /tmp/jsearch_response.json

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Request successful${NC}"
        echo ""

        # Count jobs
        JOB_COUNT=$(jq '.data | length' /tmp/jsearch_response.json 2>/dev/null || echo "0")
        echo "Jobs returned: $JOB_COUNT"
        echo ""

        if [ "$JOB_COUNT" -gt 0 ]; then
            echo "Analyzing first job:"
            echo ""

            # Extract first job details
            TITLE=$(jq -r '.data[0].job_title' /tmp/jsearch_response.json 2>/dev/null || echo "N/A")
            COMPANY=$(jq -r '.data[0].employer_name' /tmp/jsearch_response.json 2>/dev/null || echo "N/A")
            DESCRIPTION=$(jq -r '.data[0].job_description' /tmp/jsearch_response.json 2>/dev/null || echo "N/A")
            JOB_ID=$(jq -r '.data[0].job_id' /tmp/jsearch_response.json 2>/dev/null || echo "N/A")

            echo "Title: $TITLE"
            echo "Company: $COMPANY"
            echo ""
            echo "Description (first 200 chars):"
            echo -e "${BLUE}${DESCRIPTION:0:200}...${NC}"
            echo ""

            # Count words
            WORD_COUNT=$(echo "$DESCRIPTION" | wc -w)
            echo "Description word count: $WORD_COUNT"

            if [ "$WORD_COUNT" -lt 100 ]; then
                echo -e "${RED}Quality: SNIPPET - Only getting short summary${NC}"
            elif [ "$WORD_COUNT" -lt 300 ]; then
                echo -e "${YELLOW}Quality: PARTIAL - Getting some content${NC}"
            else
                echo -e "${GREEN}Quality: FULL - Getting complete description${NC}"
            fi

            echo ""
            echo "Job ID available: $([ "$JOB_ID" != "N/A" ] && echo -e "${GREEN}YES${NC}" || echo -e "${RED}NO${NC}")"
            if [ "$JOB_ID" != "N/A" ]; then
                echo "Job ID: $JOB_ID"
                echo -e "${YELLOW}→ Could fetch more details from /job-details endpoint${NC}"
            fi
        fi
    else
        echo -e "${RED}✗ Request failed${NC}"
    fi

    echo ""
fi

echo "======================================================================"
echo "SUMMARY"
echo "======================================================================"
echo ""

if [ -f /tmp/adzuna_response.json ]; then
    ADZUNA_WORDS=$(jq -r '.results[0].description' /tmp/adzuna_response.json 2>/dev/null | wc -w || echo "0")
    echo "Adzuna:"
    echo "  Average word count: $ADZUNA_WORDS"
    if [ "$ADZUNA_WORDS" -lt 100 ]; then
        echo -e "  Status: ${RED}NEEDS FIX - Getting snippets only${NC}"
        echo "  Action: Must fetch redirect_url for full descriptions"
    elif [ "$ADZUNA_WORDS" -lt 300 ]; then
        echo -e "  Status: ${YELLOW}PARTIAL - May need improvement${NC}"
    else
        echo -e "  Status: ${GREEN}OK - Getting full descriptions${NC}"
    fi
    echo ""
fi

if [ -f /tmp/jsearch_response.json ]; then
    JSEARCH_WORDS=$(jq -r '.data[0].job_description' /tmp/jsearch_response.json 2>/dev/null | wc -w || echo "0")
    echo "JSearch:"
    echo "  Average word count: $JSEARCH_WORDS"
    if [ "$JSEARCH_WORDS" -lt 100 ]; then
        echo -e "  Status: ${RED}NEEDS FIX - Getting snippets only${NC}"
        echo "  Action: Use /job-details endpoint with job_id"
    elif [ "$JSEARCH_WORDS" -lt 300 ]; then
        echo -e "  Status: ${YELLOW}PARTIAL - May need improvement${NC}"
    else
        echo -e "  Status: ${GREEN}OK - Getting full descriptions${NC}"
    fi
    echo ""
fi

echo "======================================================================"
echo ""
echo "Response files saved to:"
echo "  /tmp/adzuna_response.json"
echo "  /tmp/jsearch_response.json"
echo ""
echo "View full responses with:"
echo "  cat /tmp/adzuna_response.json | jq ."
echo "  cat /tmp/jsearch_response.json | jq ."
echo ""

# Cleanup
# rm -f /tmp/adzuna_response.json /tmp/jsearch_response.json
