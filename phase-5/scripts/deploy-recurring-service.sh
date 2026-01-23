#!/bin/bash

# Recurring Service Deployment Script for DigitalOcean Kubernetes
# Usage:
#   ./deploy-recurring-service.sh          # Deploy with :latest tag
#   ./deploy-recurring-service.sh v1.0.1   # Deploy with specific version

set -e  # Exit on error

REGISTRY="registry.digitalocean.com/taskai-registry"
NAMESPACE="todo-app"
DEPLOYMENT="todo-chatbot-recurring-service"

# Determine version tag
if [ -z "$1" ]; then
    # No argument provided, use :latest
    VERSION="latest"
    echo "📦 Using :latest tag (development mode)"
else
    # Use provided version
    VERSION="$1"
    echo "📦 Using version tag: $VERSION"
fi

IMAGE_TAG="${REGISTRY}/recurring-service:${VERSION}"

echo ""
echo "🚀 Deploying Recurring Service to Kubernetes"
echo "============================================="
echo "Registry: ${REGISTRY}"
echo "Image: recurring-service:${VERSION}"
echo "Namespace: ${NAMESPACE}"
echo "Deployment: ${DEPLOYMENT}"
echo ""

# Step 1: Build Docker image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_TAG} ./recurring-service
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi
echo "✅ Docker image built successfully"
echo ""

# Step 2: Login to registry (if needed)
echo "🔐 Logging into DigitalOcean Container Registry..."
doctl registry login
if [ $? -ne 0 ]; then
    echo "⚠️  Registry login failed, trying to continue anyway..."
fi
echo ""

# Step 3: Push Docker image
echo "📤 Pushing Docker image to registry..."
docker push ${IMAGE_TAG}
if [ $? -ne 0 ]; then
    echo "❌ Docker push failed!"
    exit 1
fi
echo "✅ Docker image pushed successfully"
echo ""

# Step 4: Update Kubernetes deployment
echo "🔄 Updating Kubernetes deployment..."
if [ "$VERSION" = "latest" ]; then
    # For :latest, use rollout restart to force pull new image
    echo "   Using rollout restart (imagePullPolicy: Always)"
    kubectl rollout restart deployment/${DEPLOYMENT} -n ${NAMESPACE}
else
    # For versioned tags, update the image
    echo "   Setting image to ${IMAGE_TAG}"
    kubectl set image deployment/${DEPLOYMENT} \
        recurring-service=${IMAGE_TAG} \
        -n ${NAMESPACE}
fi

if [ $? -ne 0 ]; then
    echo "❌ Kubernetes update failed!"
    exit 1
fi
echo "✅ Kubernetes deployment updated"
echo ""

# Step 5: Wait for rollout to complete
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE} --timeout=5m
if [ $? -ne 0 ]; then
    echo "❌ Rollout failed or timed out!"
    echo ""
    echo "📋 Recent pod events:"
    kubectl get events -n ${NAMESPACE} --sort-by='.lastTimestamp' | grep ${DEPLOYMENT} | tail -10
    exit 1
fi
echo ""

# Step 6: Show deployment status
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Current Status:"
echo "=================="
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=recurring-service
echo ""

# Show running image
echo "🖼️  Running Image:"
kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[?(@.name=="recurring-service")].image}{"\n"}'
echo ""

# Show Dapr sidecar status
echo "🔧 Dapr Status:"
DAPR_ENABLED=$(kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.template.metadata.annotations.dapr\.io/enabled}')
if [ "$DAPR_ENABLED" = "true" ]; then
    echo "✅ Dapr sidecar enabled (app-id: recurring-service)"
    echo "   Pod should show 2/2 READY (app + daprd)"
    echo ""
    echo "📡 Subscribed to Kafka topic: task-events"
    echo "   Endpoint: POST /api/events/task"
else
    echo "⚠️  Dapr sidecar disabled - recurrence feature will NOT work!"
fi
echo ""

# Check subscription status
echo "🔍 Checking Dapr subscription..."
SUBSCRIPTION_STATUS=$(kubectl get subscription task-events-subscription -n ${NAMESPACE} 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Subscription 'task-events-subscription' is active"
else
    echo "⚠️  Subscription 'task-events-subscription' NOT FOUND"
    echo "   Run: kubectl apply -f dapr/deployment/02-subscription-task-events.yaml"
fi
echo ""

echo "🎉 Recurring Service deployment complete!"
echo ""
echo "📋 Service handles task.completed events and creates recurring tasks"
echo "🔄 Recurrence patterns: daily, weekly, monthly, yearly"
echo ""

# Optional: Show logs
read -p "📋 Show recent logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📋 Recent recurring-service logs (Ctrl+C to exit):"
    kubectl logs -n ${NAMESPACE} -l app.kubernetes.io/name=recurring-service -c recurring-service --tail=50 -f
fi
