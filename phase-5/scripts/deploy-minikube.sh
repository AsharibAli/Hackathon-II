#!/bin/bash
# [Task]: T110
# [Spec]: F-009 (US11)
# [Description]: Bash script to deploy TaskAI to Minikube
# ==============================================
# TaskAI - Minikube Deployment Script (Bash)
# ==============================================
# This script deploys the TaskAI application to a local Minikube cluster
# with full microservices architecture including Dapr and Kafka.
#
# Prerequisites:
#   - minikube installed
#   - kubectl installed
#   - helm installed
#   - docker installed
#   - dapr CLI installed
#
# Usage:
#   ./scripts/deploy-minikube.sh [OPTIONS]
#
# Options:
#   --skip-build         Skip Docker image build
#   --skip-kafka         Skip Kafka/Strimzi installation
#   --skip-dapr          Skip Dapr installation
#   --clean              Clean up existing deployment first
#   --help               Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
NAMESPACE="todo-app"
RELEASE_NAME="todo-chatbot"
CHART_PATH="$PROJECT_DIR/helm/todo-chatbot"
ENV_FILE="$PROJECT_DIR/.env"

# Default values
SKIP_BUILD=false
SKIP_KAFKA=false
SKIP_DAPR=false
CLEAN=false

# Port forwarding PIDs
PF_FRONTEND_PID=""
PF_BACKEND_PID=""
PF_NOTIFICATION_PID=""
PF_RECURRING_PID=""

# Load .env file if it exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${BLUE}[INFO]${NC} Loading configuration from .env file..."
    set -a
    source "$ENV_FILE"
    set +a
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-kafka)
            SKIP_KAFKA=true
            shift
            ;;
        --skip-dapr)
            SKIP_DAPR=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --help)
            head -30 "$0" | tail -25
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    command -v minikube >/dev/null 2>&1 || missing+=("minikube")
    command -v kubectl >/dev/null 2>&1 || missing+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing+=("helm")
    command -v docker >/dev/null 2>&1 || missing+=("docker")
    if [ "$SKIP_DAPR" = false ]; then
        command -v dapr >/dev/null 2>&1 || missing+=("dapr")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing[*]}"
        log_info "Please install them and try again."
        exit 1
    fi

    log_success "All prerequisites are installed"
}

# Start Minikube
start_minikube() {
    log_info "Checking Minikube status..."

    if ! minikube status >/dev/null 2>&1; then
        log_info "Starting Minikube..."
        minikube start --cpus=4 --memory=8192 --driver=docker
        log_success "Minikube started"
    else
        log_info "Minikube is already running"
    fi

    # Enable required addons
    log_info "Enabling Minikube addons..."
    minikube addons enable metrics-server 2>/dev/null || true
    minikube addons enable storage-provisioner 2>/dev/null || true
}

# Install Strimzi Kafka
install_kafka() {
    if [ "$SKIP_KAFKA" = true ]; then
        log_info "Skipping Kafka installation (--skip-kafka)"
        return
    fi

    log_info "Installing Strimzi Kafka Operator..."

    # Create kafka namespace first
    kubectl get namespace kafka >/dev/null 2>&1 || kubectl create namespace kafka

    # Install Strimzi operator
    kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka

    log_info "Waiting for Strimzi operator to be ready..."
    kubectl wait --for=condition=available deployment/strimzi-cluster-operator -n kafka --timeout=300s

    # Deploy Kafka cluster
    log_info "Deploying Kafka cluster..."
    kubectl apply -f "$PROJECT_DIR/infra/minikube/kafka-cluster.yaml"

    log_info "Waiting for Kafka cluster to be ready (this may take a few minutes)..."
    sleep 30

    # Wait with retry logic
    local retry_count=0
    local max_retries=20
    while [ $retry_count -lt $max_retries ]; do
        local kafka_ready=$(kubectl get kafka kafka-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
        if [ "$kafka_ready" = "True" ]; then
            break
        fi
        log_info "Kafka not ready yet, waiting... (attempt $((retry_count + 1))/$max_retries)"
        sleep 30
        retry_count=$((retry_count + 1))
    done

    if [ $retry_count -eq $max_retries ]; then
        log_warning "Kafka cluster taking longer than expected. Continuing with deployment..."
    else
        log_success "Kafka cluster deployed"
    fi
}

# Install Dapr
install_dapr() {
    if [ "$SKIP_DAPR" = true ]; then
        log_info "Skipping Dapr installation (--skip-dapr)"
        return
    fi

    log_info "Installing Dapr..."

    # Check if Dapr is already installed
    if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
        log_info "Initializing Dapr in Kubernetes..."
        dapr init -k --wait
        if [ $? -ne 0 ]; then
            log_error "Failed to initialize Dapr"
            exit 1
        fi
    else
        log_info "Dapr is already installed"
    fi

    log_success "Dapr installed"
}

# Apply Dapr components
apply_dapr_components() {
    log_info "Creating namespace and Dapr components..."

    # Create todo-app namespace
    kubectl get namespace "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"

    # Apply Dapr components
    kubectl apply -f "$PROJECT_DIR/dapr/components/" -n "$NAMESPACE"

    log_success "Namespace and Dapr components created"
}

# Build Docker images
build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_info "Skipping Docker image build (--skip-build)"
        return
    fi

    log_info "Configuring Docker to use Minikube's daemon..."
    eval $(minikube docker-env)

    log_info "Building backend Docker image..."
    docker build -t todo-chatbot/backend:latest "$PROJECT_DIR/backend"
    log_success "Backend image built"

    log_info "Building frontend Docker image..."
    docker build \
        --build-arg NEXT_PUBLIC_API_URL="http://localhost:30080" \
        -t todo-chatbot/frontend:latest \
        "$PROJECT_DIR/frontend"
    log_success "Frontend image built"

    log_info "Building notification-service Docker image..."
    docker build -t todo-chatbot/notification-service:latest "$PROJECT_DIR/notification-service"
    log_success "Notification service image built"

    log_info "Building recurring-service Docker image..."
    docker build -t todo-chatbot/recurring-service:latest "$PROJECT_DIR/recurring-service"
    log_success "Recurring service image built"
}

# Clean up existing deployment
cleanup() {
    if [ "$CLEAN" = true ]; then
        log_info "Cleaning up existing deployment..."

        helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || true
        kubectl delete namespace "$NAMESPACE" 2>/dev/null || true

        # Wait for namespace to be deleted
        while kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; do
            log_info "Waiting for namespace to be deleted..."
            sleep 2
        done

        log_success "Cleanup completed"
    fi
}

# Update Helm dependencies
update_helm_deps() {
    log_info "Updating Helm dependencies..."
    helm dependency update "$CHART_PATH"
    log_success "Helm dependencies updated"
}

# Deploy with Helm
deploy_helm() {
    log_info "Deploying TaskAI with Helm..."

    # Deploy or upgrade using Minikube values
    helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
        -f "$CHART_PATH/values-minikube.yaml" \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --wait \
        --timeout 10m

    log_success "Helm deployment completed"
}

# Wait for pods to be ready
wait_for_pods() {
    log_info "Waiting for all pods to be ready..."

    kubectl wait --for=condition=ready pod \
        --all \
        --namespace "$NAMESPACE" \
        --timeout=300s

    log_success "All pods are ready"
}

# Port forwarding for local development access
start_port_forwarding() {
    log_info "Starting port forwarding for services..."

    # Kill any existing port-forward processes on our ports
    for port in 3000 8000 8001 8002; do
        local pids=$(lsof -ti :$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
    done

    # Start port forwarding in background
    log_info "Starting port forwarding for Frontend (localhost:3000)..."
    kubectl port-forward svc/todo-chatbot-frontend 3000:3000 -n "$NAMESPACE" &>/dev/null &
    PF_FRONTEND_PID=$!

    log_info "Starting port forwarding for Backend (localhost:8000)..."
    kubectl port-forward svc/todo-chatbot-backend 8000:8000 -n "$NAMESPACE" &>/dev/null &
    PF_BACKEND_PID=$!

    log_info "Starting port forwarding for Notification Service (localhost:8001)..."
    kubectl port-forward svc/todo-chatbot-notification-service 8001:8001 -n "$NAMESPACE" &>/dev/null &
    PF_NOTIFICATION_PID=$!

    log_info "Starting port forwarding for Recurring Service (localhost:8002)..."
    kubectl port-forward svc/todo-chatbot-recurring-service 8002:8002 -n "$NAMESPACE" &>/dev/null &
    PF_RECURRING_PID=$!

    # Wait a moment for port forwarding to establish
    sleep 3

    log_success "Port forwarding started for all services"
}

# Display access information
show_access_info() {
    local minikube_ip=$(minikube ip)

    echo ""
    echo -e "${GREEN}===========================================================${NC}"
    echo -e "${GREEN}  TaskAI Deployment Successful!${NC}"
    echo -e "${GREEN}===========================================================${NC}"
    echo ""
    echo -e "Access URLs (via Port Forwarding - localhost):"
    echo -e "  Frontend:     ${CYAN}http://localhost:3000${NC}"
    echo -e "  Backend API:  ${CYAN}http://localhost:8000${NC}"
    echo -e "  Swagger Docs: ${CYAN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "Access URLs (via NodePort - Minikube IP):"
    echo -e "  Frontend:     ${CYAN}http://${minikube_ip}:30000${NC}"
    echo -e "  Backend API:  ${CYAN}http://${minikube_ip}:30080${NC}"
    echo -e "  Swagger Docs: ${CYAN}http://${minikube_ip}:30080/docs${NC}"
    echo ""
    echo -e "Port Forwarding PIDs:"
    echo "  Frontend:              PID $PF_FRONTEND_PID (localhost:3000 -> todo-chatbot-frontend:3000)"
    echo "  Backend:               PID $PF_BACKEND_PID (localhost:8000 -> todo-chatbot-backend:8000)"
    echo "  Notification Service:  PID $PF_NOTIFICATION_PID (localhost:8001 -> todo-chatbot-notification-service:8001)"
    echo "  Recurring Service:     PID $PF_RECURRING_PID (localhost:8002 -> todo-chatbot-recurring-service:8002)"
    echo ""
    echo "Useful commands:"
    echo "  View pods:           kubectl get pods -n $NAMESPACE"
    echo "  View backend logs:   kubectl logs -f deploy/todo-chatbot-backend -n $NAMESPACE"
    echo "  View frontend logs:  kubectl logs -f deploy/todo-chatbot-frontend -n $NAMESPACE"
    echo "  Dapr dashboard:      dapr dashboard -k"
    echo "  Minikube dashboard:  minikube dashboard"
    echo ""
    echo -e "${YELLOW}To stop port forwarding:${NC}"
    echo "  kill $PF_FRONTEND_PID $PF_BACKEND_PID $PF_NOTIFICATION_PID $PF_RECURRING_PID"
    echo ""
    echo -e "${YELLOW}To verify deployment, run:${NC}"
    echo "  ./scripts/verify-deployment.sh"
    echo ""
    echo -e "${YELLOW}To uninstall:${NC}"
    echo "  helm uninstall $RELEASE_NAME -n $NAMESPACE"
    echo "  kubectl delete namespace $NAMESPACE"
    echo ""
    echo -e "${GREEN}===========================================================${NC}"
    echo -e "${GREEN}  Services accessible via localhost (port-forwarding)!${NC}"
    echo -e "${GREEN}===========================================================${NC}"
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${CYAN}===========================================================${NC}"
    echo -e "${CYAN}  TaskAI - Minikube Deployment${NC}"
    echo -e "${CYAN}===========================================================${NC}"
    echo ""

    check_prerequisites
    start_minikube
    cleanup
    install_kafka
    install_dapr
    apply_dapr_components
    build_images
    update_helm_deps
    deploy_helm
    wait_for_pods
    start_port_forwarding
    show_access_info
}

main "$@"
