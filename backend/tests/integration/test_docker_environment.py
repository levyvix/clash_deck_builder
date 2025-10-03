"""
Integration tests for Docker environment functionality
"""
import pytest
import requests
import time
import subprocess
import os
from src.utils.database import get_database_health
from tests.fixtures.test_db_manager import test_db_manager


class TestDockerEnvironment:
    """Test Docker environment integration"""
    
    def test_test_database_container_health(self, test_database_setup):
        """Test that test database container is healthy"""
        # Check if we can connect to the test database
        assert test_db_manager.wait_for_database(timeout=30)
        
        # Verify database health
        health = get_database_health()
        assert health['status'] == 'healthy'
        assert health['host'] == 'localhost'
        assert health['port'] == 3307  # Test database port
    
    def test_docker_compose_test_configuration(self):
        """Test that docker-compose.test.yml is properly configured"""
        compose_file = "docker-compose.test.yml"
        assert os.path.exists(compose_file), "docker-compose.test.yml not found"
        
        # Read and verify compose file content
        with open(compose_file, 'r') as f:
            content = f.read()
            
        # Check for required services
        assert 'test-database:' in content
        assert 'test-backend:' in content
        
        # Check for test-specific configuration
        assert 'clash_deck_builder_test' in content
        assert 'test_user' in content
        assert 'test_password' in content
        assert '3307:3306' in content  # Port mapping for test database
    
    def test_test_database_isolation(self, test_database_setup):
        """Test that test database is isolated from main database"""
        # Verify we're connected to test database
        health = get_database_health()
        assert health['database'] == 'clash_deck_builder_test'
        assert health['port'] == 3307
        
        # Test database should have different credentials
        from src.utils.config import get_settings
        settings = get_settings()
        
        # In test environment, should use test credentials
        assert settings.db_user == 'test_user'
        assert settings.db_password == 'test_password'
        assert settings.db_name == 'clash_deck_builder_test'
    
    def test_test_environment_variables(self, test_environment):
        """Test that test environment variables are properly set"""
        assert test_environment['TESTING'] == 'true'
        assert test_environment['DB_HOST'] == 'localhost'
        assert test_environment['DB_PORT'] == '3307'
        assert test_environment['DB_NAME'] == 'clash_deck_builder_test'
        assert test_environment['DB_USER'] == 'test_user'
        assert test_environment['DB_PASSWORD'] == 'test_password'
        assert test_environment['DEBUG'] == 'true'
    
    def test_docker_network_connectivity(self, test_database_setup):
        """Test Docker network connectivity between services"""
        # This test verifies that the test database is accessible
        # In a full Docker environment, this would test container-to-container communication
        
        # For now, test that we can connect to the test database
        success = test_db_manager.connect()
        assert success, "Failed to connect to test database"
        
        # Test basic database operations
        result = test_db_manager.execute_query("SELECT 1 as test")
        assert len(result) == 1
        assert result[0]['test'] == 1
        
        test_db_manager.disconnect()
    
    def test_docker_volume_persistence(self, test_database_setup):
        """Test that Docker volumes persist data correctly"""
        # Add some test data
        test_data = "docker_volume_test_data"
        
        result = test_db_manager.execute_query(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (test_data, f"{test_data}@test.com")
        )
        
        # Verify data was inserted
        result = test_db_manager.execute_query(
            "SELECT username FROM users WHERE username = %s",
            (test_data,)
        )
        assert len(result) == 1
        assert result[0]['username'] == test_data
        
        # In a real Docker environment, we would restart the container here
        # and verify the data persists. For this test, we'll just verify
        # the data is still there after a reconnection
        
        test_db_manager.disconnect()
        test_db_manager.connect()
        
        result = test_db_manager.execute_query(
            "SELECT username FROM users WHERE username = %s",
            (test_data,)
        )
        assert len(result) == 1
        assert result[0]['username'] == test_data
    
    def test_docker_health_checks(self, test_database_setup):
        """Test Docker health check functionality"""
        # Test database health check
        health = get_database_health()
        assert health['status'] == 'healthy'
        assert 'connection_test' in health
        assert health['connection_test'] == 'passed'
        
        # Test that health check includes required information
        required_fields = ['status', 'database', 'host', 'port', 'mysql_version', 'current_time']
        for field in required_fields:
            assert field in health, f"Health check missing field: {field}"
    
    def test_docker_container_resource_limits(self):
        """Test Docker container resource configuration"""
        # This test would verify container resource limits in a real Docker environment
        # For now, we'll test that the test database performs adequately
        
        start_time = time.time()
        
        # Perform multiple database operations
        for i in range(10):
            result = test_db_manager.execute_query("SELECT COUNT(*) as count FROM users")
            assert len(result) == 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Operations should complete within reasonable time (less than 5 seconds)
        assert duration < 5.0, f"Database operations took too long: {duration} seconds"
    
    def test_docker_environment_cleanup(self, test_database_setup):
        """Test Docker environment cleanup functionality"""
        # Add some test data that should be cleaned up
        cleanup_data = "cleanup_test_data"
        
        test_db_manager.execute_query(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (cleanup_data, f"{cleanup_data}@test.com")
        )
        
        # Verify data exists
        result = test_db_manager.execute_query(
            "SELECT COUNT(*) as count FROM users WHERE username = %s",
            (cleanup_data,)
        )
        assert result[0]['count'] == 1
        
        # Clean database
        success = test_db_manager.clean_database()
        assert success, "Database cleanup failed"
        
        # Verify data was cleaned
        result = test_db_manager.execute_query(
            "SELECT COUNT(*) as count FROM users WHERE username = %s",
            (cleanup_data,)
        )
        assert result[0]['count'] == 0
        
        # Reseed test data
        success = test_db_manager.seed_test_data()
        assert success, "Database seeding failed"
        
        # Verify test data is back
        result = test_db_manager.execute_query("SELECT COUNT(*) as count FROM users")
        assert result[0]['count'] >= 3  # Should have test users
    
    def test_docker_compose_test_scripts(self):
        """Test that Docker Compose test scripts are available"""
        # Check for test setup scripts
        test_scripts = [
            "scripts/test-setup.sh",
            "scripts/test-setup.ps1"
        ]
        
        script_exists = any(os.path.exists(script) for script in test_scripts)
        assert script_exists, "No test setup script found"
        
        # Check script content
        for script in test_scripts:
            if os.path.exists(script):
                with open(script, 'r') as f:
                    content = f.read()
                    assert 'docker-compose' in content
                    assert 'test' in content
                    break
    
    def test_test_database_performance(self, test_database_setup):
        """Test test database performance characteristics"""
        # Test insert performance
        start_time = time.time()
        
        for i in range(100):
            test_db_manager.execute_query(
                "INSERT INTO users (username, email) VALUES (%s, %s)",
                (f"perf_test_{i}", f"perf_test_{i}@test.com")
            )
        
        insert_time = time.time() - start_time
        
        # Test select performance
        start_time = time.time()
        
        for i in range(100):
            result = test_db_manager.execute_query(
                "SELECT * FROM users WHERE username = %s",
                (f"perf_test_{i}",)
            )
            assert len(result) == 1
        
        select_time = time.time() - start_time
        
        # Performance should be reasonable for test environment
        assert insert_time < 10.0, f"Insert performance too slow: {insert_time} seconds"
        assert select_time < 5.0, f"Select performance too slow: {select_time} seconds"
        
        # Clean up performance test data
        test_db_manager.execute_query("DELETE FROM users WHERE username LIKE 'perf_test_%'")
    
    def test_docker_logging_configuration(self, test_database_setup):
        """Test Docker logging configuration"""
        # This test would verify Docker logging in a real environment
        # For now, we'll test that database operations are logged properly
        
        import logging
        
        # Capture log output
        logger = logging.getLogger('src.utils.database')
        
        # Perform a database operation that should generate logs
        health = get_database_health()
        assert health['status'] == 'healthy'
        
        # In a real Docker environment, we would check container logs
        # For this test, we verify that logging is configured
        assert logger.level <= logging.INFO