#!/bin/bash

# Master Deployment Script - Deploy All TaskAI Services
# Usage:
#   ./deploy-all.sh                    # Deploy all with :latest tag
#   ./deploy-all.sh v1.0.1             # Deploy all with specific version
#   ./deploy-all.sh --services=backend,frontend   # Deploy specific services

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
VERSION="latest"
SERVICES="backend,recurring-service,notification-service,frontend"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --services=*)
            SERVICES="${arg#*=}"
            shift
            ;;
        --version=*)
            VERSION="${arg#*=}"
            shift
            ;;
        -*)
            echo "Unknown option: $arg"
            echo "Usage: ./deploy-all.sh [v1.0.1] [--services=backend,frontend]"
            exit 1
            ;;
        *)
            # Assume it's a version if it doesn't start with --
            VERSION="$arg"
            shift
            ;;
    esac
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}║         TaskAI Master Deployment Script               ║${NC}"
echo -e "${BLUE}║                                                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📦 Version: ${VERSION}${NC}"
echo -e "${YELLOW}🎯 Services: ${SERVICES}${NC}"
echo ""

# Convert services to array
IFS=',' read -ra SERVICE_ARRAY <<< "$SERVICES"

# Track deployment status
DEPLOYED=0
FAILED=0
SKIPPED=0

deploy_service() {
    local service=$1
    local script_name=""

    case $service in
        backend)
            script_name="deploy-backend.sh"
            ;;
        recurring-service|recurring)
            script_name="deploy-recurring-service.sh"
            ;;
        notification-service|notification)
            script_name="deploy-notification-service.sh"
            ;;
        frontend)
            script_name="deploy-frontend.sh"
            ;;
        *)
            echo -e "${RED}❌ Unknown service: ${service}${NC}"
            return 1
            ;;
    esac

    local script_path="${SCRIPT_DIR}/${script_name}"

    if [ ! -f "$script_path" ]; then
        echo -e "${RED}❌ Script not found: ${script_path}${NC}"
        return 1
    fi

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🚀 Deploying ${service}...${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""

    # Run deployment script
    bash "$script_path" "$VERSION"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${service} deployed successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ ${service} deployment failed${NC}"
        return 1
    fi
}

# Start deployment timer
START_TIME=$(date +%s)

# Deploy each service
for service in "${SERVICE_ARRAY[@]}"; do
    # Trim whitespace
    service=$(echo "$service" | xargs)

    if deploy_service "$service"; then
        ((DEPLOYED++))
    else
        ((FAILED++))

        # Ask if user wants to continue
        if [ ${#SERVICE_ARRAY[@]} -gt 1 ]; then
            read -p "Continue with remaining services? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Deployment cancelled by user"
                break
            fi
        fi
    fi
done

# Calculate deployment time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}           Deployment Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ Successfully deployed: ${DEPLOYED}${NC}"
echo -e "${RED}❌ Failed: ${FAILED}${NC}"
echo -e "${YELLOW}⏱️  Total time: ${MINUTES}m ${SECONDS}s${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All services deployed successfully!${NC}"
    echo ""
    echo "📊 View deployment status:"
    echo "   kubectl get pods -n todo-app"
    echo ""
    echo "🌐 Visit application:"
    echo "   https://taskai.asharib.xyz"
    echo ""
else
    echo -e "${RED}⚠️  Some deployments failed. Check logs above for details.${NC}"
    exit 1
fi
