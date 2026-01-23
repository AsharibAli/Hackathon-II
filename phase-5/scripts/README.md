# TaskAI Deployment Scripts

Automated deployment scripts for deploying TaskAI services to DigitalOcean Kubernetes.

## Quick Start

### Deploy All Services
```bash
# Deploy all services with :latest tag
./scripts/deploy-all.sh

# Deploy all services with specific version
./scripts/deploy-all.sh v1.0.5

# Deploy specific services only
./scripts/deploy-all.sh --services=backend,frontend
```

### Deploy Individual Services

#### Backend
```bash
./scripts/deploy-backend.sh           # Deploy with :latest
./scripts/deploy-backend.sh v1.0.5    # Deploy with version tag
```

#### Recurring Service
```bash
./scripts/deploy-recurring-service.sh           # Deploy with :latest
./scripts/deploy-recurring-service.sh v1.0.5    # Deploy with version tag
```

#### Notification Service
```bash
./scripts/deploy-notification-service.sh           # Deploy with :latest
./scripts/deploy-notification-service.sh v1.0.5    # Deploy with version tag
```

#### Frontend
```bash
./scripts/deploy-frontend.sh           # Deploy with :latest
./scripts/deploy-frontend.sh v1.0.5    # Deploy with version tag
```

---

## What These Scripts Do

Each deployment script performs the following steps:

1. **Build Docker Image** - Builds the service's Docker image locally
2. **Login to Registry** - Authenticates with DigitalOcean Container Registry
3. **Push Image** - Pushes the built image to the registry
4. **Update Deployment** - Updates the Kubernetes deployment with the new image
5. **Wait for Rollout** - Waits for the rollout to complete (with 5min timeout)
6. **Show Status** - Displays current pod status and running image
7. **Optional Logs** - Prompts to show recent application logs

---

## Prerequisites

Before running these scripts, ensure you have:

1. **doctl CLI** - DigitalOcean CLI tool
   ```bash
   # Install on macOS
   brew install doctl

   # Install on Linux
   cd ~
   wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
   tar xf ~/doctl-1.98.1-linux-amd64.tar.gz
   sudo mv ~/doctl /usr/local/bin
   ```

2. **kubectl** - Kubernetes CLI tool
   ```bash
   # Should already be configured if you deployed the cluster
   kubectl version
   ```

3. **Docker** - Docker engine running locally
   ```bash
   docker --version
   ```

4. **Authentication**
   ```bash
   # Login to DigitalOcean
   doctl auth init

   # Get kubeconfig for your cluster
   doctl kubernetes cluster kubeconfig save taskai-cluster

   # Verify connection
   kubectl get nodes
   ```

---

## Script Details

### deploy-all.sh
Master script that orchestrates deployment of multiple services.

**Features:**
- Deploy all services or select specific ones
- Consistent version across all services
- Error handling with user prompts
- Deployment summary with timing
- Colored output for better readability

**Examples:**
```bash
# Deploy everything
./scripts/deploy-all.sh

# Deploy with version v1.2.0
./scripts/deploy-all.sh v1.2.0

# Deploy only backend and frontend
./scripts/deploy-all.sh --services=backend,frontend

# Deploy specific services with version
./scripts/deploy-all.sh v1.2.0 --services=recurring-service,notification-service
```

### deploy-backend.sh
Deploys the FastAPI backend service.

**Details:**
- Builds from `./backend` directory
- Container name: `backend`
- Deployment: `todo-chatbot-backend`
- Replicas: 3 (high availability)
- Includes Dapr sidecar for event publishing
- Health endpoint: `/health`

**Monitors:**
- Pod status (should show 2/2 READY with Dapr)
- Dapr sidecar status
- Running image version

### deploy-recurring-service.sh
Deploys the recurring tasks service.

**Details:**
- Builds from `./recurring-service` directory
- Container name: `recurring-service`
- Deployment: `todo-chatbot-recurring-service`
- Replicas: 1
- Includes Dapr sidecar for event consumption
- Subscribes to: `task-events` topic

**Monitors:**
- Pod status (should show 2/2 READY with Dapr)
- Dapr subscription status
- Kafka topic subscription

**Verifies:**
- Dapr sidecar enabled
- Subscription `task-events-subscription` exists

### deploy-notification-service.sh
Deploys the notification service.

**Details:**
- Builds from `./notification-service` directory
- Container name: `notification-service`
- Deployment: `todo-chatbot-notification-service`
- Replicas: 1
- Includes Dapr sidecar for event consumption
- Subscribes to: `reminders` topic

**Monitors:**
- Pod status (should show 2/2 READY with Dapr)
- Dapr subscription status
- Kafka topic subscription

**Verifies:**
- Dapr sidecar enabled
- Subscription `reminders-subscription` exists

### deploy-frontend.sh
Deploys the Next.js/React frontend.

**Details:**
- Builds from `./frontend` directory
- Container name: `frontend`
- Deployment: `todo-chatbot-frontend`
- Replicas: 1
- No Dapr sidecar (not needed)
- Public URL: https://taskai.asharib.xyz

**Monitors:**
- Pod status (should show 1/1 READY)
- Running image version
- Frontend accessibility

---

## Version Management

### Using :latest Tag (Development)
```bash
./scripts/deploy-backend.sh
```

**Behavior:**
- Builds with `:latest` tag
- Uses `kubectl rollout restart` to force pull
- Requires `imagePullPolicy: Always` in deployment
- Best for rapid iteration

### Using Version Tags (Production)
```bash
./scripts/deploy-backend.sh v1.0.5
```

**Behavior:**
- Builds with specific version tag (e.g., `v1.0.5`)
- Uses `kubectl set image` to update deployment
- Enables rollback to previous versions
- Best for production deployments

**Recommended Versioning:**
- `v1.0.0` - Major releases
- `v1.0.1` - Bug fixes
- `v1.1.0` - New features
- Follow [Semantic Versioning](https://semver.org/)

---

## Troubleshooting

### Script Fails at Docker Build
**Symptom:** `❌ Docker build failed!`

**Solutions:**
1. Check Docker is running: `docker ps`
2. Check Dockerfile exists in service directory
3. Review build logs for syntax errors
4. Ensure all dependencies are available

### Script Fails at Registry Login
**Symptom:** `Registry login failed`

**Solutions:**
1. Verify doctl is installed: `doctl version`
2. Re-authenticate: `doctl auth init`
3. Check registry exists: `doctl registry get`
4. Try manual login: `doctl registry login`

### Script Fails at Docker Push
**Symptom:** `❌ Docker push failed!`

**Solutions:**
1. Verify registry authentication
2. Check image tag format matches registry
3. Ensure sufficient registry space
4. Check network connectivity

### Script Fails at Kubernetes Update
**Symptom:** `❌ Kubernetes update failed!`

**Solutions:**
1. Verify kubectl is configured: `kubectl get nodes`
2. Check namespace exists: `kubectl get ns todo-app`
3. Verify deployment exists: `kubectl get deployment -n todo-app`
4. Check RBAC permissions

### Rollout Times Out
**Symptom:** `❌ Rollout failed or timed out!`

**Solutions:**
1. Check pod events:
   ```bash
   kubectl get events -n todo-app --sort-by='.lastTimestamp'
   ```

2. Check pod logs:
   ```bash
   kubectl logs -n todo-app <pod-name>
   ```

3. Describe pod for details:
   ```bash
   kubectl describe pod -n todo-app <pod-name>
   ```

4. Common issues:
   - Image pull errors (check registry authentication)
   - Insufficient resources (check node capacity)
   - Configuration errors (check environment variables)
   - Health check failures (check /health endpoint)

### Dapr Sidecar Not Starting
**Symptom:** Pods show 1/2 READY instead of 2/2

**Solutions:**
1. Check Dapr is installed:
   ```bash
   kubectl get pods -n dapr-system
   ```

2. Check Dapr annotation in deployment:
   ```bash
   kubectl get deployment todo-chatbot-backend -n todo-app -o yaml | grep dapr
   ```

3. View Dapr sidecar logs:
   ```bash
   kubectl logs -n todo-app <pod-name> -c daprd
   ```

4. Verify Dapr components:
   ```bash
   kubectl get component -n todo-app
   ```

### Frontend Not Accessible
**Symptom:** Cannot access https://taskai.asharib.xyz

**Solutions:**
1. Check frontend pods are running:
   ```bash
   kubectl get pods -n todo-app -l app.kubernetes.io/name=frontend
   ```

2. Check service exists:
   ```bash
   kubectl get svc -n todo-app
   ```

3. Check ingress:
   ```bash
   kubectl get ingress -n todo-app
   ```

4. Test internal connectivity:
   ```bash
   kubectl port-forward -n todo-app svc/todo-chatbot-frontend 3000:3000
   ```

---

## Advanced Usage

### Manual Rollback
If a deployment fails, rollback to previous version:

```bash
# View rollout history
kubectl rollout history deployment/todo-chatbot-backend -n todo-app

# Rollback to previous version
kubectl rollout undo deployment/todo-chatbot-backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/todo-chatbot-backend -n todo-app --to-revision=2
```

### View Deployment Status
```bash
# All deployments
kubectl get deployments -n todo-app

# All pods with details
kubectl get pods -n todo-app -o wide

# Watch pod status in real-time
kubectl get pods -n todo-app -w

# View resource usage
kubectl top pods -n todo-app
```

### View Application Logs
```bash
# Backend logs (application container)
kubectl logs -n todo-app -l app.kubernetes.io/name=backend -c backend --tail=100 -f

# Backend logs (Dapr sidecar)
kubectl logs -n todo-app -l app.kubernetes.io/name=backend -c daprd --tail=100 -f

# Recurring service logs
kubectl logs -n todo-app -l app.kubernetes.io/name=recurring-service -c recurring-service --tail=100 -f

# Notification service logs
kubectl logs -n todo-app -l app.kubernetes.io/name=notification-service -c notification-service --tail=100 -f

# Frontend logs
kubectl logs -n todo-app -l app.kubernetes.io/name=frontend --tail=100 -f
```

### Scale Deployments
```bash
# Scale backend to 5 replicas
kubectl scale deployment todo-chatbot-backend -n todo-app --replicas=5

# Scale recurring service to 2 replicas
kubectl scale deployment todo-chatbot-recurring-service -n todo-app --replicas=2

# View current replicas
kubectl get deployment -n todo-app
```

### Debug Pod Issues
```bash
# Get detailed pod information
kubectl describe pod -n todo-app <pod-name>

# Execute command in pod
kubectl exec -it -n todo-app <pod-name> -c backend -- bash

# Copy files from pod
kubectl cp todo-app/<pod-name>:/app/logs ./logs -c backend

# View pod resource usage
kubectl top pod -n todo-app <pod-name>
```

---

## CI/CD Integration

These scripts can be integrated into CI/CD pipelines:

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Save kubeconfig
        run: doctl kubernetes cluster kubeconfig save taskai-cluster

      - name: Deploy all services
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          ./scripts/deploy-all.sh $VERSION
```

---

## Related Documentation

- [DEPLOYMENT-ANALYSIS.md](../DEPLOYMENT-ANALYSIS.md) - Complete deployment analysis
- [DEPLOY-DAPR-GUIDE.md](../DEPLOY-DAPR-GUIDE.md) - Dapr deployment guide
- [DEPLOYMENT-SUCCESS.md](../DEPLOYMENT-SUCCESS.md) - Testing instructions

---

## Support

For issues with deployment scripts:

1. Check logs with `-f` flag for real-time output
2. Review pod events: `kubectl get events -n todo-app`
3. Verify prerequisites are met (doctl, kubectl, docker)
4. Check cluster connectivity: `kubectl get nodes`

---

**Last Updated:** 2026-01-22
**Cluster:** do-sgp1-taskai-cluster
**Namespace:** todo-app
**Registry:** registry.digitalocean.com/taskai-registry
