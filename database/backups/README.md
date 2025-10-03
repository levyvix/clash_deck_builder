# Database Backup and Restore

This directory contains database backup and restore functionality for the Clash Royale Deck Builder application.

## Overview

The backup and restore system provides:
- Automated database dumps with timestamps
- Compression support for space efficiency
- Backup retention management
- Data validation and integrity checks
- Rollback capabilities for safe restores
- Cross-platform support (Unix/Linux and Windows)

## Backup Scripts

### Unix/Linux: `scripts/backup-database.sh`

```bash
# Basic backup with defaults
./scripts/backup-database.sh

# Custom database and retention
./scripts/backup-database.sh -d my_database -r 7

# Backup without compression
./scripts/backup-database.sh --no-compress

# Show help
./scripts/backup-database.sh --help
```

### Windows: `scripts/backup-database.ps1`

```powershell
# Basic backup with defaults
.\scripts\backup-database.ps1

# Custom database and retention
.\scripts\backup-database.ps1 -Database my_database -RetentionDays 7

# Backup without compression
.\scripts\backup-database.ps1 -NoCompress

# Show help
.\scripts\backup-database.ps1 -Help
```

## Restore Scripts

### Unix/Linux: `scripts/restore-database.sh`

```bash
# List available backups
./scripts/restore-database.sh -l

# Restore from backup (with confirmation)
./scripts/restore-database.sh database/backups/clash_deck_builder_backup_20241203_120000.sql.gz

# Force restore without rollback
./scripts/restore-database.sh -f --no-rollback backup.sql

# Show help
./scripts/restore-database.sh --help
```

### Windows: `scripts/restore-database.ps1`

```powershell
# List available backups
.\scripts\restore-database.ps1 -List

# Restore from backup (with confirmation)
.\scripts\restore-database.ps1 -BackupFile "database\backups\clash_deck_builder_backup_20241203_120000.sql.gz"

# Force restore without rollback
.\scripts\restore-database.ps1 -BackupFile "backup.sql" -Force -NoRollback

# Show help
.\scripts\restore-database.ps1 -Help
```

## Backup File Naming Convention

Backup files follow this naming pattern:
```
{database_name}_backup_{timestamp}.sql[.gz|.zip]
```

Examples:
- `clash_deck_builder_docker_backup_20241203_120000.sql.gz`
- `clash_deck_builder_dev_backup_20241203_143022.sql`

Rollback files use this pattern:
```
{database_name}_rollback_{timestamp}.sql[.gz]
```

## Features

### Backup Features
- **Timestamped backups**: Each backup includes creation timestamp
- **Compression**: Optional gzip compression to save space
- **Retention management**: Automatic cleanup of old backups
- **Integrity validation**: Backup files are validated after creation
- **Comprehensive dumps**: Includes routines, triggers, events, and data
- **Safe defaults**: Development-friendly default settings

### Restore Features
- **Validation**: Backup files are validated before restore
- **Rollback protection**: Automatic rollback backup before restore
- **Confirmation prompts**: Safety prompts to prevent accidental restores
- **Force mode**: Skip confirmations for automated scenarios
- **Integrity verification**: Post-restore validation of database state
- **Detailed logging**: Comprehensive status and error reporting

## Docker Integration

The backup and restore scripts are designed to work with the containerized MySQL database:

- **Container detection**: Automatically detects running database containers
- **Network isolation**: Works with Docker's internal networking
- **Volume persistence**: Backups are stored in persistent volumes
- **Health checks**: Validates container health before operations

## Security Considerations

- **Access control**: Scripts require Docker access and database permissions
- **File permissions**: Backup files should have restricted access
- **Credential security**: Database credentials are handled through Docker environment
- **Backup encryption**: Consider encrypting backup files for sensitive data

## Automation

### Scheduled Backups

You can set up automated backups using cron (Unix/Linux) or Task Scheduler (Windows):

#### Unix/Linux Cron Example
```bash
# Daily backup at 2 AM with 7-day retention
0 2 * * * /path/to/project/scripts/backup-database.sh -r 7 >> /var/log/db-backup.log 2>&1
```

#### Windows Task Scheduler Example
```powershell
# Create scheduled task for daily backup
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\path\to\project\scripts\backup-database.ps1 -RetentionDays 7"
$Trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
Register-ScheduledTask -TaskName "DatabaseBackup" -Action $Action -Trigger $Trigger
```

### CI/CD Integration

The scripts can be integrated into CI/CD pipelines for automated testing and deployment:

```yaml
# GitHub Actions example
- name: Backup Database
  run: ./scripts/backup-database.sh -d test_db -r 1
  
- name: Run Tests
  run: # your test commands
  
- name: Restore Database if Tests Fail
  if: failure()
  run: ./scripts/restore-database.sh -f database/backups/test_db_rollback_*.sql.gz
```

## Troubleshooting

### Common Issues

1. **Container not running**: Ensure the database container is started
2. **Permission denied**: Check Docker permissions and file access
3. **Disk space**: Ensure sufficient space for backups
4. **Compression tools**: Install 7-Zip (Windows) or gzip (Unix) for compression

### Error Recovery

1. **Failed backup**: Check container logs and disk space
2. **Corrupted backup**: Use `--no-validate` flag or restore from earlier backup
3. **Failed restore**: Use rollback backup to revert changes
4. **Missing backups**: Check backup directory and retention settings

## File Structure

```
database/
├── backups/                    # Backup storage directory
│   ├── .gitkeep               # Ensures directory exists in git
│   ├── README.md              # This documentation
│   └── *.sql.gz               # Backup files (not in git)
├── init/                      # Database initialization
└── migrations/                # Schema migrations

scripts/
├── backup-database.sh         # Unix backup script
├── backup-database.ps1        # Windows backup script
├── restore-database.sh        # Unix restore script
└── restore-database.ps1       # Windows restore script
```

## Best Practices

1. **Regular backups**: Schedule daily backups with appropriate retention
2. **Test restores**: Regularly test restore procedures
3. **Monitor disk usage**: Keep an eye on backup directory size
4. **Secure storage**: Store critical backups in secure, off-site locations
5. **Document procedures**: Maintain clear documentation for your team
6. **Version control**: Keep backup scripts in version control, but not backup files