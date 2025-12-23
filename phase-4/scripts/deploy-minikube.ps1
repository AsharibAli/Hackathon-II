# ==============================================
# TaskAI - Minikube Deployment Script (PowerShell)
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
#   .\scripts\deploy-minikube.ps1 [-OpenAIKey <key>] [-SkipBuild] [-Clean]

param(
    [string]$OpenAIKey = $env:OPENAI_API_KEY,
    [switch]$SkipBuild,
    [switch]$Clean,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$Namespace = "taskai"
$ReleaseName = "taskai"
$ChartPath = Join-Path $ProjectDir "helm\taskai"

# Helper functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

if ($Help) {
    Write-Host @"

TaskAI - Minikube Deployment Script

Usage:
    .\deploy-minikube.ps1 [OPTIONS]

Options:
    -OpenAIKey <key>    Set OpenAI API key
    -SkipBuild          Skip Docker image build
    -Clean              Clean up existing deployment first
    -Help               Show this help message

Examples:
    .\deploy-minikube.ps1 -OpenAIKey "sk-..."
    .\deploy-minikube.ps1 -SkipBuild
    .\deploy-minikube.ps1 -Clean -OpenAIKey "sk-..."

"@
    exit 0
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."

    $missing = @()

    if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) { $missing += "minikube" }
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) { $missing += "kubectl" }
    if (-not (Get-Command helm -ErrorAction SilentlyContinue)) { $missing += "helm" }
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { $missing += "docker" }

    if ($missing.Count -gt 0) {
        Write-Error "Missing required tools: $($missing -join ', ')"
        Write-Info "Please install them and try again."
        exit 1
    }

    Write-Success "All prerequisites are installed"
}

# Start Minikube
function Start-Minikube {
    Write-Info "Checking Minikube status..."

    $status = minikube status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Info "Starting Minikube..."
        minikube start --cpus=4 --memory=8192 --driver=docker
        Write-Success "Minikube started"
    } else {
        Write-Info "Minikube is already running"
    }

    # Enable required addons
    Write-Info "Enabling Minikube addons..."
    minikube addons enable metrics-server 2>$null
    minikube addons enable storage-provisioner 2>$null
}

# Build Docker images
function Build-Images {
    if ($SkipBuild) {
        Write-Info "Skipping Docker image build (-SkipBuild)"
        return
    }

    Write-Info "Configuring Docker to use Minikube's daemon..."
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression

    Write-Info "Building backend Docker image..."
    docker build -t taskai-backend:latest "$ProjectDir\backend"
    Write-Success "Backend image built"

    Write-Info "Building frontend Docker image..."
    docker build `
        --build-arg NEXT_PUBLIC_API_URL="http://localhost:30800" `
        -t taskai-frontend:latest `
        "$ProjectDir\frontend"
    Write-Success "Frontend image built"
}

# Clean up existing deployment
function Remove-ExistingDeployment {
    if ($Clean) {
        Write-Info "Cleaning up existing deployment..."

        helm uninstall $ReleaseName -n $Namespace 2>$null
        kubectl delete namespace $Namespace 2>$null

        # Wait for namespace to be deleted
        while (kubectl get namespace $Namespace 2>$null) {
            Write-Info "Waiting for namespace to be deleted..."
            Start-Sleep -Seconds 2
        }

        Write-Success "Cleanup completed"
    }
}

# Deploy with Helm
function Deploy-Helm {
    Write-Info "Deploying TaskAI with Helm..."

    # Check if OpenAI API key is set
    if ([string]::IsNullOrEmpty($OpenAIKey)) {
        Write-Warning "OPENAI_API_KEY is not set. Chat functionality will not work."
        Write-Info "Set it with: -OpenAIKey <your-key> or `$env:OPENAI_API_KEY=<your-key>"
    }

    # Check if namespace exists
    $nsExists = kubectl get namespace $Namespace 2>$null
    if ($nsExists) {
        # Check if it's managed by Helm
        $managedBy = kubectl get namespace $Namespace -o jsonpath='{.metadata.labels.app\.kubernetes\.io/managed-by}' 2>$null
        if ($managedBy -ne "Helm") {
            Write-Info "Namespace exists but not managed by Helm. Deleting and recreating..."
            kubectl delete namespace $Namespace 2>$null
            # Wait for namespace to be fully deleted
            while (kubectl get namespace $Namespace 2>$null) {
                Write-Info "Waiting for namespace to be deleted..."
                Start-Sleep -Seconds 2
            }
        }
    }

    # Deploy or upgrade
    helm upgrade --install $ReleaseName $ChartPath `
        --namespace $Namespace `
        --create-namespace `
        --set secrets.openaiApiKey="$OpenAIKey" `
        --set frontend.env.NEXT_PUBLIC_API_URL="http://localhost:30800" `
        --wait `
        --timeout 10m

    Write-Success "Helm deployment completed"
}

# Wait for pods to be ready
function Wait-ForPods {
    Write-Info "Waiting for all pods to be ready..."

    kubectl wait --for=condition=ready pod `
        --all `
        --namespace $Namespace `
        --timeout=300s

    Write-Success "All pods are ready"
}

# Display access information
function Show-AccessInfo {
    $minikubeIp = minikube ip

    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host "  TaskAI Deployment Successful!" -ForegroundColor Green
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:"
    Write-Host "  Frontend: http://${minikubeIp}:30300" -ForegroundColor Cyan
    Write-Host "  Backend API: http://${minikubeIp}:30800" -ForegroundColor Cyan
    Write-Host "  Swagger Docs: http://${minikubeIp}:30800/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Alternative (localhost access via minikube tunnel):"
    Write-Host "  Run: minikube tunnel" -ForegroundColor Yellow -NoNewline
    Write-Host " in a separate terminal"
    Write-Host "  Frontend: http://localhost:30300" -ForegroundColor Cyan
    Write-Host "  Backend: http://localhost:30800" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Useful commands:"
    Write-Host "  View pods:      kubectl get pods -n $Namespace"
    Write-Host "  View logs:      kubectl logs -f deploy/taskai-backend -n $Namespace"
    Write-Host "  Open dashboard: minikube dashboard"
    Write-Host ""
    Write-Host "To uninstall:"
    Write-Host "  helm uninstall $ReleaseName -n $Namespace"
    Write-Host "  kubectl delete namespace $Namespace"
    Write-Host ""
}

# Main execution
function Main {
    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host "  TaskAI - Minikube Deployment" -ForegroundColor Cyan
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host ""

    Test-Prerequisites
    Start-Minikube
    Remove-ExistingDeployment
    Build-Images
    Deploy-Helm
    Wait-ForPods
    Show-AccessInfo
}

Main
