#!/usr/bin/env python3
"""
Migration Runner Integration Script

This script integrates the migration runner with the backend configuration
and provides a convenient way to run migrations using the same database
configuration as the main application.
"""

import os
import sys
from pathlib import Path
import logging

# Add backend src to path to import configuration
backend_src = Path(__file__).parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

try:
    from utils.config import get_settings
except ImportError:
    # Fallback if backend config is not available
    get_settings = None

from migrate import MigrationRunner, MigrationError

logger = logging.getLogger(__name__)


def get_database_config():
    """Get database configuration from backend settings or environment"""
    
    # Try to use backend configuration first
    if get_settings:
        try:
            settings = get_settings()
            return {
                'host': settings.db_host,
                'port': settings.db_port,
                'user': settings.db_user,
                'password': settings.db_password,
                'database': settings.db_name,
                'autocommit': False
            }
        except Exception as e:
            logger.warning(f"Could not load backend settings: {e}")
    
    # Fallback to environment variables
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'clash_deck_builder'),
        'autocommit': False
    }


def run_migrations_with_config():
    """Run migrations using backend configuration"""
    
    try:
        # Get database configuration
        config = get_database_config()
        
        # Initialize migration runner
        migrations_dir = Path(__file__).parent
        runner = MigrationRunner(config, migrations_dir)
        
        # Run migrations
        logger.info("Starting database migrations...")
        results = runner.run_migrations()
        
        if results['success']:
            if results['applied_migrations']:
                logger.info(f"✅ Successfully applied {len(results['applied_migrations'])} migrations:")
                for version in results['applied_migrations']:
                    logger.info(f"  - {version}")
                logger.info(f"Total execution time: {results['total_execution_time_ms']}ms")
            else:
                logger.info("✅ No pending migrations found - database is up to date")
            return True
        else:
            logger.error(f"❌ Migration failed: {results['error']}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration runner failed: {e}")
        return False


def get_migration_status_with_config():
    """Get migration status using backend configuration"""
    
    try:
        # Get database configuration
        config = get_database_config()
        
        # Initialize migration runner
        migrations_dir = Path(__file__).parent
        runner = MigrationRunner(config, migrations_dir)
        
        # Get status
        status = runner.get_migration_status()
        
        if 'error' in status:
            logger.error(f"❌ Failed to get migration status: {status['error']}")
            return None
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get migration status: {e}")
        return None


def main():
    """CLI entry point"""
    import argparse
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Run database migrations with backend config')
    parser.add_argument('command', choices=['migrate', 'status'], 
                       help='Command to execute')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'migrate':
            success = run_migrations_with_config()
            sys.exit(0 if success else 1)
            
        elif args.command == 'status':
            status = get_migration_status_with_config()
            if status:
                print(f"📊 Migration Status:")
                print(f"  Applied: {status['applied_count']}")
                print(f"  Pending: {status['pending_count']}")
                print(f"  Total Available: {status['total_available']}")
                
                if status['pending_migrations']:
                    print("\n📋 Pending Migrations:")
                    for migration in status['pending_migrations']:
                        print(f"  - {migration['version']}: {migration['name']}")
                        
                if status['applied_migrations']:
                    print("\n✅ Applied Migrations:")
                    for migration in status['applied_migrations']:
                        print(f"  - {migration['version']}: {migration['name']}")
            else:
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()