#!/bin/bash
# [Task]: T111
# [Spec]: F-009 (US11)
# [Description]: Deployment verification script for TaskAI
# ==============================================
# TaskAI - Deployment Verification Script
# ==============================================
# This script verifies that the TaskAI application is properly deployed
# and all components are functioning correctly.
#
# Usage:
#   ./scripts/verify-deployment.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

NAMESPACE="todo-app"
PASSED=0
FAILED=0

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASSED++)); }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; ((FAILED++)); }

# Check if namespace exists
check_namespace() {
    log_info "Checking namespace..."
    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        log_success "Namespace '$NAMESPACE' exists"
    else
        log_error "Namespace '$NAMESPACE' does not exist"
        return 1
    fi
}

# Check pods status
check_pods() {
    log_info "Checking pods..."

    local pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

    if [ -z "$pods" ]; then
        log_error "No pods found in namespace '$NAMESPACE'"
        return 1
    fi

    for pod in $pods; do
        local status=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
        local ready=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[0].ready}')

        if [[ "$status" == "Running" && "$ready" == "true" ]]; then
            log_success "Pod '$pod' is running and ready"
        else
            log_error "Pod '$pod' - Status: $status, Ready: $ready"
        fi
    done
}

# Check services
check_services() {
    log_info "Checking services..."

    local services=(
        "todo-chatbot-frontend"
        "todo-chatbot-backend"
        "todo-chatbot-notification-service"
        "todo-chatbot-recurring-service"
    )

    for svc in "${services[@]}"; do
        if kubectl get svc "$svc" -n "$NAMESPACE" >/dev/null 2>&1; then
            local type=$(kubectl get svc "$svc" -n "$NAMESPACE" -o jsonpath='{.spec.type}')
            local port=$(kubectl get svc "$svc" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}')
            log_success "Service '$svc' exists (Type: $type, Port: $port)"
        else
            log_error "Service '$svc' not found"
        fi
    done
}

# Check deployments
check_deployments() {
    log_info "Checking deployments..."

    local deployments=(
        "todo-chatbot-frontend"
        "todo-chatbot-backend"
        "todo-chatbot-notification-service"
        "todo-chatbot-recurring-service"
    )

    for deploy in "${deployments[@]}"; do
        if kubectl get deployment "$deploy" -n "$NAMESPACE" >/dev/null 2>&1; then
            local ready=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
            local desired=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
            ready=${ready:-0}

            if [[ "$ready" == "$desired" ]]; then
                log_success "Deployment '$deploy' has $ready/$desired replicas ready"
            else
                log_error "Deployment '$deploy' has $ready/$desired replicas ready"
            fi
        else
            log_error "Deployment '$deploy' not found"
        fi
    done
}

# Check Dapr sidecars
check_dapr() {
    log_info "Checking Dapr sidecars..."

    local dapr_enabled_deployments=(
        "todo-chatbot-backend"
        "todo-chatbot-notification-service"
        "todo-chatbot-recurring-service"
    )

    for deploy in "${dapr_enabled_deployments[@]}"; do
        local pod=$(kubectl get pods -n "$NAMESPACE" -l "app.kubernetes.io/name=${deploy#todo-chatbot-}" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
        if [ -n "$pod" ]; then
            local containers=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}')
            if echo "$containers" | grep -q "daprd"; then
                log_success "Dapr sidecar found in '$deploy'"
            else
                log_warning "Dapr sidecar not found in '$deploy' (containers: $containers)"
            fi
        fi
    done
}

# Check Kafka cluster
check_kafka() {
    log_info "Checking Kafka cluster..."

    if kubectl get kafka kafka-cluster -n kafka >/dev/null 2>&1; then
        local ready=$(kubectl get kafka kafka-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
        if [ "$ready" = "True" ]; then
            log_success "Kafka cluster is ready"
        else
            log_warning "Kafka cluster is not ready (status: $ready)"
        fi
    else
        log_warning "Kafka cluster not found in 'kafka' namespace"
    fi
}

# Check Dapr components
check_dapr_components() {
    log_info "Checking Dapr components..."

    local components=("kafka-pubsub" "statestore")

    for component in "${components[@]}"; do
        if kubectl get component "$component" -n "$NAMESPACE" >/dev/null 2>&1; then
            log_success "Dapr component '$component' exists"
        else
            log_warning "Dapr component '$component' not found"
        fi
    done
}

# Check API health
check_api_health() {
    log_info "Checking API health..."

    local backend_url="http://localhost:8000"

    if curl -s --connect-timeout 5 "${backend_url}/health" >/dev/null 2>&1; then
        log_success "Backend API health check passed at ${backend_url}/health"
    elif curl -s --connect-timeout 5 "${backend_url}/docs" >/dev/null 2>&1; then
        log_success "Backend API is accessible at ${backend_url}/docs"
    else
        log_warning "Cannot reach backend at ${backend_url}. Make sure port-forwarding is running."
    fi

    local frontend_url="http://localhost:3000"

    if curl -s --connect-timeout 5 "${frontend_url}" >/dev/null 2>&1; then
        log_success "Frontend is accessible at ${frontend_url}"
    else
        log_warning "Cannot reach frontend at ${frontend_url}. Make sure port-forwarding is running."
    fi
}

# Check secrets
check_secrets() {
    log_info "Checking secrets..."

    if kubectl get secret todo-chatbot-backend-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
        log_success "Backend secrets exist"
    else
        log_warning "Backend secrets not found (might be using inline config)"
    fi
}

# Display resource usage
show_resources() {
    log_info "Resource usage..."

    echo ""
    echo "Pods:"
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "  (metrics-server not available or pods not ready)"
    echo ""
}

# Display pod logs summary
show_recent_logs() {
    log_info "Recent logs (last 5 lines per pod)..."
    echo ""

    local pods=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')
    for pod in $pods; do
        echo -e "${CYAN}=== $pod ===${NC}"
        kubectl logs "$pod" -n "$NAMESPACE" --tail=5 2>/dev/null || echo "  (no logs available)"
        echo ""
    done
}

# Display summary
show_summary() {
    echo ""
    echo "==========================================================="
    echo "  Verification Summary"
    echo "==========================================================="
    echo ""
    echo -e "  Passed: ${GREEN}${PASSED}${NC}"
    echo -e "  Failed: ${RED}${FAILED}${NC}"
    echo ""

    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All checks passed! Deployment is healthy.${NC}"
        echo ""
        echo "Access URLs:"
        echo -e "  Frontend:     ${CYAN}http://localhost:3000${NC}"
        echo -e "  Backend API:  ${CYAN}http://localhost:8000${NC}"
        echo -e "  Swagger Docs: ${CYAN}http://localhost:8000/docs${NC}"
        exit 0
    else
        echo -e "${RED}Some checks failed. Please review the issues above.${NC}"
        exit 1
    fi
}

# Main execution
main() {
    echo ""
    echo -e "${CYAN}===========================================================${NC}"
    echo -e "${CYAN}  TaskAI - Deployment Verification${NC}"
    echo -e "${CYAN}===========================================================${NC}"
    echo ""

    check_namespace
    echo ""
    check_pods
    echo ""
    check_services
    echo ""
    check_deployments
    echo ""
    check_dapr
    echo ""
    check_kafka
    echo ""
    check_dapr_components
    echo ""
    check_secrets
    echo ""
    check_api_health
    echo ""
    show_resources
    show_summary
}

main "$@"
