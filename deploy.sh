#!/bin/bash
# ====================================================================
# Cloud Run Deployment Script for Research Pilot
# ====================================================================
set -e

SERVICE_NAME="research-pilot-service"
REGION="us-central1"
SECRET_NAME="GEMINI_API_KEY"

# Color formatting
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}Starting Cloud Run Pre-stage and Deployment Pipeline${NC}"
echo -e "${BLUE}====================================================${NC}"

# 1. Check for active gcloud project
echo -e "\n${GREEN}[1/5] Checking active gcloud project setting...${NC}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "Error: No active Google Cloud Project configured."
    echo "Please set your project using: gcloud config set project <PROJECT-ID>"
    exit 1
fi
echo -e "Target GCP Project: ${GREEN}$PROJECT_ID${NC}"

# 2. Enable Google APIs
echo -e "\n${GREEN}[2/5] Enabling required APIs (Cloud Run, Secret Manager, Vertex AI)...${NC}"
gcloud services enable \
    run.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com

# 3. Handle Secret Manager API keys
echo -e "\n${GREEN}[3/5] Checking Google Cloud Secret Manager for $SECRET_NAME...${NC}"
SECRET_EXISTS=$(gcloud secrets list --filter="name:$SECRET_NAME" --format="value(name)" 2>/dev/null)

if [ -z "$SECRET_EXISTS" ]; then
    echo "Secret '$SECRET_NAME' was not found. Creating placeholder..."
    gcloud secrets create "$SECRET_NAME" --replication-policy="automatic"
    echo -e "Placeholder created. Please upload your Gemini API key by running:"
    echo -e "  ${BLUE}echo -n 'YOUR_API_KEY' | gcloud secrets versions add $SECRET_NAME --data-file=-${NC}"
else
    echo -e "Secret '$SECRET_NAME' exists and is ready for runtime usage."
fi

# 4. Build image using Cloud Build (remote Docker build)
echo -e "\n${GREEN}[4/5] Packaging container image and submitting to Cloud Build...${NC}"
IMAGE_URI="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"
gcloud builds submit --tag "$IMAGE_URI" .

# 5. Deploy to Cloud Run
echo -e "\n${GREEN}[5/5] Deploying container to Cloud Run...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_URI" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --set-secrets="GEMINI_API_KEY=${SECRET_NAME}:latest" \
    --no-cpu-throttling

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}Cloud Run Deployment stage successfully prepared!${NC}"
echo -e "${GREEN}====================================================${NC}"
