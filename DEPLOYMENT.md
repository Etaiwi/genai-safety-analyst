# Deployment Guide – Google Cloud Run

This document describes how to deploy the GenAI Safety Analyst service to Google Cloud Run using Docker and Artifact Registry.

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
- Check that the application is listening on the port expected by Cloud Run (by default, the application is configured to listen on port 8000 inside the container, and Cloud Run routes traffic correctly to it).

---

## 9. Summary

After following these steps, the service runs as a managed container on Google Cloud Run, using Artifact Registry for image storage and environment variables for configuration. The deployment can be updated by rebuilding the Docker image, pushing it to Artifact Registry, and redeploying the Cloud Run service.
