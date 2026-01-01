# Quickstart: Phase 5 Advanced Cloud Deployment

**Feature**: 004-phase5-cloud-deployment
**Date**: 2025-12-25

## Prerequisites

### Required Tools
| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | Latest | [docker.com](https://docker.com) |
| Minikube | 1.32+ | `winget install minikube` |
| kubectl | 1.28+ | `winget install kubectl` |
| Helm | 3.x | `winget install helm` |
| Dapr CLI | 1.12+ | `winget install dapr` |
| uv | Latest | `pip install uv` |
| pnpm | 8+ | `npm install -g pnpm` |

### Verify Installation
```bash
docker --version
minikube version
kubectl version --client
helm version
dapr --version
uv --version
pnpm --version
```

---

## Quick Deploy (Minikube)

### One-Command Setup
```bash
# From project root
./scripts/deploy-minikube.sh
```

This script:
1. Starts Minikube
2. Initializes Dapr
3. Deploys Strimzi/Kafka
4. Applies Dapr components
5. Deploys all services via Helm
6. Runs verification

### Manual Step-by-Step

#### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
```

#### 2. Initialize Dapr
```bash
dapr init -k --wait
dapr status -k
```

#### 3. Install Strimzi Kafka Operator
```bash
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

#### 4. Deploy Kafka Cluster
```bash
kubectl apply -f dapr/components/kafka-cluster.yaml -n kafka
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=300s -n kafka
```

#### 5. Create Application Namespace
```bash
kubectl create namespace todo-app
kubectl label namespace todo-app dapr.io/inject=true
```

#### 6. Apply Dapr Components
```bash
kubectl apply -f dapr/components/ -n todo-app
```

#### 7. Deploy with Helm
```bash
helm install taskai ./helm/taskai \
  -f ./helm/taskai/values-minikube.yaml \
  -n todo-app \
  --set secrets.openaiApiKey="sk-your-key"
```

#### 8. Verify Deployment
```bash
kubectl get pods -n todo-app
kubectl get pods -n kafka
dapr status -k
```

---

## Access Services

### Frontend
```bash
minikube service frontend -n todo-app
```
Or port-forward:
```bash
kubectl port-forward svc/frontend 3000:3000 -n todo-app
# Access at http://localhost:3000
```

### Backend API
```bash
kubectl port-forward svc/backend 8000:8000 -n todo-app
# Access at http://localhost:8000/docs
```

### Kafka (for debugging)
```bash
kubectl port-forward svc/kafka-cluster-kafka-bootstrap 9092:9092 -n kafka
```

---

## Local Development

### Backend (without Kubernetes)
```bash
cd backend

# Install dependencies (creates .venv automatically)
uv sync

# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run migrations
uv run alembic upgrade head

# Run with Dapr sidecar
dapr run --app-id todo-backend --app-port 8000 -- uvicorn src.main:app --reload

# Or without Dapr (reminder events won't be published)
uvicorn src.main:app --reload --port 8000
```

### Frontend (without Kubernetes)
```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev
# Access at http://localhost:3000
```

### Notification Service
```bash
cd notification-service

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run with Dapr sidecar
dapr run --app-id notification-service --app-port 8001 -- uvicorn src.main:app --reload
```

### Recurring Service
```bash
cd recurring-service

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run with Dapr sidecar
dapr run --app-id recurring-service --app-port 8002 -- uvicorn src.main:app --reload
```

---

## Environment Variables

### Backend
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/todo
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-your-openai-api-key
DAPR_HTTP_PORT=3500
PUBSUB_NAME=kafka-pubsub
REMINDER_SCHEDULER_ENABLED=true
REMINDER_POLL_INTERVAL=60
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Notification Service
```env
DAPR_HTTP_PORT=3500
PUBSUB_NAME=kafka-pubsub
LOG_JSON=true
LOG_LEVEL=20
```

### Recurring Service
```env
DAPR_HTTP_PORT=3500
PUBSUB_NAME=kafka-pubsub
BACKEND_URL=http://localhost:8000
LOG_JSON=true
LOG_LEVEL=20
```

---

## Testing

### Run Unit Tests
```bash
# Backend
cd backend && pytest tests/unit

# Frontend
cd frontend && pnpm test
```

### Run Integration Tests
```bash
# Requires running services
cd backend && pytest tests/integration
```

### Test Event Publishing
```bash
# Publish test event via Dapr
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"task.completed","task_id":1,"task_data":{"id":1,"title":"Test","recurrence":"weekly"},"user_id":"test"}'
```

### Verify Event Consumption
```bash
# Check notification-service logs
kubectl logs -l app=notification-service -n todo-app -f

# Check recurring-service logs
kubectl logs -l app=recurring-service -n todo-app -f
```

---

## Troubleshooting

### Pods Not Starting
```bash
# Check events
kubectl describe pod <pod-name> -n todo-app

# Check Dapr sidecar
kubectl logs <pod-name> -c daprd -n todo-app
```

### Kafka Issues
```bash
# Check Kafka cluster status
kubectl get kafka -n kafka

# Check Kafka pods
kubectl get pods -n kafka

# View Kafka logs
kubectl logs kafka-cluster-kafka-0 -n kafka
```

### Dapr Issues
```bash
# Check Dapr status
dapr status -k

# Check Dapr dashboard
dapr dashboard -k
```

### Reset Everything
```bash
helm uninstall taskai -n todo-app
kubectl delete namespace todo-app
kubectl delete namespace kafka
minikube delete
```

---

## Next Steps

1. **Test Phase 5 Features**:
   - Chat: "create a high priority task to finish report"
   - Chat: "add tag 'work' to finish report"
   - Chat: "set due date tomorrow for finish report"
   - Chat: "set reminder for finish report at 9am"
   - Chat: "show overdue tasks"
   - GUI: Use filters, search, and sort options
2. **Monitor Events**: Watch Dapr dashboard for pub/sub activity
   ```bash
   dapr dashboard -k
   ```
3. **Check Service Logs**:
   ```bash
   kubectl logs -l app=notification-service -n todo-app -f
   kubectl logs -l app=recurring-service -n todo-app -f
   ```
4. **Scale Services**: `kubectl scale deployment backend --replicas=3 -n todo-app`
5. **Deploy to Cloud**: Update values files for AKS/GKE/OKE
