# Database Backup Script for Clash Royale Deck Builder (PowerShell)
# Creates timestamped MySQL database dumps with compression

param(
    [string]$Database = "clash_deck_builder_docker",
    [string]$Container = "clash-db",
    [string]$OutputDir = "",
    [int]$RetentionDays = 30,
    [switch]$NoCompress,
    [switch]$Help
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DefaultBackupDir = Join-Path $ProjectRoot "database\backups"
$BackupDir = if ($OutputDir) { $OutputDir } else { $DefaultBackupDir }
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\backup-database.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Database NAME         Database name (default: clash_deck_builder_docker)"
    Write-Host "  -Container NAME        Container name (default: clash-db)"
    Write-Host "  -OutputDir DIR         Output directory (default: database\backups)"
    Write-Host "  -RetentionDays DAYS    Backup retention in days (default: 30)"
    Write-Host "  -NoCompress           Don't compress the backup file"
    Write-Host "  -Help                 Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\backup-database.ps1                                    # Basic backup with defaults"
    Write-Host "  .\backup-database.ps1 -Database my_database -RetentionDays 7  # Custom database, 7-day retention"
    Write-Host "  .\backup-database.ps1 -NoCompress                       # Backup without compression"
}

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# Check if Docker container is running
try {
    $runningContainers = docker ps --format "{{.Names}}"
    if ($runningContainers -notcontains $Container) {
        Write-Error "Database container '$Container' is not running"
        Write-Status "Available containers:"
        docker ps --format "table {{.Names}}`t{{.Status}}"
        exit 1
    }
} catch {
    Write-Error "Failed to check Docker containers. Is Docker running?"
    exit 1
}

# Generate backup filename
$BackupFileName = "${Database}_backup_${Timestamp}.sql"
if (-not $NoCompress) {
    $BackupFile = Join-Path $BackupDir "${BackupFileName}.gz"
    $TempFile = Join-Path $BackupDir $BackupFileName
} else {
    $BackupFile = Join-Path $BackupDir $BackupFileName
}

Write-Status "Starting database backup..."
Write-Status "Database: $Database"
Write-Status "Container: $Container"
Write-Status "Output: $BackupFile"

# Create database dump
Write-Status "Creating database dump..."
try {
    $dumpArgs = @(
        "exec", $Container, "mysqldump",
        "--single-transaction",
        "--routines",
        "--triggers", 
        "--events",
        "--add-drop-database",
        "--databases", $Database
    )
    
    if (-not $NoCompress) {
        docker @dumpArgs | Out-File -FilePath $TempFile -Encoding UTF8
    } else {
        docker @dumpArgs | Out-File -FilePath $BackupFile -Encoding UTF8
    }
    
    # Compress if requested
    if (-not $NoCompress) {
        Write-Status "Compressing backup..."
        
        # Use 7-Zip if available, otherwise use PowerShell compression
        if (Get-Command "7z" -ErrorAction SilentlyContinue) {
            & 7z a -tgzip "$BackupFile" "$TempFile" | Out-Null
            Remove-Item $TempFile -Force
        } elseif (Get-Command "Compress-Archive" -ErrorAction SilentlyContinue) {
            Compress-Archive -Path $TempFile -DestinationPath ($BackupFile -replace '\.gz$', '.zip') -Force
            Remove-Item $TempFile -Force
            $BackupFile = $BackupFile -replace '\.gz$', '.zip'
        } else {
            Write-Warning "No compression utility found. Keeping uncompressed backup."
            Move-Item $TempFile $BackupFile -Force
        }
    }
    
    # Get backup file size
    if (Test-Path $BackupFile) {
        $BackupSize = [math]::Round((Get-Item $BackupFile).Length / 1MB, 2)
        Write-Status "Backup completed successfully"
        Write-Status "Backup size: ${BackupSize} MB"
        Write-Status "Backup location: $BackupFile"
    } else {
        Write-Error "Backup file not found after creation"
        exit 1
    }
} catch {
    Write-Error "Failed to create database dump: $($_.Exception.Message)"
    # Clean up temp file if it exists
    if (Test-Path $TempFile) {
        Remove-Item $TempFile -Force
    }
    exit 1
}

# Clean up old backups based on retention policy
if ($RetentionDays -gt 0) {
    Write-Status "Cleaning up backups older than $RetentionDays days..."
    
    $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $OldBackups = Get-ChildItem -Path $BackupDir -Name "${Database}_backup_*.sql*" | 
                  Where-Object { (Get-Item (Join-Path $BackupDir $_)).LastWriteTime -lt $CutoffDate }
    
    if ($OldBackups) {
        foreach ($OldBackup in $OldBackups) {
            $OldBackupPath = Join-Path $BackupDir $OldBackup
            Write-Status "Removing old backup: $OldBackup"
            Remove-Item $OldBackupPath -Force
        }
    } else {
        Write-Status "No old backups found to clean up"
    }
}

# Verify backup integrity
Write-Status "Verifying backup integrity..."
if (Test-Path $BackupFile) {
    $FileSize = (Get-Item $BackupFile).Length
    if ($FileSize -gt 0) {
        Write-Status "Backup file integrity verified"
    } else {
        Write-Error "Backup file is empty"
        exit 1
    }
} else {
    Write-Error "Backup file not found"
    exit 1
}

Write-Status "Database backup completed successfully!"
Write-Status "Backup file: $BackupFile"

# List recent backups
Write-Status "Recent backups in ${BackupDir}:"
Get-ChildItem -Path $BackupDir -Name "${Database}_backup_*.sql*" | 
    Sort-Object | 
    Select-Object -Last 5 |
    ForEach-Object {
        $FilePath = Join-Path $BackupDir $_
        $FileInfo = Get-Item $FilePath
        $Size = [math]::Round($FileInfo.Length / 1MB, 2)
        Write-Host "  $_ (${Size} MB, $($FileInfo.LastWriteTime))"
    }

exit 0