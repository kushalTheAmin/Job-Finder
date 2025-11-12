# Google Cloud Deployment Guide

This guide will help you deploy the Job Finder system to Google Cloud.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. A **Google Cloud Project** created

## Step 1: Enable Required APIs

Run these commands to enable necessary APIs:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable gmail.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 2: Set Up Firestore

1. Go to [Firestore Console](https://console.cloud.google.com/firestore)
2. Click **Create Database**
3. Select **Native Mode**
4. Choose a location (e.g., `us-central1`)
5. Click **Create**

## Step 3: Create Service Account

```bash
# Create service account
gcloud iam service-accounts create job-finder-sa \
    --display-name="Job Finder Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:job-finder-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:job-finder-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/datastore.user"

# Create and download key
gcloud iam service-accounts keys create ../service-account-key.json \
    --iam-account=job-finder-sa@$PROJECT_ID.iam.gserviceaccount.com
```

## Step 4: Configure Gmail

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Enable 2-Step Verification if not already enabled
4. Go to **App Passwords**
5. Generate a new app password for "Mail"
6. Save this password for your `.env` file

## Step 5: Set Up Google Drive

1. Go to [Google Drive](https://drive.google.com)
2. Create a new folder called "Job Finder Resumes"
3. Open the folder and get the folder ID from the URL:
   - URL format: `https://drive.google.com/drive/folders/FOLDER_ID`
   - Copy the `FOLDER_ID` part
4. Save this ID for your `.env` file

## Step 6: Get API Keys

### Adzuna API
1. Go to [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Sign up for free account
3. Get your App ID and App Key

### JSearch API (RapidAPI)
1. Go to [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Sign up for free account
3. Subscribe to free tier
4. Get your API key

## Step 7: Configure Environment

Create `.env` file in project root:

```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json

# Adzuna API
ADZUNA_APP_ID=your-app-id
ADZUNA_APP_KEY=your-app-key

# JSearch API
JSEARCH_API_KEY=your-rapidapi-key

# Gmail
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
```

## Step 8: Update Configuration

Edit `config.yaml` with your preferences:

```yaml
google_cloud:
  project_id: "your-project-id"

notifications:
  email_to: "your.email@gmail.com"
  google_drive_folder_id: "your-folder-id"
```

## Step 9: Deploy to Google Cloud

Run the deployment script:

```bash
cd deploy
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Deploy the Cloud Function
- Set up Cloud Scheduler (if you choose)
- Configure automatic daily runs

## Step 10: Test the Deployment

Test your function manually:

```bash
# Get function URL
FUNCTION_URL=$(gcloud functions describe job-finder --gen2 --region=us-central1 --format="value(serviceConfig.uri)")

# Trigger function
curl $FUNCTION_URL
```

Check logs:

```bash
gcloud functions logs read job-finder --gen2 --region=us-central1 --limit=50
```

## Alternative: Cloud Run Deployment

For longer execution times, deploy to Cloud Run:

```bash
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/job-finder

# Deploy to Cloud Run
gcloud run deploy job-finder \
    --image gcr.io/$PROJECT_ID/job-finder \
    --platform managed \
    --region us-central1 \
    --memory 2Gi \
    --timeout 3600 \
    --no-allow-unauthenticated
```

## Costs Estimate

Based on daily runs:

- **Cloud Functions/Run**: ~$2-5/month
- **Vertex AI (Gemini Flash)**: ~$3-8/month
- **Firestore**: ~$0-1/month
- **Cloud Storage**: ~$0.50/month
- **Gmail API**: Free
- **Drive API**: Free

**Total: ~$5-15/month**

## Monitoring

View logs in Cloud Console:
- [Cloud Functions Logs](https://console.cloud.google.com/functions)
- [Cloud Scheduler Jobs](https://console.cloud.google.com/cloudscheduler)
- [Firestore Data](https://console.cloud.google.com/firestore)

## Troubleshooting

### Function times out
- Increase timeout in `deploy.sh`
- Use Cloud Run instead of Cloud Functions

### Permission errors
- Check service account permissions
- Ensure all APIs are enabled

### Email not sending
- Verify Gmail app password is correct
- Check 2-Step Verification is enabled

### Scraping fails
- Web scrapers may need updates
- Consider using only API sources

## Support

For issues, check logs and refer to the main README.md file.
