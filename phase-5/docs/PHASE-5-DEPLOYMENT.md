# [Task]: T125
# [Spec]: Phase 5 Cloud Deployment
# [Description]: Comprehensive deployment documentation for Phase 5

# Phase 5: Advanced Cloud Deployment Guide

This guide covers the deployment of the TaskAI application using the Phase 5 microservices architecture with Dapr and Kafka.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TaskAI                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │   Frontend   │  │   Backend    │  │ Notification   │  │  Recurring    │ │
│  │   (Next.js)  │  │   (FastAPI)  │  │   Service      │  │   Service     │ │
│  │   :30000     │  │   :30080     │  │   :8001        │  │   :8002       │ │
│  └──────────────┘  └──────┬───────┘  └────────┬───────┘  └───────┬───────┘ │
│                           │                   │                   │         │
│  ┌────────────────────────┴───────────────────┴───────────────────┴───────┐ │
│  │                           Dapr Sidecar                                 │ │
│  │                     (Service invocation, Pub/Sub)                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                     │                                       │
│  ┌──────────────────────────────────┴────────────────────────────────────┐  │
│  │                         Kafka (Strimzi/Redpanda)                       │  │
│  │                    Topics: task-events, reminders                      │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         PostgreSQL Database                           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools

- **minikube** >= 1.32.0
- **kubectl** >= 1.28.0
- **helm** >= 3.13.0
- **docker** >= 24.0.0
- **dapr CLI** >= 1.12.0

### Installation Commands

```powershell
# Windows (using Chocolatey)
choco install minikube kubernetes-cli helm docker-desktop

# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

## Quick Start - Minikube Deployment

### 1. Clone and Navigate

```powershell
cd phase-5
```

### 2. Deploy with Single Command

```powershell
.\scripts\deploy-minikube.ps1
```

This script will:
1. Start Minikube (8GB RAM, 4 CPUs)
2. Install Strimzi Kafka Operator
3. Deploy Kafka cluster with topics
4. Install Dapr runtime
5. Apply Dapr components
6. Build Docker images
7. Deploy application via Helm

### 3. Verify Deployment

```powershell
.\scripts\verify-deployment.ps1
```

### 4. Access the Application

```powershell
# Get Minikube IP
$MINIKUBE_IP = minikube ip

# Access URLs
Frontend:     http://$MINIKUBE_IP:30000
Backend API:  http://$MINIKUBE_IP:30080
API Docs:     http://$MINIKUBE_IP:30080/docs
```

## Manual Deployment Steps

### 1. Start Minikube

```powershell
minikube start --memory=8192 --cpus=4 --driver=docker
minikube addons enable metrics-server
minikube addons enable storage-provisioner
```

### 2. Install Strimzi Kafka

```powershell
# Install operator
kubectl create namespace strimzi-system
kubectl apply -f 'https://strimzi.io/install/latest?namespace=strimzi-system' -n strimzi-system
kubectl wait --for=condition=available deployment/strimzi-cluster-operator -n strimzi-system --timeout=300s

# Deploy cluster
kubectl apply -f infra/minikube/kafka-cluster.yaml
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka
```

### 3. Install Dapr

```powershell
dapr init -k --wait
dapr status -k
```

### 4. Apply Dapr Components

```powershell
kubectl create namespace todo-app
kubectl apply -f dapr/components/ -n todo-app
```

### 5. Build Docker Images

```powershell
# Configure Docker for Minikube
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build images
docker build -t todo-chatbot/backend:latest ./backend
docker build -t todo-chatbot/frontend:latest ./frontend
docker build -t todo-chatbot/notification-service:latest ./notification-service
docker build -t todo-chatbot/recurring-service:latest ./recurring-service
```

### 6. Deploy with Helm

```powershell
cd helm/todo-chatbot
helm dependency update
helm upgrade --install todo-chatbot . `
  -f values-minikube.yaml `
  --namespace todo-app `
  --create-namespace `
  --wait `
  --timeout 10m
```

## Cloud Deployment

### Staging Environment

```bash
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-staging.yaml \
  --namespace todo-app-staging \
  --create-namespace \
  --set backend.image.tag=<version> \
  --set frontend.image.tag=<version> \
  --atomic \
  --wait
```

### Production Environment

```bash
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-production.yaml \
  --namespace todo-app-production \
  --create-namespace \
  --set backend.image.tag=<version> \
  --set frontend.image.tag=<version> \
  --atomic \
  --wait
```

### Required Cloud Secrets

Create these secrets before deployment:

```bash
# Database credentials
kubectl create secret generic database-credentials \
  --from-literal=username=<user> \
  --from-literal=password=<password> \
  -n todo-app-staging

# Redpanda Cloud credentials
kubectl create secret generic redpanda-credentials \
  --from-literal=brokers=<broker-url>:9092 \
  --from-literal=username=<user> \
  --from-literal=password=<password> \
  -n todo-app-staging
```

## Event-Driven Architecture

### Topics

| Topic | Publisher | Subscriber | Events |
|-------|-----------|------------|--------|
| `task-events` | Backend | Recurring Service | task.created, task.updated, task.completed, task.deleted |
| `reminders` | Backend | Notification Service | reminder.due |

### Event Flow: Recurring Task

1. User creates task with `recurrence: weekly`
2. Backend stores task, publishes `task.created` event
3. User completes task
4. Backend publishes `task.completed` event
5. Recurring Service receives event
6. Recurring Service calculates next due date
7. Recurring Service creates new task via Backend API

### Event Flow: Reminder

1. User sets reminder on task
2. Backend's reminder scheduler polls for due reminders
3. When reminder is due, Backend publishes `reminder.due` event
4. Notification Service receives event
5. Notification Service logs/sends notification

## Monitoring & Debugging

### View Logs

```powershell
# Backend logs
kubectl logs -f deployment/todo-chatbot-backend -n todo-app

# Frontend logs
kubectl logs -f deployment/todo-chatbot-frontend -n todo-app

# Notification service logs
kubectl logs -f deployment/todo-chatbot-notification-service -n todo-app

# Recurring service logs
kubectl logs -f deployment/todo-chatbot-recurring-service -n todo-app
```

### Dapr Dashboard

```powershell
dapr dashboard -k
# Opens browser at http://localhost:8080
```

### Kafka Monitoring

```powershell
# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# View messages in topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic task-events --from-beginning
```

## Troubleshooting

### Pods Not Starting

```powershell
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app
```

### Kafka Connection Issues

```powershell
# Check Kafka status
kubectl get kafka -n kafka
kubectl get kafkatopics -n kafka

# Check Dapr component
kubectl get components -n todo-app
kubectl describe component kafka-pubsub -n todo-app
```

### Database Connection Issues

```powershell
# Check PostgreSQL pod
kubectl get pods -n todo-app | grep postgres

# Test database connection
kubectl exec -it <backend-pod> -n todo-app -- python -c "from core.database import engine; print(engine.url)"
```

## Cleanup

### Remove Application

```powershell
helm uninstall todo-chatbot -n todo-app
kubectl delete namespace todo-app
```

### Remove Kafka

```powershell
kubectl delete -f infra/minikube/kafka-cluster.yaml
kubectl delete namespace kafka
kubectl delete -f 'https://strimzi.io/install/latest?namespace=strimzi-system' -n strimzi-system
kubectl delete namespace strimzi-system
```

### Remove Dapr

```powershell
dapr uninstall -k
```

### Stop Minikube

```powershell
minikube stop
minikube delete  # To remove completely
```

## Configuration Reference

### Environment Variables

| Variable | Service | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `SECRET_KEY` | Backend | JWT signing key |
| `DAPR_ENABLED` | Backend | Enable Dapr pub/sub |
| `DAPR_HTTP_PORT` | All | Dapr sidecar port (default: 3500) |
| `PUBSUB_NAME` | All | Dapr pubsub component name |
| `LOG_LEVEL` | All | Logging level (DEBUG, INFO, WARNING) |
| `BACKEND_URL` | Recurring | Backend API URL for creating tasks |

### Helm Values

See `helm/todo-chatbot/values.yaml` for all configurable options.

Key configurations:
- `replicaCount`: Number of pod replicas
- `image.tag`: Docker image tag
- `service.type`: NodePort (Minikube) or LoadBalancer (Cloud)
- `dapr.enabled`: Enable Dapr sidecar injection
- `resources`: CPU/memory limits and requests
- `autoscaling`: HPA configuration
