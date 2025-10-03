# backend/src/utils/database.py

import logging
from contextlib import contextmanager
from typing import Generator, Optional
import mysql.connector
from mysql.connector import pooling, Error as MySQLError
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager with connection pooling and transaction support."""
    
    def __init__(self):
        self._pool: Optional[pooling.MySQLConnectionPool] = None
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the database connection pool."""
        if self._initialized:
            return
        
        try:
            # Parse database URL to extract connection parameters
            db_config = self._parse_database_url(settings.database_url)
            
            # Create connection pool
            self._pool = pooling.MySQLConnectionPool(
                pool_name="clash_deck_builder_pool",
                pool_size=10,
                pool_reset_session=True,
                **db_config
            )
            
            self._initialized = True
            logger.info("Database connection pool initialized successfully")
            
            # Test the connection
            self._test_connection()
            
        except MySQLError as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def _parse_database_url(self, database_url: str) -> dict:
        """Parse database URL into connection parameters."""
        # Expected format: mysql+mysqlconnector://user:password@host:port/database
        if not database_url.startswith("mysql+mysqlconnector://"):
            raise ValueError("Database URL must start with 'mysql+mysqlconnector://'")
        
        # Remove the protocol part
        url_without_protocol = database_url.replace("mysql+mysqlconnector://", "")
        
        # Split user:password@host:port/database
        if "@" not in url_without_protocol:
            raise ValueError("Database URL must contain user credentials")
        
        credentials, host_db = url_without_protocol.split("@", 1)
        
        if ":" not in credentials:
            raise ValueError("Database URL must contain user:password")
        
        user, password = credentials.split(":", 1)
        
        if "/" not in host_db:
            raise ValueError("Database URL must contain database name")
        
        host_port, database = host_db.split("/", 1)
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host = host_port
            port = 3306
        
        return {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "database": database,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "raise_on_warnings": True
        }
    
    def _test_connection(self) -> None:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                if result[0] != 1:
                    raise MySQLError("Database connection test failed")
                logger.info("Database connection test successful")
        except MySQLError as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[MySQLConnection, None, None]:
        """Get a database connection from the pool."""
        if not self._initialized:
            self.initialize()
        
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
        except MySQLError as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_session(self) -> Generator[MySQLCursor, None, None]:
        """Get a database session with automatic transaction management."""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                yield cursor
                connection.commit()
                logger.debug("Transaction committed successfully")
            except Exception as e:
                connection.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
            finally:
                cursor.close()
    
    @contextmanager
    def get_transaction(self) -> Generator[MySQLCursor, None, None]:
        """Get a database transaction with explicit commit/rollback control."""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                connection.start_transaction()
                yield cursor
                # Note: Caller must explicitly commit or rollback
            except Exception as e:
                connection.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script (for schema initialization)."""
        if not self._initialized:
            self.initialize()
        
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                # Split script into individual statements
                statements = [stmt.strip() for stmt in script.split(';') if stmt.strip()]
                
                for statement in statements:
                    cursor.execute(statement)
                    logger.debug(f"Executed SQL statement: {statement[:50]}...")
                
                connection.commit()
                logger.info("SQL script executed successfully")
            except MySQLError as e:
                connection.rollback()
                logger.error(f"Failed to execute SQL script: {e}")
                raise
            finally:
                cursor.close()
    
    def close(self) -> None:
        """Close all connections in the pool."""
        if self._pool:
            # Note: mysql-connector-python doesn't have a direct way to close the pool
            # The connections will be closed when the pool is garbage collected
            self._pool = None
            self._initialized = False
            logger.info("Database connection pool closed")


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for common operations
@contextmanager
def get_db_connection() -> Generator[MySQLConnection, None, None]:
    """Get a database connection."""
    with db_manager.get_connection() as connection:
        yield connection


@contextmanager
def get_db_session() -> Generator[MySQLCursor, None, None]:
    """Get a database session with automatic transaction management."""
    with db_manager.get_session() as session:
        yield session


@contextmanager
def get_db_transaction() -> Generator[MySQLCursor, None, None]:
    """Get a database transaction with explicit commit/rollback control."""
    with db_manager.get_transaction() as transaction:
        yield transaction


def initialize_database() -> None:
    """Initialize the database connection pool."""
    db_manager.initialize()


def execute_sql_script(script: str) -> None:
    """Execute a SQL script."""
    db_manager.execute_script(script)


def initialize_schema() -> None:
    """Initialize the database schema from schema.sql file."""
    import os
    
    # Get the path to the schema file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, "..", "models", "schema.sql")
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_script = f.read()
        
        execute_sql_script(schema_script)
        logger.info("Database schema initialized successfully")
    except FileNotFoundError:
        logger.error(f"Schema file not found at {schema_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise


def close_database() -> None:
    """Close the database connection pool."""
    db_manager.close()