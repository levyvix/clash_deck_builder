# Test environment setup script for Windows PowerShell
# This script sets up the test database containers and runs tests

param(
    [switch]$SkipTests = $false,
    [switch]$Cleanup = $false
)

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker and try again."
        return $false
    }
}

# Function to wait for service to be healthy
function Wait-ForService {
    param(
        [string]$ServiceName,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "Waiting for $ServiceName to be healthy..." -ForegroundColor Yellow
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        $status = docker-compose -f docker-compose.test.yml ps $ServiceName
        if ($status -match "healthy") {
            Write-Host "$ServiceName is healthy!" -ForegroundColor Green
            return $true
        }
        
        Write-Host "Attempt $attempt/$MaxAttempts`: $ServiceName not ready yet..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
    
    Write-Error "$ServiceName failed to become healthy after $MaxAttempts attempts"
    return $false
}

# Function to cleanup test environment
function Invoke-Cleanup {
    Write-Host "Cleaning up test environment..." -ForegroundColor Yellow
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
}

try {
    Write-Host "Setting up test environment..." -ForegroundColor Cyan
    
    # Check Docker
    if (-not (Test-Docker)) {
        exit 1
    }
    
    # Cleanup if requested
    if ($Cleanup) {
        Invoke-Cleanup
        Write-Host "Cleanup completed!" -ForegroundColor Green
        exit 0
    }
    
    # Stop any existing test containers
    Write-Host "Stopping existing test containers..." -ForegroundColor Yellow
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
    
    # Start test database
    Write-Host "Starting test database..." -ForegroundColor Yellow
    docker-compose -f docker-compose.test.yml up -d test-database
    
    # Wait for database to be healthy
    if (-not (Wait-ForService "test-database")) {
        exit 1
    }
    
    if (-not $SkipTests) {
        # Run database tests
        Write-Host "Running database integration tests..." -ForegroundColor Cyan
        Set-Location backend
        
        # Install dependencies if needed
        if (-not (Test-Path ".venv")) {
            Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
            uv sync
        }
        
        # Run tests with test environment
        Write-Host "Running tests..." -ForegroundColor Yellow
        uv run pytest tests/integration/ -v --tb=short
        
        Set-Location ..
    }
    
    Write-Host "Test setup completed successfully!" -ForegroundColor Green
}
catch {
    Write-Error "An error occurred: $_"
    exit 1
}
finally {
    # Cleanup on exit unless explicitly skipped
    if (-not $SkipTests) {
        Invoke-Cleanup
    }
}