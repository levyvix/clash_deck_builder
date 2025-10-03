#!/usr/bin/env python3
"""
Health Check Script for Backend Container

This script performs comprehensive health checks including:
- Database connectivity
- Migration status verification
- Application readiness
"""

import os
import sys
import requests
import mysql.connector
from pathlib import Path

def check_database_connection():
    """Check if database is accessible"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'database'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

def check_migrations_table():
    """Check if migrations table exists and has been used"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'database'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        cursor = conn.cursor()
        
        # Check if migrations table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'schema_migrations'
        """, (os.getenv('DB_NAME'),))
        
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            # Check if any migrations have been applied
            cursor.execute("SELECT COUNT(*) FROM schema_migrations")
            migration_count = cursor.fetchone()[0]
            print(f"Migrations table exists with {migration_count} applied migrations")
        else:
            print("Migrations table does not exist yet")
        
        cursor.close()
        conn.close()
        
        return table_exists
    except Exception as e:
        print(f"Migration table check failed: {e}")
        return False


def check_migration_status():
    """Check migration status and verify no failures occurred"""
    try:
        # Check for migration success/failure markers
        success_marker = Path("/app/database/migrations/logs/migration_success")
        failure_marker = Path("/app/database/migrations/logs/migration_failure")
        
        if failure_marker.exists():
            print("Migration failure marker found - migrations failed during startup")
            return False
        
        if success_marker.exists():
            print("Migration success marker found - migrations completed successfully")
            return True
        
        # If no markers exist, check if migrations are needed
        # This could happen on first startup before migrations run
        print("No migration markers found - checking if migrations are needed")
        
        # Try to connect and check migration status
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'database'),
            port=int(os.getenv('DB_PORT', '3306')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        cursor = conn.cursor()
        
        # Check if migrations table exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'schema_migrations'
        """, (os.getenv('DB_NAME'),))
        
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("Migrations table doesn't exist - migrations may not have run yet")
            cursor.close()
            conn.close()
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration status check failed: {e}")
        return False

def check_application_endpoint():
    """Check if application is responding"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Application endpoint check failed: {e}")
        return False

def main():
    """Main health check function"""
    
    checks = [
        ("Database Connection", check_database_connection),
        ("Migrations Table", check_migrations_table),
        ("Migration Status", check_migration_status),
        ("Application Endpoint", check_application_endpoint)
    ]
    
    all_passed = True
    
    print("🔍 Running container health checks...")
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{check_name}: {status}")
            
            if not result:
                all_passed = False
        except Exception as e:
            print(f"{check_name}: ❌ ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print("🎉 All health checks passed")
        sys.exit(0)
    else:
        print("💥 Some health checks failed")
        sys.exit(1)

if __name__ == '__main__':
    main()