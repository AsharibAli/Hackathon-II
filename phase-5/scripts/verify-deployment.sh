#!/bin/bash
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
NC='\033[0m'

NAMESPACE="taskai"
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

    local services=("taskai-frontend" "taskai-backend" "taskai-postgresql")

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

    local deployments=("taskai-frontend" "taskai-backend" "taskai-postgresql")

    for deploy in "${deployments[@]}"; do
        if kubectl get deployment "$deploy" -n "$NAMESPACE" >/dev/null 2>&1; then
            local ready=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
            local desired=$(kubectl get deployment "$deploy" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')

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

# Check PVC
check_pvc() {
    log_info "Checking persistent volume claims..."

    if kubectl get pvc -n "$NAMESPACE" 2>/dev/null | grep -q "taskai.*postgresql"; then
        local status=$(kubectl get pvc -n "$NAMESPACE" -o jsonpath='{.items[0].status.phase}')
        if [[ "$status" == "Bound" ]]; then
            log_success "PostgreSQL PVC is bound"
        else
            log_warning "PostgreSQL PVC status: $status"
        fi
    else
        log_warning "No PostgreSQL PVC found (might be using emptyDir)"
    fi
}

# Check API health
check_api_health() {
    log_info "Checking API health..."

    local backend_url="http://localhost:8080"

    if curl -s --connect-timeout 5 "${backend_url}/docs" >/dev/null 2>&1; then
        log_success "Backend API is accessible at ${backend_url}"
    else
        log_warning "Cannot reach backend at ${backend_url}. Make sure port-forwarding is running."
    fi
}

# Check secrets
check_secrets() {
    log_info "Checking secrets..."

    if kubectl get secret taskai-secrets -n "$NAMESPACE" >/dev/null 2>&1; then
        local keys=$(kubectl get secret taskai-secrets -n "$NAMESPACE" -o jsonpath='{.data}' | grep -o '"[^"]*":' | tr -d '":')
        log_success "Secret 'taskai-secrets' exists with keys: $(echo $keys | tr '\n' ', ')"
    else
        log_error "Secret 'taskai-secrets' not found"
    fi
}

# Display resource usage
show_resources() {
    log_info "Resource usage..."

    echo ""
    echo "Pods:"
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "  (metrics-server not available)"
    echo ""
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
        exit 0
    else
        echo -e "${RED}Some checks failed. Please review the issues above.${NC}"
        exit 1
    fi
}

# Main execution
main() {
    echo ""
    echo "==========================================================="
    echo "  TaskAI - Deployment Verification"
    echo "==========================================================="
    echo ""

    check_namespace
    echo ""
    check_pods
    echo ""
    check_services
    echo ""
    check_deployments
    echo ""
    check_pvc
    echo ""
    check_secrets
    echo ""
    check_api_health
    echo ""
    show_resources
    show_summary
}

main "$@"
