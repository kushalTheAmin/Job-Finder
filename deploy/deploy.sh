#!/bin/bash
# Deployment script for Google Cloud Functions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Job Finder - Cloud Function Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Load project configuration
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Check required variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "${RED}Error: GOOGLE_CLOUD_PROJECT not set in .env${NC}"
    exit 1
fi

# Configuration
FUNCTION_NAME="job-finder"
REGION="us-central1"
RUNTIME="python311"
ENTRY_POINT="job_finder_handler"
MEMORY="2048MB"
TIMEOUT="540s"  # 9 minutes (max for Cloud Functions is 540s)

echo -e "\n${YELLOW}Deployment Configuration:${NC}"
echo "  Project: $GOOGLE_CLOUD_PROJECT"
echo "  Function: $FUNCTION_NAME"
echo "  Region: $REGION"
echo "  Runtime: $RUNTIME"
echo "  Memory: $MEMORY"
echo "  Timeout: $TIMEOUT"

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Copy necessary files to deploy directory
echo -e "\n${YELLOW}Preparing deployment files...${NC}"
cp -r ../src .
cp -r ../data .
cp ../config.yaml .
cp ../.env .

# Deploy Cloud Function
echo -e "\n${YELLOW}Deploying Cloud Function...${NC}"
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=$RUNTIME \
    --region=$REGION \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --memory=$MEMORY \
    --timeout=$TIMEOUT \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
    --project=$GOOGLE_CLOUD_PROJECT

# Clean up temporary files
echo -e "\n${YELLOW}Cleaning up...${NC}"
rm -rf src data config.yaml .env

# Get function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --project=$GOOGLE_CLOUD_PROJECT --format="value(serviceConfig.uri)")

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Function URL: ${YELLOW}$FUNCTION_URL${NC}"

# Set up Cloud Scheduler
echo -e "\n${YELLOW}Do you want to set up Cloud Scheduler? (y/n)${NC}"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    JOB_NAME="job-finder-daily"
    SCHEDULE="0 8 * * *"  # 8 AM daily
    TIMEZONE="America/New_York"

    echo -e "${YELLOW}Setting up Cloud Scheduler...${NC}"

    # Check if job already exists
    if gcloud scheduler jobs describe $JOB_NAME --location=$REGION --project=$GOOGLE_CLOUD_PROJECT &> /dev/null; then
        echo "Job already exists. Updating..."
        gcloud scheduler jobs update http $JOB_NAME \
            --location=$REGION \
            --schedule="$SCHEDULE" \
            --uri="$FUNCTION_URL" \
            --http-method=GET \
            --time-zone="$TIMEZONE" \
            --project=$GOOGLE_CLOUD_PROJECT
    else
        echo "Creating new job..."
        gcloud scheduler jobs create http $JOB_NAME \
            --location=$REGION \
            --schedule="$SCHEDULE" \
            --uri="$FUNCTION_URL" \
            --http-method=GET \
            --time-zone="$TIMEZONE" \
            --project=$GOOGLE_CLOUD_PROJECT
    fi

    echo -e "${GREEN}Cloud Scheduler configured successfully!${NC}"
    echo -e "Schedule: ${YELLOW}$SCHEDULE ($TIMEZONE)${NC}"
fi

echo -e "\n${GREEN}All done! Your Job Finder is now running on Google Cloud.${NC}"
