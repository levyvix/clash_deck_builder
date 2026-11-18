#!/usr/bin/env python3
"""
Container Migration Runner

Simplified migration runner for use within Docker containers.
This version uses environment variables for configuration and
provides container-friendly logging and error handling with
enhanced Docker integration features.
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from migrate import MigrationRunner, MigrationError

# Configure logging for container environment with enhanced formatting
log_level = os.getenv('MIGRATION_LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - MIGRATION - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Migration configuration from environment
MIGRATION_TIMEOUT = int(os.getenv('MIGRATION_TIMEOUT', '300'))
MIGRATION_RETRY_COUNT = int(os.getenv('MIGRATION_RETRY_COUNT', '3'))
MIGRATION_RETRY_DELAY = int(os.getenv('MIGRATION_RETRY_DELAY', '5'))


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
    """Run migrations in container environment with retry logic and enhanced logging"""
    
    start_time = datetime.now()
    logger.info("� StarSting container migration process...")
    logger.info(f"⚙️  Configuration: timeout={MIGRATION_TIMEOUT}s, retries={MIGRATION_RETRY_COUNT}, delay={MIGRATION_RETRY_DELAY}s")
    
    for attempt in range(1, MIGRATION_RETRY_COUNT + 1):
        try:
            logger.info(f"🎯 Migration attempt {attempt}/{MIGRATION_RETRY_COUNT}")
            
            # Get database configuration from environment
            config = get_container_database_config()
            logger.info(f"📡 Connecting to database: {config['host']}:{config['port']}/{config['database']}")
            
            # Initialize migration runner
            migrations_dir = Path(__file__).parent
            runner = MigrationRunner(config, migrations_dir)
            
            # Test database connection first
            logger.info("🔍 Testing database connection...")
            runner.check_connection()
            logger.info("✅ Database connection successful")
            
            # Run migrations
            logger.info("🚀 Executing migrations...")
            results = runner.run_migrations()
            
            if results['success']:
                end_time = datetime.now()
                total_time = (end_time - start_time).total_seconds()
                
                if results['applied_migrations']:
                    logger.info(f"✅ Successfully applied {len(results['applied_migrations'])} migrations:")
                    for version in results['applied_migrations']:
                        logger.info(f"  📦 {version}")
                    logger.info(f"⏱️  Migration execution time: {results['total_execution_time_ms']}ms")
                    logger.info(f"⏱️  Total process time: {total_time:.2f}s")
                    
                    # Log migration summary
                    _log_migration_summary(results, total_time)
                else:
                    logger.info("✅ No pending migrations found - database is up to date")
                    logger.info(f"⏱️  Total process time: {total_time:.2f}s")
                
                return True
            else:
                logger.error(f"❌ Migration failed: {results['error']}")
                if attempt < MIGRATION_RETRY_COUNT:
                    logger.warning(f"⏳ Retrying in {MIGRATION_RETRY_DELAY} seconds...")
                    time.sleep(MIGRATION_RETRY_DELAY)
                    continue
                else:
                    logger.error("💥 All migration attempts failed")
                    return False
                    
        except MigrationError as e:
            logger.error(f"❌ Migration error on attempt {attempt}: {e}")
            if attempt < MIGRATION_RETRY_COUNT:
                logger.warning(f"⏳ Retrying in {MIGRATION_RETRY_DELAY} seconds...")
                time.sleep(MIGRATION_RETRY_DELAY)
                continue
            else:
                logger.error("💥 All migration attempts failed due to migration errors")
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error on attempt {attempt}: {e}")
            if attempt < MIGRATION_RETRY_COUNT:
                logger.warning(f"⏳ Retrying in {MIGRATION_RETRY_DELAY} seconds...")
                time.sleep(MIGRATION_RETRY_DELAY)
                continue
            else:
                logger.error("💥 All migration attempts failed due to unexpected errors")
                return False
    
    return False


def _log_migration_summary(results, total_time):
    """Log a summary of migration results"""
    logger.info("📋 Migration Summary:")
    logger.info(f"  ✅ Applied migrations: {len(results['applied_migrations'])}")
    logger.info(f"  ⏱️  Execution time: {results['total_execution_time_ms']}ms")
    logger.info(f"  ⏱️  Total time: {total_time:.2f}s")
    logger.info(f"  📅 Completed at: {datetime.now().isoformat()}")
    
    if results['skipped_migrations']:
        logger.info(f"  ⏭️  Skipped migrations: {len(results['skipped_migrations'])}")


def wait_for_database_ready(max_attempts=30, delay=2):
    """Wait for database to be ready before running migrations"""
    logger.info("⏳ Waiting for database to be ready...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            config = get_container_database_config()
            
            # Try to connect and execute a simple query
            import mysql.connector
            with mysql.connector.connect(**config) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            logger.info(f"✅ Database is ready after {attempt} attempts")
            return True
            
        except Exception as e:
            if attempt < max_attempts:
                logger.info(f"⏳ Database not ready (attempt {attempt}/{max_attempts}): {e}")
                time.sleep(delay)
            else:
                logger.error(f"❌ Database failed to become ready after {max_attempts} attempts: {e}")
                return False
    
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
    """CLI entry point for container migrations with enhanced Docker integration"""
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'migrate'
    
    # Log startup information
    logger.info(f"🐳 Container Migration Runner starting...")
    logger.info(f"📋 Command: {command}")
    logger.info(f"🕐 Started at: {datetime.now().isoformat()}")
    logger.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    try:
        if command == 'migrate':
            logger.info("� Running rdatabase migrations...")
            
            # Wait for database to be ready first
            if not wait_for_database_ready():
                logger.error("� Da tabase is not ready, cannot proceed with migrations")
                sys.exit(1)
            
            # Run migrations
            success = run_container_migrations()
            
            if success:
                logger.info("🎉 Migration process completed successfully")
                
                # Create success marker for health checks
                marker_file = Path("/app/database/migrations/logs/migration_success")
                marker_file.parent.mkdir(parents=True, exist_ok=True)
                marker_file.write_text(f"{datetime.now().isoformat()}\n")
                
                sys.exit(0)
            else:
                logger.error("💥 Migration process failed")
                
                # Create failure marker for health checks
                marker_file = Path("/app/database/migrations/logs/migration_failure")
                marker_file.parent.mkdir(parents=True, exist_ok=True)
                marker_file.write_text(f"{datetime.now().isoformat()}\n")
                
                sys.exit(1)
                
        elif command == 'status':
            logger.info("📊 Getting migration status...")
            
            # Wait for database to be ready
            if not wait_for_database_ready(max_attempts=10, delay=1):
                logger.error("💥 Database is not ready, cannot get migration status")
                sys.exit(1)
            
            status = get_container_migration_status()
            
            if status:
                print("📊 Migration Status:")
                print(f"  ✅ Applied: {status['applied_count']}")
                print(f"  ⏳ Pending: {status['pending_count']}")
                print(f"  📦 Total Available: {status['total_available']}")
                print(f"  🕐 Checked at: {datetime.now().isoformat()}")
                
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
                logger.error("💥 Failed to get migration status")
                sys.exit(1)
                
        elif command == 'wait':
            # Special command for waiting for database readiness
            logger.info("⏳ Waiting for database readiness...")
            if wait_for_database_ready():
                logger.info("✅ Database is ready")
                sys.exit(0)
            else:
                logger.error("❌ Database failed to become ready")
                sys.exit(1)
                
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Available commands: migrate, status, wait")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == '__main__':
    main()
