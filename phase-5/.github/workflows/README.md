# [Task]: T124
# [Spec]: F-011 (US13)
# [Description]: Documentation for GitHub Actions workflows and required secrets

# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for building and deploying the TaskAI application.

## Workflows

### 1. Build Workflow (`build.yaml`)

Builds and pushes Docker images for all services when changes are detected.

**Triggers:**
- Push to `main` or `develop` branches (with path filtering)
- Pull requests to `main` (build only, no push)
- Manual dispatch with service selection

**Services Built:**
- `backend` - FastAPI backend API
- `frontend` - Next.js frontend application
- `notification-service` - Reminder notification handler
- `recurring-service` - Recurring task processor

### 2. Deploy Workflow (`deploy.yaml`)

Deploys the application to staging or production Kubernetes clusters.

**Triggers:**
- Push to `main` branch → Deploy to staging
- Push of version tag (`v*.*.*`) → Deploy to production
- Manual dispatch with environment selection

**Features:**
- Atomic Helm deployments (automatic rollback on failure)
- Deployment verification with rollout status checks
- Slack notifications for deployment status

## Required Secrets

Configure these secrets in your GitHub repository settings:

### Container Registry

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Automatically provided, used for GHCR authentication |

### Kubernetes Clusters

| Secret | Description |
|--------|-------------|
| `STAGING_KUBECONFIG` | Kubeconfig for staging Kubernetes cluster |
| `PRODUCTION_KUBECONFIG` | Kubeconfig for production Kubernetes cluster |

### Notifications (Optional)

| Secret | Description |
|--------|-------------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL for deployment notifications |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL (alternative to Slack) |

### Application Secrets

These should be configured in your Kubernetes clusters, not GitHub:

| Secret Name | Keys | Description |
|-------------|------|-------------|
| `database-credentials` | `username`, `password` | Database credentials |
| `redpanda-credentials` | `brokers`, `username`, `password` | Redpanda Cloud credentials |
| `app-secrets` | `secret-key` | Application secret key |

## Required Variables

Configure these variables in your GitHub repository settings:

| Variable | Description | Example |
|----------|-------------|---------|
| `STAGING_URL` | URL of staging environment | `https://staging.todo.example.com` |
| `PRODUCTION_URL` | URL of production environment | `https://todo.example.com` |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend | `https://api.todo.example.com` |

## Environment Setup

### Creating Kubernetes Secrets

1. **Database Credentials:**
   ```bash
   kubectl create secret generic database-credentials \
     --from-literal=username=<db-user> \
     --from-literal=password=<db-password> \
     -n todo-app-staging
   ```

2. **Redpanda Cloud Credentials:**
   ```bash
   kubectl create secret generic redpanda-credentials \
     --from-literal=brokers=<broker-url>:9092 \
     --from-literal=username=<redpanda-user> \
     --from-literal=password=<redpanda-password> \
     -n todo-app-staging
   ```

3. **Application Secrets:**
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=secret-key=<your-secret-key> \
     -n todo-app-staging
   ```

### Setting Up Kubeconfig Secrets

1. Get your cluster kubeconfig:
   ```bash
   # For AKS
   az aks get-credentials --resource-group <rg> --name <cluster> --file kubeconfig.yaml

   # For GKE
   gcloud container clusters get-credentials <cluster> --zone <zone> --project <project>
   ```

2. Base64 encode and add to GitHub secrets:
   ```bash
   cat kubeconfig.yaml | base64 -w 0
   ```

### Setting Up Slack Notifications

1. Create a Slack App at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add to a channel and copy the webhook URL
4. Add `SLACK_WEBHOOK_URL` secret to GitHub

## Manual Deployment

You can manually trigger deployments from the Actions tab:

1. Go to Actions → Deploy to Kubernetes
2. Click "Run workflow"
3. Select environment (staging/production)
4. Optionally specify an image tag
5. Click "Run workflow"

## Rollback

If a deployment fails:

1. The `--atomic` flag ensures automatic rollback on failure
2. For manual rollback, use:
   ```bash
   helm rollback todo-chatbot <revision> -n <namespace>
   ```

## Monitoring Deployments

Check deployment status:
```bash
# View pods
kubectl get pods -n todo-app-staging

# View deployment history
helm history todo-chatbot -n todo-app-staging

# View logs
kubectl logs -f deployment/todo-chatbot-backend -n todo-app-staging
```
