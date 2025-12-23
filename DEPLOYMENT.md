# Deployment (Google Cloud Run)

This project is deployed as a containerized FastAPI service on **Google Cloud Run**.

Cloud Run runs containers behind an HTTPS endpoint, can scale to zero when idle, and is well-suited for portfolio demos.

---

## Prerequisites

- A Google Cloud account
- A Google Cloud project
- Billing enabled on the project (Cloud Run has a free tier, but Google still requires billing to be enabled)
- Installed tools:
  - Google Cloud SDK (`gcloud`)
  - Docker

---

## 1) Authenticate and select project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth configure-docker
```

---

## 2) Build and push the container image

### Option A: Build with Cloud Build (recommended)
This builds in Google Cloud and pushes to Artifact Registry.

Enable APIs:
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Create a repository (one time):
```bash
gcloud artifacts repositories create genai-repo \
  --repository-format=docker \
  --location=us-central1
```

Build and push:
```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/genai-repo/genai-safety-analyst:latest
```

---

## 3) Deploy to Cloud Run

```bash
gcloud run deploy genai-safety-analyst \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/genai-repo/genai-safety-analyst:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

Cloud Run will provide a public HTTPS URL.

---

## 4) Set environment variables

```bash
gcloud run services update genai-safety-analyst \
  --region us-central1 \
  --set-env-vars GROQ_API_KEY=YOUR_KEY,MAX_TEXT_CHARS=1200,RATE_LIMIT_MAX_REQUESTS=20,RATE_LIMIT_WINDOW_SECONDS=60
```

---

## 5) Verify

- Open the Cloud Run URL in a browser.
- UI should load at `/`
- API docs should load at `/docs`
- Health check: `/health`

---

## Troubleshooting

Check logs:
```bash
gcloud run services logs read genai-safety-analyst --region us-central1
```
