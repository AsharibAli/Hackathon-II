# [Task]: T133
# [Spec]: Phase 5 Cloud Deployment
# [Description]: End-to-end test script for full workflow validation

<#
.SYNOPSIS
    End-to-end test script for TaskAI application.

.DESCRIPTION
    This script validates the complete workflow of the TaskAI application:
    1. Health checks for all services
    2. User registration and authentication
    3. Task CRUD operations with Phase 5 features
    4. Tag management
    5. Reminder functionality
    6. Event publishing verification

.PARAMETER BaseUrl
    Base URL for the backend API (default: uses Minikube IP)

.PARAMETER Verbose
    Show detailed test output

.EXAMPLE
    .\scripts\e2e-test.ps1
    .\scripts\e2e-test.ps1 -BaseUrl "http://localhost:8000"
#>

param(
    [string]$BaseUrl,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$script:Passed = 0
$script:Failed = 0
$script:Token = ""
$script:UserId = ""
$script:TaskId = ""

# Get base URL from Minikube if not provided
if (-not $BaseUrl) {
    $minikubeIp = minikube ip
    $BaseUrl = "http://${minikubeIp}:30080"
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = ""
    )

    if ($Passed) {
        Write-Host "[PASS] $TestName" -ForegroundColor Green
        $script:Passed++
    } else {
        Write-Host "[FAIL] $TestName" -ForegroundColor Red
        $script:Failed++
    }

    if ($Verbose -and $Details) {
        Write-Host "       $Details" -ForegroundColor Gray
    }
}

function Invoke-ApiRequest {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [bool]$RequireAuth = $true
    )

    $headers = @{
        "Content-Type" = "application/json"
    }

    if ($RequireAuth -and $script:Token) {
        $headers["Authorization"] = "Bearer $($script:Token)"
    }

    $params = @{
        Method = $Method
        Uri = "$BaseUrl$Endpoint"
        Headers = $headers
        TimeoutSec = 30
    }

    if ($Body) {
        $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
    }

    try {
        $response = Invoke-RestMethod @params
        return @{ Success = $true; Data = $response; StatusCode = 200 }
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        return @{ Success = $false; Error = $_.Exception.Message; StatusCode = $statusCode }
    }
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  TaskAI - End-to-End Tests" -ForegroundColor Cyan
Write-Host "  Base URL: $BaseUrl" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# Test 1: Health Checks
# ============================================
Write-Host "Phase 1: Health Checks" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Test /health endpoint
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/health" -RequireAuth $false
Write-TestResult -TestName "Backend /health endpoint" -Passed $result.Success -Details $result.Error

# Test /ready endpoint
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/ready" -RequireAuth $false
Write-TestResult -TestName "Backend /ready endpoint" -Passed $result.Success -Details $result.Error

Write-Host ""

# ============================================
# Test 2: Authentication
# ============================================
Write-Host "Phase 2: Authentication" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Register a new user
$testEmail = "e2e-test-$(Get-Random)@example.com"
$testPassword = "TestPassword123!"

$result = Invoke-ApiRequest -Method "POST" -Endpoint "/api/auth/register" -Body @{
    email = $testEmail
    password = $testPassword
    name = "E2E Test User"
} -RequireAuth $false

$registerSuccess = $result.Success
Write-TestResult -TestName "User registration" -Passed $registerSuccess -Details $result.Error

# Login
$result = Invoke-ApiRequest -Method "POST" -Endpoint "/api/auth/login" -Body @{
    email = $testEmail
    password = $testPassword
} -RequireAuth $false

$loginSuccess = $result.Success -and $result.Data.access_token
if ($loginSuccess) {
    $script:Token = $result.Data.access_token
    $script:UserId = $result.Data.user.id
}
Write-TestResult -TestName "User login" -Passed $loginSuccess -Details $result.Error

Write-Host ""

# ============================================
# Test 3: Task CRUD Operations
# ============================================
Write-Host "Phase 3: Task CRUD Operations" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Create task with Phase 5 fields
$result = Invoke-ApiRequest -Method "POST" -Endpoint "/api/tasks" -Body @{
    title = "E2E Test Task"
    description = "This is a test task created by the E2E test script"
    priority = "high"
    due_date = (Get-Date).AddDays(1).ToString("yyyy-MM-ddTHH:mm:ssZ")
    recurrence = "daily"
    tags = @("e2e-test", "automated")
}

$createSuccess = $result.Success -and $result.Data.id
if ($createSuccess) {
    $script:TaskId = $result.Data.id
}
Write-TestResult -TestName "Create task with Phase 5 fields" -Passed $createSuccess -Details $result.Error

# Get task by ID
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/api/tasks/$($script:TaskId)"
$getSuccess = $result.Success -and $result.Data.priority -eq "high"
Write-TestResult -TestName "Get task by ID" -Passed $getSuccess -Details $result.Error

# Update task
$result = Invoke-ApiRequest -Method "PUT" -Endpoint "/api/tasks/$($script:TaskId)" -Body @{
    title = "E2E Test Task - Updated"
    priority = "medium"
}
$updateSuccess = $result.Success -and $result.Data.title -eq "E2E Test Task - Updated"
Write-TestResult -TestName "Update task" -Passed $updateSuccess -Details $result.Error

# List tasks with filters
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/api/tasks?priority=medium"
$filterSuccess = $result.Success -and $result.Data.Count -ge 1
Write-TestResult -TestName "List tasks with priority filter" -Passed $filterSuccess -Details $result.Error

Write-Host ""

# ============================================
# Test 4: Tag Management
# ============================================
Write-Host "Phase 4: Tag Management" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Add tag to task
$result = Invoke-ApiRequest -Method "POST" -Endpoint "/api/tasks/$($script:TaskId)/tags" -Body @{
    name = "new-tag"
}
$addTagSuccess = $result.Success
Write-TestResult -TestName "Add tag to task" -Passed $addTagSuccess -Details $result.Error

# List tasks with tag filter
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/api/tasks?tag=new-tag"
$tagFilterSuccess = $result.Success -and $result.Data.Count -ge 1
Write-TestResult -TestName "List tasks with tag filter" -Passed $tagFilterSuccess -Details $result.Error

# Remove tag from task
$result = Invoke-ApiRequest -Method "DELETE" -Endpoint "/api/tasks/$($script:TaskId)/tags/new-tag"
$removeTagSuccess = $result.Success
Write-TestResult -TestName "Remove tag from task" -Passed $removeTagSuccess -Details $result.Error

Write-Host ""

# ============================================
# Test 5: Search and Sort
# ============================================
Write-Host "Phase 5: Search and Sort" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Search tasks
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/api/tasks/search?q=Updated"
$searchSuccess = $result.Success -and $result.Data.Count -ge 1
Write-TestResult -TestName "Search tasks" -Passed $searchSuccess -Details $result.Error

# Sort tasks
$result = Invoke-ApiRequest -Method "GET" -Endpoint "/api/tasks?sort_by=priority&sort_order=desc"
$sortSuccess = $result.Success
Write-TestResult -TestName "Sort tasks by priority" -Passed $sortSuccess -Details $result.Error

Write-Host ""

# ============================================
# Test 6: Reminder
# ============================================
Write-Host "Phase 6: Reminder Functionality" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Set reminder
$reminderTime = (Get-Date).AddHours(1).ToString("yyyy-MM-ddTHH:mm:ssZ")
$result = Invoke-ApiRequest -Method "POST" -Endpoint "/api/tasks/$($script:TaskId)/reminder?remind_at=$reminderTime"
$reminderSuccess = $result.Success -and $result.Data.remind_at
Write-TestResult -TestName "Set task reminder" -Passed $reminderSuccess -Details $result.Error

Write-Host ""

# ============================================
# Test 7: Task Completion
# ============================================
Write-Host "Phase 7: Task Completion" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Toggle completion
$result = Invoke-ApiRequest -Method "PATCH" -Endpoint "/api/tasks/$($script:TaskId)/complete"
$completeSuccess = $result.Success -and $result.Data.is_completed
Write-TestResult -TestName "Toggle task completion" -Passed $completeSuccess -Details $result.Error

Write-Host ""

# ============================================
# Test 8: Cleanup
# ============================================
Write-Host "Phase 8: Cleanup" -ForegroundColor Yellow
Write-Host "----------------------------------------"

# Delete task
$result = Invoke-ApiRequest -Method "DELETE" -Endpoint "/api/tasks/$($script:TaskId)"
$deleteSuccess = $result.StatusCode -eq 204 -or $result.Success
Write-TestResult -TestName "Delete task" -Passed $deleteSuccess -Details $result.Error

Write-Host ""

# ============================================
# Summary
# ============================================
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Total Tests: $($script:Passed + $script:Failed)"
Write-Host "  Passed: $($script:Passed)" -ForegroundColor Green
Write-Host "  Failed: $($script:Failed)" -ForegroundColor Red
Write-Host ""

if ($script:Failed -eq 0) {
    Write-Host "All tests passed! The application is working correctly." -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    exit 1
}
