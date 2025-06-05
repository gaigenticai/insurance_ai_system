"""
Database connection module for the Insurance AI System.
Provides connection pooling and management for PostgreSQL on Railway.com.
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator, Any, Dict, Optional
import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, DictCursor, Json
from psycopg2 import sql
from psycopg2.extensions import register_adapter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Register adapter for dict to JSONB - Keep this fix
register_adapter(dict, Json)

# Get database connection details from environment variables
# Railway.com automatically provides these environment variables
DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
DB_PORT = os.environ.get('POSTGRES_PORT', '5432')
DB_NAME = os.environ.get('POSTGRES_DB', 'insurance_ai')
DB_USER = os.environ.get('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
DB_SCHEMA = os.getenv("DB_SCHEMA", "insurance_ai")

# Connection pool settings
MIN_CONNECTIONS = 1
MAX_CONNECTIONS = 10

# Initialize the connection pool lazily
connection_pool = None

def initialize_db_pool():
    """Initialize the database connection pool"""
    global connection_pool
    
    # Skip initialization if disabled
    if os.getenv('SKIP_DB_INIT', '').lower() == 'true':
        logger.info("Database initialization skipped (SKIP_DB_INIT=true)")
        return
    
    if connection_pool is not None:
        logger.info("Database connection pool already initialized")
        return
    
    try:
        connection_pool = SimpleConnectionPool(
            MIN_CONNECTIONS,
            MAX_CONNECTIONS,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e}")
        connection_pool = None

def close_db_pool():
    """Close the database connection pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None
        logger.info("Database connection pool closed")


@contextmanager
def get_db_connection() -> Generator[Any, None, None]:
    """
    Context manager for database connections.
    Yields a connection from the pool and ensures it's returned properly.
    """
    # Initialize pool if not already done
    if connection_pool is None:
        initialize_db_pool()
    
    connection = None
    try:
        if not connection_pool:
             raise ConnectionError("Database connection pool is not initialized.")
        connection = connection_pool.getconn()
        yield connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if connection:
            connection_pool.putconn(connection)


@contextmanager
def get_db_cursor(commit: bool = False) -> Generator[Any, None, None]:
    """
    Context manager for database cursors.
    Yields a cursor and handles commits and rollbacks.
    
    Args:
        commit: Whether to commit the transaction after operations
    """
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            # Set search path to our schema
            # Use sql.SQL for safety
            cursor.execute(sql.SQL("SET search_path TO {}, public;").format(sql.Identifier(DB_SCHEMA)))
            yield cursor
            if commit:
                connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Database operation error: {e}")
            # Log the specific SQL query and params if available in the exception context
            if hasattr(e, 'diag'):
                logger.error(f"SQLSTATE: {e.diag.sqlstate}, Message: {e.diag.message_primary}")
            if hasattr(cursor, 'query'):
                 logger.error(f"Failed Query: {cursor.query}")
            raise
        finally:
            cursor.close()


def execute_query(query: str, params: Dict = None, commit: bool = False) -> list:
    """
    Execute a SQL query and return the results.
    
    Args:
        query: SQL query string (can be sql.SQL object or plain string)
        params: Query parameters dictionary
        commit: Whether to commit the transaction
        
    Returns:
        List of query results (list of dicts)
    """
    with get_db_cursor(commit=commit) as cursor:
        # Log query safely
        log_query = query.as_string(cursor) if isinstance(query, sql.Composed) else query
        logger.info(f"Executing query: {log_query} with params: {params}")
        cursor.execute(query, params or {})
        if cursor.description:
            # Fetch all results as dictionaries
            return cursor.fetchall()
        return []


def insert_record(table: str, data: Dict, returning: str = "id") -> Optional[Dict]:
    """
    Insert a record into a table and return the specified column.
    Handles dictionary to JSONB adaptation automatically via register_adapter.
    
    Args:
        table: Table name
        data: Dictionary of column names and values
        returning: Column to return after insert (or None)
        
    Returns:
        Dictionary containing the returned column value, or None if returning is None
    """
    if not data:
        logger.warning(f"Attempted to insert empty data into table {table}")
        return None
        
    columns = list(data.keys())
    
    # Use sql module for safe identifiers and placeholders
    returning_clause = sql.SQL(" RETURNING {}").format(sql.Identifier(returning)) if returning else sql.SQL("")
    
    query = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({}){}").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(sql.Placeholder(col) for col in columns),
        returning_clause
    )
    
    with get_db_cursor(commit=True) as cursor:
        try:
            log_query = query.as_string(cursor)
        except Exception:
            log_query = str(query)
        logger.info(f"Executing insert: {log_query} with data: {data}")
        cursor.execute(query, data)
        if returning:
            return cursor.fetchone()
        return None # Return None if not returning anything


def update_record(table: str, id_value: Any, data: Dict, id_column: str = "id") -> bool:
    """
    Update a record in a table.
    Handles dictionary to JSONB adaptation automatically via register_adapter.
    
    Args:
        table: Table name
        id_value: Value of the ID column
        data: Dictionary of column names and values to update
        id_column: Name of the ID column
        
    Returns:
        True if successful (at least one row updated), False otherwise
    """
    if not data:
        logger.warning(f"Attempted to update with empty data for table {table}, id {id_value}")
        return False
    
    # Use sql module for safe identifiers and placeholders
    set_clause = sql.SQL(', ').join(
        sql.SQL("{} = {} ").format(sql.Identifier(col), sql.Placeholder(col))
        for col in data.keys()
    )
    
    query = sql.SQL("UPDATE {}.{} SET {} WHERE {} = %(id_value)s").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        set_clause,
        sql.Identifier(id_column)
    )
    
    # Combine data and id_value for parameters
    params = {**data, "id_value": id_value}
    
    with get_db_cursor(commit=True) as cursor:
        try:
            log_query = query.as_string(cursor)
        except Exception:
            log_query = str(query)
        logger.info(f"Executing update: {log_query} with params: {params}")
        cursor.execute(query, params)
        return cursor.rowcount > 0


def get_record_by_id(table: str, id_value: Any, id_column: str = "id") -> Optional[Dict]:
    """
    Get a single record by its ID.
    
    Args:
        table: Table name
        id_value: Value of the ID column
        id_column: Name of the ID column
        
    Returns:
        Dictionary containing the record data, or None if not found
    """
    params = {"id_value": id_value}
    query = sql.SQL("SELECT * FROM {}.{} WHERE {} = %(id_value)s LIMIT 1").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.Identifier(id_column)
    )
    
    with get_db_cursor() as cursor:
        try:
            log_query = query.as_string(cursor)
        except Exception:
            log_query = str(query)
        logger.info(f"Executing query: {log_query} with params: {params}")
        cursor.execute(query, params)
        return cursor.fetchone() # Fetch one record


def get_records(table: str, conditions: Optional[Dict[str, Any]] = None, schema: str = DB_SCHEMA) -> list:
    """Retrieve records from a table based on optional conditions."""
    
    query_parts = [sql.SQL("SELECT * FROM {}.{}").format(
        sql.Identifier(schema),
        sql.Identifier(table)
    )]
    params = {}
    if conditions:
        where_clauses = []
        for i, (col, val) in enumerate(conditions.items()):
            param_name = f"param_{i}"
            where_clauses.append(sql.SQL("{} = {}").format(
                sql.Identifier(col),
                sql.Placeholder(param_name)
            ))
            params[param_name] = val

        if where_clauses:
            query_parts.append(sql.SQL(" WHERE {}").format(
                sql.SQL(" AND ").join(where_clauses)
            ))

    query = sql.SQL("").join(query_parts)

    with get_db_cursor() as cursor:
        try:
            log_query = query.as_string(cursor)
        except Exception:
            log_query = str(query)
        logger.info(f"Executing query: {log_query} with params: {params}")
        cursor.execute(query, params)
        return cursor.fetchall()


def delete_record(table: str, id_value: Any, id_column: str = "id") -> bool:
    """
    Delete a record from a table.
    
    Args:
        table: Table name
        id_value: Value of the ID column
        id_column: Name of the ID column
        
    Returns:
        True if successful (at least one row deleted), False otherwise
    """
    params = {"id_value": id_value}
    query = sql.SQL("DELETE FROM {}.{} WHERE {} = %(id_value)s").format(
        sql.Identifier(DB_SCHEMA),
        sql.Identifier(table),
        sql.Identifier(id_column)
    )
    
    with get_db_cursor(commit=True) as cursor:
        try:
            log_query = query.as_string(cursor)
        except Exception:
            log_query = str(query)
        logger.info(f"Executing delete: {log_query} with params: {params}")
        cursor.execute(query, params)
        return cursor.rowcount > 0


def execute_custom_query(query: str, params: Dict = None, commit: bool = False) -> list:
    """
    Execute a custom SQL query.
    
    Args:
        query: SQL query string (can be sql.SQL object or plain string)
        params: Query parameters dictionary
        commit: Whether to commit the transaction
        
    Returns:
        List of query results (list of dicts)
    """
    # This function essentially duplicates execute_query, kept for compatibility if used elsewhere
    logger.warning("execute_custom_query is deprecated, use execute_query instead.")
    return execute_query(query, params, commit)


def close_all_connections():
    """Close all database connections in the pool."""
    if connection_pool:
        connection_pool.closeall()
        logger.info("All database connections closed")
    else:
        logger.warning("Attempted to close connections, but pool was not initialized.")

