"""
Integration tests for database connection and basic operations
"""
import pytest
import mysql.connector
from mysql.connector import Error as MySQLError
from src.utils.database import (
    DatabaseManager, 
    get_db_connection, 
    get_db_session, 
    get_database_health,
    initialize_database
)
from src.utils.config import Settings


class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_database_manager_initialization(self, test_environment):
        """Test that DatabaseManager can be initialized with test settings"""
        test_settings = Settings(
            db_host="localhost",
            db_port=3307,
            db_name="clash_deck_builder_test",
            db_user="test_user",
            db_password="test_password"
        )
        
        db_manager = DatabaseManager(test_settings)
        assert db_manager.settings.db_host == "localhost"
        assert db_manager.settings.db_port == 3307
        assert db_manager.settings.db_name == "clash_deck_builder_test"
    
    def test_database_connection_context_manager(self, test_database_setup):
        """Test database connection context manager"""
        with get_db_connection() as conn:
            assert conn is not None
            assert conn.is_connected()
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()
    
    def test_database_session_context_manager(self, test_database_setup):
        """Test database session context manager with transaction"""
        with get_db_session() as session:
            assert session is not None
            
            # Test basic query
            session.execute("SELECT COUNT(*) as count FROM users")
            result = session.fetchone()
            assert 'count' in result
            assert result['count'] >= 0
    
    def test_database_health_check(self, test_database_setup):
        """Test database health check functionality"""
        health = get_database_health()
        
        assert health['status'] == 'healthy'
        assert health['database'] == 'clash_deck_builder_test'
        assert health['host'] == 'localhost'
        assert health['port'] == 3307
        assert health['pool_initialized'] is True
        assert 'mysql_version' in health
        assert 'current_time' in health
        assert 'table_count' in health
        assert health['table_count'] > 0  # Should have tables from schema
    
    def test_database_connection_retry_logic(self, test_environment):
        """Test database connection retry logic with invalid credentials"""
        invalid_settings = Settings(
            db_host="localhost",
            db_port=3307,
            db_name="clash_deck_builder_test",
            db_user="invalid_user",
            db_password="invalid_password"
        )
        
        db_manager = DatabaseManager(invalid_settings)
        
        with pytest.raises(Exception):  # Should raise ConnectionPoolError
            db_manager.initialize()
    
    def test_database_connection_with_invalid_host(self, test_environment):
        """Test database connection with invalid host"""
        invalid_settings = Settings(
            db_host="invalid_host",
            db_port=3307,
            db_name="clash_deck_builder_test",
            db_user="test_user",
            db_password="test_password"
        )
        
        db_manager = DatabaseManager(invalid_settings)
        
        with pytest.raises(Exception):  # Should raise ConnectionPoolError
            db_manager.initialize()
    
    def test_database_schema_validation(self, test_database_setup):
        """Test that required database tables exist"""
        with get_db_session() as session:
            # Check that required tables exist
            session.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'clash_deck_builder_test'
            """)
            tables = session.fetchall()
            table_names = [table['table_name'] for table in tables]
            
            # Verify required tables exist
            required_tables = ['users', 'decks', 'cards_cache']
            for table in required_tables:
                assert table in table_names, f"Required table '{table}' not found"
    
    def test_database_foreign_key_constraints(self, test_database_setup):
        """Test that foreign key constraints are properly set up"""
        with get_db_session() as session:
            # Check foreign key constraints
            session.execute("""
                SELECT 
                    CONSTRAINT_NAME,
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE CONSTRAINT_SCHEMA = 'clash_deck_builder_test'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            constraints = session.fetchall()
            
            # Should have at least one foreign key constraint (decks -> users)
            assert len(constraints) > 0
            
            # Check specific constraint exists
            deck_user_constraint = any(
                c['TABLE_NAME'] == 'decks' and 
                c['REFERENCED_TABLE_NAME'] == 'users' and
                c['COLUMN_NAME'] == 'user_id'
                for c in constraints
            )
            assert deck_user_constraint, "Foreign key constraint from decks to users not found"
    
    def test_database_indexes_exist(self, test_database_setup):
        """Test that performance indexes are created"""
        with get_db_session() as session:
            # Check indexes on decks table
            session.execute("""
                SELECT INDEX_NAME, COLUMN_NAME
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = 'clash_deck_builder_test'
                AND TABLE_NAME = 'decks'
                AND INDEX_NAME != 'PRIMARY'
            """)
            deck_indexes = session.fetchall()
            
            # Should have indexes on user_id, name, created_at
            index_columns = [idx['COLUMN_NAME'] for idx in deck_indexes]
            assert 'user_id' in index_columns
            assert 'name' in index_columns
            assert 'created_at' in index_columns
    
    def test_database_connection_pool_behavior(self, test_database_setup):
        """Test database connection pool behavior with multiple connections"""
        connections = []
        
        try:
            # Get multiple connections
            for i in range(5):
                with get_db_connection() as conn:
                    assert conn.is_connected()
                    cursor = conn.cursor()
                    cursor.execute("SELECT CONNECTION_ID() as conn_id")
                    result = cursor.fetchone()
                    connections.append(result[0])
                    cursor.close()
            
            # All connections should be different (from pool)
            assert len(set(connections)) == len(connections)
            
        except Exception as e:
            pytest.fail(f"Connection pool test failed: {e}")
    
    def test_database_transaction_rollback(self, test_database_setup):
        """Test database transaction rollback functionality"""
        initial_count = 0
        
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            result = session.fetchone()
            initial_count = result['count']
        
        # Test transaction rollback
        try:
            with get_db_session() as session:
                # Insert a test user
                session.execute(
                    "INSERT INTO users (username, email) VALUES (%s, %s)",
                    ("rollback_test", "rollback@test.com")
                )
                
                # Force an error to trigger rollback
                session.execute("INSERT INTO users (username, email) VALUES (%s, %s)",
                              ("rollback_test", "rollback@test.com"))  # Duplicate username
        except Exception:
            # Expected to fail due to duplicate username
            pass
        
        # Verify rollback occurred
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            result = session.fetchone()
            final_count = result['count']
            
            assert final_count == initial_count, "Transaction rollback failed"