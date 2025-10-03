#!/usr/bin/env python3
"""
Integration test runner for database operations
"""
import sys
import os
import subprocess
import time
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tests.fixtures.test_db_manager import test_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_docker_available():
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def start_test_database():
    """Start test database container"""
    logger.info("Starting test database container...")
    
    try:
        # Stop any existing test containers
        subprocess.run(['docker-compose', '-f', 'docker-compose.test.yml', 'down', '-v'], 
                      capture_output=True, timeout=30)
        
        # Start test database
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.test.yml', 
            'up', '-d', 'test-database'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logger.error(f"Failed to start test database: {result.stderr}")
            return False
        
        logger.info("Test database container started")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout starting test database container")
        return False
    except Exception as e:
        logger.error(f"Error starting test database: {e}")
        return False


def wait_for_database():
    """Wait for test database to be ready"""
    logger.info("Waiting for test database to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        if test_db_manager.wait_for_database(timeout=5):
            logger.info("Test database is ready!")
            return True
        
        logger.info(f"Attempt {attempt + 1}/{max_attempts}: Database not ready yet...")
        time.sleep(2)
    
    logger.error("Test database failed to become ready")
    return False


def setup_test_database():
    """Set up test database with schema and data"""
    logger.info("Setting up test database...")
    
    try:
        success = test_db_manager.setup_test_database()
        if success:
            logger.info("Test database setup completed")
        else:
            logger.error("Test database setup failed")
        return success
    except Exception as e:
        logger.error(f"Error setting up test database: {e}")
        return False


def run_tests():
    """Run integration tests"""
    logger.info("Running integration tests...")
    
    try:
        # Change to backend directory
        os.chdir(Path(__file__).parent.parent)
        
        # Run pytest with integration tests
        result = subprocess.run([
            'uv', 'run', 'pytest', 
            'tests/integration/', 
            '-v', 
            '--tb=short',
            '--durations=10'
        ], timeout=300)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("Tests timed out")
        return False
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False


def cleanup_test_environment():
    """Clean up test environment"""
    logger.info("Cleaning up test environment...")
    
    try:
        # Stop test containers
        subprocess.run(['docker-compose', '-f', 'docker-compose.test.yml', 'down', '-v'], 
                      capture_output=True, timeout=30)
        logger.info("Test environment cleaned up")
    except Exception as e:
        logger.warning(f"Error cleaning up test environment: {e}")


def main():
    """Main test runner function"""
    logger.info("Starting integration test runner...")
    
    # Check if Docker is available
    if not check_docker_available():
        logger.error("Docker is not available. Please install and start Docker.")
        return 1
    
    try:
        # Start test database
        if not start_test_database():
            return 1
        
        # Wait for database to be ready
        if not wait_for_database():
            return 1
        
        # Set up test database
        if not setup_test_database():
            return 1
        
        # Run tests
        if not run_tests():
            logger.error("Integration tests failed")
            return 1
        
        logger.info("All integration tests passed!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Test run interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        cleanup_test_environment()


if __name__ == "__main__":
    sys.exit(main())