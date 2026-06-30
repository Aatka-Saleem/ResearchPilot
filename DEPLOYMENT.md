# Deployment and Onboarding Guide (DEPLOYMENT.md)

This guide details the steps to set up, test, containerize, and deploy `research-pilot` locally and to the cloud.

---

## 💻 Local Setup & Execution

### Prerequisites
* **Python**: Version `3.13` or higher.
* **uv**: Astral's package manager. If not installed, get it via:
  ```bash
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 1. Initialize and Install Dependencies
Sync virtual environment and lockfiles:
```bash
uv sync
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Google Gemini API Key:
```env
GEMINI_API_KEY=AIzaSy...
```

### 3. Run Pipeline CLI
Run a research flow on any topic:
```bash
uv run main.py --topic "RAG Evaluation Frameworks and ROUGE/BLEU limitations"
```

### 4. Run Verification Suite
Run local unit tests:
```bash
uv run python -m unittest discover -s tests
```

---

## 🐳 Local Containerization

### 1. Build Docker Image
To verify Docker building locally:
```bash
docker build -t research-pilot:latest .
```

### 2. Run Container Locally
To run the container, pass the API key as an environment variable and mount a directory to capture the output files:
```bash
docker run --env GEMINI_API_KEY="AIzaSy..." -v "$(pwd)/output:/app/output" research-pilot:latest --topic "Quantum cryptanalysis"
```

---

## ☁️ Google Cloud Platform Deployment

Our container is optimized to run as a secure Cloud Run service, drawing the Google Gemini API key dynamically from GCP Secret Manager at launch.

### Step 1: Install & Login to gcloud SDK
Make sure you are authenticated with active billing:
```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

### Step 2: Configure Secret Manager
Create and record the runtime secret:
```bash
gcloud secrets create GEMINI_API_KEY --replication-policy="automatic"
echo -n "YOUR_GEMINI_API_KEY_HERE" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
```

### Step 3: Run Deployment Automation Script
Make `deploy.sh` executable and run it to compile, package, and deploy automatically:
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Enable `run.googleapis.com` (Cloud Run), `secretmanager.googleapis.com`, and `aiplatform.googleapis.com` (Vertex AI).
2. Remote build the container image using **Cloud Build**.
3. Deploy the container to **Cloud Run**, attaching the secret to the `GEMINI_API_KEY` environment variable.
