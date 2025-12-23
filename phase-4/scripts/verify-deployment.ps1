# ==============================================
# TaskAI - Deployment Verification Script (PowerShell)
# ==============================================
# This script verifies that the TaskAI application is properly deployed
# and all components are functioning correctly.
#
# Usage:
#   .\scripts\verify-deployment.ps1

$ErrorActionPreference = "Continue"

$Namespace = "taskai"
$script:Passed = 0
$script:Failed = 0

# Helper functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Pass { param($Message) Write-Host "[PASS] $Message" -ForegroundColor Green; $script:Passed++ }
function Write-Warning { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Fail { param($Message) Write-Host "[FAIL] $Message" -ForegroundColor Red; $script:Failed++ }

# Check if namespace exists
function Test-Namespace {
    Write-Info "Checking namespace..."
    $result = kubectl get namespace $Namespace 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Namespace '$Namespace' exists"
    } else {
        Write-Fail "Namespace '$Namespace' does not exist"
    }
}

# Check pods status
function Test-Pods {
    Write-Info "Checking pods..."

    $pods = kubectl get pods -n $Namespace -o json | ConvertFrom-Json

    foreach ($pod in $pods.items) {
        $name = $pod.metadata.name
        $phase = $pod.status.phase
        $ready = $pod.status.containerStatuses[0].ready

        if ($phase -eq "Running" -and $ready -eq $true) {
            Write-Pass "Pod '$name' is running and ready"
        } else {
            Write-Fail "Pod '$name' - Status: $phase, Ready: $ready"
        }
    }
}

# Check services
function Test-Services {
    Write-Info "Checking services..."

    $services = @("taskai-frontend", "taskai-backend", "taskai-postgresql")

    foreach ($svc in $services) {
        $result = kubectl get svc $svc -n $Namespace -o json 2>&1
        if ($LASTEXITCODE -eq 0) {
            $svcObj = $result | ConvertFrom-Json
            $type = $svcObj.spec.type
            $port = $svcObj.spec.ports[0].port
            Write-Pass "Service '$svc' exists (Type: $type, Port: $port)"
        } else {
            Write-Fail "Service '$svc' not found"
        }
    }
}

# Check deployments
function Test-Deployments {
    Write-Info "Checking deployments..."

    $deployments = @("taskai-frontend", "taskai-backend", "taskai-postgresql")

    foreach ($deploy in $deployments) {
        $result = kubectl get deployment $deploy -n $Namespace -o json 2>&1
        if ($LASTEXITCODE -eq 0) {
            $depObj = $result | ConvertFrom-Json
            $ready = $depObj.status.readyReplicas
            $desired = $depObj.spec.replicas

            if ($ready -eq $desired) {
                Write-Pass "Deployment '$deploy' has $ready/$desired replicas ready"
            } else {
                Write-Fail "Deployment '$deploy' has $ready/$desired replicas ready"
            }
        } else {
            Write-Fail "Deployment '$deploy' not found"
        }
    }
}

# Check secrets
function Test-Secrets {
    Write-Info "Checking secrets..."

    $result = kubectl get secret taskai-secrets -n $Namespace -o json 2>&1
    if ($LASTEXITCODE -eq 0) {
        $secret = $result | ConvertFrom-Json
        $keys = $secret.data.PSObject.Properties.Name -join ", "
        Write-Pass "Secret 'taskai-secrets' exists with keys: $keys"
    } else {
        Write-Fail "Secret 'taskai-secrets' not found"
    }
}

# Check API health
function Test-APIHealth {
    Write-Info "Checking API health..."

    $backendUrl = "http://localhost:30800"

    # Try to get Minikube IP
    $minikubeIp = minikube ip 2>$null
    if ($LASTEXITCODE -eq 0) {
        $backendUrl = "http://${minikubeIp}:30800"
    }

    try {
        $response = Invoke-WebRequest -Uri "$backendUrl/docs" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Pass "Backend API is accessible at $backendUrl"
        }
    } catch {
        Write-Warning "Cannot reach backend at $backendUrl. Run 'minikube tunnel' if using localhost."
    }
}

# Display summary
function Show-Summary {
    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host "  Verification Summary" -ForegroundColor Cyan
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Passed: $script:Passed" -ForegroundColor Green
    Write-Host "  Failed: $script:Failed" -ForegroundColor Red
    Write-Host ""

    if ($script:Failed -eq 0) {
        Write-Host "All checks passed! Deployment is healthy." -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Some checks failed. Please review the issues above." -ForegroundColor Red
        exit 1
    }
}

# Main execution
function Main {
    Write-Host ""
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host "  TaskAI - Deployment Verification" -ForegroundColor Cyan
    Write-Host "===========================================================" -ForegroundColor Cyan
    Write-Host ""

    Test-Namespace
    Write-Host ""
    Test-Pods
    Write-Host ""
    Test-Services
    Write-Host ""
    Test-Deployments
    Write-Host ""
    Test-Secrets
    Write-Host ""
    Test-APIHealth
    Write-Host ""
    Show-Summary
}

Main
