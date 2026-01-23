#!/bin/bash
# TaskAI Dapr-Enabled Deployment Script for DigitalOcean Kubernetes
# This script deploys TaskAI with Dapr enabled to enable recurrence and notifications

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="todo-app"
KUBECONFIG="${KUBECONFIG:-taskai-cluster-kubeconfig.yaml}"
HELM_RELEASE="todo-chatbot"
HELM_CHART="./helm/todo-chatbot"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TaskAI Dapr-Enabled Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Verify prerequisites
echo -e "${YELLOW}Step 1: Verifying prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm not found. Please install helm.${NC}"
    exit 1
fi

if [ ! -f "$KUBECONFIG" ]; then
    echo -e "${RED}❌ Kubeconfig file not found: $KUBECONFIG${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites verified${NC}"
echo ""

# Step 2: Check Dapr installation
echo -e "${YELLOW}Step 2: Checking Dapr installation...${NC}"

if ! kubectl --kubeconfig="$KUBECONFIG" get namespace dapr-system &> /dev/null; then
    echo -e "${RED}❌ Dapr system namespace not found. Please install Dapr first.${NC}"
    echo -e "${YELLOW}Install Dapr with: helm repo add dapr https://dapr.github.io/helm-charts/ && helm install dapr dapr/dapr --namespace dapr-system --create-namespace${NC}"
    exit 1
fi

DAPR_PODS=$(kubectl --kubeconfig="$KUBECONFIG" get pods -n dapr-system --no-headers | wc -l)
if [ "$DAPR_PODS" -lt 3 ]; then
    echo -e "${RED}❌ Dapr system pods not running properly${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dapr is installed and running${NC}"
echo ""

# Step 3: Check namespace and secrets
echo -e "${YELLOW}Step 3: Checking namespace and secrets...${NC}"

if ! kubectl --kubeconfig="$KUBECONFIG" get namespace "$NAMESPACE" &> /dev/null; then
    echo -e "${RED}❌ Namespace $NAMESPACE not found${NC}"
    exit 1
fi

REQUIRED_SECRETS=("kafka-credentials" "database-credentials" "backend-secrets")
for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! kubectl --kubeconfig="$KUBECONFIG" get secret "$secret" -n "$NAMESPACE" &> /dev/null; then
        echo -e "${RED}❌ Required secret not found: $secret${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Secret exists: $secret${NC}"
done
echo ""

# Step 4: Deploy Dapr components
echo -e "${YELLOW}Step 4: Deploying Dapr components...${NC}"

echo "Deploying Kafka pub/sub component..."
kubectl --kubeconfig="$KUBECONFIG" apply -f dapr/deployment/01-kafka-pubsub-component.yaml

echo "Deploying task-events subscription..."
kubectl --kubeconfig="$KUBECONFIG" apply -f dapr/deployment/02-subscription-task-events.yaml

echo "Deploying reminders subscription..."
kubectl --kubeconfig="$KUBECONFIG" apply -f dapr/deployment/03-subscription-reminders.yaml

echo ""
echo -e "${GREEN}✅ Dapr components deployed${NC}"
echo ""

# Step 5: Verify components
echo -e "${YELLOW}Step 5: Verifying Dapr components...${NC}"

sleep 3  # Wait for components to be created

COMPONENTS=$(kubectl --kubeconfig="$KUBECONFIG" get component -n "$NAMESPACE" --no-headers | wc -l)
SUBSCRIPTIONS=$(kubectl --kubeconfig="$KUBECONFIG" get subscription -n "$NAMESPACE" --no-headers | wc -l)

echo "Components: $COMPONENTS"
echo "Subscriptions: $SUBSCRIPTIONS"

if [ "$COMPONENTS" -lt 1 ]; then
    echo -e "${RED}❌ Kafka component not created${NC}"
    exit 1
fi

if [ "$SUBSCRIPTIONS" -lt 2 ]; then
    echo -e "${RED}❌ Subscriptions not created properly${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dapr components verified${NC}"
echo ""

# Step 6: Deploy with Helm
echo -e "${YELLOW}Step 6: Deploying services with Dapr enabled...${NC}"
echo "This may take 5-10 minutes..."
echo ""

helm upgrade "$HELM_RELEASE" "$HELM_CHART" \
  --kubeconfig="$KUBECONFIG" \
  --namespace "$NAMESPACE" \
  --values helm-values-dapr-enabled.yaml \
  --timeout 10m \
  --wait \
  --atomic

echo ""
echo -e "${GREEN}✅ Helm deployment complete${NC}"
echo ""

# Step 7: Wait for pods to be ready
echo -e "${YELLOW}Step 7: Waiting for pods to be ready...${NC}"

echo "Waiting for backend pods..."
kubectl --kubeconfig="$KUBECONFIG" wait --for=condition=ready pod \
  -l app.kubernetes.io/name=backend \
  -n "$NAMESPACE" \
  --timeout=300s

echo "Waiting for recurring service pods..."
kubectl --kubeconfig="$KUBECONFIG" wait --for=condition=ready pod \
  -l app.kubernetes.io/name=recurring-service \
  -n "$NAMESPACE" \
  --timeout=300s

echo "Waiting for notification service pods..."
kubectl --kubeconfig="$KUBECONFIG" wait --for=condition=ready pod \
  -l app.kubernetes.io/name=notification-service \
  -n "$NAMESPACE" \
  --timeout=300s

echo ""
echo -e "${GREEN}✅ All pods are ready${NC}"
echo ""

# Step 8: Verify Dapr sidecars
echo -e "${YELLOW}Step 8: Verifying Dapr sidecars...${NC}"

BACKEND_POD=$(kubectl --kubeconfig="$KUBECONFIG" get pod -n "$NAMESPACE" -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
RECURRING_POD=$(kubectl --kubeconfig="$KUBECONFIG" get pod -n "$NAMESPACE" -l app.kubernetes.io/name=recurring-service -o jsonpath='{.items[0].metadata.name}')
NOTIFICATION_POD=$(kubectl --kubeconfig="$KUBECONFIG" get pod -n "$NAMESPACE" -l app.kubernetes.io/name=notification-service -o jsonpath='{.items[0].metadata.name}')

BACKEND_CONTAINERS=$(kubectl --kubeconfig="$KUBECONFIG" get pod "$BACKEND_POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}' | wc -w)
RECURRING_CONTAINERS=$(kubectl --kubeconfig="$KUBECONFIG" get pod "$RECURRING_POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}' | wc -w)
NOTIFICATION_CONTAINERS=$(kubectl --kubeconfig="$KUBECONFIG" get pod "$NOTIFICATION_POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}' | wc -w)

if [ "$BACKEND_CONTAINERS" -ge 2 ]; then
    echo -e "${GREEN}✅ Backend has Dapr sidecar (${BACKEND_CONTAINERS} containers)${NC}"
else
    echo -e "${RED}❌ Backend missing Dapr sidecar (${BACKEND_CONTAINERS} containers)${NC}"
fi

if [ "$RECURRING_CONTAINERS" -ge 2 ]; then
    echo -e "${GREEN}✅ Recurring service has Dapr sidecar (${RECURRING_CONTAINERS} containers)${NC}"
else
    echo -e "${RED}❌ Recurring service missing Dapr sidecar (${RECURRING_CONTAINERS} containers)${NC}"
fi

if [ "$NOTIFICATION_CONTAINERS" -ge 2 ]; then
    echo -e "${GREEN}✅ Notification service has Dapr sidecar (${NOTIFICATION_CONTAINERS} containers)${NC}"
else
    echo -e "${RED}❌ Notification service missing Dapr sidecar (${NOTIFICATION_CONTAINERS} containers)${NC}"
fi

echo ""

# Step 9: Test Dapr connectivity
echo -e "${YELLOW}Step 9: Testing Dapr connectivity...${NC}"

echo "Testing backend Dapr sidecar..."
if kubectl --kubeconfig="$KUBECONFIG" exec -n "$NAMESPACE" "$BACKEND_POD" -c backend -- curl -s http://localhost:3500/v1.0/healthz | grep -q "OK"; then
    echo -e "${GREEN}✅ Backend can reach Dapr sidecar${NC}"
else
    echo -e "${YELLOW}⚠️  Backend Dapr health check returned unexpected result${NC}"
fi

echo ""

# Step 10: Display summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Services Status:${NC}"
kubectl --kubeconfig="$KUBECONFIG" get pods -n "$NAMESPACE" -l 'app.kubernetes.io/name in (backend,frontend,recurring-service,notification-service)'
echo ""

echo -e "${BLUE}Dapr Components:${NC}"
kubectl --kubeconfig="$KUBECONFIG" get component,subscription -n "$NAMESPACE"
echo ""

echo -e "${BLUE}Application URL:${NC}"
echo -e "${GREEN}https://taskai.asharib.xyz${NC}"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "1. Test recurrence: Create a task with 'daily' recurrence, complete it, and check for new task"
echo "2. Check logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=recurring-service --tail=50"
echo "3. Monitor events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
echo ""

echo -e "${BLUE}Troubleshooting:${NC}"
echo "- View backend logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=backend -c backend"
echo "- View Dapr logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=backend -c daprd"
echo "- Check components: kubectl describe component kafka-pubsub -n $NAMESPACE"
echo ""

echo -e "${GREEN}✨ Happy coding!${NC}"
