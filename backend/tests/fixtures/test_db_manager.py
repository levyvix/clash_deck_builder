"""
Test database manager for handling test database setup and cleanup
"""
import mysql.connector
from mysql.connector import Error as MySQLError
import logging
import os
from pathlib import Path
from typing import Optional
import time

logger = logging.getLogger(__name__)


class TestDatabaseManager:
    """Manages test database setup, seeding, and cleanup"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 3307,
                 database: str = "clash_deck_builder_test",
                 user: str = "test_user",
                 password: str = "test_password",
                 root_password: str = "test_root_password"):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.root_password = root_password
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        
    def wait_for_database(self, timeout: int = 60) -> bool:
        """Wait for database to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                conn = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user="root",
                    password=self.root_password,
                    database=self.database
                )
                conn.close()
                logger.info("Test database is ready")
                return True
            except MySQLError:
                time.sleep(2)
                continue
        
        logger.error(f"Test database not ready after {timeout} seconds")
        return False
    
    def connect(self) -> bool:
        """Connect to test database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            logger.info("Connected to test database")
            return True
        except MySQLError as e:
            logger.error(f"Failed to connect to test database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from test database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Disconnected from test database")
    
    def clean_database(self) -> bool:
        """Clean all data from test database tables"""
        if not self.connection or not self.connection.is_connected():
            logger.error("Not connected to database")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Disable foreign key checks temporarily
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            # Truncate all tables except schema_migrations
            for (table_name,) in tables:
                if table_name != 'schema_migrations':
                    cursor.execute(f"TRUNCATE TABLE {table_name}")
                    logger.debug(f"Truncated table: {table_name}")
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.connection.commit()
            cursor.close()
            logger.info("Test database cleaned successfully")
            return True
            
        except MySQLError as e:
            logger.error(f"Failed to clean test database: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def seed_test_data(self) -> bool:
        """Seed test database with test data"""
        if not self.connection or not self.connection.is_connected():
            logger.error("Not connected to database")
            return False
        
        try:
            # Load test data SQL file
            fixtures_dir = Path(__file__).parent
            test_data_file = fixtures_dir / "test_data.sql"
            
            if not test_data_file.exists():
                logger.error(f"Test data file not found: {test_data_file}")
                return False
            
            with open(test_data_file, 'r') as f:
                sql_content = f.read()
            
            # Split SQL statements and execute them
            cursor = self.connection.cursor()
            
            # Split by semicolon and filter out empty statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
                    logger.debug(f"Executed: {statement[:50]}...")
            
            self.connection.commit()
            cursor.close()
            logger.info("Test data seeded successfully")
            return True
            
        except MySQLError as e:
            logger.error(f"Failed to seed test data: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def setup_test_database(self) -> bool:
        """Complete test database setup: wait, connect, clean, seed"""
        if not self.wait_for_database():
            return False
        
        if not self.connect():
            return False
        
        if not self.clean_database():
            return False
        
        if not self.seed_test_data():
            return False
        
        logger.info("Test database setup completed successfully")
        return True
    
    def teardown_test_database(self) -> bool:
        """Clean up test database after tests"""
        if not self.connection or not self.connection.is_connected():
            return True
        
        success = self.clean_database()
        self.disconnect()
        return success
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Execute a query and return results"""
        if not self.connection or not self.connection.is_connected():
            raise RuntimeError("Not connected to database")
        
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return []
        finally:
            cursor.close()
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table"""
        result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
        return result[0]['count'] if result else 0


# Global test database manager instance
test_db_manager = TestDatabaseManager()