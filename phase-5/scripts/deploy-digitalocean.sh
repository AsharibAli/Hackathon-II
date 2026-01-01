#!/bin/bash
# [Task]: Cloud-Native Implementation
# [Description]: Deployment script for DigitalOcean Kubernetes (DOKS)
#
# Prerequisites:
#   - doctl (DigitalOcean CLI) installed and authenticated
#   - kubectl installed
#   - helm 3.x installed
#   - dapr CLI installed (optional, for Dapr initialization)
#
# Usage:
#   ./scripts/deploy-digitalocean.sh [OPTIONS]
#
# Options:
#   --cluster-name    DOKS cluster name (required)
#   --registry        DOCR registry name (required)
#   --namespace       Kubernetes namespace (default: todo-app)
#   --environment     Environment: staging or production (default: staging)
#   --image-tag       Image tag to deploy (default: latest)
#   --domain          Domain for ingress (required for TLS)
#   --email           Email for Let's Encrypt (required for TLS)
#   --dry-run         Perform a dry run without deploying
#   --skip-dapr       Skip Dapr installation
#   --skip-secrets    Skip secret creation prompts
#   --help            Show this help message

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="todo-app"
ENVIRONMENT="staging"
IMAGE_TAG="latest"
DRY_RUN=false
SKIP_DAPR=false
SKIP_SECRETS=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show help
show_help() {
    head -30 "$0" | tail -25
    exit 0
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cluster-name)
                CLUSTER_NAME="$2"
                shift 2
                ;;
            --registry)
                REGISTRY_NAME="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --image-tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            --domain)
                DOMAIN="$2"
                shift 2
                ;;
            --email)
                EMAIL="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-dapr)
                SKIP_DAPR=true
                shift
                ;;
            --skip-secrets)
                SKIP_SECRETS=true
                shift
                ;;
            --help)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "${CLUSTER_NAME:-}" ]]; then
        log_error "--cluster-name is required"
        exit 1
    fi
    if [[ -z "${REGISTRY_NAME:-}" ]]; then
        log_error "--registry is required"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    if ! command -v doctl &> /dev/null; then
        missing+=("doctl")
    fi

    if ! command -v kubectl &> /dev/null; then
        missing+=("kubectl")
    fi

    if ! command -v helm &> /dev/null; then
        missing+=("helm")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        log_info "Install instructions:"
        log_info "  doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        log_info "  kubectl: https://kubernetes.io/docs/tasks/tools/"
        log_info "  helm: https://helm.sh/docs/intro/install/"
        exit 1
    fi

    # Check doctl authentication
    if ! doctl account get &> /dev/null; then
        log_error "doctl is not authenticated. Run: doctl auth init"
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

# Connect to DOKS cluster
connect_cluster() {
    log_info "Connecting to DOKS cluster: $CLUSTER_NAME..."

    doctl kubernetes cluster kubeconfig save "$CLUSTER_NAME"

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Failed to connect to cluster"
        exit 1
    fi

    log_success "Connected to cluster"
    kubectl get nodes
}

# Login to DOCR
login_registry() {
    log_info "Logging in to DigitalOcean Container Registry..."
    doctl registry login --expiry-seconds 3600
    log_success "Logged in to DOCR"
}

# Install Dapr
install_dapr() {
    if [[ "$SKIP_DAPR" == "true" ]]; then
        log_info "Skipping Dapr installation"
        return
    fi

    log_info "Checking Dapr installation..."

    if kubectl get namespace dapr-system &> /dev/null; then
        log_info "Dapr is already installed"
        return
    fi

    if ! command -v dapr &> /dev/null; then
        log_warn "Dapr CLI not found. Installing Dapr via Helm..."

        helm repo add dapr https://dapr.github.io/helm-charts/
        helm repo update
        helm upgrade --install dapr dapr/dapr \
            --namespace dapr-system \
            --create-namespace \
            --wait
    else
        log_info "Installing Dapr with CLI..."
        dapr init -k --wait
    fi

    log_success "Dapr installed successfully"
}

# Install cert-manager
install_cert_manager() {
    log_info "Checking cert-manager installation..."

    if kubectl get namespace cert-manager &> /dev/null; then
        log_info "cert-manager is already installed"
        return
    fi

    log_info "Installing cert-manager..."

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

    log_info "Waiting for cert-manager to be ready..."
    kubectl wait --for=condition=Available deployment --all -n cert-manager --timeout=300s

    log_success "cert-manager installed successfully"
}

# Install NGINX Ingress Controller
install_ingress() {
    log_info "Checking NGINX Ingress Controller..."

    if kubectl get namespace ingress-nginx &> /dev/null; then
        log_info "NGINX Ingress Controller is already installed"
        return
    fi

    log_info "Installing NGINX Ingress Controller..."

    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.annotations."service\.beta\.kubernetes\.io/do-loadbalancer-name"="todo-chatbot-lb" \
        --wait

    log_success "NGINX Ingress Controller installed"

    # Wait for LoadBalancer IP
    log_info "Waiting for LoadBalancer IP assignment..."
    sleep 30
    kubectl get svc -n ingress-nginx ingress-nginx-controller
}

# Create secrets
create_secrets() {
    if [[ "$SKIP_SECRETS" == "true" ]]; then
        log_info "Skipping secret creation"
        return
    fi

    log_info "Setting up secrets..."

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Check for existing secrets
    local secrets_to_create=()

    if ! kubectl get secret database-credentials -n "$NAMESPACE" &> /dev/null; then
        secrets_to_create+=("database-credentials")
    fi

    if ! kubectl get secret kafka-credentials -n "$NAMESPACE" &> /dev/null; then
        secrets_to_create+=("kafka-credentials")
    fi

    if ! kubectl get secret backend-secrets -n "$NAMESPACE" &> /dev/null; then
        secrets_to_create+=("backend-secrets")
    fi

    if ! kubectl get secret docr-credentials -n "$NAMESPACE" &> /dev/null; then
        secrets_to_create+=("docr-credentials")
    fi

    if [[ ${#secrets_to_create[@]} -eq 0 ]]; then
        log_info "All required secrets already exist"
        return
    fi

    log_warn "The following secrets need to be created: ${secrets_to_create[*]}"

    for secret in "${secrets_to_create[@]}"; do
        case $secret in
            database-credentials)
                log_info ""
                log_info "Create database-credentials secret with:"
                log_info "  kubectl create secret generic database-credentials \\"
                log_info "    --from-literal=username=<db-username> \\"
                log_info "    --from-literal=password=<db-password> \\"
                log_info "    --from-literal=host=<db-host> \\"
                log_info "    --from-literal=connection-string='postgresql://<user>:<pass>@<host>:25060/<db>?sslmode=require' \\"
                log_info "    -n $NAMESPACE"
                ;;
            kafka-credentials)
                log_info ""
                log_info "Create kafka-credentials secret with:"
                log_info "  kubectl create secret generic kafka-credentials \\"
                log_info "    --from-literal=brokers=<kafka-broker-url>:25073 \\"
                log_info "    --from-literal=username=doadmin \\"
                log_info "    --from-literal=password=<kafka-password> \\"
                log_info "    -n $NAMESPACE"
                ;;
            backend-secrets)
                log_info ""
                log_info "Create backend-secrets secret with:"
                log_info "  kubectl create secret generic backend-secrets \\"
                log_info "    --from-literal=SECRET_KEY=<your-secret-key> \\"
                log_info "    --from-literal=OPENAI_API_KEY=<your-openai-key> \\"
                log_info "    --from-literal=RESEND_API_KEY=<your-resend-key> \\"
                log_info "    -n $NAMESPACE"
                ;;
            docr-credentials)
                log_info ""
                log_info "Create docr-credentials secret (for image pulling):"
                log_info "  doctl registry kubernetes-manifest | kubectl apply -n $NAMESPACE -f -"
                ;;
        esac
    done

    log_warn ""
    log_warn "Please create the required secrets and run this script again with --skip-secrets"
    exit 1
}

# Deploy application
deploy_application() {
    log_info "Deploying TaskAI to $ENVIRONMENT environment..."

    local helm_args=(
        "upgrade" "--install" "todo-chatbot"
        "$PROJECT_ROOT/helm/todo-chatbot"
        "--namespace" "$NAMESPACE"
        "--create-namespace"
        "--values" "$PROJECT_ROOT/helm/todo-chatbot/values-digitalocean.yaml"
        "--set" "global.imageRegistry=registry.digitalocean.com/$REGISTRY_NAME"
        "--set" "global.namespace=$NAMESPACE"
        "--set" "backend.image.tag=$IMAGE_TAG"
        "--set" "frontend.image.tag=$IMAGE_TAG"
        "--set" "notification-service.image.tag=$IMAGE_TAG"
        "--set" "recurring-service.image.tag=$IMAGE_TAG"
    )

    # Add domain configuration if provided
    if [[ -n "${DOMAIN:-}" ]]; then
        helm_args+=(
            "--set" "ingress.hosts[0].host=$DOMAIN"
            "--set" "ingress.tls[0].hosts[0]=$DOMAIN"
        )
    fi

    # Add email for cert-manager if provided
    if [[ -n "${EMAIL:-}" ]]; then
        helm_args+=(
            "--set" "certManager.clusterIssuer.email=$EMAIL"
        )
    fi

    # Add deployment flags
    if [[ "$DRY_RUN" == "true" ]]; then
        helm_args+=("--dry-run" "--debug")
    else
        helm_args+=("--atomic" "--timeout" "10m" "--wait")
    fi

    # Update dependencies
    log_info "Updating Helm dependencies..."
    helm dependency update "$PROJECT_ROOT/helm/todo-chatbot"

    # Run deployment
    log_info "Running Helm deployment..."
    helm "${helm_args[@]}"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Dry run completed successfully"
        return
    fi

    log_success "Helm deployment completed"
}

# Apply Dapr components
apply_dapr_components() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "Skipping Dapr components in dry-run mode"
        return
    fi

    log_info "Applying Dapr components..."

    # Use DigitalOcean-specific components
    kubectl apply -f "$PROJECT_ROOT/dapr/components/kafka-pubsub-digitalocean.yaml" -n "$NAMESPACE"
    kubectl apply -f "$PROJECT_ROOT/dapr/components/statestore-digitalocean.yaml" -n "$NAMESPACE"
    kubectl apply -f "$PROJECT_ROOT/dapr/components/subscription-reminders.yaml" -n "$NAMESPACE"
    kubectl apply -f "$PROJECT_ROOT/dapr/components/subscription-task-events.yaml" -n "$NAMESPACE"

    log_success "Dapr components applied"
}

# Verify deployment
verify_deployment() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return
    fi

    log_info "Verifying deployment..."

    local deployments=(
        "todo-chatbot-backend"
        "todo-chatbot-frontend"
        "todo-chatbot-notification-service"
        "todo-chatbot-recurring-service"
    )

    for deployment in "${deployments[@]}"; do
        log_info "Checking $deployment..."
        if ! kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s; then
            log_error "Deployment $deployment failed to become ready"
            kubectl logs deployment/"$deployment" -n "$NAMESPACE" --tail=50
            exit 1
        fi
    done

    log_success "All deployments are ready"
}

# Print summary
print_summary() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return
    fi

    echo ""
    log_success "=========================================="
    log_success "  TaskAI Deployment Complete!"
    log_success "=========================================="
    echo ""
    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
    log_info "Image Tag: $IMAGE_TAG"
    echo ""

    log_info "Services:"
    kubectl get services -n "$NAMESPACE"
    echo ""

    log_info "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""

    log_info "Ingress:"
    kubectl get ingress -n "$NAMESPACE"
    echo ""

    if [[ -n "${DOMAIN:-}" ]]; then
        log_info "Application URL: https://$DOMAIN"
        log_info "API URL: https://$DOMAIN/api"
    else
        local ingress_ip
        ingress_ip=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        if [[ -n "$ingress_ip" ]]; then
            log_info "LoadBalancer IP: $ingress_ip"
            log_info "Application URL: http://$ingress_ip"
        fi
    fi
}

# Main function
main() {
    parse_args "$@"

    echo ""
    log_info "=========================================="
    log_info "  TaskAI DigitalOcean Deployment"
    log_info "=========================================="
    echo ""
    log_info "Cluster: $CLUSTER_NAME"
    log_info "Registry: $REGISTRY_NAME"
    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
    log_info "Image Tag: $IMAGE_TAG"
    [[ -n "${DOMAIN:-}" ]] && log_info "Domain: $DOMAIN"
    [[ "$DRY_RUN" == "true" ]] && log_warn "DRY RUN MODE"
    echo ""

    check_prerequisites
    connect_cluster
    login_registry
    install_dapr
    install_cert_manager
    install_ingress
    create_secrets
    deploy_application
    apply_dapr_components
    verify_deployment
    print_summary
}

main "$@"
