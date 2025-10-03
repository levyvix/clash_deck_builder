# =============================================================================
# CLASH ROYALE DECK BUILDER - DEPLOYMENT SCRIPT (PowerShell)
# =============================================================================
# This script handles deployment with environment variable validation
# and security best practices for Windows environments.
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("development", "docker", "production")]
    [string]$Environment = "development",
    
    [switch]$ValidateOnly,
    [switch]$Help
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Function to validate required environment variables
function Test-EnvironmentVariables {
    param([string]$EnvFile)
    
    Write-Info "Validating environment variables in $EnvFile..."
    
    if (-not (Test-Path $EnvFile)) {
        Write-Error "Environment file $EnvFile not found!"
        return $false
    }
    
    # Load environment variables from file
    $envVars = @{}
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $envVars[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
    
    # Required variables for all environments
    $requiredVars = @(
        "DB_ROOT_PASSWORD",
        "DB_NAME",
        "DB_USER", 
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "CLASH_ROYALE_API_KEY",
        "DEBUG",
        "LOG_LEVEL",
        "CORS_ORIGINS",
        "ENVIRONMENT",
        "BACKEND_HOST",
        "BACKEND_PORT",
        "JWT_SECRET_KEY"
    )
    
    # Check each required variable
    $missingVars = @()
    foreach ($var in $requiredVars) {
        if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($envVars[$var])) {
            $missingVars += $var
        }
    }
    
    # Report missing variables
    if ($missingVars.Count -gt 0) {
        Write-Error "Missing required environment variables:"
        $missingVars | ForEach-Object { Write-Host "  - $_" }
        return $false
    }
    
    Write-Success "All required environment variables are set"
    
    # Store variables for validation
    $script:envVars = $envVars
    return $true
}

# Function to validate environment variable values
function Test-EnvironmentValues {
    Write-Info "Validating environment variable values..."
    
    # Validate database port
    $dbPort = [int]$script:envVars["DB_PORT"]
    if ($dbPort -lt 1 -or $dbPort -gt 65535) {
        Write-Error "DB_PORT must be a valid port number (1-65535)"
        return $false
    }
    
    # Validate backend port
    $backendPort = [int]$script:envVars["BACKEND_PORT"]
    if ($backendPort -lt 1 -or $backendPort -gt 65535) {
        Write-Error "BACKEND_PORT must be a valid port number (1-65535)"
        return $false
    }
    
    # Validate debug flag
    if ($script:envVars["DEBUG"] -notin @("true", "false")) {
        Write-Error "DEBUG must be either 'true' or 'false'"
        return $false
    }
    
    # Validate log level
    $validLogLevels = @("debug", "info", "warning", "error", "critical")
    if ($script:envVars["LOG_LEVEL"] -notin $validLogLevels) {
        Write-Error "LOG_LEVEL must be one of: $($validLogLevels -join ', ')"
        return $false
    }
    
    # Validate environment type
    $validEnvironments = @("development", "docker", "production")
    if ($script:envVars["ENVIRONMENT"] -notin $validEnvironments) {
        Write-Error "ENVIRONMENT must be one of: $($validEnvironments -join ', ')"
        return $false
    }
    
    # Security checks for production
    if ($script:envVars["ENVIRONMENT"] -eq "production") {
        Write-Info "Performing additional security checks for production..."
        
        # Check for default/weak passwords
        $weakPatterns = @("password", "123", "test", "default", "admin", "root")
        foreach ($pattern in $weakPatterns) {
            if ($script:envVars["DB_ROOT_PASSWORD"] -like "*$pattern*" -or 
                $script:envVars["DB_PASSWORD"] -like "*$pattern*") {
                Write-Error "Production passwords should not contain common patterns like '$pattern'"
                return $false
            }
        }
        
        # Check password length
        if ($script:envVars["DB_ROOT_PASSWORD"].Length -lt 12 -or 
            $script:envVars["DB_PASSWORD"].Length -lt 12) {
            Write-Error "Production passwords should be at least 12 characters long"
            return $false
        }
        
        # Check for test API key
        if ($script:envVars["CLASH_ROYALE_API_KEY"] -like "*test*" -or 
            $script:envVars["CLASH_ROYALE_API_KEY"] -like "*mock*") {
            Write-Error "Production environment requires a real Clash Royale API key"
            return $false
        }
        
        # Check JWT secret strength
        if ($script:envVars["JWT_SECRET_KEY"].Length -lt 32) {
            Write-Error "Production JWT secret should be at least 32 characters long"
            return $false
        }
        
        Write-Success "Production security checks passed"
    }
    
    Write-Success "Environment variable values are valid"
    return $true
}

# Function to check Docker availability
function Test-Docker {
    Write-Info "Checking Docker availability..."
    
    try {
        $null = Get-Command docker -ErrorAction Stop
    } catch {
        Write-Error "Docker is not installed or not in PATH"
        return $false
    }
    
    try {
        $null = docker info 2>$null
    } catch {
        Write-Error "Docker daemon is not running"
        return $false
    }
    
    try {
        $null = Get-Command docker-compose -ErrorAction Stop
    } catch {
        Write-Error "Docker Compose is not installed or not in PATH"
        return $false
    }
    
    Write-Success "Docker and Docker Compose are available"
    return $true
}

# Function to deploy to specific environment
function Start-Deployment {
    param([string]$Environment)
    
    Write-Info "Deploying to $Environment environment..."
    
    # Determine compose files and environment file based on environment
    $composeFiles = ""
    $envFile = ""
    
    switch ($Environment) {
        "development" {
            $composeFiles = "-f docker-compose.yml -f docker-compose.dev.yml"
            $envFile = ".env.local"
        }
        "docker" {
            $composeFiles = "-f docker-compose.yml -f docker-compose.dev.yml"
            $envFile = ".env.docker"
        }
        "production" {
            $composeFiles = "-f docker-compose.yml -f docker-compose.prod.yml"
            $envFile = ".env"
        }
        default {
            Write-Error "Unknown environment: $Environment"
            Write-Error "Valid environments: development, docker, production"
            return $false
        }
    }
    
    # Validate environment variables
    if (-not (Test-EnvironmentVariables $envFile)) {
        return $false
    }
    
    if (-not (Test-EnvironmentValues)) {
        return $false
    }
    
    # Check Docker availability
    if (-not (Test-Docker)) {
        return $false
    }
    
    # Stop existing containers
    Write-Info "Stopping existing containers..."
    try {
        Invoke-Expression "docker-compose $composeFiles down --remove-orphans" 2>$null
    } catch {
        # Ignore errors when stopping non-existent containers
    }
    
    # Pull latest images
    Write-Info "Pulling latest images..."
    Invoke-Expression "docker-compose $composeFiles pull"
    
    # Build and start containers
    Write-Info "Building and starting containers..."
    Invoke-Expression "docker-compose $composeFiles up -d --build"
    
    # Wait for services to be healthy
    Write-Info "Waiting for services to be healthy..."
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        $status = Invoke-Expression "docker-compose $composeFiles ps" | Out-String
        if ($status -match "Up \(healthy\)") {
            Write-Success "Services are healthy!"
            break
        }
        
        if ($attempt -eq $maxAttempts) {
            Write-Error "Services failed to become healthy within timeout"
            Invoke-Expression "docker-compose $composeFiles logs"
            return $false
        }
        
        Write-Info "Attempt $attempt/$maxAttempts - waiting for services..."
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    # Show running services
    Write-Info "Running services:"
    Invoke-Expression "docker-compose $composeFiles ps"
    
    Write-Success "Deployment to $Environment completed successfully!"
    
    # Show access information
    Write-Host ""
    Write-Info "Access Information:"
    Write-Host "  Backend API: http://localhost:8000"
    Write-Host "  API Documentation: http://localhost:8000/docs"
    Write-Host "  Health Check: http://localhost:8000/health"
    Write-Host ""
    Write-Info "Useful Commands:"
    Write-Host "  View logs: docker-compose $composeFiles logs -f"
    Write-Host "  Stop services: docker-compose $composeFiles down"
    Write-Host "  Restart services: docker-compose $composeFiles restart"
    
    return $true
}

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 [ENVIRONMENT] [OPTIONS]"
    Write-Host ""
    Write-Host "ENVIRONMENT:"
    Write-Host "  development  Deploy for local development (uses .env.local)"
    Write-Host "  docker       Deploy for containerized development (uses .env.docker)"
    Write-Host "  production   Deploy for production (uses .env)"
    Write-Host ""
    Write-Host "OPTIONS:"
    Write-Host "  -ValidateOnly  Only validate environment variables, don't deploy"
    Write-Host "  -Help          Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 development           # Deploy for local development"
    Write-Host "  .\deploy.ps1 docker               # Deploy for containerized development"
    Write-Host "  .\deploy.ps1 production           # Deploy for production"
    Write-Host "  .\deploy.ps1 production -ValidateOnly  # Only validate production environment"
}

# Main execution
if ($Help) {
    Show-Usage
    exit 0
}

Write-Info "Starting deployment script for Clash Royale Deck Builder..."
Write-Info "Target environment: $Environment"

if ($ValidateOnly) {
    Write-Info "Validation-only mode enabled"
    
    # Determine environment file
    $envFile = switch ($Environment) {
        "development" { ".env.local" }
        "docker" { ".env.docker" }
        "production" { ".env" }
    }
    
    # Validate environment variables
    if ((Test-EnvironmentVariables $envFile) -and (Test-EnvironmentValues)) {
        Write-Success "Environment validation passed!"
        exit 0
    } else {
        Write-Error "Environment validation failed!"
        exit 1
    }
} else {
    # Full deployment
    if (Start-Deployment $Environment) {
        Write-Success "Deployment completed successfully!"
        exit 0
    } else {
        Write-Error "Deployment failed!"
        exit 1
    }
}