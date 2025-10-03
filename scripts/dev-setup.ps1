# =============================================================================
# DEVELOPMENT SETUP SCRIPT (PowerShell)
# =============================================================================
# This script helps set up different development environments for the
# Clash Royale Deck Builder application on Windows.
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("setup", "containerized", "frontend", "backend", "status", "stop", "cleanup", "help")]
    [string]$Command = "help"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$CommandName)
    return (Get-Command $CommandName -ErrorAction SilentlyContinue) -ne $null
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    $missingDeps = @()
    
    if (-not (Test-Command "docker")) {
        $missingDeps += "docker"
    }
    
    if (-not (Test-Command "docker-compose")) {
        $missingDeps += "docker-compose"
    }
    
    if (-not (Test-Command "node")) {
        $missingDeps += "node"
    }
    
    if (-not (Test-Command "npm")) {
        $missingDeps += "npm"
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Error "Missing required dependencies: $($missingDeps -join ', ')"
        Write-Error "Please install the missing dependencies and try again."
        exit 1
    }
    
    Write-Success "All prerequisites are installed"
}

# Function to set up environment files
function Initialize-Environment {
    Write-Status "Setting up environment files..."
    
    # Run the main environment setup script if it exists
    if (Test-Path ".\scripts\setup-env.sh") {
        bash .\scripts\setup-env.sh
    } else {
        Write-Warning "Environment setup script not found, creating basic files..."
        
        # Create basic environment files if they don't exist
        if (-not (Test-Path ".env.local") -and (Test-Path ".env.example")) {
            Copy-Item ".env.example" ".env.local"
            Write-Status "Created .env.local from template"
        }
        
        if (-not (Test-Path ".env.docker") -and (Test-Path ".env.example")) {
            Copy-Item ".env.example" ".env.docker"
            Write-Status "Created .env.docker from template"
        }
    }
    
    # Create frontend environment files
    if (-not (Test-Path "frontend\.env")) {
        $frontendEnv = @"
# Frontend environment configuration
REACT_APP_API_BASE_URL=http://localhost:8000
GENERATE_SOURCEMAP=true
BROWSER=none
PORT=3000
"@
        $frontendEnv | Out-File -FilePath "frontend\.env" -Encoding UTF8
        Write-Status "Created frontend\.env"
    }
    
    Write-Success "Environment files are ready"
}

# Function to install frontend dependencies
function Install-FrontendDependencies {
    Write-Status "Installing frontend dependencies..."
    
    Push-Location frontend
    try {
        if (Test-Path "package-lock.json") {
            npm ci
        } else {
            npm install
        }
    } finally {
        Pop-Location
    }
    
    Write-Success "Frontend dependencies installed"
}

# Function to start full containerized development
function Start-ContainerizedDevelopment {
    Write-Status "Starting containerized development environment..."
    
    # Start backend and database containers
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 10
    
    # Check if services are healthy
    $containerStatus = docker-compose ps
    if ($containerStatus -match "Up.*healthy") {
        Write-Success "Containerized backend and database are running"
        Write-Status "Backend API: http://localhost:8000"
        Write-Status "Database: localhost:3306"
        Write-Status ""
        Write-Status "To start the frontend:"
        Write-Status "  cd frontend && npm start"
        Write-Status ""
        Write-Status "To view logs:"
        Write-Status "  docker-compose logs -f backend"
        Write-Status "  docker-compose logs -f database"
    } else {
        Write-Error "Some services failed to start properly"
        docker-compose ps
        exit 1
    }
}

# Function to start frontend only
function Start-FrontendOnly {
    Write-Status "Starting frontend development server..."
    
    Push-Location frontend
    try {
        Start-Process -FilePath "npm" -ArgumentList "start" -NoNewWindow
    } finally {
        Pop-Location
    }
    
    Write-Success "Frontend starting..."
    Write-Status "Frontend: http://localhost:3000"
    Write-Status "Make sure the backend is running on http://localhost:8000"
}

# Function to start backend only
function Start-BackendOnly {
    Write-Status "Starting backend-only development..."
    
    # Start only database container
    docker-compose up -d database
    
    Write-Status "Database container started"
    Write-Status "To start the backend locally:"
    Write-Status "  cd backend"
    Write-Status "  uv install"
    Write-Status "  Copy-Item ..\.env.local .env"
    Write-Status "  # Edit .env and set DB_HOST=localhost"
    Write-Status "  uv run uvicorn main:app --reload"
}

# Function to show status
function Show-Status {
    Write-Status "Development environment status:"
    Write-Status ""
    
    # Check Docker containers
    $containerStatus = docker-compose ps 2>$null
    if ($containerStatus -match "Up") {
        Write-Status "Docker containers:"
        docker-compose ps
    } else {
        Write-Status "No Docker containers running"
    }
    
    Write-Status ""
    
    # Check if frontend is running
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction Stop
        Write-Success "Frontend is running on http://localhost:3000"
    } catch {
        Write-Status "Frontend is not running"
    }
    
    # Check if backend is running
    try {
        $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        Write-Success "Backend is running on http://localhost:8000"
    } catch {
        Write-Status "Backend is not running"
    }
}

# Function to stop all services
function Stop-AllServices {
    Write-Status "Stopping all development services..."
    
    # Stop Docker containers
    docker-compose down
    
    # Kill any running frontend processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*react-scripts*" } | Stop-Process -Force
    
    Write-Success "All services stopped"
}

# Function to clean up
function Invoke-Cleanup {
    Write-Status "Cleaning up development environment..."
    
    # Stop and remove containers and volumes
    docker-compose down -v
    
    # Remove node_modules (optional)
    $removeNodeModules = Read-Host "Remove frontend node_modules? (y/N)"
    if ($removeNodeModules -eq "y" -or $removeNodeModules -eq "Y") {
        Remove-Item -Path "frontend\node_modules" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Status "Removed frontend\node_modules"
    }
    
    Write-Success "Cleanup completed"
}

# Function to show help
function Show-Help {
    Write-Host "Development Setup Script for Clash Royale Deck Builder" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\dev-setup.ps1 [COMMAND]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor White
    Write-Host "  setup           Set up development environment (run this first)" -ForegroundColor Gray
    Write-Host "  containerized   Start full containerized development (recommended)" -ForegroundColor Gray
    Write-Host "  frontend        Start frontend development server only" -ForegroundColor Gray
    Write-Host "  backend         Start backend-only development (with containerized DB)" -ForegroundColor Gray
    Write-Host "  status          Show current development environment status" -ForegroundColor Gray
    Write-Host "  stop            Stop all development services" -ForegroundColor Gray
    Write-Host "  cleanup         Clean up development environment" -ForegroundColor Gray
    Write-Host "  help            Show this help message" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\scripts\dev-setup.ps1 setup           # Initial setup" -ForegroundColor Gray
    Write-Host "  .\scripts\dev-setup.ps1 containerized   # Start full development environment" -ForegroundColor Gray
    Write-Host "  .\scripts\dev-setup.ps1 frontend        # Start only frontend (backend must be running)" -ForegroundColor Gray
    Write-Host "  .\scripts\dev-setup.ps1 status          # Check what's running" -ForegroundColor Gray
    Write-Host "  .\scripts\dev-setup.ps1 stop            # Stop everything" -ForegroundColor Gray
}

# Main script logic
switch ($Command) {
    "setup" {
        Test-Prerequisites
        Initialize-Environment
        Install-FrontendDependencies
        Write-Success "Development environment setup completed!"
        Write-Status "Run '.\scripts\dev-setup.ps1 containerized' to start the full development environment"
    }
    "containerized" {
        Test-Prerequisites
        Initialize-Environment
        Start-ContainerizedDevelopment
    }
    "frontend" {
        Test-Prerequisites
        Install-FrontendDependencies
        Start-FrontendOnly
    }
    "backend" {
        Test-Prerequisites
        Initialize-Environment
        Start-BackendOnly
    }
    "status" {
        Show-Status
    }
    "stop" {
        Stop-AllServices
    }
    "cleanup" {
        Invoke-Cleanup
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}