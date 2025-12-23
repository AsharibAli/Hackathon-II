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
#   .\scripts\deploy-minikube.ps1 [-OpenAIKey <key>] [-DatabaseUrl <url>] [-SkipBuild] [-Clean]

param(
    [string]$OpenAIKey = $env:OPENAI_API_KEY,
    [string]$DatabaseUrl = $env:DATABASE_URL,
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
$EnvFile = Join-Path $ProjectDir ".env"

# Load .env file if it exists
if (Test-Path $EnvFile) {
    Write-Host "[INFO] Loading configuration from .env file..." -ForegroundColor Blue
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Only set if not already provided via parameter or env var
            if ($key -eq "DATABASE_URL" -and [string]::IsNullOrEmpty($DatabaseUrl)) {
                $script:DatabaseUrl = $value
            }
            if ($key -eq "OPENAI_API_KEY" -and [string]::IsNullOrEmpty($OpenAIKey)) {
                $script:OpenAIKey = $value
            }
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
    -OpenAIKey <key>     Set OpenAI API key
    -DatabaseUrl <url>   Set external database URL (e.g., Neon PostgreSQL)
    -SkipBuild           Skip Docker image build
    -Clean               Clean up existing deployment first
    -Help                Show this help message

Examples:
    .\deploy-minikube.ps1 -OpenAIKey "sk-..."
    .\deploy-minikube.ps1 -OpenAIKey "sk-..." -DatabaseUrl "postgresql://..."  
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
        --build-arg NEXT_PUBLIC_API_URL="http://localhost:8080" `
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
    $helmArgs = @(
        "upgrade", "--install", $ReleaseName, $ChartPath,
        "--namespace", $Namespace,
        "--create-namespace",
        "--set", "secrets.openaiApiKey=$OpenAIKey",
        "--set", "frontend.env.NEXT_PUBLIC_API_URL=http://localhost:8080",
        "--wait",
        "--timeout", "10m"
    )

    # Add external database config if DATABASE_URL is provided
    if (-not [string]::IsNullOrEmpty($DatabaseUrl)) {
        Write-Info "Using external database (DATABASE_URL provided)"
        $helmArgs += "--set", "externalDatabase.enabled=true"
        $helmArgs += "--set", "externalDatabase.url=$DatabaseUrl"
        $helmArgs += "--set", "postgresql.enabled=false"
    } else {
        Write-Info "Using local PostgreSQL database"
    }

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

# Start port forwarding for services
function Start-PortForwarding {
    Write-Info "Setting up port forwarding for localhost access..."

    # Kill any existing port-forward processes on our ports
    $existingProcesses = Get-NetTCPConnection -LocalPort 8080, 3000 -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $existingProcesses) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }

    # Start port forwarding for backend (8080 -> backend service)
    $backendJob = Start-Job -ScriptBlock {
        param($ns)
        kubectl port-forward svc/taskai-backend 8080:8000 -n $ns 2>&1
    } -ArgumentList $Namespace

    # Start port forwarding for frontend (3000 -> frontend service)
    $frontendJob = Start-Job -ScriptBlock {
        param($ns)
        kubectl port-forward svc/taskai-frontend 3000:3000 -n $ns 2>&1
    } -ArgumentList $Namespace

    # Wait a moment for port forwarding to establish
    Start-Sleep -Seconds 3

    # Verify port forwarding is working
    $backendJobState = Get-Job -Id $backendJob.Id
    $frontendJobState = Get-Job -Id $frontendJob.Id

    if ($backendJobState.State -eq "Running" -and $frontendJobState.State -eq "Running") {
        Write-Success "Port forwarding established successfully"
    } else {
        Write-Warning "Port forwarding may not be fully established. Check the job status with Get-Job"
    }

    # Store job IDs for later reference
    $script:BackendJobId = $backendJob.Id
    $script:FrontendJobId = $frontendJob.Id
}

# Display access information
function Show-AccessInfo {
    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host "  TaskAI Deployment Successful!" -ForegroundColor Green
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs (via port-forwarding):" -ForegroundColor White
    Write-Host "  Frontend:     " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  Backend API:  " -NoNewline; Write-Host "http://localhost:8080" -ForegroundColor Cyan
    Write-Host "  Swagger Docs: " -NoNewline; Write-Host "http://localhost:8080/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Port Forwarding Status:" -ForegroundColor Yellow
    Write-Host "  Backend Job ID:  $script:BackendJobId (port 8080 -> backend:8000)"
    Write-Host "  Frontend Job ID: $script:FrontendJobId (port 3000 -> frontend:3000)"
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor White
    Write-Host "  View pods:         kubectl get pods -n $Namespace"
    Write-Host "  View backend logs: kubectl logs -f deploy/taskai-backend -n $Namespace"
    Write-Host "  View frontend logs: kubectl logs -f deploy/taskai-frontend -n $Namespace"
    Write-Host "  Open dashboard:    minikube dashboard"
    Write-Host "  Check port-forward: Get-Job | Where-Object { `$_.State -eq 'Running' }"
    Write-Host ""
    Write-Host "To stop port forwarding:" -ForegroundColor Yellow
    Write-Host "  Stop-Job $script:BackendJobId, $script:FrontendJobId"
    Write-Host "  Remove-Job $script:BackendJobId, $script:FrontendJobId"
    Write-Host ""
    Write-Host "To uninstall:" -ForegroundColor Yellow
    Write-Host "  helm uninstall $ReleaseName -n $Namespace"
    Write-Host "  kubectl delete namespace $Namespace"
    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Green
    Write-Host "  Services are now accessible on localhost!" -ForegroundColor Green
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
    Build-Images
    Deploy-Helm
    Wait-ForPods
    Start-PortForwarding
    Show-AccessInfo
}

Main
