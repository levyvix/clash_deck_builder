# backend/src/utils/database.py

import logging
import time
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from mysql.connector import pooling, Error as MySQLError
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from .config import get_settings

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom database error for application-specific handling."""
    pass


class ConnectionPoolError(DatabaseError):
    """Error related to connection pool operations."""
    pass


class TransactionError(DatabaseError):
    """Error related to transaction operations."""
    pass


class DatabaseManager:
    """Enhanced database connection manager with connection pooling, retry logic, and comprehensive error handling."""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._pool: Optional[pooling.MySQLConnectionPool] = None
        self._initialized = False
        self._connection_attempts = 0
        self._max_connection_attempts = 5
        self._retry_delay = 2  # seconds
    
    def initialize(self) -> None:
        """Initialize the database connection pool with retry logic."""
        if self._initialized:
            return
        
        for attempt in range(self._max_connection_attempts):
            try:
                self._connection_attempts = attempt + 1
                logger.info(f"Initializing database connection pool (attempt {self._connection_attempts}/{self._max_connection_attempts})")
                
                # Get database configuration from settings
                db_config = self.settings.get_database_config()
                
                # Create connection pool with enhanced configuration
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
                return
                
            except MySQLError as e:
                logger.warning(f"Database connection attempt {self._connection_attempts} failed: {e}")
                if attempt < self._max_connection_attempts - 1:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    time.sleep(self._retry_delay)
                else:
                    logger.error("All database connection attempts failed")
                    raise ConnectionPoolError(f"Failed to initialize database connection pool after {self._max_connection_attempts} attempts: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during database initialization: {e}")
                raise ConnectionPoolError(f"Unexpected error during database initialization: {e}")
    
    def _test_connection(self) -> None:
        """Test database connection and validate schema."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Test basic connectivity
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                if not result or result[0] != 1:
                    raise MySQLError("Database connection test failed")
                
                # Test database exists and is accessible
                cursor.execute("SELECT DATABASE() as current_db")
                db_result = cursor.fetchone()
                current_db = db_result[0] if db_result else None
                
                if current_db != self.settings.db_name:
                    logger.warning(f"Connected to database '{current_db}', expected '{self.settings.db_name}'")
                
                cursor.close()
                logger.info(f"Database connection test successful - connected to '{current_db}'")
                
        except MySQLError as e:
            logger.error(f"Database connection test failed: {e}")
            raise ConnectionPoolError(f"Database connection test failed: {e}")
    
    @contextmanager
    def get_connection(self) -> Generator[MySQLConnection, None, None]:
        """Get a database connection from the pool with automatic retry and error handling."""
        if not self._initialized:
            self.initialize()
        
        connection = None
        try:
            connection = self._pool.get_connection()
            if not connection.is_connected():
                connection.reconnect(attempts=3, delay=1)
            yield connection
            
        except MySQLError as e:
            logger.error(f"Database connection error: {e}")
            # Handle specific MySQL errors
            if e.errno == 2003:  # Can't connect to MySQL server
                raise ConnectionPoolError("Cannot connect to MySQL server - check if database is running")
            elif e.errno == 1045:  # Access denied
                raise ConnectionPoolError("Access denied - check database credentials")
            elif e.errno == 1049:  # Unknown database
                raise ConnectionPoolError(f"Unknown database '{self.settings.db_name}' - check database name")
            else:
                raise DatabaseError(f"Database connection error: {e}")
                
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            raise DatabaseError(f"Unexpected database error: {e}")
            
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_session(self) -> Generator[MySQLCursor, None, None]:
        """Get a database session with automatic transaction management and error handling."""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                yield cursor
                connection.commit()
                logger.debug("Transaction committed successfully")
                
            except MySQLError as e:
                connection.rollback()
                logger.error(f"MySQL error in session, transaction rolled back: {e}")
                # Handle specific MySQL errors
                if e.errno == 1062:  # Duplicate entry
                    raise DatabaseError("Duplicate entry - record already exists")
                elif e.errno == 1452:  # Foreign key constraint fails
                    raise DatabaseError("Foreign key constraint violation")
                elif e.errno == 1406:  # Data too long
                    raise DatabaseError("Data too long for column")
                else:
                    raise TransactionError(f"Database transaction failed: {e}")
                    
            except Exception as e:
                connection.rollback()
                logger.error(f"Unexpected error in session, transaction rolled back: {e}")
                raise TransactionError(f"Transaction failed due to unexpected error: {e}")
                
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
                
            except MySQLError as e:
                connection.rollback()
                logger.error(f"MySQL error in transaction, rolled back: {e}")
                raise TransactionError(f"Transaction failed: {e}")
                
            except Exception as e:
                connection.rollback()
                logger.error(f"Unexpected error in transaction, rolled back: {e}")
                raise TransactionError(f"Transaction failed due to unexpected error: {e}")
                
            finally:
                cursor.close()
    
    def execute_script(self, script: str) -> None:
        """Execute a SQL script with enhanced error handling."""
        if not self._initialized:
            self.initialize()
        
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                # Split script into individual statements
                statements = [stmt.strip() for stmt in script.split(';') if stmt.strip()]
                
                for i, statement in enumerate(statements):
                    try:
                        cursor.execute(statement)
                        logger.debug(f"Executed SQL statement {i+1}/{len(statements)}: {statement[:50]}...")
                    except MySQLError as e:
                        logger.error(f"Failed to execute statement {i+1}: {statement[:100]}...")
                        raise TransactionError(f"SQL script execution failed at statement {i+1}: {e}")
                
                connection.commit()
                logger.info(f"SQL script executed successfully ({len(statements)} statements)")
                
            except MySQLError as e:
                connection.rollback()
                logger.error(f"Failed to execute SQL script: {e}")
                raise TransactionError(f"SQL script execution failed: {e}")
                
            finally:
                cursor.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check."""
        health_status = {
            "status": "unhealthy",
            "database": self.settings.db_name,
            "host": self.settings.db_host,
            "port": self.settings.db_port,
            "pool_initialized": self._initialized,
            "connection_attempts": self._connection_attempts,
            "error": None
        }
        
        try:
            if not self._initialized:
                self.initialize()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Test basic connectivity
                cursor.execute("SELECT 1 as test, NOW() as current_time, VERSION() as version")
                result = cursor.fetchone()
                
                if result:
                    health_status.update({
                        "status": "healthy",
                        "current_time": str(result[1]),
                        "mysql_version": result[2],
                        "connection_test": "passed"
                    })
                
                # Test table existence (basic schema validation)
                cursor.execute("""
                    SELECT COUNT(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (self.settings.db_name,))
                
                table_result = cursor.fetchone()
                if table_result:
                    health_status["table_count"] = table_result[0]
                
                cursor.close()
                
        except Exception as e:
            health_status["error"] = str(e)
            logger.error(f"Database health check failed: {e}")
        
        return health_status
    
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


def get_database_health() -> Dict[str, Any]:
    """Get database health status."""
    return db_manager.health_check()


def close_database() -> None:
    """Close the database connection pool."""
    db_manager.close()