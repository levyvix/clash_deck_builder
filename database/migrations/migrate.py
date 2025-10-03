#!/usr/bin/env python3
"""
Database Migration Runner

This module provides a framework for executing schema migrations and tracking
their application status. It supports both forward migrations and rollbacks.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Custom exception for migration-related errors"""
    pass


class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version: str, name: str, file_path: Path):
        self.version = version
        self.name = name
        self.file_path = file_path
        self.applied_at: Optional[datetime] = None
    
    def __str__(self):
        return f"Migration {self.version}: {self.name}"
    
    def __repr__(self):
        return f"Migration(version='{self.version}', name='{self.name}')"


class MigrationRunner:
    """
    Handles database migration execution and tracking
    
    Migration files should follow the naming convention:
    YYYYMMDD_HHMMSS_description.sql
    
    Example: 20241203_120000_add_user_preferences_table.sql
    """
    
    def __init__(self, connection_config: Dict[str, str], migrations_dir: Optional[Path] = None):
        self.config = connection_config
        self.migrations_dir = migrations_dir or Path(__file__).parent
        self.migrations_table = "schema_migrations"
        
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Migration runner initialized with directory: {self.migrations_dir}")
    
    def _get_connection(self):
        """Create database connection"""
        try:
            return mysql.connector.connect(**self.config)
        except MySQLError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise MigrationError(f"Database connection failed: {e}")
    
    def _ensure_migrations_table(self, cursor):
        """Create migrations tracking table if it doesn't exist"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.migrations_table} (
            version VARCHAR(255) PRIMARY KEY,
            name VARCHAR(500) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64),
            execution_time_ms INT DEFAULT 0
        )
        """
        
        try:
            cursor.execute(create_table_sql)
            logger.debug(f"Ensured {self.migrations_table} table exists")
        except MySQLError as e:
            logger.error(f"Failed to create migrations table: {e}")
            raise MigrationError(f"Could not create migrations table: {e}")
    
    def _get_applied_migrations(self, cursor) -> Dict[str, Migration]:
        """Get list of already applied migrations"""
        try:
            cursor.execute(f"""
                SELECT version, name, applied_at 
                FROM {self.migrations_table} 
                ORDER BY version
            """)
            
            applied = {}
            for version, name, applied_at in cursor.fetchall():
                migration = Migration(version, name, Path())
                migration.applied_at = applied_at
                applied[version] = migration
            
            logger.debug(f"Found {len(applied)} applied migrations")
            return applied
            
        except MySQLError as e:
            logger.error(f"Failed to get applied migrations: {e}")
            raise MigrationError(f"Could not retrieve applied migrations: {e}")
    
    def _discover_migration_files(self) -> List[Migration]:
        """Discover migration files in the migrations directory"""
        migration_files = []
        
        # Look for .sql files with version prefix
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            filename = file_path.name
            
            # Skip rollback files (they should end with .rollback.sql)
            if filename.endswith('.rollback.sql'):
                logger.debug(f"Skipping rollback file: {filename}")
                continue
            
            # Skip if it doesn't match expected pattern
            if not self._is_valid_migration_filename(filename):
                logger.warning(f"Skipping invalid migration filename: {filename}")
                continue
            
            # Extract version and name from filename
            version, name = self._parse_migration_filename(filename)
            migration = Migration(version, name, file_path)
            migration_files.append(migration)
        
        logger.info(f"Discovered {len(migration_files)} migration files")
        return migration_files
    
    def _is_valid_migration_filename(self, filename: str) -> bool:
        """Check if filename follows migration naming convention"""
        # Expected format: YYYYMMDD_HHMMSS_description.sql
        parts = filename.replace('.sql', '').split('_', 2)
        
        if len(parts) < 3:
            return False
        
        date_part, time_part = parts[0], parts[1]
        
        # Check date part (YYYYMMDD)
        if len(date_part) != 8 or not date_part.isdigit():
            return False
        
        # Check time part (HHMMSS)
        if len(time_part) != 6 or not time_part.isdigit():
            return False
        
        return True
    
    def _parse_migration_filename(self, filename: str) -> tuple[str, str]:
        """Parse migration filename to extract version and name"""
        base_name = filename.replace('.sql', '')
        parts = base_name.split('_', 2)
        
        version = f"{parts[0]}_{parts[1]}"
        name = parts[2].replace('_', ' ').title() if len(parts) > 2 else "Unnamed Migration"
        
        return version, name
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate checksum for migration file content"""
        import hashlib
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def _execute_migration(self, cursor, migration: Migration) -> int:
        """Execute a single migration and return execution time in milliseconds"""
        logger.info(f"Applying migration: {migration}")
        
        try:
            # Read migration file
            with open(migration.file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Track execution time
            start_time = datetime.now()
            
            # Split and execute SQL statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    cursor.execute(statement)
            
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Record migration as applied
            checksum = self._calculate_checksum(migration.file_path)
            cursor.execute(f"""
                INSERT INTO {self.migrations_table} 
                (version, name, checksum, execution_time_ms) 
                VALUES (%s, %s, %s, %s)
            """, (migration.version, migration.name, checksum, execution_time_ms))
            
            logger.info(f"Successfully applied {migration} in {execution_time_ms}ms")
            return execution_time_ms
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration}: {e}")
            raise MigrationError(f"Migration {migration.version} failed: {e}")
    
    def run_migrations(self, target_version: Optional[str] = None) -> Dict[str, any]:
        """
        Run all pending migrations up to target version
        
        Args:
            target_version: Stop at this version (None = run all)
            
        Returns:
            Dictionary with migration results
        """
        results = {
            'applied_migrations': [],
            'skipped_migrations': [],
            'total_execution_time_ms': 0,
            'success': True,
            'error': None
        }
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure migrations table exists
                self._ensure_migrations_table(cursor)
                
                # Get applied migrations
                applied_migrations = self._get_applied_migrations(cursor)
                
                # Discover available migrations
                available_migrations = self._discover_migration_files()
                
                # Filter pending migrations
                pending_migrations = [
                    m for m in available_migrations 
                    if m.version not in applied_migrations
                ]
                
                if not pending_migrations:
                    logger.info("No pending migrations found")
                    return results
                
                # Apply pending migrations
                for migration in pending_migrations:
                    # Stop if we've reached target version
                    if target_version and migration.version > target_version:
                        results['skipped_migrations'].append(migration.version)
                        continue
                    
                    try:
                        execution_time = self._execute_migration(cursor, migration)
                        results['applied_migrations'].append(migration.version)
                        results['total_execution_time_ms'] += execution_time
                        
                        # Commit after each successful migration
                        conn.commit()
                        
                    except Exception as e:
                        conn.rollback()
                        results['success'] = False
                        results['error'] = str(e)
                        logger.error(f"Migration failed, rolling back: {e}")
                        break
                
                if results['applied_migrations']:
                    logger.info(f"Applied {len(results['applied_migrations'])} migrations successfully")
                
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            logger.error(f"Migration run failed: {e}")
        
        return results
    
    def rollback_migration(self, target_version: str) -> Dict[str, any]:
        """
        Rollback migrations to target version
        
        Note: This requires rollback scripts following naming convention:
        YYYYMMDD_HHMMSS_description.rollback.sql
        """
        results = {
            'rolled_back_migrations': [],
            'success': True,
            'error': None
        }
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get applied migrations after target version
                cursor.execute(f"""
                    SELECT version, name FROM {self.migrations_table} 
                    WHERE version > %s 
                    ORDER BY version DESC
                """, (target_version,))
                
                migrations_to_rollback = cursor.fetchall()
                
                if not migrations_to_rollback:
                    logger.info(f"No migrations to rollback from version {target_version}")
                    return results
                
                # Execute rollback for each migration
                for version, name in migrations_to_rollback:
                    rollback_file = self.migrations_dir / f"{version}_{name.lower().replace(' ', '_')}.rollback.sql"
                    
                    if not rollback_file.exists():
                        logger.warning(f"No rollback script found for {version}: {rollback_file}")
                        continue
                    
                    try:
                        # Execute rollback script
                        with open(rollback_file, 'r', encoding='utf-8') as f:
                            rollback_sql = f.read()
                        
                        statements = [stmt.strip() for stmt in rollback_sql.split(';') if stmt.strip()]
                        for statement in statements:
                            if statement:
                                cursor.execute(statement)
                        
                        # Remove from migrations table
                        cursor.execute(f"DELETE FROM {self.migrations_table} WHERE version = %s", (version,))
                        
                        results['rolled_back_migrations'].append(version)
                        conn.commit()
                        
                        logger.info(f"Rolled back migration {version}")
                        
                    except Exception as e:
                        conn.rollback()
                        results['success'] = False
                        results['error'] = f"Rollback failed for {version}: {e}"
                        logger.error(f"Rollback failed for {version}: {e}")
                        break
                
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            logger.error(f"Rollback operation failed: {e}")
        
        return results
    
    def get_migration_status(self) -> Dict[str, any]:
        """Get current migration status"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure migrations table exists
                self._ensure_migrations_table(cursor)
                
                # Get applied migrations
                applied_migrations = self._get_applied_migrations(cursor)
                
                # Get available migrations
                available_migrations = self._discover_migration_files()
                
                # Calculate pending migrations
                pending_migrations = [
                    m for m in available_migrations 
                    if m.version not in applied_migrations
                ]
                
                return {
                    'applied_count': len(applied_migrations),
                    'pending_count': len(pending_migrations),
                    'total_available': len(available_migrations),
                    'applied_migrations': [
                        {
                            'version': m.version,
                            'name': m.name,
                            'applied_at': m.applied_at.isoformat() if m.applied_at else None
                        }
                        for m in applied_migrations.values()
                    ],
                    'pending_migrations': [
                        {
                            'version': m.version,
                            'name': m.name,
                            'file_path': str(m.file_path)
                        }
                        for m in pending_migrations
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}


def main():
    """CLI entry point for migration runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('command', choices=['migrate', 'rollback', 'status'], 
                       help='Migration command to execute')
    parser.add_argument('--target', help='Target migration version')
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=3306, help='Database port')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--migrations-dir', help='Migrations directory path')
    
    args = parser.parse_args()
    
    # Build connection config
    config = {
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'password': args.password,
        'database': args.database,
        'autocommit': False
    }
    
    # Initialize migration runner
    migrations_dir = Path(args.migrations_dir) if args.migrations_dir else None
    runner = MigrationRunner(config, migrations_dir)
    
    try:
        if args.command == 'migrate':
            results = runner.run_migrations(args.target)
            if results['success']:
                print(f"✅ Applied {len(results['applied_migrations'])} migrations")
                for version in results['applied_migrations']:
                    print(f"  - {version}")
            else:
                print(f"❌ Migration failed: {results['error']}")
                sys.exit(1)
                
        elif args.command == 'rollback':
            if not args.target:
                print("❌ Target version required for rollback")
                sys.exit(1)
            
            results = runner.rollback_migration(args.target)
            if results['success']:
                print(f"✅ Rolled back {len(results['rolled_back_migrations'])} migrations")
                for version in results['rolled_back_migrations']:
                    print(f"  - {version}")
            else:
                print(f"❌ Rollback failed: {results['error']}")
                sys.exit(1)
                
        elif args.command == 'status':
            status = runner.get_migration_status()
            if 'error' in status:
                print(f"❌ Failed to get status: {status['error']}")
                sys.exit(1)
            
            print(f"📊 Migration Status:")
            print(f"  Applied: {status['applied_count']}")
            print(f"  Pending: {status['pending_count']}")
            print(f"  Total Available: {status['total_available']}")
            
            if status['pending_migrations']:
                print("\n📋 Pending Migrations:")
                for migration in status['pending_migrations']:
                    print(f"  - {migration['version']}: {migration['name']}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()