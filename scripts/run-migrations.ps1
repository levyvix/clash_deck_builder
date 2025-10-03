# PowerShell script to run database migrations manually
# This can be used for troubleshooting or manual migration execution

param(
    [string]$Command = "migrate",
    [string]$Container = "clash-backend",
    [string]$Environment = "docker",
    [string]$Target = "",
    [switch]$Help
)

if ($Help) {
    Write-Host "Manual Migration Runner" -ForegroundColor Cyan
    Write-Host "=======================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run-migrations.ps1 [OPTIONS] [COMMAND]" -ForegroundColor White
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -Command COMMAND       Migration command (migrate, status, rollback)" -ForegroundColor White
    Write-Host "  -Container NAME        Container name (default: clash-backend)" -ForegroundColor White
    Write-Host "  -Environment ENV       Environment (default: docker)" -ForegroundColor White
    Write-Host "  -Target VERSION        Target version for rollback" -ForegroundColor White
    Write-Host "  -Help                  Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run-migrations.ps1                                    # Run migrations" -ForegroundColor White
    Write-Host "  .\run-migrations.ps1 -Command status                   # Check status" -ForegroundColor White
    Write-Host "  .\run-migrations.ps1 -Command rollback -Target 20241203_120000  # Rollback" -ForegroundColor White
    Write-Host "  .\run-migrations.ps1 -Container my-backend -Command migrate     # Custom container" -ForegroundColor White
    exit 0
}

Write-Host "🔄 Manual Migration Runner" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running or not accessible" -ForegroundColor Red
    exit 1
}

# Check if container exists
$containerExists = docker ps -a --format "table {{.Names}}" | Select-String -Pattern "^$Container$"
if (-not $containerExists) {
    Write-Host "❌ Container '$Container' not found" -ForegroundColor Red
    Write-Host "Available containers:" -ForegroundColor Yellow
    docker ps -a --format "table {{.Names}}`t{{.Status}}"
    exit 1
}

# Check if container is running
$containerRunning = docker ps --format "table {{.Names}}" | Select-String -Pattern "^$Container$"
if (-not $containerRunning) {
    Write-Host "⚠️  Container '$Container' is not running" -ForegroundColor Yellow
    Write-Host "Starting container..." -ForegroundColor White
    
    switch ($Environment) {
        "development" { docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend }
        "dev" { docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d backend }
        "production" { docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d backend }
        "prod" { docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d backend }
        default { docker-compose up -d backend }
    }
    
    Write-Host "⏳ Waiting for container to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

# Execute migration command in container
Write-Host "🚀 Executing migration command: $Command" -ForegroundColor Green

try {
    switch ($Command) {
        "migrate" {
            docker exec -it $Container python /app/database/migrations/container_migrate.py migrate
        }
        "status" {
            docker exec -it $Container python /app/database/migrations/container_migrate.py status
        }
        "rollback" {
            if (-not $Target) {
                Write-Host "❌ Rollback requires a target version" -ForegroundColor Red
                Write-Host "Usage: .\run-migrations.ps1 -Command rollback -Target VERSION" -ForegroundColor White
                exit 1
            }
            
            # Get environment variables for rollback
            $envVars = docker exec $Container printenv | Where-Object { $_ -match "^DB_" }
            $dbUser = ($envVars | Where-Object { $_ -match "^DB_USER=" }) -replace "DB_USER=", ""
            $dbPassword = ($envVars | Where-Object { $_ -match "^DB_PASSWORD=" }) -replace "DB_PASSWORD=", ""
            $dbName = ($envVars | Where-Object { $_ -match "^DB_NAME=" }) -replace "DB_NAME=", ""
            
            docker exec -it $Container python /app/database/migrations/migrate.py rollback --target $Target --host database --port 3306 --user $dbUser --password $dbPassword --database $dbName
        }
        default {
            Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
            Write-Host "Available commands: migrate, status, rollback" -ForegroundColor White
            exit 1
        }
    }
    
    Write-Host "✅ Migration command completed successfully" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Migration command failed: $_" -ForegroundColor Red
    exit 1
}