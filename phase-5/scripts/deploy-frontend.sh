#!/bin/bash

# Frontend Deployment Script for DigitalOcean Kubernetes
# Usage:
#   ./deploy-frontend.sh          # Deploy with :latest tag
#   ./deploy-frontend.sh v1.0.1   # Deploy with specific version

set -e  # Exit on error

REGISTRY="registry.digitalocean.com/taskai-registry"
NAMESPACE="todo-app"
DEPLOYMENT="todo-chatbot-frontend"

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

IMAGE_TAG="${REGISTRY}/frontend:${VERSION}"

echo ""
echo "🚀 Deploying Frontend to Kubernetes"
echo "=================================="
echo "Registry: ${REGISTRY}"
echo "Image: frontend:${VERSION}"
echo "Namespace: ${NAMESPACE}"
echo "Deployment: ${DEPLOYMENT}"
echo ""

# Step 1: Build Docker image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_TAG} ./frontend
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
        frontend=${IMAGE_TAG} \
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
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=frontend
echo ""

# Show running image
echo "🖼️  Running Image:"
kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
echo ""

echo "🎉 Frontend deployment complete!"
echo ""
echo "🌐 Visit: https://taskai.asharib.xyz"
echo ""

# Optional: Show logs
read -p "📋 Show recent logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📋 Recent logs (Ctrl+C to exit):"
    kubectl logs -n ${NAMESPACE} -l app.kubernetes.io/name=frontend --tail=50 -f
fi
