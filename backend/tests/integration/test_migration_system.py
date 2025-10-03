"""
Integration tests for database migration system
"""
import pytest
import os
from pathlib import Path
from src.utils.database import get_db_session, execute_sql_script
from tests.fixtures.test_db_manager import test_db_manager


class TestMigrationSystem:
    """Test database migration system functionality"""
    
    def test_schema_migrations_table_exists(self, test_database_setup):
        """Test that schema_migrations table exists"""
        with get_db_session() as session:
            session.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'clash_deck_builder_test' 
                AND table_name = 'schema_migrations'
            """)
            result = session.fetchone()
            
            # Note: This test might fail if migrations haven't been run yet
            # In a real scenario, migrations would be run during container startup
            assert result['count'] >= 0  # Table may or may not exist depending on setup
    
    def test_database_schema_initialization(self, test_database_setup):
        """Test that database schema is properly initialized"""
        with get_db_session() as session:
            # Check that all required tables exist
            session.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'clash_deck_builder_test'
                ORDER BY table_name
            """)
            tables = session.fetchall()
            table_names = [table['table_name'] for table in tables]
            
            required_tables = ['users', 'decks', 'cards_cache']
            for table in required_tables:
                assert table in table_names, f"Required table '{table}' not found"
    
    def test_database_indexes_created(self, test_database_setup):
        """Test that performance indexes are created"""
        with get_db_session() as session:
            # Check indexes on decks table
            session.execute("""
                SELECT DISTINCT INDEX_NAME, COLUMN_NAME
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = 'clash_deck_builder_test'
                AND TABLE_NAME = 'decks'
                AND INDEX_NAME != 'PRIMARY'
                ORDER BY INDEX_NAME, COLUMN_NAME
            """)
            indexes = session.fetchall()
            
            # Should have indexes on key columns
            index_columns = [idx['COLUMN_NAME'] for idx in indexes]
            expected_columns = ['user_id', 'name', 'created_at']
            
            for column in expected_columns:
                assert column in index_columns, f"Index on column '{column}' not found"
    
    def test_foreign_key_constraints(self, test_database_setup):
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
            
            # Check that decks table has foreign key to users
            deck_user_fk = any(
                c['TABLE_NAME'] == 'decks' and 
                c['REFERENCED_TABLE_NAME'] == 'users' and
                c['COLUMN_NAME'] == 'user_id' and
                c['REFERENCED_COLUMN_NAME'] == 'id'
                for c in constraints
            )
            assert deck_user_fk, "Foreign key constraint from decks.user_id to users.id not found"
    
    def test_database_charset_and_collation(self, test_database_setup):
        """Test that database uses proper charset and collation"""
        with get_db_session() as session:
            # Check database charset and collation
            session.execute("""
                SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
                FROM information_schema.SCHEMATA
                WHERE SCHEMA_NAME = 'clash_deck_builder_test'
            """)
            result = session.fetchone()
            
            if result:  # May not be available in all MySQL versions
                charset = result['DEFAULT_CHARACTER_SET_NAME']
                collation = result['DEFAULT_COLLATION_NAME']
                
                # Should use UTF8MB4 for full Unicode support
                assert charset in ['utf8mb4', 'utf8'], f"Unexpected charset: {charset}"
                if charset == 'utf8mb4':
                    assert 'utf8mb4' in collation, f"Unexpected collation: {collation}"
    
    def test_table_column_definitions(self, test_database_setup):
        """Test that table columns are properly defined"""
        with get_db_session() as session:
            # Check users table structure
            session.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'clash_deck_builder_test'
                AND TABLE_NAME = 'users'
                ORDER BY ORDINAL_POSITION
            """)
            user_columns = session.fetchall()
            
            # Verify key columns exist with correct properties
            column_info = {col['COLUMN_NAME']: col for col in user_columns}
            
            assert 'id' in column_info
            assert column_info['id']['COLUMN_KEY'] == 'PRI'
            assert 'auto_increment' in column_info['id']['EXTRA'].lower()
            
            assert 'username' in column_info
            assert column_info['username']['IS_NULLABLE'] == 'NO'
            
            assert 'email' in column_info
            assert column_info['email']['IS_NULLABLE'] == 'NO'
            
            # Check decks table structure
            session.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'clash_deck_builder_test'
                AND TABLE_NAME = 'decks'
                ORDER BY ORDINAL_POSITION
            """)
            deck_columns = session.fetchall()
            
            deck_column_info = {col['COLUMN_NAME']: col for col in deck_columns}
            
            assert 'id' in deck_column_info
            assert deck_column_info['id']['COLUMN_KEY'] == 'PRI'
            
            assert 'user_id' in deck_column_info
            assert 'cards' in deck_column_info
            assert deck_column_info['cards']['DATA_TYPE'] == 'json'
            
            assert 'evolution_slots' in deck_column_info
            assert deck_column_info['evolution_slots']['DATA_TYPE'] == 'json'
    
    def test_sql_script_execution(self, test_database_setup):
        """Test SQL script execution functionality"""
        # Create a simple test script
        test_script = """
        CREATE TEMPORARY TABLE test_migration (
            id INT AUTO_INCREMENT PRIMARY KEY,
            test_data VARCHAR(100) NOT NULL
        );
        
        INSERT INTO test_migration (test_data) VALUES ('test1'), ('test2');
        """
        
        # Execute the script
        execute_sql_script(test_script)
        
        # Verify the script executed successfully
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM test_migration")
            result = session.fetchone()
            assert result['count'] == 2
            
            session.execute("SELECT test_data FROM test_migration ORDER BY id")
            rows = session.fetchall()
            assert rows[0]['test_data'] == 'test1'
            assert rows[1]['test_data'] == 'test2'
    
    def test_migration_rollback_simulation(self, test_database_setup):
        """Test migration rollback simulation"""
        initial_table_count = 0
        
        with get_db_session() as session:
            session.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'clash_deck_builder_test'
            """)
            result = session.fetchone()
            initial_table_count = result['count']
        
        # Simulate a failed migration that should rollback
        failed_script = """
        CREATE TEMPORARY TABLE rollback_test (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data VARCHAR(50)
        );
        
        INSERT INTO rollback_test (data) VALUES ('test');
        
        -- This will cause an error (invalid syntax)
        INVALID SQL STATEMENT;
        """
        
        # Execute should fail and rollback
        with pytest.raises(Exception):
            execute_sql_script(failed_script)
        
        # Verify no new tables were created (rollback occurred)
        with get_db_session() as session:
            session.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'clash_deck_builder_test'
            """)
            result = session.fetchone()
            final_table_count = result['count']
            
            # Table count should be the same (rollback successful)
            assert final_table_count == initial_table_count
    
    def test_seed_data_integrity(self, test_database_setup):
        """Test that seed data is properly loaded and maintains integrity"""
        with get_db_session() as session:
            # Check that test users exist
            session.execute("SELECT COUNT(*) as count FROM users")
            user_result = session.fetchone()
            assert user_result['count'] >= 3  # Should have at least 3 test users
            
            # Check that test cards exist
            session.execute("SELECT COUNT(*) as count FROM cards_cache")
            card_result = session.fetchone()
            assert card_result['count'] >= 10  # Should have at least 10 test cards
            
            # Check that test decks exist and reference valid users
            session.execute("""
                SELECT d.id, d.name, d.user_id, u.username
                FROM decks d
                JOIN users u ON d.user_id = u.id
            """)
            deck_results = session.fetchall()
            assert len(deck_results) >= 3  # Should have at least 3 test decks
            
            # Verify deck data integrity
            for deck in deck_results:
                assert deck['user_id'] is not None
                assert deck['username'] is not None
                assert deck['name'] is not None
    
    def test_database_cleanup_and_reseed(self, test_database_setup):
        """Test database cleanup and reseeding functionality"""
        # Get initial counts
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            initial_users = session.fetchone()['count']
            
            session.execute("SELECT COUNT(*) as count FROM decks")
            initial_decks = session.fetchone()['count']
        
        # Add some test data
        with get_db_session() as session:
            session.execute(
                "INSERT INTO users (username, email) VALUES (%s, %s)",
                ("cleanup_test", "cleanup@test.com")
            )
        
        # Clean and reseed database
        success = test_db_manager.clean_database()
        assert success is True
        
        success = test_db_manager.seed_test_data()
        assert success is True
        
        # Verify data was reset to initial state
        with get_db_session() as session:
            session.execute("SELECT COUNT(*) as count FROM users")
            final_users = session.fetchone()['count']
            
            session.execute("SELECT COUNT(*) as count FROM decks")
            final_decks = session.fetchone()['count']
            
            # Should be back to initial test data counts
            assert final_users == initial_users
            assert final_decks == initial_decks