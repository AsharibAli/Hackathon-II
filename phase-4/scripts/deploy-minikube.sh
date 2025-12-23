#!/bin/bash
# ==============================================
# TaskAI - Minikube Deployment Script
# ==============================================
# This script deploys the TaskAI application to a local Minikube cluster
# using Helm charts.
#
# Prerequisites:
#   - minikube installed
#   - kubectl installed
#   - helm installed
#   - docker installed
#
# Usage:
#   ./scripts/deploy-minikube.sh [OPTIONS]
#
# Options:
#   --openai-key <key>    Set OpenAI API key
#   --skip-build          Skip Docker image build
#   --clean               Clean up existing deployment first
#   --help                Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
NAMESPACE="taskai"
RELEASE_NAME="taskai"
CHART_PATH="$PROJECT_DIR/helm/taskai"

# Default values
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
SKIP_BUILD=false
CLEAN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --openai-key)
            OPENAI_API_KEY="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
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

# Build Docker images
build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_info "Skipping Docker image build (--skip-build)"
        return
    fi

    log_info "Configuring Docker to use Minikube's daemon..."
    eval $(minikube docker-env)

    log_info "Building backend Docker image..."
    docker build -t taskai-backend:latest "$PROJECT_DIR/backend"
    log_success "Backend image built"

    log_info "Building frontend Docker image..."
    docker build \
        --build-arg NEXT_PUBLIC_API_URL="http://localhost:30800" \
        -t taskai-frontend:latest \
        "$PROJECT_DIR/frontend"
    log_success "Frontend image built"
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

# Deploy with Helm
deploy_helm() {
    log_info "Deploying TaskAI with Helm..."

    # Check if OpenAI API key is set
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warning "OPENAI_API_KEY is not set. Chat functionality will not work."
        log_info "Set it with: --openai-key <your-key> or export OPENAI_API_KEY=<your-key>"
    fi

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" 2>/dev/null || true

    # Deploy or upgrade
    helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        --set secrets.openaiApiKey="$OPENAI_API_KEY" \
        --set frontend.env.NEXT_PUBLIC_API_URL="http://localhost:30800" \
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

# Display access information
show_access_info() {
    echo ""
    echo "==========================================================="
    echo -e "${GREEN}  TaskAI Deployment Successful!${NC}"
    echo "==========================================================="
    echo ""
    echo "Access URLs:"
    echo -e "  Frontend: ${BLUE}http://$(minikube ip):30300${NC}"
    echo -e "  Backend API: ${BLUE}http://$(minikube ip):30800${NC}"
    echo -e "  Swagger Docs: ${BLUE}http://$(minikube ip):30800/docs${NC}"
    echo ""
    echo "Alternative (localhost access via minikube tunnel):"
    echo -e "  Run: ${YELLOW}minikube tunnel${NC} in a separate terminal"
    echo -e "  Frontend: ${BLUE}http://localhost:30300${NC}"
    echo -e "  Backend: ${BLUE}http://localhost:30800${NC}"
    echo ""
    echo "Useful commands:"
    echo "  View pods:     kubectl get pods -n $NAMESPACE"
    echo "  View logs:     kubectl logs -f deploy/taskai-backend -n $NAMESPACE"
    echo "  Open dashboard: minikube dashboard"
    echo ""
    echo "To uninstall:"
    echo "  helm uninstall $RELEASE_NAME -n $NAMESPACE"
    echo "  kubectl delete namespace $NAMESPACE"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "==========================================================="
    echo "  TaskAI - Minikube Deployment"
    echo "==========================================================="
    echo ""

    check_prerequisites
    start_minikube
    cleanup
    build_images
    deploy_helm
    wait_for_pods
    show_access_info
}

main "$@"
