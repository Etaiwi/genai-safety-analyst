# Deployment Guide

This document describes how to deploy the GenAI Safety Analyst service to Hugging Face Spaces and Google Cloud Run.

## Hugging Face Spaces (Recommended)

Hugging Face Spaces provides a simple and free way to deploy machine learning applications with automatic scaling and SSL certificates.

### Prerequisites

1. A Hugging Face account
2. A Groq API key
3. A Hugging Face access token (recommended for reliable model downloads)

### Deployment Steps

1. **Fork the Repository**
   - Go to the [GenAI Safety Analyst repository](https://huggingface.co/spaces) on Hugging Face
   - Fork it to your account (or upload your modified version)

2. **Create a New Space**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose:
     - Space name: `genai-safety-analyst` (or your preferred name)
     - License: Select appropriate license
     - SDK: `Docker`
     - Visibility: `Public` or `Private`

3. **Connect Repository**
   - Select "Connect your repository" option
   - Choose your forked repository

4. **Configure Secrets**
   - In your Space settings, go to "Settings" → "Secrets"
   - Add the following secrets:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     HF_TOKEN=your_huggingface_token_here
     MAX_TEXT_CHARS=1200
     RATE_LIMIT_MAX_REQUESTS=20
     RATE_LIMIT_WINDOW_SECONDS=60
     ```

5. **Deploy**
   - HF Spaces will automatically build and deploy your application
   - The build process may take 10-20 minutes
   - Once deployed, your app will be available at `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

### Updating Your Space

When you make code changes:

1. Push changes to your repository
2. HF Spaces will automatically rebuild and redeploy

### Hardware Requirements

- **Memory**: At least 2GB RAM (recommended) or 1GB (minimum)
- **Storage**: ~500MB for models and dependencies

---

## Google Cloud Run

This section describes deployment to Google Cloud Run using Docker and Artifact Registry.

The same container image can be deployed to other environments (for example, a VM or another container platform), but this guide focuses on Cloud Run.

---

## 1. Prerequisites

1. A Google Cloud project.
2. `gcloud` CLI installed and initialized:

   ```bash
   gcloud init
   gcloud auth login
   ```

3. Docker installed locally.
4. A Groq API key and a Hugging Face access token (for model downloads).
5. The following APIs enabled in the Google Cloud project:

   ```bash
   gcloud services enable      run.googleapis.com      artifactregistry.googleapis.com
   ```

---

## 2. Variables

Set the following shell variables to avoid repeating values (adjust to your environment):

```bash
PROJECT_ID=<your-gcp-project-id>
REGION=us-central1
REPO_NAME=genai-repo
IMAGE_NAME=genai-safety-analyst
SERVICE_NAME=genai-safety-analyst
```

---

## 3. Create an Artifact Registry Repository

Create a Docker repository in Artifact Registry (one-time step):

```bash
gcloud artifacts repositories create $REPO_NAME   --repository-format=docker   --location=$REGION
```

If the repository already exists, this command will fail with an error indicating that it already exists; in that case, it can be ignored.

Configure Docker to authenticate with Artifact Registry for the chosen region:

```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

---

## 4. Build and Push the Docker Image

From the project root (where the `Dockerfile` is located), build the image:

```bash
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest .
```

Push the image to Artifact Registry:

```bash
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest
```

---

## 5. First Deployment to Cloud Run

Deploy the image as a Cloud Run service:

```bash
gcloud run deploy $SERVICE_NAME   --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest   --platform managed   --region $REGION   --allow-unauthenticated   --memory=1Gi   --set-env-vars="GROQ_API_KEY=<your-groq-api-key>,HF_TOKEN=<your-hf-token>,MAX_TEXT_CHARS=1200,RATE_LIMIT_MAX_REQUESTS=20,RATE_LIMIT_WINDOW_SECONDS=60"
```

Notes:

- `--memory=1Gi` is important because loading the sentence-transformer embeddings model and running the vector store can exceed the default 512 MiB memory limit.
- If a demo token is required to protect the public UI, it can be added to the `--set-env-vars` string as `DEMO_TOKEN=<some-secret-value>`.

After a successful deployment, the command prints a `Service URL`. This is the HTTPS URL of the deployed service.

---

## 6. Updating the Service

When code changes are made:

1. Rebuild and push the image:

   ```bash
   docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest .
   docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest
   ```

2. Redeploy the Cloud Run service:

   ```bash
   gcloud run deploy $SERVICE_NAME      --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest      --platform managed      --region $REGION      --allow-unauthenticated      --memory=1Gi
   ```

If environment variables do not need to change, they do not have to be passed again; Cloud Run keeps the previous configuration.

---

## 7. Verifying the Deployment

### 7.1 Health Check

Use a browser or curl:

```bash
curl https://<service-url>/health
```

A healthy service returns a small JSON payload, for example:

```json
{"status": "ok"}
```

### 7.2 Web UI and API Docs

- Web UI: `https://<service-url>/`
- OpenAPI / Swagger docs: `https://<service-url>/docs`

The UI allows entering text and submitting an analysis request. The docs page provides an interactive view of the available endpoints.

---

## 8. Logs and Troubleshooting

### 8.1 Viewing Logs

Use the Cloud Run logs command:

```bash
gcloud run services logs read $SERVICE_NAME --region $REGION --limit 100
```

Or use the Logs section in the Cloud Run web console to filter by service and revision.

### 8.2 Memory Errors

If logs show messages similar to:

> Memory limit of 512 MiB exceeded

increase the memory limit for the service:

```bash
gcloud run services update $SERVICE_NAME   --region $REGION   --memory=1Gi
```

### 8.3 Connectivity or Startup Errors

If the container fails to start:

- Verify that the image can be run locally with Docker.
- Confirm that required environment variables (`GROQ_API_KEY`, `HF_TOKEN`, and guardrail parameters) are set.
- Check that the application is listening on the port expected by Cloud Run (by default, the application is configured to listen on port 7860 inside the container, and Cloud Run routes traffic correctly to it).

---

## 9. Summary

After following these steps, the service runs as a managed container on Google Cloud Run, using Artifact Registry for image storage and environment variables for configuration. The deployment can be updated by rebuilding the Docker image, pushing it to Artifact Registry, and redeploying the Cloud Run service.

---

## HF Spaces Troubleshooting

### Build Failures

If the Space fails to build:

- Check the build logs in the Space settings
- Ensure all dependencies in `requirements.txt` are compatible with HF Spaces
- Verify that the Dockerfile uses the correct base image and exposes port 7860

### Runtime Errors

Common issues:

- **Missing API Keys**: Ensure `GROQ_API_KEY` secret is set in Space settings
- **Memory Issues**: If the app crashes due to memory, you may need to upgrade to a paid tier with more RAM
- **Model Download Issues**: If `HF_TOKEN` is not set, model downloads may fail or be rate-limited

### Accessing Logs

- Build logs: Available in Space settings under "Build" tab
- Runtime logs: Available in Space settings under "Logs" tab

---

## Summary

The GenAI Safety Analyst can be deployed to both Hugging Face Spaces (recommended for simplicity) and Google Cloud Run (for more control). HF Spaces provides automatic scaling, SSL certificates, and a user-friendly interface, while Cloud Run offers more customization options and integration with Google Cloud services.

Both deployment methods use the same Docker container and require:
- At least 1GB RAM
- GROQ_API_KEY environment variable
- Optional HF_TOKEN for reliable model downloads
