# Database Restore Script for Clash Royale Deck Builder (PowerShell)
# Restores MySQL database from backup files with validation and rollback capabilities

param(
    [string]$BackupFile = "",
    [string]$Database = "clash_deck_builder_docker",
    [string]$Container = "clash-db",
    [string]$BackupDir = "",
    [switch]$Force,
    [switch]$NoRollback,
    [switch]$NoValidate,
    [switch]$List,
    [switch]$Help
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$DefaultBackupDir = Join-Path $ProjectRoot "database\backups"
$BackupDirectory = if ($BackupDir) { $BackupDir } else { $DefaultBackupDir }

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\restore-database.ps1 [OPTIONS] -BackupFile BACKUP_FILE"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -BackupFile FILE       Path to backup file (.sql or .sql.gz/.zip)"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Database NAME         Database name (default: clash_deck_builder_docker)"
    Write-Host "  -Container NAME        Container name (default: clash-db)"
    Write-Host "  -BackupDir DIR         Backup directory (default: database\backups)"
    Write-Host "  -Force                Skip confirmation prompts"
    Write-Host "  -NoRollback           Don't create rollback backup before restore"
    Write-Host "  -NoValidate           Skip backup file validation"
    Write-Host "  -List                 List available backup files"
    Write-Host "  -Help                 Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\restore-database.ps1 -BackupFile 'database\backups\clash_deck_builder_backup_20241203_120000.sql.gz'"
    Write-Host "  .\restore-database.ps1 -BackupFile 'backup.sql' -Force -NoRollback    # Force restore without rollback"
    Write-Host "  .\restore-database.ps1 -List                                          # List available backups"
    Write-Host "  .\restore-database.ps1 -BackupFile 'backup.sql' -Database 'my_db'     # Restore to different database"
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

function Write-Prompt {
    param([string]$Message)
    Write-Host "[PROMPT] $Message" -ForegroundColor Blue
}

# Function to list available backups
function Get-AvailableBackups {
    Write-Status "Available backup files in ${BackupDirectory}:"
    
    if (!(Test-Path $BackupDirectory)) {
        Write-Warning "Backup directory does not exist: $BackupDirectory"
        return $false
    }
    
    $BackupFiles = Get-ChildItem -Path $BackupDirectory -Include "*.sql", "*.sql.gz", "*.sql.zip" -File | Sort-Object LastWriteTime -Descending
    
    if ($BackupFiles.Count -eq 0) {
        Write-Warning "No backup files found in $BackupDirectory"
        return $false
    }
    
    foreach ($BackupFile in $BackupFiles) {
        $Size = [math]::Round($BackupFile.Length / 1MB, 2)
        $Date = $BackupFile.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
        Write-Host "  $($BackupFile.Name) (${Size} MB, $Date)"
    }
    
    return $true
}

# Function to validate backup file
function Test-BackupFile {
    param([string]$FilePath)
    
    Write-Status "Validating backup file: $(Split-Path -Leaf $FilePath)"
    
    # Check if file exists
    if (!(Test-Path $FilePath)) {
        Write-Error "Backup file does not exist: $FilePath"
        return $false
    }
    
    # Check file size
    $FileInfo = Get-Item $FilePath
    if ($FileInfo.Length -eq 0) {
        Write-Error "Backup file is empty: $FilePath"
        return $false
    }
    
    # Validate compressed files
    if ($FilePath -match '\.(gz|zip)$') {
        # For .gz files, try to test with 7-Zip if available
        if ($FilePath -match '\.gz$' -and (Get-Command "7z" -ErrorAction SilentlyContinue)) {
            try {
                $TestResult = & 7z t "$FilePath" 2>&1
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "Backup file is corrupted (7z test failed): $FilePath"
                    return $false
                }
            } catch {
                Write-Warning "Could not validate compressed file integrity"
            }
        }
        
        # For .zip files, use PowerShell's built-in validation
        if ($FilePath -match '\.zip$') {
            try {
                Add-Type -AssemblyName System.IO.Compression.FileSystem
                $Archive = [System.IO.Compression.ZipFile]::OpenRead($FilePath)
                $Archive.Dispose()
            } catch {
                Write-Error "Backup file is corrupted (zip test failed): $FilePath"
                return $false
            }
        }
    } else {
        # Validate uncompressed SQL files
        try {
            $FirstLines = Get-Content $FilePath -TotalCount 10 -ErrorAction Stop
            $SqlKeywords = $FirstLines | Where-Object { $_ -match "(CREATE|INSERT|DROP|USE)" }
            if ($SqlKeywords.Count -eq 0) {
                Write-Error "Backup file does not appear to contain valid SQL: $FilePath"
                return $false
            }
        } catch {
            Write-Error "Could not read backup file: $FilePath"
            return $false
        }
    }
    
    Write-Status "Backup file validation passed"
    return $true
}

# Function to create rollback backup
function New-RollbackBackup {
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $RollbackFile = Join-Path $BackupDirectory "${Database}_rollback_${Timestamp}.sql"
    
    Write-Status "Creating rollback backup: $(Split-Path -Leaf $RollbackFile)"
    
    # Create backup directory if it doesn't exist
    if (!(Test-Path $BackupDirectory)) {
        New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null
    }
    
    try {
        # Create rollback backup
        $DumpArgs = @(
            "exec", $Container, "mysqldump",
            "--single-transaction",
            "--routines",
            "--triggers",
            "--events", 
            "--add-drop-database",
            "--databases", $Database
        )
        
        docker @DumpArgs | Out-File -FilePath $RollbackFile -Encoding UTF8
        
        if (Test-Path $RollbackFile -and (Get-Item $RollbackFile).Length -gt 0) {
            Write-Status "Rollback backup created: $(Split-Path -Leaf $RollbackFile)"
            return $RollbackFile
        } else {
            Write-Error "Failed to create rollback backup"
            return $null
        }
    } catch {
        Write-Error "Failed to create rollback backup: $($_.Exception.Message)"
        return $null
    }
}

# Function to restore database
function Restore-Database {
    param([string]$BackupFilePath)
    
    Write-Status "Starting database restore..."
    Write-Status "Source: $(Split-Path -Leaf $BackupFilePath)"
    Write-Status "Target database: $Database"
    Write-Status "Container: $Container"
    
    try {
        # Prepare restore command based on file type
        if ($BackupFilePath -match '\.gz$') {
            Write-Status "Decompressing and restoring from compressed backup..."
            
            if (Get-Command "7z" -ErrorAction SilentlyContinue) {
                # Use 7-Zip to decompress and pipe to docker
                & 7z x "$BackupFilePath" -so | docker exec -i $Container mysql
            } else {
                Write-Error "7-Zip not found. Cannot decompress .gz files."
                return $false
            }
        } elseif ($BackupFilePath -match '\.zip$') {
            Write-Status "Extracting and restoring from zip backup..."
            
            # Extract zip file temporarily
            $TempDir = Join-Path $env:TEMP "restore_temp_$(Get-Date -Format 'yyyyMMddHHmmss')"
            Expand-Archive -Path $BackupFilePath -DestinationPath $TempDir -Force
            
            # Find SQL file in extracted content
            $SqlFile = Get-ChildItem -Path $TempDir -Filter "*.sql" | Select-Object -First 1
            if ($SqlFile) {
                Get-Content $SqlFile.FullName | docker exec -i $Container mysql
                Remove-Item $TempDir -Recurse -Force
            } else {
                Write-Error "No SQL file found in zip archive"
                Remove-Item $TempDir -Recurse -Force
                return $false
            }
        } else {
            Write-Status "Restoring from uncompressed backup..."
            Get-Content $BackupFilePath | docker exec -i $Container mysql
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Database restore completed successfully"
            return $true
        } else {
            Write-Error "Database restore failed"
            return $false
        }
    } catch {
        Write-Error "Database restore failed: $($_.Exception.Message)"
        return $false
    }
}

# Function to verify restore
function Test-RestoreResult {
    Write-Status "Verifying database restore..."
    
    try {
        # Check if database exists and has tables
        $TablesResult = docker exec $Container mysql -e "USE $Database; SHOW TABLES;" 2>$null
        $Tables = $TablesResult -split "`n" | Where-Object { $_ -and $_ -notmatch "^Tables_in_" }
        
        if ($Tables.Count -gt 0) {
            Write-Status "Database restore verification passed ($($Tables.Count) tables found)"
            
            # Show table summary
            Write-Status "Restored tables:"
            foreach ($Table in $Tables) {
                try {
                    $RowCountResult = docker exec $Container mysql -e "USE $Database; SELECT COUNT(*) FROM $Table;" 2>$null
                    $RowCount = ($RowCountResult -split "`n" | Where-Object { $_ -match '^\d+$' })[0]
                    Write-Host "  - $Table ($RowCount rows)"
                } catch {
                    Write-Host "  - $Table (count unavailable)"
                }
            }
            
            return $true
        } else {
            Write-Error "Database restore verification failed (no tables found)"
            return $false
        }
    } catch {
        Write-Error "Database restore verification failed: $($_.Exception.Message)"
        return $false
    }
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# List backups if requested
if ($List) {
    Get-AvailableBackups
    exit 0
}

# Check if backup file was provided
if (-not $BackupFile) {
    Write-Error "No backup file specified"
    Write-Host ""
    Get-AvailableBackups | Out-Null
    Write-Host ""
    Show-Usage
    exit 1
}

# Convert relative path to absolute if needed
if (-not [System.IO.Path]::IsPathRooted($BackupFile)) {
    if ($BackupFile -match '[/\\]') {
        $BackupFile = Join-Path $ProjectRoot $BackupFile
    } else {
        $BackupFile = Join-Path $BackupDirectory $BackupFile
    }
}

# Check if Docker container is running
try {
    $RunningContainers = docker ps --format "{{.Names}}"
    if ($RunningContainers -notcontains $Container) {
        Write-Error "Database container '$Container' is not running"
        Write-Status "Available containers:"
        docker ps --format "table {{.Names}}`t{{.Status}}"
        exit 1
    }
} catch {
    Write-Error "Failed to check Docker containers. Is Docker running?"
    exit 1
}

# Validate backup file if requested
if (-not $NoValidate) {
    if (-not (Test-BackupFile $BackupFile)) {
        exit 1
    }
}

# Show restore summary and get confirmation
Write-Host ""
Write-Status "=== RESTORE SUMMARY ==="
Write-Status "Backup file: $(Split-Path -Leaf $BackupFile)"
Write-Status "File size: $([math]::Round((Get-Item $BackupFile).Length / 1MB, 2)) MB"
Write-Status "Target database: $Database"
Write-Status "Container: $Container"
Write-Status "Create rollback: $(-not $NoRollback)"
Write-Host ""

if (-not $Force) {
    Write-Warning "This operation will REPLACE all data in the '$Database' database!"
    $Confirmation = Read-Host "Are you sure you want to continue? (yes/no)"
    
    if ($Confirmation -notin @("yes", "y")) {
        Write-Status "Restore operation cancelled"
        exit 0
    }
}

# Create rollback backup if requested
$RollbackFile = $null
if (-not $NoRollback) {
    $RollbackFile = New-RollbackBackup
    if ($RollbackFile) {
        Write-Status "Rollback backup available at: $(Split-Path -Leaf $RollbackFile)"
    } else {
        if (-not $Force) {
            Write-Error "Failed to create rollback backup. Aborting restore."
            exit 1
        } else {
            Write-Warning "Failed to create rollback backup, but continuing due to -Force flag"
        }
    }
}

# Perform the restore
if (Restore-Database $BackupFile) {
    # Verify the restore
    if (Test-RestoreResult) {
        Write-Status "Database restore completed successfully!"
        
        if ($RollbackFile) {
            Write-Status "Rollback backup available at: $(Split-Path -Leaf $RollbackFile)"
            Write-Status "To rollback this restore, run:"
            Write-Status "  .\restore-database.ps1 -BackupFile '$RollbackFile'"
        }
    } else {
        Write-Error "Database restore verification failed"
        
        if ($RollbackFile) {
            Write-Warning "Consider rolling back using: .\restore-database.ps1 -BackupFile '$RollbackFile'"
        }
        exit 1
    }
} else {
    Write-Error "Database restore failed"
    
    if ($RollbackFile) {
        Write-Warning "Consider rolling back using: .\restore-database.ps1 -BackupFile '$RollbackFile'"
    }
    exit 1
}

exit 0