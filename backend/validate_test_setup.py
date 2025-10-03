#!/usr/bin/env python3
"""
Validation script for testing setup
"""
import sys
import os
from pathlib import Path

def validate_imports():
    """Validate that all required modules can be imported"""
    print("Validating imports...")
    
    try:
        from src.utils.config import Settings
        print("✓ Config module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from src.utils.database import DatabaseManager
        print("✓ Database module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import database: {e}")
        return False
    
    try:
        from tests.fixtures.test_db_manager import TestDatabaseManager
        print("✓ Test database manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import test database manager: {e}")
        return False
    
    return True

def validate_files():
    """Validate that all required files exist"""
    print("\nValidating files...")
    
    required_files = [
        ("../docker-compose.test.yml", "docker-compose.test.yml"),
        ("tests/conftest.py", "tests/conftest.py"),
        ("tests/fixtures/test_db_manager.py", "tests/fixtures/test_db_manager.py"),
        ("tests/fixtures/test_data.sql", "tests/fixtures/test_data.sql"),
        ("tests/integration/test_database_connection.py", "tests/integration/test_database_connection.py"),
        ("tests/integration/test_deck_operations.py", "tests/integration/test_deck_operations.py"),
        ("tests/integration/test_migration_system.py", "tests/integration/test_migration_system.py"),
        ("tests/integration/test_backup_restore.py", "tests/integration/test_backup_restore.py"),
        ("tests/integration/test_docker_environment.py", "tests/integration/test_docker_environment.py"),
        ("../scripts/test-setup.sh", "scripts/test-setup.sh"),
        ("../scripts/test-setup.ps1", "scripts/test-setup.ps1")
    ]
    
    missing_files = []
    for file_path, display_name in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✓ {display_name}")
        else:
            print(f"✗ {display_name} (missing)")
            missing_files.append(display_name)
    
    return len(missing_files) == 0

def validate_test_structure():
    """Validate test structure and configuration"""
    print("\nValidating test structure...")
    
    try:
        import pytest
        print("✓ pytest is available")
    except ImportError:
        print("✗ pytest not available")
        return False
    
    # Check pytest configuration
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        with open(pyproject_path, 'r') as f:
            content = f.read()
            if '[tool.pytest.ini_options]' in content:
                print("✓ pytest configuration found")
            else:
                print("✗ pytest configuration missing")
                return False
    else:
        print("✗ pyproject.toml not found")
        return False
    
    return True

def main():
    """Main validation function"""
    print("Validating comprehensive testing setup...\n")
    
    # Change to backend directory
    os.chdir(Path(__file__).parent)
    
    success = True
    
    # Validate imports
    if not validate_imports():
        success = False
    
    # Validate files
    if not validate_files():
        success = False
    
    # Validate test structure
    if not validate_test_structure():
        success = False
    
    print(f"\n{'='*50}")
    if success:
        print("✓ All validations passed! Testing setup is ready.")
        print("\nTo run tests:")
        print("1. Start test database: docker-compose -f docker-compose.test.yml up -d test-database")
        print("2. Run tests: uv run pytest tests/integration/ -v")
        print("3. Or use scripts: ./scripts/test-setup.sh (Linux/macOS) or .\\scripts\\test-setup.ps1 (Windows)")
    else:
        print("✗ Some validations failed. Please check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())