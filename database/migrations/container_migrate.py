#!/usr/bin/env python3
"""
Container Migration Runner

Simplified migration runner for use within Docker containers.
This version uses environment variables for configuration and
provides container-friendly logging and error handling.
"""

import os
import sys
import logging
from pathlib import Path
from migrate import MigrationRunner, MigrationError

# Configure logging for container environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_container_database_config():
    """Get database configuration from container environment variables"""
    
    config = {
        'host': os.getenv('DB_HOST', 'database'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'autocommit': False
    }
    
    # Validate required configuration
    required_fields = ['user', 'password', 'database']
    missing_fields = [field for field in required_fields if not config[field]]
    
    if missing_fields:
        raise MigrationError(f"Missing required environment variables: {missing_fields}")
    
    return config


def run_container_migrations():
    """Run migrations in container environment"""
    
    try:
        logger.info("🔄 Starting container migration process...")
        
        # Get database configuration from environment
        config = get_container_database_config()
        logger.info(f"📡 Connecting to database: {config['host']}:{config['port']}/{config['database']}")
        
        # Initialize migration runner
        migrations_dir = Path(__file__).parent
        runner = MigrationRunner(config, migrations_dir)
        
        # Run migrations
        results = runner.run_migrations()
        
        if results['success']:
            if results['applied_migrations']:
                logger.info(f"✅ Successfully applied {len(results['applied_migrations'])} migrations:")
                for version in results['applied_migrations']:
                    logger.info(f"  📦 {version}")
                logger.info(f"⏱️  Total execution time: {results['total_execution_time_ms']}ms")
            else:
                logger.info("✅ No pending migrations found - database is up to date")
            
            return True
        else:
            logger.error(f"❌ Migration failed: {results['error']}")
            return False
            
    except MigrationError as e:
        logger.error(f"❌ Migration error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration: {e}")
        return False


def get_container_migration_status():
    """Get migration status in container environment"""
    
    try:
        # Get database configuration from environment
        config = get_container_database_config()
        
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
    """CLI entry point for container migrations"""
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'migrate'
    
    try:
        if command == 'migrate':
            logger.info("🚀 Running database migrations...")
            success = run_container_migrations()
            if success:
                logger.info("🎉 Migration process completed successfully")
                sys.exit(0)
            else:
                logger.error("💥 Migration process failed")
                sys.exit(1)
                
        elif command == 'status':
            logger.info("📊 Getting migration status...")
            status = get_container_migration_status()
            
            if status:
                print(f"📊 Migration Status:")
                print(f"  ✅ Applied: {status['applied_count']}")
                print(f"  ⏳ Pending: {status['pending_count']}")
                print(f"  📦 Total Available: {status['total_available']}")
                
                if status['pending_migrations']:
                    print("\n📋 Pending Migrations:")
                    for migration in status['pending_migrations']:
                        print(f"  - {migration['version']}: {migration['name']}")
                        
                if status['applied_migrations']:
                    print("\n✅ Applied Migrations:")
                    for migration in status['applied_migrations']:
                        print(f"  - {migration['version']}: {migration['name']}")
                
                sys.exit(0)
            else:
                sys.exit(1)
                
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Available commands: migrate, status")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()