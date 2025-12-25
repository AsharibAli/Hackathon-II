# [Task]: T110
# [Spec]: F-009 (US11)
# [Description]: PowerShell script to deploy TaskAI to Minikube
# ==============================================
# TaskAI - Minikube Deployment Script (PowerShell)
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
#   .\scripts\deploy-minikube.ps1 [-SkipBuild] [-SkipKafka] [-SkipDapr] [-Clean]

param(
    [switch]$SkipBuild,
    [switch]$SkipKafka,
    [switch]$SkipDapr,
    [switch]$Clean,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$Namespace = "todo-app"
$ReleaseName = "todo-chatbot"
$ChartPath = Join-Path $ProjectDir "helm\todo-chatbot"
$EnvFile = Join-Path $ProjectDir ".env"

# Load .env file if it exists
if (Test-Path $EnvFile) {
    Write-Host "[INFO] Loading configuration from .env file..." -ForegroundColor Blue
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$key" -Value $value -ErrorAction SilentlyContinue
        }
    }
}

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
    -SkipBuild           Skip Docker image build
    -SkipKafka           Skip Kafka/Strimzi installation
    -SkipDapr            Skip Dapr installation
    -Clean               Clean up existing deployment first
    -Help                Show this help message

Examples:
    .\deploy-minikube.ps1
    .\deploy-minikube.ps1 -SkipBuild
    .\deploy-minikube.ps1 -SkipKafka -SkipDapr
    .\deploy-minikube.ps1 -Clean

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
    if (-not $SkipDapr -and -not (Get-Command dapr -ErrorAction SilentlyContinue)) { $missing += "dapr" }

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

# Install Strimzi Kafka
function Install-Kafka {
    if ($SkipKafka) {
        Write-Info "Skipping Kafka installation (-SkipKafka)"
        return
    }

    Write-Info "Installing Strimzi Kafka Operator..."

    # Check if Strimzi namespace exists
    $strimziNs = kubectl get namespace strimzi-system --ignore-not-found -o name 2>&1
    if (-not $strimziNs) {
        kubectl create namespace strimzi-system
    }

    # Install Strimzi operator
    kubectl apply -f "https://strimzi.io/install/latest?namespace=strimzi-system" -n strimzi-system

    Write-Info "Waiting for Strimzi operator to be ready..."
    kubectl wait --for=condition=available deployment/strimzi-cluster-operator -n strimzi-system --timeout=300s

    # Deploy Kafka cluster
    Write-Info "Deploying Kafka cluster..."
    kubectl apply -f "$ProjectDir/infra/minikube/kafka-cluster.yaml"

    Write-Info "Waiting for Kafka cluster to be ready (this may take a few minutes)..."
    Start-Sleep -Seconds 30
    kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=600s -n kafka

    Write-Success "Kafka cluster deployed"
}

# Install Dapr
function Install-Dapr {
    if ($SkipDapr) {
        Write-Info "Skipping Dapr installation (-SkipDapr)"
        return
    }

    Write-Info "Installing Dapr..."

    # Check if Dapr is already installed
    $daprInstalled = dapr status -k 2>&1
    if ($LASTEXITCODE -ne 0) {
        dapr init -k --wait
    } else {
        Write-Info "Dapr is already installed"
    }

    Write-Success "Dapr installed"
}

# Apply Dapr components
function Apply-DaprComponents {
    Write-Info "Creating namespace and Dapr components..."

    # Create todo-app namespace
    $todoNs = kubectl get namespace $Namespace --ignore-not-found -o name 2>&1
    if (-not $todoNs) {
        kubectl create namespace $Namespace
    }

    # Apply Dapr components
    kubectl apply -f "$ProjectDir/dapr/components/" -n $Namespace

    Write-Success "Namespace and Dapr components created"
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
    docker build -t todo-chatbot/backend:latest "$ProjectDir\backend"
    Write-Success "Backend image built"

    Write-Info "Building frontend Docker image..."
    docker build `
        --build-arg NEXT_PUBLIC_API_URL="http://localhost:30080" `
        -t todo-chatbot/frontend:latest `
        "$ProjectDir\frontend"
    Write-Success "Frontend image built"

    Write-Info "Building notification-service Docker image..."
    docker build -t todo-chatbot/notification-service:latest "$ProjectDir\notification-service"
    Write-Success "Notification service image built"

    Write-Info "Building recurring-service Docker image..."
    docker build -t todo-chatbot/recurring-service:latest "$ProjectDir\recurring-service"
    Write-Success "Recurring service image built"
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

# Update Helm dependencies
function Update-HelmDeps {
    Write-Info "Updating Helm dependencies..."
    Push-Location "$ProjectDir/helm/todo-chatbot"
    helm dependency update
    Pop-Location
    Write-Success "Helm dependencies updated"
}

# Deploy with Helm
function Deploy-Helm {
    Write-Info "Deploying TaskAI with Helm..."

    # Deploy or upgrade using Minikube values
    $helmArgs = @(
        "upgrade", "--install", $ReleaseName, $ChartPath,
        "-f", "$ChartPath/values-minikube.yaml",
        "--namespace", $Namespace,
        "--create-namespace",
        "--wait",
        "--timeout", "10m"
    )

    & helm @helmArgs

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

# No port forwarding needed - using NodePort in Minikube

# Display access information
function Show-AccessInfo {
    $minikubeIp = minikube ip

    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host "  TaskAI Deployment Successful!" -ForegroundColor Green
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs (via NodePort):" -ForegroundColor White
    Write-Host "  Frontend:     " -NoNewline; Write-Host "http://${minikubeIp}:30000" -ForegroundColor Cyan
    Write-Host "  Backend API:  " -NoNewline; Write-Host "http://${minikubeIp}:30080" -ForegroundColor Cyan
    Write-Host "  Swagger Docs: " -NoNewline; Write-Host "http://${minikubeIp}:30080/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor White
    Write-Host "  View pods:           kubectl get pods -n $Namespace"
    Write-Host "  View backend logs:   kubectl logs -f deploy/todo-chatbot-backend -n $Namespace"
    Write-Host "  View frontend logs:  kubectl logs -f deploy/todo-chatbot-frontend -n $Namespace"
    Write-Host "  Dapr dashboard:      dapr dashboard -k"
    Write-Host "  Minikube dashboard:  minikube dashboard"
    Write-Host ""
    Write-Host "To verify deployment, run:" -ForegroundColor Yellow
    Write-Host "  .\scripts\verify-deployment.ps1"
    Write-Host ""
    Write-Host "To uninstall:" -ForegroundColor Yellow
    Write-Host "  helm uninstall $ReleaseName -n $Namespace"
    Write-Host "  kubectl delete namespace $Namespace"
    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host "  Services are now accessible via Minikube IP!" -ForegroundColor Green
    Write-Host "===========================================================" -ForegroundColor Green
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
    Install-Kafka
    Install-Dapr
    Apply-DaprComponents
    Build-Images
    Update-HelmDeps
    Deploy-Helm
    Wait-ForPods
    Show-AccessInfo
}

Main
