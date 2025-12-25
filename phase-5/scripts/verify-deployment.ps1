# [Task]: T111
# [Spec]: F-009 (US11)
# [Description]: PowerShell script to verify TaskAI Minikube deployment
# ==============================================
# TaskAI - Deployment Verification Script (PowerShell)
# ==============================================
# This script verifies that the TaskAI application is properly deployed
# and all components are functioning correctly.
#
# Usage:
#   .\scripts\verify-deployment.ps1 [-Detailed]

param(
    [switch]$Detailed
)

$ErrorActionPreference = "Continue"

$Namespace = "todo-app"
$script:Passed = 0
$script:Failed = 0

# Helper functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Pass { param($Message) Write-Host "[PASS] $Message" -ForegroundColor Green; $script:Passed++ }
function Write-Warning { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Fail { param($Message) Write-Host "[FAIL] $Message" -ForegroundColor Red; $script:Failed++ }

# Check Minikube status
function Test-Minikube {
    Write-Info "Checking Minikube..."
    $minikubeStatus = minikube status --format='{{.Host}}' 2>&1
    if ($minikubeStatus -eq "Running") {
        Write-Pass "Minikube is running"
    } else {
        Write-Fail "Minikube is not running"
    }
}

# Check if namespaces exist
function Test-Namespaces {
    Write-Info "Checking namespaces..."
    $namespaces = @($Namespace, "kafka", "dapr-system")
    foreach ($ns in $namespaces) {
        $result = kubectl get namespace $ns --ignore-not-found -o name 2>&1
        if ($result) {
            Write-Pass "Namespace '$ns' exists"
        } else {
            Write-Fail "Namespace '$ns' does not exist"
        }
    }
}

# Check pods status
function Test-Pods {
    Write-Info "Checking pods in $Namespace namespace..."

    $expectedPods = @("backend", "frontend", "notification-service", "recurring-service")
    $pods = kubectl get pods -n $Namespace -o json 2>&1 | ConvertFrom-Json

    foreach ($expectedPod in $expectedPods) {
        $pod = $pods.items | Where-Object { $_.metadata.name -like "*$expectedPod*" } | Select-Object -First 1
        if ($pod) {
            $phase = $pod.status.phase
            $readyCount = ($pod.status.containerStatuses | Where-Object { $_.ready }).Count
            $totalCount = $pod.status.containerStatuses.Count

            if ($phase -eq "Running" -and $readyCount -eq $totalCount) {
                Write-Pass "Pod '$expectedPod' is running ($readyCount/$totalCount containers ready)"
            } else {
                Write-Fail "Pod '$expectedPod' - Status: $phase ($readyCount/$totalCount ready)"
            }

            if ($Detailed) {
                Write-Host "    Full name: $($pod.metadata.name)" -ForegroundColor Gray
                Write-Host "    Node: $($pod.spec.nodeName)" -ForegroundColor Gray
                Write-Host "    Started: $($pod.status.startTime)" -ForegroundColor Gray
            }
        } else {
            Write-Fail "Pod '$expectedPod' not found"
        }
    }
}

# Check services
function Test-Services {
    Write-Info "Checking services..."

    $services = kubectl get services -n $Namespace -o json 2>&1 | ConvertFrom-Json

    foreach ($svc in $services.items) {
        $name = $svc.metadata.name
        $type = $svc.spec.type
        $ports = ($svc.spec.ports | ForEach-Object {
            if ($_.nodePort) { "$($_.port):$($_.nodePort)" } else { "$($_.port)" }
        }) -join ", "
        Write-Pass "Service '$name' exists (Type: $type, Ports: $ports)"
    }
}

# Check Kafka
function Test-Kafka {
    Write-Info "Checking Kafka cluster..."

    $kafkaCluster = kubectl get kafka kafka-cluster -n kafka -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>&1
    if ($kafkaCluster -eq "True") {
        Write-Pass "Kafka cluster is ready"
    } else {
        Write-Warning "Kafka cluster status: $kafkaCluster"
    }

    # Check Kafka topics
    $topics = @("task-events", "reminders")
    foreach ($topic in $topics) {
        $topicExists = kubectl get kafkatopic $topic -n kafka --ignore-not-found -o name 2>&1
        if ($topicExists) {
            Write-Pass "Kafka topic '$topic' exists"
        } else {
            Write-Warning "Kafka topic '$topic' not found"
        }
    }
}

# Check Dapr
function Test-Dapr {
    Write-Info "Checking Dapr..."

    $daprStatus = dapr status -k 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Pass "Dapr runtime is installed"

        # Check Dapr components
        $components = kubectl get components -n $Namespace -o json 2>&1 | ConvertFrom-Json
        foreach ($comp in $components.items) {
            Write-Pass "Dapr component '$($comp.metadata.name)' ($($comp.spec.type))"
        }
    } else {
        Write-Fail "Dapr runtime is not installed"
    }
}

# Check secrets (optional)
function Test-Secrets {
    Write-Info "Checking secrets..."

    $secrets = kubectl get secrets -n $Namespace -o json 2>&1 | ConvertFrom-Json
    $appSecrets = $secrets.items | Where-Object { $_.metadata.name -like "*todo-chatbot*" -or $_.metadata.name -like "*backend*" }

    if ($appSecrets.Count -gt 0) {
        foreach ($secret in $appSecrets) {
            Write-Pass "Secret '$($secret.metadata.name)' exists"
        }
    } else {
        Write-Warning "No application secrets found (may be using ConfigMaps instead)"
    }
}

# Check API health
function Test-APIHealth {
    Write-Info "Checking health endpoints..."

    $minikubeIp = minikube ip

    # Backend health
    try {
        $backendHealth = Invoke-RestMethod -Uri "http://${minikubeIp}:30080/health" -TimeoutSec 5
        Write-Pass "Backend /health endpoint OK"
    } catch {
        Write-Fail "Backend /health endpoint failed: $($_.Exception.Message)"
    }

    # Backend ready
    try {
        $backendReady = Invoke-RestMethod -Uri "http://${minikubeIp}:30080/ready" -TimeoutSec 5
        Write-Pass "Backend /ready endpoint OK"
    } catch {
        Write-Warning "Backend /ready endpoint failed: $($_.Exception.Message)"
    }

    # Frontend
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://${minikubeIp}:30000" -TimeoutSec 5 -UseBasicParsing
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Pass "Frontend is accessible"
        } else {
            Write-Fail "Frontend returned status $($frontendResponse.StatusCode)"
        }
    } catch {
        Write-Fail "Frontend not accessible: $($_.Exception.Message)"
    }
}

# Display summary
function Show-Summary {
    $minikubeIp = minikube ip

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
        Write-Host ""
        Write-Host "Application URLs:" -ForegroundColor Yellow
        Write-Host "  Frontend:     http://${minikubeIp}:30000" -ForegroundColor White
        Write-Host "  Backend API:  http://${minikubeIp}:30080" -ForegroundColor White
        Write-Host "  API Docs:     http://${minikubeIp}:30080/docs" -ForegroundColor White
        Write-Host ""
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

    Test-Minikube
    Write-Host ""
    Test-Namespaces
    Write-Host ""
    Test-Pods
    Write-Host ""
    Test-Services
    Write-Host ""
    Test-Kafka
    Write-Host ""
    Test-Dapr
    Write-Host ""
    Test-Secrets
    Write-Host ""
    Test-APIHealth
    Write-Host ""
    Show-Summary
}

Main
